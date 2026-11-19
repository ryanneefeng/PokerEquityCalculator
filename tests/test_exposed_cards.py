import io
import random
from contextlib import redirect_stdout
from unittest.mock import patch

import main
from src.deck import Card, Deck
from src.equity import calculate_equity, monte_carlo_equity, exact_equity_river, project_next_street
from src.evaluator import best_hand
from src.pots import create_players, calculate_pot_equity


HAND = [Card("K", "Clubs"), Card("K", "Diamonds")]
BOARD = [Card("2", "Hearts"), Card("3", "Diamonds"), Card("7", "Clubs"), Card("8", "Spades"), Card("9", "Hearts")]
ACE = Card("A", "Hearts")


def test_exact_river_completes_a_single_exposed_card_uniformly():
    equity, tie = calculate_equity(HAND, BOARD, 2, known_opponents=[[ACE]])
    # Only the three remaining aces improve this opponent enough to beat kings.
    assert abs(equity - 41 / 44) < 1e-12
    assert tie == 0


def test_exact_turn_partial_hand_matches_independent_ordered_deals():
    board = BOARD[:4]
    remaining = [card for card in Deck().cards if card not in HAND + board + [ACE]]
    wins = ties = total = 0
    for river in remaining:
        hero_score = best_hand(HAND + board + [river])
        for second_card in remaining:
            if second_card == river:
                continue
            opponent_score = best_hand([ACE, second_card] + board + [river])
            wins += hero_score > opponent_score
            ties += hero_score == opponent_score
            total += 1
    equity, tie = calculate_equity(HAND, board, 2, known_opponents=[[ACE]])
    assert abs(equity - (wins + ties / 2) / total) < 1e-12
    assert abs(tie - ties / total) < 1e-12


def test_monte_carlo_partial_hand_agrees_with_exact_river():
    state = random.getstate()
    try:
        random.seed(20261118)
        equity, tie = monte_carlo_equity(HAND, BOARD, 2, [[ACE]], [], simulations=1000)
    finally:
        random.setstate(state)
    assert abs(equity - 41 / 44) < .04
    assert tie == 0


def test_multiway_partial_hands_keep_exposed_cards_and_deal_distinct_completions():
    exposed = [[ACE], [Card("Q", "Diamonds")]]
    calls = []

    def inspect(hand_and_board):
        calls.append(list(hand_and_board))
        return 1, [0]

    with patch("src.equity.best_hand", side_effect=inspect):
        equity, tie = monte_carlo_equity(HAND, [], 3, exposed, [], simulations=3)
    assert abs(equity - 1 / 3) < 1e-12
    assert tie == 1
    for start in range(0, len(calls), 3):
        hero, first, second = calls[start:start + 3]
        assert first[0] == ACE
        assert second[0] == exposed[1][0]
        dealt = hero + first[:2] + second[:2]
        assert len(dealt) == len(set(dealt))
        assert hero[2:] == first[2:] == second[2:]


def test_partial_hand_projection_removes_the_exposed_card_from_board_candidates():
    seen = []
    def estimate(board):
        seen.append(board)
        return .5
    project_next_street(HAND, BOARD[:4], 2, [[ACE]], [], 1, equity_calculator=estimate)
    assert all(ACE not in board for board in seen)


def test_direct_exact_multiway_supports_one_partial_but_rejects_two_incomplete_hands():
    full = [Card("Q", "Clubs"), Card("Q", "Diamonds")]
    equity, tie = exact_equity_river(HAND, BOARD, 3, [[ACE], full], [])
    assert abs(equity - 39 / 42) < 1e-12
    assert tie == 0
    try:
        exact_equity_river(HAND, BOARD, 3, [[ACE], [full[0]]], [])
    except ValueError:
        pass
    else:
        raise AssertionError("Two incomplete exact hands must be rejected")


def test_card_entry_rejects_duplicate_cards_and_can_complete_a_live_hand_later():
    players = create_players(2)
    used = set(HAND + BOARD)
    with patch("builtins.input", side_effect=["1", "2", "3", "1", "K Clubs", "A Hearts"]), redirect_stdout(io.StringIO()):
        main.get_exposed_cards(players, 1, used)
    assert players[2]["hand"] == [ACE]
    assert not players[2]["folded"]
    with patch("builtins.input", side_effect=["2", "2", "1", "Q Hearts"]), redirect_stdout(io.StringIO()):
        main.get_exposed_cards(players, 1, used)
    assert players[2]["hand"] == [ACE, Card("Q", "Hearts")]
    assert set(players[2]["hand"]) <= used


def test_exposed_all_in_opponent_stays_live():
    players = create_players(2)
    players[2]["stack"] = 0
    with patch("builtins.input", side_effect=["2", "2", "A Hearts", "A Clubs"]), redirect_stdout(io.StringIO()):
        main.get_exposed_cards(players, 1, set(HAND))
    assert not players[2]["folded"]
    assert players[2]["stack"] == 0


def test_known_folder_keeps_cards_attached_to_seat_and_removed_from_other_pots():
    players = create_players(3)
    for player in players.values():
        player.update(contribution=50, street_contribution=50, stack=100, seen=True)
    players[2]["hand"] = [ACE, Card("Q", "Clubs")]
    active = [1, 2, 3]
    with patch("builtins.input", side_effect=["y", "1", "2"]), redirect_stdout(io.StringIO()):
        count, known, dead = main.handle_folds(3, [], [], set(HAND + BOARD + players[2]["hand"]), active, 1, players)
    assert count == 2 and active == [1, 3]
    with patch("src.pots.calculate_equity", return_value=(.5, 0)) as calculate:
        calculate_pot_equity(HAND, BOARD, players, 1, dead)
    assert set(calculate.call_args.kwargs["dead_cards"]) == set(players[2]["hand"])
    assert calculate.call_args.kwargs["known_opponents"] == []


def test_partial_known_hand_is_removed_when_ineligible_for_side_pot():
    players = create_players(3)
    for seat, amount in enumerate([100, 50, 100], 1):
        players[seat].update(contribution=amount, street_contribution=amount, stack=0, seen=True)
    players[2]["hand"] = [ACE]
    with patch("src.pots.calculate_equity", return_value=(.5, 0)) as calculate:
        calculate_pot_equity(HAND, BOARD, players, 1)
    assert calculate.call_args_list[0].kwargs["known_opponents"] == [[ACE]]
    assert calculate.call_args_list[1].kwargs["dead_cards"] == [ACE]


def test_single_mode_cards_command_keeps_partial_opponent_live():
    inputs = ["1", "2", "K Clubs", "K Diamonds", "5", "2 Hearts", "3 Diamonds", "7 Clubs", "8 Spades", "9 Hearts",
              "cards", "2", "1", "A Hearts", "n", "100", "20", "500", "1", "0", "0", "40",
              "y", "20", "40", "500", "20", "n"]
    with patch("builtins.input", side_effect=inputs), redirect_stdout(io.StringIO()), \
         patch("src.pots.calculate_equity", return_value=(.9, 0)) as calculate:
        main.main()
    assert calculate.call_args.args[2] == 2
    assert calculate.call_args.kwargs["known_opponents"] == [[ACE]]


def test_folded_partial_card_can_be_recorded_as_dead_without_a_second_card():
    players = create_players(3)
    players[2]["folded"] = True
    with patch("builtins.input", side_effect=["2", "1", "A Hearts"]), redirect_stdout(io.StringIO()):
        main.get_exposed_cards(players, 1, set(HAND + BOARD))
    assert players[2]["folded"] and players[2]["hand"] == [ACE]
