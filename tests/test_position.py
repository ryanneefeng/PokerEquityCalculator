import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import get_acting_order

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