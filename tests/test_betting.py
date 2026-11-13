import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import io
from contextlib import redirect_stdout
from unittest.mock import patch
import main
from src.deck import Card

def test_check_facing_bet_is_rejected():
    with patch('builtins.input', side_effect=['check', 'call']) as user_input, redirect_stdout(io.StringIO()):
        action = main.get_player_action('Call', 20, 100)
    assert action == 'call'
    assert user_input.call_count == 2

def test_call_with_no_bet_is_rejected():
    with patch('builtins.input', side_effect=['call', 'check']) as user_input, redirect_stdout(io.StringIO()):
        action = main.get_player_action('Check', 0, 100)
    assert action == 'check'
    assert user_input.call_count == 2

def test_raise_without_raising_rights_is_rejected():
    with patch('builtins.input', side_effect=['raise', 'fold']) as user_input, redirect_stdout(io.StringIO()):
        action = main.get_player_action('Call', 30, 100, can_raise=False)
    assert action == 'fold'
    assert user_input.call_count == 2

def test_raise_with_only_enough_chips_to_call_is_rejected():
    with patch('builtins.input', side_effect=['raise', 'call']) as user_input, redirect_stdout(io.StringIO()):
        action = main.get_player_action('Call (All-In)', 20, 20)
    assert action == 'call'
    assert user_input.call_count == 2

def test_short_stack_can_call_all_in():
    with patch('builtins.input', return_value='call'), redirect_stdout(io.StringIO()):
        action = main.get_player_action('Call (All-In)', 100, 30)
    assert action == 'call'

def test_free_check_is_accepted():
    with patch('builtins.input', return_value='check'), redirect_stdout(io.StringIO()):
        action = main.get_player_action('Check', 0, 100)
    assert action == 'check'

def test_betting_round_does_not_end_on_an_illegal_check():
    hand = [Card('A', 'Hearts'), Card('K', 'Diamonds')]
    board = [Card('2', 'Hearts'), Card('3', 'Diamonds'), Card('7', 'Clubs'), Card('8', 'Spades'), Card('9', 'Hearts')]
    with patch('builtins.input', side_effect=['n', '100', '20', '500', '0', '20', 'check', 'fold']), \
         redirect_stdout(io.StringIO()), patch('main.calculate_equity', return_value=(0.5, 0)):
        result = main.run_betting_round('River', 2, [], [], set(hand + board), hand, board, False, None, None)
    assert result['status'] == 'folded'
    assert result['player_action'] == 'fold'

def test_raise_amount_below_minimum_is_rejected():
    with patch('builtins.input', side_effect=['40', '50']) as user_input, redirect_stdout(io.StringIO()):
        amount = main.get_raise_amount(30, 10, 100, 20, 2)
    assert amount == 50
    assert user_input.call_count == 2

def test_short_raise_is_allowed_only_for_entire_stack():
    with patch('builtins.input', side_effect=['35', '40']) as user_input, redirect_stdout(io.StringIO()):
        amount = main.get_raise_amount(30, 10, 30, 20, 2)
    assert amount == 40
    assert user_input.call_count == 2

def test_raise_cannot_exceed_available_chips_or_equal_a_call():
    with patch('builtins.input', side_effect=['120', '30', '50']) as user_input, redirect_stdout(io.StringIO()):
        amount = main.get_raise_amount(30, 10, 100, 20, 2)
    assert amount == 50
    assert user_input.call_count == 3

def test_opening_bet_must_reach_big_blind():
    with patch('builtins.input', side_effect=['0.90', '1.00']) as user_input, redirect_stdout(io.StringIO()):
        amount = main.get_raise_amount(0, 0, 100, 1, 1)
    assert amount == 1
    assert user_input.call_count == 2

def test_short_opening_all_in_is_allowed():
    with patch('builtins.input', return_value='0.50'), redirect_stdout(io.StringIO()):
        amount = main.get_raise_amount(0, 0, 0.5, 1, 1)
    assert amount == 0.5

def test_nonfinite_raise_amounts_are_rejected():
    with patch('builtins.input', side_effect=['nan', 'inf', '-10', '50']) as user_input, redirect_stdout(io.StringIO()):
        amount = main.get_raise_amount(30, 10, 100, 20, 2)
    assert amount == 50
    assert user_input.call_count == 4

def test_betting_info_uses_total_wager_and_valid_full_increment():
    with patch('builtins.input', side_effect=['10', '1', '40', '20']) as user_input, redirect_stdout(io.StringIO()):
        contribution, last_raise = main.get_betting_info(20, 2)
    assert contribution == 10
    assert last_raise == 20
    assert user_input.call_count == 4

def test_big_blind_option_uses_existing_blind_contribution():
    with patch('builtins.input', return_value='2'), redirect_stdout(io.StringIO()):
        contribution, last_raise = main.get_betting_info(0, 2)
    assert contribution == 2
    assert last_raise == 2

def run_river_actions(inputs, big_blind=2):
    hand = [Card('A', 'Hearts'), Card('K', 'Diamonds')]
    board = [Card('2', 'Hearts'), Card('3', 'Diamonds'), Card('7', 'Clubs'), Card('8', 'Spades'), Card('9', 'Hearts')]
    output = io.StringIO()
    with patch('builtins.input', side_effect=inputs), redirect_stdout(output), \
         patch('main.calculate_equity', return_value=(0.8, 0)), \
         patch('main.get_recommendation', wraps=main.get_recommendation) as recommendations:
        result = main.run_betting_round('River', 3, [], [], set(hand + board), hand, board,
                                       False, None, None, big_blind=big_blind)
    raising_rights = [call.args[-1] for call in recommendations.call_args_list]
    return result, output.getvalue(), raising_rights

