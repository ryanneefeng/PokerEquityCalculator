import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.decision import get_recommendation

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
