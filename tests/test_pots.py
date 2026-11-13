import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.deck import Card
from src.pots import create_players, add_chips, build_side_pots, return_uncalled_chips
from src.pots import calculate_pot_equity, calculate_call_equity, get_call_amount, get_opponent_limit
from src.decision import get_recommendation

def make_players(contributions, stacks=None, folded=None):
    players = create_players(len(contributions))
    for position, amount in enumerate(contributions, 1):
        players[position].update({
            'contribution': amount, 'street_contribution': amount,
            'stack': stacks[position - 1] if stacks else 0,
            'folded': position in (folded or []), 'seen': True,
        })
    return players

def test_short_stack_cannot_win_deeper_side_pot():
    pots, refunds = build_side_pots(make_players([50, 200, 200]))
    assert pots == [{'amount': 150, 'eligible': [1, 2, 3]}, {'amount': 300, 'eligible': [2, 3]}]
    assert refunds == {}

def test_multiple_all_in_levels_make_separate_pots():
    pots, refunds = build_side_pots(make_players([25, 50, 100, 100]))
    assert pots == [{'amount': 100, 'eligible': [1, 2, 3, 4]},
                    {'amount': 75, 'eligible': [2, 3, 4]}, {'amount': 100, 'eligible': [3, 4]}]
    assert refunds == {}

def test_folded_money_stays_but_folder_cannot_win():
    pots, refunds = build_side_pots(make_players([50, 100, 100], folded=[3]))
    assert pots == [{'amount': 150, 'eligible': [1, 2]}, {'amount': 100, 'eligible': [2]}]
    assert refunds == {}

def test_folded_contribution_does_not_make_an_unnecessary_pot():
    pots, refunds = build_side_pots(make_players([100, 100, 20], folded=[3]))
    assert pots == [{'amount': 220, 'eligible': [1, 2]}]

def test_uncalled_excess_is_not_a_side_pot():
    pots, refunds = build_side_pots(make_players([50, 200, 100]))
    assert pots == [{'amount': 150, 'eligible': [1, 2, 3]}, {'amount': 100, 'eligible': [2, 3]}]
    assert refunds == {2: 100}

def test_returning_uncalled_chips_restores_stack():
    players = make_players([100, 60], stacks=[0, 0])
    refunds = return_uncalled_chips(players)
    assert refunds == {1: 40}
    assert players[1]['stack'] == 40
    assert players[1]['contribution'] == 60
    assert players[1]['street_contribution'] == 60

def test_ante_money_is_contested_without_matching_individual_antes():
    pots, refunds = build_side_pots(make_players([50, 200, 200]), dead_money=30)
    assert pots[0] == {'amount': 180, 'eligible': [1, 2, 3]}
    assert pots[1] == {'amount': 300, 'eligible': [2, 3]}

def test_player_all_in_for_only_ante_can_only_win_ante_pot():
    pots, refunds = build_side_pots(make_players([0, 100, 100]), dead_money=30)
    assert pots == [{'amount': 30, 'eligible': [1, 2, 3]}, {'amount': 200, 'eligible': [2, 3]}]

def test_money_is_conserved_with_fractional_contributions():
    players = make_players([0.10, 0.30, 0.20])
    pots, refunds = build_side_pots(players, dead_money=0.05)
    assert round(sum(pot['amount'] for pot in pots) + sum(refunds.values()), 2) == 0.65
    assert refunds == {2: 0.1}

def test_all_in_opponents_still_set_the_call_amount():
    players = make_players([20, 50, 100], stacks=[500, 0, 0])
    assert get_call_amount(players, 1) == 80
    assert get_opponent_limit(players, 1) == 0

def test_only_live_funded_opponents_can_contest_another_raise():
    players = make_players([20, 50, 100], stacks=[500, 30, 1000], folded=[3])
    assert get_call_amount(players, 1) == 30
    assert get_opponent_limit(players, 1) == 80

def test_short_big_blind_does_not_lower_bring_in_with_two_funded_players():
    players = make_players([1, 0.5, 0], stacks=[100, 0, 100])
    assert get_call_amount(players, 3, big_blind=2, preflop=True) == 2

