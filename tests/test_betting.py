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
    with patch('builtins.input', side_effect=['n', '100', '20', '500', 'check', 'fold']), \
         redirect_stdout(io.StringIO()), patch('main.calculate_equity', return_value=(0.5, 0)):
        result = main.run_betting_round('River', 2, [], [], set(hand + board), hand, board, False, None, None)
    assert result['status'] == 'folded'
    assert result['player_action'] == 'fold'
