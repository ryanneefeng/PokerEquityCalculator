import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import io
from contextlib import redirect_stdout
from unittest.mock import patch
import main
from src.deck import Card
from src.pots import create_players

def make_players(contributions, stacks):
    players = create_players(len(contributions))
    for p, amount in enumerate(contributions, 1):
        players[p].update({'contribution': amount, 'street_contribution': amount,
                           'stack': stacks[p - 1], 'seen': True})
    return players

def run_tracked_round(players, inputs):
    hand = [Card('A', 'Hearts'), Card('K', 'Diamonds')]
    board = [Card('2', 'Hearts'), Card('3', 'Diamonds'), Card('7', 'Clubs'), Card('8', 'Spades'), Card('9', 'Hearts')]
    output = io.StringIO()
    with patch('builtins.input', side_effect=inputs) as user_input, redirect_stdout(output), \
         patch('src.pots.calculate_equity', return_value=(0.8, 0)):
        result = main.run_betting_round('River', len(players), [], [], set(hand + board), hand, board,
                                       False, None, None, position=1, big_blind=2, players=players)
    return result, output.getvalue(), user_input.call_count

def test_lone_all_in_opponent_does_not_create_a_betting_turn():
    players = make_players([50, 50], [500, 0])
    result, output, prompts = run_tracked_round(players, [])
    assert prompts == 0
    assert result['prev_stack'] == 500
    assert result['is_all_in'] is False
    assert 'no opponent can bet' in output
    assert 'What did you do?' not in output

def test_calling_an_all_in_is_allowed_but_raising_is_not():
    players = make_players([20, 50], [500, 0])
    result, output, prompts = run_tracked_round(players, ['70', '0', '50', 'raise', 'call'])
    assert result['player_action'] == 'call'
    assert result['prev_stack'] == 470
    assert result['prev_pot'] == 100
    assert 'Raising is not available' in output

def test_funded_players_can_bet_into_side_pot_around_all_in():
    players = make_players([50, 50, 50], [500, 0, 500])
    result, output, prompts = run_tracked_round(players, ['n', '150', '0', '50', '50', 'raise', '100', 'n', '100'])
    assert result['player_action'] == 'raise'
    assert result['prev_stack'] == 450
    assert result['prev_pot'] == 250
    assert players[2]['contribution'] == 50
    assert players[3]['contribution'] == 100

def test_hero_all_in_tracks_opponent_side_bets_without_asking_hero_to_act():
    players = make_players([50, 50, 50], [0, 500, 500])
    result, output, prompts = run_tracked_round(players, ['n', '100', '100'])
    assert result['is_all_in'] is True
    assert result['prev_pot'] == 250
    assert 'Side pot 1: $100.0 -- you are not eligible' in output
    assert 'What did you do?' not in output

def test_short_call_returns_uncalled_excess_to_opponent():
    players = make_players([0, 100], [50, 0])
    result, output, prompts = run_tracked_round(players, ['100', '100', '100', 'call'])
    assert result['is_all_in'] is True
    assert result['prev_pot'] == 100
    assert players[2]['stack'] == 50
    assert players[2]['contribution'] == 50
    assert 'Uncalled $50.0 returned to seat 2' in output

def test_legal_raise_above_short_opponent_capacity_returns_excess():
    players = make_players([0, 100], [1000, 50])
    result, output, prompts = run_tracked_round(players, ['n', '100', '100', '100', '100', 'raise', '200', 'n', '150'])
    assert result['prev_stack'] == 850
    assert result['prev_pot'] == 300
    assert players[1]['contribution'] == 150
    assert players[2]['stack'] == 0
    assert 'Uncalled $50.0 returned to seat 1' in output

def test_snapshot_mismatch_can_be_corrected_without_duplicating_chips():
    players = create_players(2)
    players[1]['stack'] = 100
    players[1]['street_contribution'] = 10
    inputs = ['0', '10', '0', '100', '0', '20', '0', '100']
    with patch('builtins.input', side_effect=inputs), redirect_stdout(io.StringIO()):
        total = main.get_player_updates(players, 1, expected_pot=30)
    assert total == 30
    assert players[1]['contribution'] == 10
    assert players[2]['contribution'] == 20

