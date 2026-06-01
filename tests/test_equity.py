import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.deck import Card
from src.equity import calculate_equity

def make_cards(card_list):
    return [Card(rank, suit) for rank, suit in card_list]

def test_equity_returns_valid_range():
    player_hand = make_cards([("A", "Hearts"), ("A", "Diamonds")])
    board = []
    equity, tie_rate = calculate_equity(player_hand, board, 2, simulations=500)
    assert 0.0 <= equity <= 1.0
    assert 0.0 <= tie_rate <= 1.0

def test_pocket_aces_beat_trash_hand():
    aces = make_cards([("A", "Hearts"), ("A", "Diamonds")])
    trash = make_cards([("2", "Hearts"), ("7", "Diamonds")])
    board = []
    aces_equity, _ = calculate_equity(aces, board, 2, simulations=500)
    trash_equity, _ = calculate_equity(trash, board, 2, simulations=500)
    assert aces_equity > trash_equity

def test_equity_with_board():
    player_hand = make_cards([("A", "Hearts"), ("A", "Diamonds")])
    board = make_cards([("A", "Clubs"), ("K", "Hearts"), ("2", "Spades")])
    equity, tie_rate = calculate_equity(player_hand, board, 2, simulations=500)
    assert equity > 0.80

def test_tie_rate_heads_up_identical_board():
    player_hand = make_cards([("2", "Hearts"), ("3", "Diamonds")])
    board = make_cards([("A", "Clubs"), ("A", "Hearts"), ("A", "Spades"), ("A", "Diamonds"), ("K", "Clubs")])
    equity, tie_rate = calculate_equity(player_hand, board, 2, simulations=500)
    assert tie_rate > 0.0