def test_no_extra_blind_is_paid_against_lone_short_all_in():
    players = make_players([1, 0.5], stacks=[100, 0])
    assert get_call_amount(players, 1, big_blind=2, preflop=True) == 0

def test_adding_chips_updates_both_contributions_and_stack():
    players = make_players([20, 20], stacks=[100, 100])
    add_chips(players[1], 30)
    assert players[1]['contribution'] == 50
    assert players[1]['street_contribution'] == 50
    assert players[1]['stack'] == 70

def test_contribution_cannot_exceed_stack():
    players = make_players([20, 20], stacks=[10, 100])
    try:
        add_chips(players[1], 20)
    except ValueError:
        pass
    else:
        assert False, 'An over-stack contribution was accepted'
    assert players[1]['contribution'] == 20

def test_all_boards_split_only_the_pots_you_are_eligible_for():
    hand = [Card('2', 'Clubs'), Card('3', 'Diamonds')]
    board = [Card(rank, 'Hearts') for rank in ['A', 'K', 'Q', 'J', '10']]
    result = calculate_pot_equity(hand, board, make_players([50, 200, 200]), 1, simulations=30)
    assert result['eligible_pot'] == 150
    assert abs(result['expected_return'] - 50) < 0.000001
    assert result['pots'][1]['equity'] == 0

def test_you_can_lose_main_pot_but_win_side_pot():
    players = make_players([100, 50, 100])
    hand = [Card('K', 'Clubs'), Card('K', 'Diamonds')]
    board = [Card('2', 'Hearts'), Card('3', 'Diamonds'), Card('7', 'Clubs'), Card('8', 'Spades'), Card('9', 'Hearts')]
    players[2]['hand'] = [Card('A', 'Clubs'), Card('A', 'Diamonds')]
    players[3]['hand'] = [Card('Q', 'Clubs'), Card('Q', 'Diamonds')]
    result = calculate_pot_equity(hand, board, players, 1, simulations=10)
    assert result['pots'][0]['equity'] == 0
    assert result['pots'][1]['equity'] == 1
    assert result['expected_return'] == 100
    assert result['equity'] == 0.4

def test_short_call_uses_eligible_money_not_large_opponent_side_pot():
    players = make_players([0, 200, 200], stacks=[50, 0, 0])
    hand = [Card('2', 'Clubs'), Card('3', 'Diamonds')]
    board = [Card(rank, 'Hearts') for rank in ['A', 'K', 'Q', 'J', '10']]
    result = calculate_call_equity(hand, board, players, 1, 200, simulations=30)
    assert result['call_amount'] == 50
    assert result['eligible_pot'] == 150
    assert result['decision_pot'] == 100
    assert players[1]['contribution'] == 0
    action, explanation = get_recommendation(result['equity'], result['tie_rate'], result['decision_pot'], 200, 50)
    assert action == 'Call (All-In)'
    assert '33.3%' in explanation

def test_two_way_side_split_and_three_way_main_split_are_weighted():
    hand = [Card('2', 'Clubs'), Card('3', 'Diamonds')]
    board = [Card(rank, 'Hearts') for rank in ['A', 'K', 'Q', 'J', '10']]
    result = calculate_pot_equity(hand, board, make_players([200, 50, 200]), 1, simulations=30)
    assert abs(result['expected_return'] - 200) < 0.000001
    assert abs(result['equity'] - 200 / 450) < 0.000001
    assert result['tie_rate'] == 1

def test_large_side_pot_does_not_justify_a_losing_short_call():
    players = make_players([0, 200, 200], stacks=[50, 0, 0])
    hand = [Card('A', 'Hearts'), Card('K', 'Hearts')]
    board = [Card('2', 'Hearts'), Card('7', 'Hearts'), Card('3', 'Clubs'), Card('8', 'Spades')]
    players[2]['hand'] = [Card('A', 'Spades'), Card('A', 'Clubs')]
    players[3]['hand'] = [Card('Q', 'Clubs'), Card('Q', 'Diamonds')]
    result = calculate_call_equity(hand, board, players, 1, 200, simulations=1000)
    assert result['expected_return'] < 50
    action, explanation = get_recommendation(result['equity'], result['tie_rate'], result['decision_pot'], 200, 50)
    assert action == 'Fold'