def test_folded_player_final_chips_stay_in_pot():
    players = make_players([50, 50, 50], [100, 100, 100])
    players[3]['folded'] = True
    players[3]['needs_update'] = True
    with patch('builtins.input', side_effect=['50', '70']), redirect_stdout(io.StringIO()):
        total = main.get_player_updates(players, 1)
    assert total == 170
    assert players[3]['stack'] == 80
    assert players[3]['contribution'] == 70

def test_all_in_seat_cannot_be_selected_as_folder():
    players = make_players([50, 50, 50], [100, 0, 100])
    active = [1, 2, 3]
    inputs = ['y', '2', '1', '2', '3', 'n']
    with patch('builtins.input', side_effect=inputs), redirect_stdout(io.StringIO()):
        count, known, dead = main.handle_folds(3, [], [], set(), active, 1, players)
    assert count == 2
    assert active == [1, 2]
    assert players[2]['folded'] is False
    assert players[3]['folded'] is True

def test_all_in_players_leave_acting_order_but_stay_live():
    players = make_players([50, 50, 50], [100, 0, 100])
    assert main.get_acting_order(3, 1, 'postflop', [1, 2, 3], players) == [1, 3]
    assert players[2]['folded'] is False

def test_displaying_all_in_hero_does_not_crash():
    players = make_players([50, 50], [0, 100])
    output = io.StringIO()
    with redirect_stdout(output):
        main.display_acting_order(2, 1, 'postflop', [1, 2], players)
    assert 'no betting turn' in output.getvalue()
    assert 'All-in seats still in the hand: [1]' in output.getvalue()

def test_lone_funded_opponent_cannot_add_an_uncontested_bet():
    players = make_players([50, 20], [0, 100])
    with patch('builtins.input', side_effect=['60', '50']) as user_input, redirect_stdout(io.StringIO()):
        main.get_player_updates(players, 1)
    assert players[2]['street_contribution'] == 50
    assert players[2]['stack'] == 70
    assert user_input.call_count == 2

def test_incomplete_opponent_response_must_be_finished_before_next_street():
    players = make_players([100, 20], [100, 100])
    with patch('builtins.input', side_effect=['20', 'y', '100']), redirect_stdout(io.StringIO()):
        total, stack = main.finish_betting_round(players, 1)
    assert total == 200
    assert players[2]['stack'] == 20

def test_opponent_raise_automatically_returns_action_without_yes_no_prompt():
    players = make_players([20, 20], [500, 500])
    inputs = ['n', '40', '0', '20', '20', 'check', 'n', '50',
              '30', 'call', 'n', '50']
    result, output, prompts = run_tracked_round(players, inputs)
    assert result['prev_stack'] == 470
    assert result['prev_pot'] == 100
    assert output.count('Action:') == 2
    assert 'Action returns' in output

def test_short_all_in_return_uses_funded_opponent_and_raising_rights_separately():
    players = make_players([100, 100, 100], [1000, 30, 1000])
    inputs = ['n', '300', '0', '100', '100', '100', 'check', 'n', '130', '130',
              '100', 'raise', 'call', 'n', '130']
    result, output, prompts = run_tracked_round(players, inputs)
    assert result['prev_stack'] == 970
    assert result['prev_pot'] == 390
    assert players[2]['stack'] == 0
    assert 'extra amount is less than a full raise' in output
    assert 'Raising is not available' in output

def test_ante_only_all_in_player_never_gets_a_betting_turn():
    players = make_players([0, 100, 100], [0, 0, 0])
    hand = [Card('2', 'Clubs'), Card('3', 'Diamonds')]
    board = [Card(rank, 'Hearts') for rank in ['A', 'K', 'Q', 'J', '10']]
    output = io.StringIO()
    with patch('builtins.input') as user_input, redirect_stdout(output):
        result = main.run_betting_round('River', 3, [], [], set(hand + board), hand, board,
                                       True, 230, 0, position=1, players=players, dead_money=30)
    user_input.assert_not_called()
    assert result['is_all_in'] is True
    assert 'Main pot: $30' in output.getvalue()
    assert 'Side pot 1: $200.0 -- you are not eligible' in output.getvalue()
