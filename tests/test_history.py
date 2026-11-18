import io
import json
import sqlite3
import tempfile
from contextlib import closing, contextmanager, redirect_stdout
from pathlib import Path
from unittest.mock import patch

import main
import src.session as session
from src.deck import Card
from src.pots import create_players


@contextmanager
def database():
    with tempfile.TemporaryDirectory() as temp, patch.object(session, "DB_FILE", str(Path(temp) / "session.db")):
        yield


def decision(action="call", recommendation="Call", street="River"):
    return dict(street=street, board=[], equity=.5, recommendation=recommendation, player_action=action,
                pot_size=100, bet_to_call=20, stack_before=100, contribution_before=0,
                chips_added=20, stack_after=80, raise_to=None, players={})


def log(**kwargs):
    return session.log_hand([], [], 2, .5, "", "", True, **kwargs)


def test_migration_preserves_old_hands_and_removes_empty_action_follow_credit():
    with database():
        with closing(sqlite3.connect(session.DB_FILE)) as conn, conn:
            conn.execute("""CREATE TABLE hands (id INTEGER PRIMARY KEY, date TEXT, hole_cards TEXT, board TEXT,
                num_players INTEGER, final_equity REAL, recommendation TEXT, player_action TEXT,
                followed_recommendation INTEGER, won INTEGER)""")
            conn.execute("INSERT INTO hands VALUES (1, 'old', 'cards', '', 2, 50, '', '', 1, 1)")
        session.initialize_db()
        session.initialize_db()
        with closing(sqlite3.connect(session.DB_FILE)) as conn, conn:
            assert conn.execute("SELECT id, date, hole_cards, won, followed_recommendation, payout FROM hands").fetchone() == (
                1, "old", "cards", 1, None, None)
        assert session.get_stats()["evaluated_hands"] == 0


def test_each_decision_is_saved_in_order_and_last_action_is_retained():
    with database():
        hand_id = log(history=[decision("call", "Raise", "Pre-Flop"), decision("raise", "Raise", "Flop"),
                               decision("fold", "Fold", "Flop")], outcome="folded", contribution=100, payout=0)
        with closing(sqlite3.connect(session.DB_FILE)) as conn, conn:
            assert conn.execute("SELECT sequence, street, player_action FROM decisions ORDER BY sequence").fetchall() == [
                (1, "Pre-Flop", "call"), (2, "Flop", "raise"), (3, "Flop", "fold")]
            assert conn.execute("SELECT id, recommendation, player_action, followed_recommendation, net_profit FROM hands").fetchone() == (
                hand_id, "Fold", "fold", 0, -100)
        stats = session.get_stats()
        assert stats["decision_count"] == 3
        assert stats["decision_follow_rate"] == 66.7


def test_empty_and_unrecognized_actions_are_not_counted_as_decisions():
    for recommendation, action in [("Call", ""), ("", ""), ("No action (All-In)", ""), ("Call", "all")]:
        assert session.recommendation_followed(recommendation, action) is None
    assert session.recommendation_followed("Raise Small or Call", "call") == 1
    assert session.recommendation_followed("Raise if confident or Check", "check") == 1
    with database():
        log(history=[])
        log(history=[decision()])
        stats = session.get_stats()
        assert stats["total_hands"] == 2
        assert stats["evaluated_hands"] == 1
        assert stats["follow_rate"] == 100


def test_unknown_payout_does_not_become_zero_profit_and_splits_are_distinct():
    with database():
        log(history=[], outcome="split", contribution=100, payout=50,
            pots=[{"amount": 200, "eligible": [1, 2], "payout": 50}])
        log(history=[], outcome="won", contribution=100, payout=None)
        with closing(sqlite3.connect(session.DB_FILE)) as conn, conn:
            rows = conn.execute("SELECT outcome, payout, net_profit, pots_json FROM hands ORDER BY id").fetchall()
        assert rows[0][:3] == ("split", 50, -50)
        assert json.loads(rows[0][3])[0]["payout"] == 50
        assert rows[1][:3] == ("won", None, None)
        assert session.get_stats()["measured_hands"] == 1
        assert session.get_stats()["net_profit"] == -50
        assert session.get_stats()["splits"] == 1


def test_failed_decision_insert_rolls_back_whole_hand():
    with database():
        try:
            log(history=[{"recommendation": "Call", "player_action": "call"}])
        except KeyError:
            pass
        else:
            raise AssertionError("Malformed history must fail")
        with closing(sqlite3.connect(session.DB_FILE)) as conn, conn:
            assert conn.execute("SELECT COUNT(*) FROM hands").fetchone()[0] == 0


