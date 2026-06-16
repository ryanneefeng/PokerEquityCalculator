import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.deck import Card
from src.evaluator import evaluate_hand, best_hand, describe_hand, best_hand_cards

def make_cards(card_list):
    return [Card(rank, suit) for rank, suit in card_list]

def test_straight_flush():
    cards = make_cards([("9", "Hearts"), ("8", "Hearts"), ("7", "Hearts"), ("6", "Hearts"), ("5", "Hearts")])
    assert evaluate_hand(cards)[0] == 9

def test_four_of_a_kind():
    cards = make_cards([("A", "Hearts"), ("A", "Diamonds"), ("A", "Clubs"), ("A", "Spades"), ("K", "Hearts")])
    assert evaluate_hand(cards)[0] == 8

def test_full_house():
    cards = make_cards([("A", "Hearts"), ("A", "Diamonds"), ("A", "Clubs"), ("K", "Hearts"), ("K", "Spades")])
    assert evaluate_hand(cards)[0] == 7

def test_flush():
    cards = make_cards([("A", "Hearts"), ("K", "Hearts"), ("Q", "Hearts"), ("J", "Hearts"), ("9", "Hearts")])
    assert evaluate_hand(cards)[0] == 6

def test_straight():
    cards = make_cards([("9", "Hearts"), ("8", "Diamonds"), ("7", "Clubs"), ("6", "Spades"), ("5", "Hearts")])
    assert evaluate_hand(cards)[0] == 5

def test_three_of_a_kind():
    cards = make_cards([("A", "Hearts"), ("A", "Diamonds"), ("A", "Clubs"), ("K", "Hearts"), ("Q", "Spades")])
    assert evaluate_hand(cards)[0] == 4

def test_two_pair():
    cards = make_cards([("A", "Hearts"), ("A", "Diamonds"), ("K", "Clubs"), ("K", "Hearts"), ("Q", "Spades")])
    assert evaluate_hand(cards)[0] == 3

def test_pair():
    cards = make_cards([("A", "Hearts"), ("A", "Diamonds"), ("K", "Clubs"), ("Q", "Hearts"), ("J", "Spades")])
    assert evaluate_hand(cards)[0] == 2

def test_high_card():
    cards = make_cards([("A", "Hearts"), ("K", "Diamonds"), ("Q", "Clubs"), ("J", "Spades"), ("9", "Hearts")])
    assert evaluate_hand(cards)[0] == 1

def test_tiebreaker_flush():
    ace_high = make_cards([("A", "Hearts"), ("K", "Hearts"), ("Q", "Hearts"), ("J", "Hearts"), ("9", "Hearts")])
    king_high = make_cards([("K", "Hearts"), ("Q", "Hearts"), ("J", "Hearts"), ("10", "Hearts"), ("8", "Hearts")])
    assert evaluate_hand(ace_high) > evaluate_hand(king_high)

def test_best_hand_picks_correct_five():
    all_cards = make_cards([
        ("A", "Hearts"), ("A", "Diamonds"),
        ("A", "Clubs"), ("A", "Spades"),
        ("K", "Hearts"), ("2", "Diamonds"), ("3", "Clubs")
    ])
    assert best_hand(all_cards)[0] == 8

def test_ace_low_straight():
    cards = make_cards([("A", "Hearts"), ("2", "Diamonds"), ("3", "Clubs"), ("4", "Spades"), ("5", "Hearts")])
    assert evaluate_hand(cards)[0] == 5

def test_describe_pocket_pair():
    hole_cards = make_cards([("A", "Hearts"), ("A", "Diamonds")])
    assert describe_hand(hole_cards, []) == "Pocket As"

def test_describe_suited():
    hole_cards = make_cards([("A", "Hearts"), ("K", "Hearts")])
    assert describe_hand(hole_cards, []) == "A-K Suited"

def test_describe_offsuit():
    hole_cards = make_cards([("A", "Hearts"), ("K", "Clubs")])
    assert describe_hand(hole_cards, []) == "A-K Offsuit"

def test_describe_made_hand_on_river():
    hole_cards = make_cards([("A", "Hearts"), ("A", "Diamonds")])
    board = make_cards([("A", "Clubs"), ("K", "Hearts"), ("2", "Spades"), ("3", "Diamonds"), ("4", "Clubs")])
    assert describe_hand(hole_cards, board) == "Three of a Kind"

def test_describe_flush_draw():
    hole_cards = make_cards([("A", "Hearts"), ("K", "Hearts")])
    board = make_cards([("2", "Hearts"), ("7", "Hearts"), ("9", "Clubs")])
    result = describe_hand(hole_cards, board)
    assert "Flush Draw" in result

def test_describe_open_ended_straight_draw():
    hole_cards = make_cards([("9", "Hearts"), ("10", "Diamonds")])
    board = make_cards([("8", "Clubs"), ("7", "Spades"), ("2", "Hearts")])
    result = describe_hand(hole_cards, board)
    assert "Open Ended Straight Draw" in result

def test_best_hand_cards_returns_correct_five():
    all_cards = make_cards([
        ("A", "Hearts"), ("A", "Diamonds"),
        ("A", "Clubs"), ("A", "Spades"),
        ("K", "Hearts"), ("2", "Diamonds"), ("3", "Clubs")
    ])
    result = best_hand_cards(all_cards)
    assert len(result) == 5
    ranks_in_result = [card.rank for card in result]
    assert ranks_in_result.count("A") == 4