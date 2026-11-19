import io
from contextlib import redirect_stdout
from copy import deepcopy
from unittest.mock import patch

import main
from src.deck import Card
from src.pots import create_players, project_pot_equity
from src.equity import project_next_street


HAND = [Card("K", "Clubs"), Card("2", "Diamonds")]
BOARD = [Card("A", suit) for suit in ("Hearts", "Diamonds", "Clubs", "Spades")]


def players_with_pots(contributions, stacks=None):
    players = create_players(len(contributions))
    for seat, amount in enumerate(contributions, 1):
        players[seat].update(contribution=amount, street_contribution=amount,
                             stack=stacks[seat - 1] if stacks else 0, seen=True)
    players[2]["hand"] = [Card("K", "Diamonds"), Card("3", "Spades")]
    players[3]["hand"] = [Card("Q", "Clubs"), Card("4", "Spades")]
    return players


def test_display_results_prints_projections_and_labels_sampling_uncertainty():
    output = io.StringIO()
    with redirect_stdout(output):
        main.display_results(.7, 0, 100, 0, 500, HAND, BOARD,
                             [(Card("K", "Hearts"), .4)], .7)
    assert "Key cards next street" in output.getvalue()
    assert "Monte Carlo estimates" in output.getvalue()
    assert "sampling noise" in output.getvalue()
    assert "Sampled baseline: 70.0%" in output.getvalue()
    assert "K of Hearts -> 40.0% (-30.0 percentage points)" in output.getvalue()


def test_next_card_projection_excludes_all_known_and_dead_cards():
    known = [[Card("Q", "Hearts"), Card("J", "Hearts")]]
    dead = [Card("10", "Hearts")]
    boards = []

    def estimate(board):
        boards.append(board)
        return .5

    projections, base = project_next_street(HAND, BOARD, 2, known, dead, 1, equity_calculator=estimate)
    assert base == .5
    assert len(projections) == 5
    assert len(boards) == 1 + 52 - len(HAND + BOARD + known[0] + dead)
    assert all(board[-1] not in HAND + BOARD + known[0] + dead for board in boards[1:])


def test_pot_projections_weight_main_and_side_pot_split_shares():
    players = players_with_pots([100, 50, 100])
    original = deepcopy(players)
    projections, base = project_pot_equity(HAND, BOARD, players, 1, simulations=10)
    by_card = dict(projections)
    for suit in ("Hearts", "Spades"):
        # A king on the board splits the main pot three ways and side pot two ways.
        assert abs(by_card[Card("K", suit)] - .4) < 1e-9
    assert all(abs(equity - .7) < 1e-9 for card, equity in projections if card.rank != "K")
    assert .4 <= base <= .7 + 1e-9
    assert players == original


def test_projection_short_call_excludes_deeper_ineligible_side_pot():
    players = players_with_pots([0, 200, 200], [50, 0, 0])
    original = deepcopy(players)
    projections, base = project_pot_equity(HAND, BOARD, players, 1, 200, simulations=10)
    assert all(abs(equity - (1 / 3 if card.rank == "K" else .5)) < 1e-9
               for card, equity in projections)
    assert players == original


def test_pot_projection_removes_folded_cards_even_when_already_recorded_dead():
    players = players_with_pots([100, 50, 100])
    players[2]["folded"] = True
    seen_boards = []

    def calculate(hand, board, *args, **kwargs):
        seen_boards.append(board)
        return .5, 0

    with patch("src.pots.monte_carlo_equity", side_effect=calculate):
        project_pot_equity(HAND, BOARD, players, 1, dead_cards=players[2]["hand"], simulations=1)
    assert all(board[-1] not in players[2]["hand"] for board in seen_boards)


def test_tracked_betting_round_shows_eligible_pot_projections():
    players = players_with_pots([100, 50, 100], [500, 0, 500])
    for player in players.values():
        player["street_contribution"] = 0
    output = io.StringIO()
    with patch("builtins.input", side_effect=["n", "250", "0", "0", "check", "n", "0"]), \
         redirect_stdout(output), patch("src.pots.calculate_equity", return_value=(.5, 0)), \
         patch("main.project_pot_equity", return_value=([(Card("K", "Hearts"), .4)], .7)) as project:
        result = main.run_betting_round("Turn", 3, [], [], set(HAND + BOARD), HAND, BOARD,
                                       False, None, None, show_projections=True, players=players, position=1)
    assert result["player_action"] == "check"
    assert "Key cards next street" in output.getvalue()
    assert project.call_args.args[2] is players


def test_all_in_runout_still_displays_projections_without_a_decision():
    players = players_with_pots([100, 50, 100])
    output = io.StringIO()
    with patch("builtins.input") as user_input, redirect_stdout(output), \
         patch("src.pots.calculate_equity", return_value=(.5, 0)), \
         patch("main.project_pot_equity", return_value=([(Card("K", "Hearts"), .4)], .7)):
        result = main.run_betting_round("Turn", 3, [], [], set(HAND + BOARD), HAND, BOARD,
                                       True, None, None, show_projections=True, players=players, position=1)
    assert result["is_all_in"] is True
    assert "Key cards next street" in output.getvalue()
    user_input.assert_not_called()


def test_single_mode_flop_displays_projections():
    inputs = ["1", "2", "K Clubs", "2 Diamonds", "3", "A Hearts", "A Diamonds", "A Clubs", "n",
              "100", "0", "500", "1", "0", "0", "50", "y", "0", "50", "500", "n"]
    output = io.StringIO()
    with patch("builtins.input", side_effect=inputs), redirect_stdout(output), \
         patch("src.pots.calculate_equity", return_value=(.5, 0)), \
         patch("main.project_pot_equity", return_value=([(Card("K", "Hearts"), .8)], .5)) as project:
        main.main()
    project.assert_called_once()
    assert "Key cards next street" in output.getvalue()


def test_no_next_street_projection_on_preflop_or_river():
    players = players_with_pots([100, 50, 100])
    assert project_pot_equity(HAND, [], players, 1) == []
    assert project_pot_equity(HAND, BOARD + [Card("9", "Hearts")], players, 1) == []
