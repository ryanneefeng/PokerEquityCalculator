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

def test_tiebreaker_pair_rank_before_kickers():
    kings = make_cards([("K", "Hearts"), ("K", "Diamonds"), ("Q", "Clubs"), ("J", "Spades"), ("9", "Hearts")])
    queens = make_cards([("Q", "Hearts"), ("Q", "Diamonds"), ("A", "Clubs"), ("K", "Spades"), ("J", "Hearts")])
    assert evaluate_hand(kings) > evaluate_hand(queens)

def test_tiebreaker_pair_kickers():
    ace_kicker = make_cards([("7", "Hearts"), ("7", "Diamonds"), ("A", "Clubs"), ("J", "Spades"), ("9", "Hearts")])
    king_kicker = make_cards([("7", "Clubs"), ("7", "Spades"), ("K", "Clubs"), ("Q", "Spades"), ("10", "Hearts")])
    higher_second = make_cards([("7", "Hearts"), ("7", "Diamonds"), ("A", "Clubs"), ("Q", "Spades"), ("8", "Hearts")])
    higher_third = make_cards([("7", "Clubs"), ("7", "Spades"), ("A", "Diamonds"), ("J", "Hearts"), ("10", "Clubs")])
    assert evaluate_hand(ace_kicker) > evaluate_hand(king_kicker)
    assert evaluate_hand(higher_second) > evaluate_hand(ace_kicker)
    assert evaluate_hand(higher_third) > evaluate_hand(ace_kicker)

def test_tiebreaker_trips_rank_before_kickers():
    eights = make_cards([("8", "Hearts"), ("8", "Diamonds"), ("8", "Clubs"), ("Q", "Spades"), ("J", "Hearts")])
    sevens = make_cards([("7", "Hearts"), ("7", "Diamonds"), ("7", "Clubs"), ("A", "Spades"), ("K", "Hearts")])
    assert evaluate_hand(eights) > evaluate_hand(sevens)

def test_tiebreaker_trips_kickers():
    ace_kicker = make_cards([("7", "Hearts"), ("7", "Diamonds"), ("7", "Clubs"), ("A", "Spades"), ("9", "Hearts")])
    king_kicker = make_cards([("7", "Hearts"), ("7", "Diamonds"), ("7", "Spades"), ("K", "Clubs"), ("Q", "Hearts")])
    higher_second = make_cards([("7", "Hearts"), ("7", "Diamonds"), ("7", "Spades"), ("A", "Clubs"), ("10", "Hearts")])
    assert evaluate_hand(ace_kicker) > evaluate_hand(king_kicker)
    assert evaluate_hand(higher_second) > evaluate_hand(ace_kicker)

def test_tiebreaker_two_pair_high_pair_before_kicker():
    kings_and_twos = make_cards([("K", "Hearts"), ("K", "Diamonds"), ("2", "Clubs"), ("2", "Spades"), ("10", "Hearts")])
    queens_and_jacks = make_cards([("Q", "Hearts"), ("Q", "Diamonds"), ("J", "Clubs"), ("J", "Spades"), ("A", "Hearts")])
    assert evaluate_hand(kings_and_twos) > evaluate_hand(queens_and_jacks)

def test_tiebreaker_two_pair_low_pair_before_kicker():
    kings_and_queens = make_cards([("K", "Hearts"), ("K", "Diamonds"), ("Q", "Clubs"), ("Q", "Spades"), ("9", "Hearts")])
    kings_and_jacks = make_cards([("K", "Clubs"), ("K", "Spades"), ("J", "Clubs"), ("J", "Spades"), ("A", "Hearts")])
    assert evaluate_hand(kings_and_queens) > evaluate_hand(kings_and_jacks)

def test_tiebreaker_two_pair_kicker():
    ace_kicker = make_cards([("K", "Hearts"), ("K", "Diamonds"), ("Q", "Clubs"), ("Q", "Spades"), ("A", "Hearts")])
    jack_kicker = make_cards([("K", "Clubs"), ("K", "Spades"), ("Q", "Hearts"), ("Q", "Diamonds"), ("J", "Hearts")])
    assert evaluate_hand(ace_kicker) > evaluate_hand(jack_kicker)