def test_invalid_payouts_and_contributions_are_rejected():
    with database():
        for value in [-1, float("nan"), float("inf")]:
            for key in ("payout", "contribution"):
                try:
                    log(**{key: value})
                except ValueError:
                    pass
                else:
                    raise AssertionError("Invalid money must be rejected")


def test_call_raise_fold_on_one_street_retains_every_decision():
    hand = [Card("A", "Hearts"), Card("K", "Diamonds")]
    board = [Card("2", "Hearts"), Card("3", "Diamonds"), Card("7", "Clubs"), Card("8", "Spades"), Card("9", "Hearts")]
    inputs = ["n", "300", "100", "1000", "0", "100", "call", "n", "y",
              "n", "500", "100", "100", "raise", "300", "n", "y",
              "n", "900", "200", "200", "fold"]
    history = []
    with patch("builtins.input", side_effect=inputs), redirect_stdout(io.StringIO()), \
         patch("main.calculate_equity", return_value=(.8, 0)):
        result = main.run_betting_round("River", 3, [], [], set(hand + board), hand, board,
                                       False, None, None, big_blind=2, decision_history=history)
    assert result["status"] == "folded"
    assert [d["player_action"] for d in history] == ["call", "raise", "fold"]
    assert [d["chips_added"] for d in history] == [100, 200, 0]
    assert [d["stack_after"] for d in history] == [900, 700, 700]
    assert history[1]["raise_to"] == 300


def test_all_in_runout_does_not_erase_the_preflop_call():
    hand = [Card("A", "Hearts"), Card("K", "Diamonds")]
    inputs = ["1", "1", "0", "50", "50", "50", "0", "0", "50", "0", "0", "50", "call",
              "cards", "2", "1", "A Clubs", "", "2 Hearts", "3 Diamonds", "7 Clubs",
              "cards", "2", "1", "K Spades", "", "8 Spades", "", "9 Hearts", "split", "50"]
    with database(), patch("builtins.input", side_effect=inputs), redirect_stdout(io.StringIO()), \
         patch("src.pots.calculate_equity", return_value=(.5, 0)), \
         patch("main.project_pot_equity", return_value=([], .5)):
        main.continuous_game(2, hand, used_cards=set(hand))
        with closing(sqlite3.connect(session.DB_FILE)) as conn, conn:
            assert conn.execute("SELECT player_action, outcome, payout, net_profit FROM hands").fetchone() == (
                "call", "split", 50, 0)
            assert conn.execute("SELECT street, player_action, stack_after FROM decisions").fetchall() == [
                ("Pre-Flop", "call", 0)]
            seats = json.loads(conn.execute("SELECT players_json FROM hands").fetchone()[0])
            assert seats["2"]["hand"] == ["A of Clubs", "K of Spades"]


def test_settlement_records_each_pot_and_does_not_count_refunds_as_profit():
    players = create_players(3)
    for seat, amount in enumerate([200, 50, 100], 1):
        players[seat].update(contribution=amount, street_contribution=amount, stack=0, seen=True)
    with patch("builtins.input", side_effect=["50", "100"]), redirect_stdout(io.StringIO()):
        result = main.get_settlement(players, 1, 0, "split")
    assert result["contribution"] == 100  # $100 of the original $200 is uncalled.
    assert result["payout"] == 150
    assert [p["payout"] for p in result["pots"]] == [50, 100]


def test_unknown_ante_cost_and_unknown_payout_stay_unknown():
    players = create_players(2)
    for player in players.values():
        player.update(contribution=50, street_contribution=50, stack=0, seen=True)
    with patch("builtins.input", side_effect=["", ""]), redirect_stdout(io.StringIO()):
        result = main.get_settlement(players, 1, 10, "split")
    assert result["contribution"] is None
    assert result["payout"] is None


def test_optional_payout_rejects_nonfinite_negative_and_over_pot_values():
    with patch("builtins.input", side_effect=["nan", "inf", "-1", "101", "50"]), redirect_stdout(io.StringIO()):
        assert main.get_optional_money("payout", 100) == 50


def test_zero_payout_is_reentered_for_a_reported_split():
    players = create_players(2)
    for player in players.values():
        player.update(contribution=50, street_contribution=50, stack=0, seen=True)
    with patch("builtins.input", side_effect=["0", "50"]), redirect_stdout(io.StringIO()):
        assert main.get_settlement(players, 1, 0, "split")["payout"] == 50


def test_inconsistent_outcome_or_pot_payout_is_rejected():
    with database():
        cases = [dict(outcome="lost", payout=1), dict(outcome="split", payout=0),
                 dict(payout=100, pots=[{"amount": 50, "payout": 100}]),
                 dict(payout=100, pots=[{"amount": 200, "payout": 50}])]
        for kwargs in cases:
            try:
                log(**kwargs)
            except ValueError:
                pass
            else:
                raise AssertionError("Contradictory settlement must fail")
