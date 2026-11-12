import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import io
from contextlib import redirect_stdout
from unittest.mock import patch
import main
from src.deck import Card

def test_button_can_reach_flop_after_an_opponent_folds():
    hand = [Card("A", "Hearts"), Card("K", "Diamonds")]
    inputs = ['6', 'n', '100', '20', '500', 'call', 'y', '1', '1', 'n', 'n',
              '', '2 Hearts', '3 Diamonds', '7 Clubs', 'n', '200', '0', '480', 'fold']
    output = io.StringIO()
    with patch('builtins.input', side_effect=inputs), redirect_stdout(output), \
         patch('main.calculate_equity', return_value=(0.5, 0)) as calculation, \
         patch('main.project_next_street', return_value=([], 0.5)), patch('main.log_hand') as log:
        main.continuous_game(6, hand, used_cards=set(hand))
    assert [call.args[2] for call in calculation.call_args_list] == [6, 5]
    assert "Dealer [seat 6] (YOU)" in output.getvalue()
    assert "You act 5 of 5" in output.getvalue()
    assert log.call_args.args[2] == 5

def test_single_mode_shown_folder_is_removed_from_simulation():
    inputs = ['1', '3', 'A Hearts', 'K Diamonds', '5', '2 Hearts', '3 Diamonds',
              '7 Clubs', '8 Spades', '9 Hearts', 'y', '1', '4 Spades', '5 Spades',
              '100', '10', '500', 'n']
    with patch('builtins.input', side_effect=inputs), redirect_stdout(io.StringIO()), \
         patch('main.calculate_equity', return_value=(0.5, 0)) as calculation:
        main.main()
    assert calculation.call_args.args[2] == 2
    assert calculation.call_args.kwargs['dead_cards'] == [Card("4", "Spades"), Card("5", "Spades")]

def test_single_mode_multiple_shown_folders_are_removed():
    inputs = ['1', '4', 'A Hearts', 'K Diamonds', '0', 'y', '2',
              '4 Spades', '5 Spades', '6 Clubs', '7 Clubs', '100', '10', '500', 'n']
    with patch('builtins.input', side_effect=inputs), redirect_stdout(io.StringIO()), \
         patch('main.calculate_equity', return_value=(0.5, 0)) as calculation:
        main.main()
    assert calculation.call_args.args[2] == 2
    assert len(calculation.call_args.kwargs['dead_cards']) == 4

def test_single_mode_everyone_folding_ends_without_simulation():
    inputs = ['1', '2', 'A Hearts', 'K Diamonds', '0', 'y', '1', 'n']
    with patch('builtins.input', side_effect=inputs), redirect_stdout(io.StringIO()), \
         patch('main.calculate_equity') as calculation:
        main.main()
    calculation.assert_not_called()
