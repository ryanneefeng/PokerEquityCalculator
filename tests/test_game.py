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

def test_zero_stack_preflop_does_not_try_to_display_five_cards():
    hand = [Card("A", "Hearts"), Card("K", "Diamonds")]
    output = io.StringIO()
    with patch('builtins.input', side_effect=['n', '100', '0', '0', 'n']), redirect_stdout(output), \
         patch('main.calculate_equity', return_value=(0.5, 0)), \
         patch('main.best_hand_cards') as best_cards, patch('main.get_player_action') as action:
        result = main.run_betting_round('Pre-Flop', 2, [], [], set(hand), hand, [], False, None, None)
    assert result['status'] == 'continue'
    assert result['is_all_in'] is True
    assert "A-K Offsuit" in output.getvalue()
    assert "Best 5:" not in output.getvalue()
    best_cards.assert_not_called()
    action.assert_not_called()

def test_existing_preflop_all_in_only_asks_for_pot_and_folds():
    hand = [Card("A", "Hearts"), Card("K", "Diamonds")]
    with patch('builtins.input', side_effect=['n', '100', 'n']) as user_input, redirect_stdout(io.StringIO()), \
         patch('main.calculate_equity', return_value=(0.5, 0)), \
         patch('main.get_player_action') as action, patch('main.ask_action_reopened') as reopened:
        result = main.run_betting_round('Pre-Flop', 2, [], [], set(hand), hand, [], True, 100, 0)
    assert result['is_all_in'] is True
    assert user_input.call_count == 3
    action.assert_not_called()
    reopened.assert_not_called()

def test_all_in_flop_still_displays_best_five():
    hand = [Card("A", "Hearts"), Card("K", "Diamonds")]
    board = [Card("2", "Hearts"), Card("3", "Diamonds"), Card("7", "Clubs")]
    output = io.StringIO()
    with patch('builtins.input', side_effect=['n', '100', 'n']), redirect_stdout(output), \
         patch('main.calculate_equity', return_value=(0.5, 0)):
        result = main.run_betting_round('Flop', 2, [], [], set(hand + board), hand, board, True, 100, 0)
    assert result['is_all_in'] is True
    assert "Best 5:" in output.getvalue()

def test_preflop_all_in_can_run_through_every_street():
    hand = [Card("A", "Hearts"), Card("K", "Diamonds")]
    inputs = ['1', '100', '0', '0', 'n',
              '', '2 Hearts', '3 Diamonds', '7 Clubs', 'n', '100', 'n',
              '', '8 Spades', 'n', '100', 'n',
              '', '9 Hearts', 'n', '100', 'n', 'y']
    output = io.StringIO()
    with patch('builtins.input', side_effect=inputs), redirect_stdout(output), \
         patch('main.calculate_equity', return_value=(0.5, 0)) as calculation, \
         patch('main.get_player_action') as action, patch('main.log_hand') as log:
        main.continuous_game(2, hand, used_cards=set(hand))
    assert [len(call.args[1]) for call in calculation.call_args_list] == [0, 3, 4, 5]
    assert "Best 5:" not in output.getvalue().split('-- FLOP --')[0]
    assert output.getvalue().count("Best 5:") == 3
    assert len(log.call_args.args[1]) == 5
    assert log.call_args.args[-1] is True
    action.assert_not_called()
