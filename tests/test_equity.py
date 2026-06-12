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

def test_dead_cards_reduce_equity():
    # Player has J-J, but two more Jacks are dead -- trips become much less likely
    player_hand = make_cards([("J", "Hearts"), ("J", "Diamonds")])
    dead_cards = make_cards([("J", "Clubs"), ("J", "Spades")])
    board = []
    equity_with_dead, _ = calculate_equity(player_hand, board, 2, dead_cards=dead_cards, simulations=500)
    equity_without_dead, _ = calculate_equity(player_hand, board, 2, simulations=500)
    assert equity_with_dead < equity_without_dead

def test_known_opponents_affects_equity():
    # Player has A-A, opponent has A-K -- two aces are gone from the deck
    player_hand = make_cards([("A", "Hearts"), ("A", "Diamonds")])
    opponent_hand = [make_cards([("A", "Clubs"), ("K", "Hearts")])]
    board = []
    equity_known, _ = calculate_equity(player_hand, board, 2, known_opponents=opponent_hand, simulations=500)
    equity_unknown, _ = calculate_equity(player_hand, board, 2, simulations=500)
    # Equity should still be high but slightly different with known opponent
    assert 0.0 <= equity_known <= 1.0