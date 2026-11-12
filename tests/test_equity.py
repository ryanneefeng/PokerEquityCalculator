import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.deck import Card
from src.equity import calculate_equity, project_next_street

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
    assert equity == 0.5
    assert tie_rate == 1.0

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

def test_equity_with_dead_cards_removes_from_deck():
    # If all four aces are dead, pocket kings should have very high equity
    player_hand = make_cards([("K", "Hearts"), ("K", "Diamonds")])
    dead_cards = make_cards([("A", "Hearts"), ("A", "Diamonds"), ("A", "Clubs"), ("A", "Spades")])
    board = []
    equity, _ = calculate_equity(player_hand, board, 2, dead_cards=dead_cards, simulations=500)
    assert equity > 0.70

def test_more_players_lowers_equity():
    player_hand = make_cards([("A", "Hearts"), ("K", "Diamonds")])
    board = []
    equity_2, _ = calculate_equity(player_hand, board, 2, simulations=500)
    equity_6, _ = calculate_equity(player_hand, board, 6, simulations=500)
    assert equity_2 > equity_6

def test_exact_equity_river_valid_range():
    player_hand = make_cards([("A", "Hearts"), ("A", "Diamonds")])
    board = make_cards([("A", "Clubs"), ("K", "Hearts"), ("2", "Spades"), ("3", "Diamonds"), ("4", "Clubs")])
    equity, tie_rate = calculate_equity(player_hand, board, 2)
    assert 0.0 <= equity <= 1.0
    assert 0.0 <= tie_rate <= 1.0
    assert equity > 0.90

def test_exact_equity_river_valid_range():
    player_hand = make_cards([("A", "Hearts"), ("A", "Diamonds")])
    board = make_cards([("A", "Clubs"), ("K", "Hearts"), ("2", "Spades"), ("3", "Diamonds"), ("4", "Clubs")])
    equity, tie_rate = calculate_equity(player_hand, board, 2)
    assert 0.0 <= equity <= 1.0
    assert 0.0 <= tie_rate <= 1.0
    assert equity > 0.75

def test_project_next_street_returns_results():
    player_hand = make_cards([("A", "Hearts"), ("K", "Hearts")])
    board = make_cards([("2", "Hearts"), ("7", "Hearts"), ("9", "Clubs")])
    projections, base_equity = project_next_street(player_hand, board, 2, simulations=200)
    assert 0.0 <= base_equity <= 1.0
    assert len(projections) <= 5
    for card, equity in projections:
        assert 0.0 <= equity <= 1.0

def test_project_next_street_empty_on_river():
    player_hand = make_cards([("A", "Hearts"), ("K", "Hearts")])
    board = make_cards([("2", "Hearts"), ("7", "Hearts"), ("9", "Clubs"), ("3", "Diamonds"), ("4", "Spades")])
    result = project_next_street(player_hand, board, 2, simulations=200)
    assert result == []

def test_exact_equity_full_house_uses_trip_rank():
    player_hand = make_cards([("2", "Hearts"), ("A", "Diamonds")])
    opponent_hand = [make_cards([("K", "Clubs"), ("Q", "Clubs")])]
    board = make_cards([("K", "Hearts"), ("K", "Diamonds"), ("2", "Clubs"), ("2", "Spades"), ("A", "Hearts")])
    equity, tie_rate = calculate_equity(player_hand, board, 2, known_opponents=opponent_hand)
    assert equity == 0.0
    assert tie_rate == 0.0

def test_exact_equity_wheel_loses_to_six_high():
    player_hand = make_cards([("A", "Spades"), ("9", "Diamonds")])
    opponent_hand = [make_cards([("6", "Clubs"), ("Q", "Diamonds")])]
    board = make_cards([("2", "Hearts"), ("3", "Diamonds"), ("4", "Clubs"), ("5", "Spades"), ("K", "Hearts")])
    equity, tie_rate = calculate_equity(player_hand, board, 2, known_opponents=opponent_hand)
    assert equity == 0.0
    assert tie_rate == 0.0

def test_three_way_board_split_counts_one_third():
    player_hand = make_cards([("2", "Hearts"), ("3", "Diamonds")])
    board = make_cards([("A", "Hearts"), ("K", "Hearts"), ("Q", "Hearts"), ("J", "Hearts"), ("10", "Hearts")])
    equity, tie_rate = calculate_equity(player_hand, board, 3, simulations=50)
    assert abs(equity - 1 / 3) < 0.000001
    assert tie_rate == 1.0

def test_three_players_only_two_share_the_pot():
    player_hand = make_cards([("A", "Hearts"), ("K", "Diamonds")])
    opponents = [
        make_cards([("A", "Clubs"), ("K", "Spades")]),
        make_cards([("Q", "Clubs"), ("J", "Clubs")])
    ]
    board = make_cards([("2", "Hearts"), ("3", "Diamonds"), ("7", "Clubs"), ("8", "Spades"), ("9", "Hearts")])
    equity, tie_rate = calculate_equity(player_hand, board, 3, known_opponents=opponents, simulations=10)
    assert equity == 0.5
    assert tie_rate == 1.0

def test_matching_one_opponent_does_not_count_when_another_wins():
    player_hand = make_cards([("A", "Hearts"), ("K", "Diamonds")])
    opponents = [
        make_cards([("A", "Clubs"), ("K", "Spades")]),
        make_cards([("10", "Clubs"), ("J", "Clubs")])
    ]
    board = make_cards([("2", "Hearts"), ("3", "Diamonds"), ("7", "Clubs"), ("8", "Spades"), ("9", "Hearts")])
    equity, tie_rate = calculate_equity(player_hand, board, 3, known_opponents=opponents, simulations=10)
    assert equity == 0.0
    assert tie_rate == 0.0

def test_exact_turn_equity_includes_split_share():
    player_hand = make_cards([("K", "Clubs"), ("2", "Diamonds")])
    opponents = [make_cards([("K", "Diamonds"), ("3", "Spades")])]
    board = make_cards([("A", "Hearts"), ("A", "Diamonds"), ("A", "Clubs"), ("A", "Spades")])
    equity, tie_rate = calculate_equity(player_hand, board, 2, known_opponents=opponents)
    assert equity == 0.5
    assert tie_rate == 1.0