def test_tiebreaker_full_house_trips_before_pair():
    kings_full = make_cards([("K", "Hearts"), ("K", "Diamonds"), ("K", "Clubs"), ("2", "Spades"), ("2", "Hearts")])
    twos_full = make_cards([("2", "Hearts"), ("2", "Diamonds"), ("2", "Clubs"), ("A", "Spades"), ("A", "Hearts")])
    assert evaluate_hand(kings_full) > evaluate_hand(twos_full)

def test_tiebreaker_full_house_pair():
    kings_full_of_queens = make_cards([("K", "Hearts"), ("K", "Diamonds"), ("K", "Clubs"), ("Q", "Spades"), ("Q", "Hearts")])
    kings_full_of_jacks = make_cards([("K", "Hearts"), ("K", "Diamonds"), ("K", "Spades"), ("J", "Clubs"), ("J", "Hearts")])
    assert evaluate_hand(kings_full_of_queens) > evaluate_hand(kings_full_of_jacks)

def test_tiebreaker_quads_rank_before_kicker():
    kings = make_cards([("K", "Hearts"), ("K", "Diamonds"), ("K", "Clubs"), ("K", "Spades"), ("Q", "Hearts")])
    twos = make_cards([("2", "Hearts"), ("2", "Diamonds"), ("2", "Clubs"), ("2", "Spades"), ("A", "Hearts")])
    assert evaluate_hand(kings) > evaluate_hand(twos)

def test_tiebreaker_quads_kicker():
    ace_kicker = make_cards([("2", "Hearts"), ("2", "Diamonds"), ("2", "Clubs"), ("2", "Spades"), ("A", "Hearts")])
    king_kicker = make_cards([("2", "Hearts"), ("2", "Diamonds"), ("2", "Clubs"), ("2", "Spades"), ("K", "Hearts")])
    assert evaluate_hand(ace_kicker) > evaluate_hand(king_kicker)

def test_wheel_loses_to_six_high_straight():
    wheel = make_cards([("A", "Hearts"), ("2", "Diamonds"), ("3", "Clubs"), ("4", "Spades"), ("5", "Hearts")])
    six_high = make_cards([("2", "Hearts"), ("3", "Diamonds"), ("4", "Clubs"), ("5", "Spades"), ("6", "Hearts")])
    assert evaluate_hand(six_high) > evaluate_hand(wheel)

def test_wheel_straight_flush_loses_to_six_high():
    wheel = make_cards([("A", "Hearts"), ("2", "Hearts"), ("3", "Hearts"), ("4", "Hearts"), ("5", "Hearts")])
    six_high = make_cards([("2", "Spades"), ("3", "Spades"), ("4", "Spades"), ("5", "Spades"), ("6", "Spades")])
    assert evaluate_hand(wheel)[0] == 9
    assert evaluate_hand(six_high) > evaluate_hand(wheel)

def test_wheels_with_different_suits_tie():
    first = make_cards([("A", "Hearts"), ("2", "Diamonds"), ("3", "Clubs"), ("4", "Spades"), ("5", "Hearts")])
    second = make_cards([("A", "Clubs"), ("2", "Spades"), ("3", "Hearts"), ("4", "Diamonds"), ("5", "Clubs")])
    assert evaluate_hand(first) == evaluate_hand(second)

def test_best_hand_compares_full_houses_on_shared_board():
    board = make_cards([("K", "Hearts"), ("K", "Diamonds"), ("2", "Clubs"), ("2", "Spades"), ("A", "Hearts")])
    kings = make_cards([("K", "Clubs"), ("Q", "Clubs")])
    twos = make_cards([("2", "Hearts"), ("A", "Diamonds")])
    assert best_hand(kings + board) > best_hand(twos + board)

def test_best_hand_cards_prefers_six_high_over_wheel():
    all_cards = make_cards([
        ("A", "Hearts"), ("K", "Diamonds"),
        ("2", "Clubs"), ("3", "Spades"), ("4", "Hearts"),
        ("5", "Diamonds"), ("6", "Clubs")
    ])
    result = best_hand_cards(all_cards)
    assert {card.rank for card in result} == {"2", "3", "4", "5", "6"}
    assert best_hand(all_cards) == evaluate_hand(result)
