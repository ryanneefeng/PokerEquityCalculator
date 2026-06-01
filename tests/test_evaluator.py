import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.deck import Card
from src.evaluator import evaluate_hand, best_hand

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