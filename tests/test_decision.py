import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.decision import get_recommendation, min_raise

def test_profitable_all_in_call_uses_pot_odds():
    action, explanation = get_recommendation(0.30, 0, 1000, 100, 100)
    assert action == "Call (All-In)"
    assert "9.1%" in explanation

def test_unprofitable_all_in_call_is_folded():
    action, explanation = get_recommendation(0.40, 0, 101, 100, 100)
    assert action == "Fold"
    assert "49.8%" in explanation

def test_break_even_all_in_call():
    action, explanation = get_recommendation(0.25, 0, 75, 25, 25)
    assert action == "Call (All-In)"

def test_cheap_call_has_no_minimum_equity_floor():
    action, explanation = get_recommendation(0.19, 0, 1000, 10, 500)
    assert action == "Call"

def test_call_below_pot_odds_is_folded():
    action, explanation = get_recommendation(0.29, 0, 100, 50, 500)
    assert action == "Fold"

def test_tie_share_is_not_added_to_equity_twice():
    action, explanation = get_recommendation(0.20, 0.40, 100, 50, 500)
    assert action == "Fold"

def test_high_tie_rate_still_needs_correct_pot_odds():
    action, explanation = get_recommendation(0.45, 0.90, 101, 100, 500)
    assert action == "Fold"

def test_certain_split_can_be_checked():
    action, explanation = get_recommendation(0.5, 1.0, 100, 0, 500)
    assert action == "Check"
    assert "on the board" not in explanation

def test_certain_split_with_good_price_is_called():
    action, explanation = get_recommendation(0.5, 1.0, 100, 10, 500)
    assert action == "Call"

def test_certain_split_with_bad_price_is_folded():
    action, explanation = get_recommendation(1 / 3, 1.0, 100, 100, 500)
    assert action == "Fold"

def test_all_in_call_amount_cannot_exceed_stack():
    action, explanation = get_recommendation(0.8, 0, 200, 100, 30)
    assert action == "Call (All-In)"
    assert "$30" in explanation
    assert "$100" not in explanation

def test_weak_hand_can_check_when_no_bet_is_faced():
    action, explanation = get_recommendation(0.19, 0, 100, 0, 500)
    assert action == "Check"

def test_minimum_reraise_uses_last_increment():
    assert min_raise(30, 0, last_raise=20, big_blind=2) == 50

def test_minimum_opening_bet_is_big_blind():
    assert min_raise(0, 0.9, last_raise=1, big_blind=1) == 1

def test_short_all_in_does_not_reduce_next_raise_increment():
    assert min_raise(130, 0, last_raise=100, big_blind=2) == 230

def test_raise_over_short_opening_adds_a_full_increment():
    assert min_raise(0.5, 0, last_raise=1, big_blind=1) == 1.5

def test_raise_recommendation_counts_chips_already_committed():
    action, explanation = get_recommendation(0.7, 0, 100, 20, 50,
                                            current_contribution=40, last_raise=20, big_blind=2)
    assert action == 'Raise'
    assert '$80' in explanation

def test_big_blind_option_recommends_a_raise_over_the_blind():
    action, explanation = get_recommendation(0.7, 0, 3, 0, 100,
                                            current_contribution=2, last_raise=2, big_blind=2)
    assert action == 'Raise'
    assert '$4' in explanation

def test_recommended_short_raise_is_an_all_in():
    action, explanation = get_recommendation(0.7, 0, 100, 20, 30,
                                            current_contribution=40, last_raise=20, big_blind=2)
    assert action == 'Raise'
    assert 'All-In' in explanation

def test_strong_equity_cannot_recommend_a_raise_without_raising_rights():
    action, explanation = get_recommendation(0.99, 0, 300, 30, 500,
                                            current_contribution=100, last_raise=100, big_blind=2, can_raise=False)
    assert action == 'Call'
    assert 'has not reopened' in explanation

def test_lack_of_raising_rights_does_not_force_a_bad_call():
    action, explanation = get_recommendation(0.1, 0, 100, 50, 500, can_raise=False)
    assert action == 'Fold'

def test_no_raising_rights_with_no_bet_recommends_check():
    action, explanation = get_recommendation(0.99, 0, 100, 0, 500, can_raise=False)
    assert action == 'Check'

def test_minimum_raise_rounds_currency_before_comparing():
    assert min_raise(0.1, 0, last_raise=0.2, big_blind=0.05) == 0.3