def test_known_ineligible_cards_are_removed_from_side_pot_simulation():
    from unittest.mock import patch
    players = make_players([100, 50, 100])
    hand = [Card('A', 'Hearts'), Card('K', 'Hearts')]
    players[2]['hand'] = [Card('Q', 'Clubs'), Card('Q', 'Diamonds')]
    players[3]['hand'] = [Card('J', 'Clubs'), Card('J', 'Diamonds')]
    board = [Card('2', 'Hearts'), Card('7', 'Hearts'), Card('3', 'Clubs')]
    with patch('src.pots.calculate_equity', return_value=(0.5, 0)) as calculation:
        calculate_pot_equity(hand, board, players, 1)
    side_call = calculation.call_args_list[1]
    assert side_call.args[2] == 2
    assert set(side_call.kwargs['dead_cards']) == set(players[2]['hand'])
    assert side_call.kwargs['known_opponents'] == [players[3]['hand']]

def test_pot_amounts_and_eligible_money_match_independent_caps():
    import random
    rng = random.Random(125)
    for i in range(100):
        contributions = [rng.randint(1, 500) for p in range(4)]
        players = make_players(contributions)
        pots, refunds = build_side_pots(players, dead_money=10)
        assert sum(pot['amount'] for pot in pots) + sum(refunds.values()) == sum(contributions) + 10
        hero_cap = min(contributions[0], max(contributions[1:]))
        expected = hero_cap + sum(min(amount, contributions[0]) for amount in contributions[1:]) + 10
        assert sum(pot['amount'] for pot in pots if 1 in pot['eligible']) == expected

def test_unmatched_wager_from_a_previous_street_is_not_silently_refunded():
    players = make_players([100, 60])
    players[1]['street_contribution'] = 0
    try:
        return_uncalled_chips(players)
    except ValueError:
        pass
    else:
        assert False, 'An inconsistent earlier-street wager was accepted'
    assert players[1]['contribution'] == 100

def test_last_live_hand_wins_contested_money_after_folds():
    pots, refunds = build_side_pots(make_players([50, 100, 100], folded=[2, 3]))
    assert pots == [{'amount': 250, 'eligible': [1]}]
    assert refunds == {}

def test_only_ante_all_in_player_has_no_claim_to_betting_pot():
    hand = [Card('2', 'Clubs'), Card('3', 'Diamonds')]
    board = [Card(rank, 'Hearts') for rank in ['A', 'K', 'Q', 'J', '10']]
    result = calculate_pot_equity(hand, board, make_players([0, 100, 100]), 1, simulations=30, dead_money=30)
    assert result['eligible_pot'] == 30
    assert abs(result['expected_return'] - 10) < 0.000001

def test_short_big_blind_call_separates_required_commitment_from_matched_cost():
    players = make_players([0, 0.5, 0], stacks=[100, 0, 100])
    hand = [Card('2', 'Clubs'), Card('3', 'Diamonds')]
    board = [Card(rank, 'Hearts') for rank in ['A', 'K', 'Q', 'J', '10']]
    result = calculate_call_equity(hand, board, players, 1, 2, simulations=10)
    assert result['call_amount'] == 2
    assert result['call_refund'] == 1.5
    assert result['call_cost'] == 0.5
    assert result['eligible_pot'] == 1
    action, explanation = get_recommendation(result['equity'], result['tie_rate'], result['decision_pot'], 2, 100,
                                            can_raise=False, call_cost=result['call_cost'])
    assert action == 'Call'
    assert '50.0%' in explanation

def test_existing_uncalled_chips_are_not_subtracted_from_new_call_cost_twice():
    players = make_players([1, 0.5, 0], stacks=[100, 0, 100])
    hand = [Card('2', 'Clubs'), Card('3', 'Diamonds')]
    board = [Card(rank, 'Hearts') for rank in ['A', 'K', 'Q', 'J', '10']]
    result = calculate_call_equity(hand, board, players, 1, 1, simulations=10)
    assert result['call_refund'] == 1
    assert result['call_cost'] == 0
    assert result['decision_pot'] == 1