def test_short_all_in_requires_another_decision_without_allowing_raise():
    inputs = ['n', '300', '100', '1000', '0', '100', 'call', 'n', 'y',
              'n', '430', '30', '100', 'raise', 'call', 'n', 'n']
    result, output, raising_rights = run_river_actions(inputs)
    assert raising_rights == [True, False]
    assert result['player_action'] == 'call'
    assert result['prev_stack'] == 870
    assert result['prev_pot'] == 460
    assert 'Raising is not available' in output

def test_full_raise_reopens_raising_and_counts_prior_call():
    inputs = ['n', '300', '100', '1000', '0', '100', 'call', 'n', 'y',
              'n', '500', '100', '100', 'raise', '300', 'n', 'n']
    result, output, raising_rights = run_river_actions(inputs)
    assert raising_rights == [True, True]
    assert result['player_action'] == 'raise'
    assert result['prev_stack'] == 700
    assert result['prev_pot'] == 700

def test_check_followed_by_full_bet_allows_check_raise():
    inputs = ['n', '100', '0', '500', '0', 'check', 'n', 'y',
              'n', '200', '100', '100', 'raise', '200', 'n', 'n']
    result, output, raising_rights = run_river_actions(inputs)
    assert raising_rights == [True, True]
    assert result['prev_stack'] == 300
    assert result['prev_pot'] == 400

def test_check_followed_by_short_opening_only_allows_call_or_fold():
    inputs = ['n', '100', '0', '500', '0', 'check', 'n', 'y',
              'n', '120', '20', 'raise', 'call', 'n', 'n']
    result, output, raising_rights = run_river_actions(inputs, big_blind=100)
    assert raising_rights == [True, False]
    assert result['prev_stack'] == 480
    assert 'Raising is not available' in output

def test_first_action_keeps_raising_rights_when_facing_short_raise():
    inputs = ['n', '330', '30', '500', '100', '100', 'raise', '230', 'n', 'n']
    result, output, raising_rights = run_river_actions(inputs, big_blind=100)
    assert raising_rights == [True]
    assert result['prev_stack'] == 370

def test_cumulative_short_all_ins_can_reopen_raising():
    inputs = ['n', '300', '100', '1000', '0', '100', 'call', 'n', 'y',
              'n', '600', '100', '100', 'raise', '300', 'n', 'n']
    result, output, raising_rights = run_river_actions(inputs)
    assert raising_rights == [True, True]
    assert result['prev_stack'] == 700

def test_calling_a_short_raise_resets_your_reopening_threshold():
    inputs = ['n', '300', '100', '1000', '0', '100', 'call', 'n', 'y',
              'n', '430', '30', '100', 'call', 'n', 'y',
              'n', '600', '70', '100', 'raise', 'call', 'n', 'n']
    result, output, raising_rights = run_river_actions(inputs)
    assert raising_rights == [True, False, False]
    assert result['prev_stack'] == 800
    assert result['prev_pot'] == 670

def test_full_opening_then_short_raise_still_allows_check_raise():
    inputs = ['n', '100', '0', '500', '0', 'check', 'n', 'y',
              'n', '330', '130', '100', 'raise', '230', 'n', 'n']
    result, output, raising_rights = run_river_actions(inputs)
    assert raising_rights == [True, True]
    assert result['prev_stack'] == 270

def test_your_bet_sets_the_full_increment_for_returning_action():
    inputs = ['n', '100', '0', '1000', '0', 'raise', '100', 'n', 'y',
              'n', '330', '30', '30', '100', 'call', 'n', 'n']
    result, output, raising_rights = run_river_actions(inputs)
    assert raising_rights == [True, False]
    assert result['prev_stack'] == 870
    assert 'allowed range' in output

def test_calling_last_chips_does_not_ask_for_another_action():
    inputs = ['n', '300', '100', '30', '0', '100', 'call', 'n']
    result, output, raising_rights = run_river_actions(inputs)
    assert result['is_all_in'] is True
    assert result['prev_stack'] == 0
    assert result['prev_pot'] == 330

def test_short_all_in_raise_does_not_ask_for_another_action():
    inputs = ['n', '100', '20', '30', '10', '20', 'raise', '40', 'n']
    result, output, raising_rights = run_river_actions(inputs)
    assert result['is_all_in'] is True
    assert result['prev_stack'] == 0
    assert result['prev_pot'] == 130

def test_fractional_minimum_raise_is_not_rejected_by_float_rounding():
    with patch('builtins.input', return_value='0.30') as user_input, redirect_stdout(io.StringIO()):
        amount = main.get_raise_amount(0.1, 0, 1, 0.2, 0.05)
    assert amount == 0.3
    assert user_input.call_count == 1

def test_returned_action_uses_recorded_stack_without_asking_again():
    with patch('builtins.input', side_effect=['200', '30']) as user_input, redirect_stdout(io.StringIO()):
        pot, bet, stack = main.get_pot_info(remaining_stack=80)
    assert (pot, bet, stack) == (200, 30, 80)
    assert user_input.call_count == 2

def test_no_extra_wager_does_not_create_another_decision():
    inputs = ['n', '100', '0', '500', '0', 'check', 'n', 'y', 'n', '100', '0']
    result, output, raising_rights = run_river_actions(inputs)
    assert raising_rights == [True]
    assert result['player_action'] == 'check'
