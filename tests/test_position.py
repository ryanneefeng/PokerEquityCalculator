import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import get_acting_order, display_acting_order, remove_folded_positions, handle_folds_before, handle_folds
from unittest.mock import patch
from contextlib import redirect_stdout
import io

def test_preflop_utg_acts_first():
    order = get_acting_order(4, 3, "preflop")
    assert order[0] == 3

def test_preflop_blinds_act_last():
    order = get_acting_order(4, 3, "preflop")
    assert order[-2] == 1  # SB second to last
    assert order[-1] == 2  # BB last

def test_postflop_sb_acts_first():
    order = get_acting_order(4, 1, "postflop")
    assert order[0] == 1

def test_postflop_dealer_acts_last():
    order = get_acting_order(4, 4, "postflop")
    assert order[-1] == 4

def test_preflop_dealer_acts_before_blinds():
    order = get_acting_order(4, 4, "preflop")
    dealer_index = order.index(4)
    sb_index = order.index(1)
    bb_index = order.index(2)
    assert dealer_index < sb_index
    assert dealer_index < bb_index

def test_acting_order_includes_all_players():
    order = get_acting_order(6, 3, "preflop")
    assert len(order) == 6
    assert set(order) == {1, 2, 3, 4, 5, 6}

def test_button_keeps_seat_after_blinds_fold():
    active_positions = [3, 4, 5, 6]
    assert get_acting_order(6, 6, "postflop", active_positions) == [3, 4, 5, 6]
    output = io.StringIO()
    with redirect_stdout(output):
        display_acting_order(6, 6, "postflop", active_positions)
    assert "Dealer [seat 6] (YOU)" in output.getvalue()
    assert "You act 4 of 4" in output.getvalue()

def test_folded_button_does_not_move_to_another_player():
    output = io.StringIO()
    with redirect_stdout(output):
        display_acting_order(6, 5, "postflop", [1, 2, 3, 4, 5])
    assert "Dealer" not in output.getvalue()
    assert "Cutoff [seat 5] (YOU)" in output.getvalue()

def test_preflop_order_omits_folded_seats():
    assert get_acting_order(6, 6, "preflop", [2, 4, 6]) == [4, 6, 2]

def test_heads_up_big_blind_acts_first_postflop():
    assert get_acting_order(2, 1, "preflop") == [1, 2]
    assert get_acting_order(2, 1, "postflop") == [2, 1]

def test_two_survivors_keep_original_multiway_order():
    assert get_acting_order(6, 6, "postflop", [1, 6]) == [1, 6]

def test_folded_seats_must_be_active_opponents():
    active_positions = [1, 2, 3, 6]
    with patch('builtins.input', side_effect=['6', '5', 'bad', '1', '1', '2']), redirect_stdout(io.StringIO()):
        remove_folded_positions(2, active_positions, 6)
    assert active_positions == [3, 6]

def test_everyone_folding_leaves_only_your_seat():
    active_positions = [1, 3, 6]
    with patch('builtins.input') as user_input:
        remove_folded_positions(2, active_positions, 6)
    assert active_positions == [6]
    user_input.assert_not_called()

def test_folds_before_action_update_active_seats_and_count():
    active_positions = [1, 2, 3, 4, 5, 6]
    with patch('builtins.input', side_effect=['y', '1', '2', 'n']), redirect_stdout(io.StringIO()):
        num_players, known, dead = handle_folds_before(6, [], [], set(), active_positions, 6)
    assert num_players == 5
    assert active_positions == [1, 3, 4, 5, 6]

def test_folds_after_action_update_active_seats_and_count():
    active_positions = [1, 2, 3, 4, 5, 6]
    with patch('builtins.input', side_effect=['y', '1', '1', 'n']), redirect_stdout(io.StringIO()):
        num_players, known, dead = handle_folds(6, [], [], set(), active_positions, 6)
    assert num_players == 5
    assert active_positions == [2, 3, 4, 5, 6]
