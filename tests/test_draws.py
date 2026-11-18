from src.deck import Card
from src.evaluator import describe_hand


def cards(text):
    suits = {"h": "Hearts", "d": "Diamonds", "c": "Clubs", "s": "Spades"}
    return [Card(token[:-1], suits[token[-1]]) for token in text.split()]


def test_backdoor_flush_requires_two_remaining_board_cards():
    assert "Backdoor Flush Draw" in describe_hand(cards("Ah Kh"), cards("2h 7d 9c"))
    assert describe_hand(cards("Ah Kh"), cards("2h 7d 9c Js")) == "High Card"


def test_wheel_and_broadway_one_rank_draws_are_gutshots():
    for hand, board in [("Ah 2d", "3c 4s 9h"), ("Ah 3d", "4c 5s 9h"),
                        ("Jh Qd", "Kc As 2h"), ("2h 3d", "4c 6s Kh")]:
        assert describe_hand(cards(hand), cards(board)) == "High Card with Gutshot Straight Draw"


def test_open_ended_draws_have_two_completion_ranks():
    for hand, board in [("3h 4d", "5c 6s Kh"), ("9h 10d", "Jc Qs 2h"),
                        ("2h 3d", "4c 5s 9h")]:
        assert describe_hand(cards(hand), cards(board)) == "High Card with Open Ended Straight Draw"


def test_double_gutshot_is_distinguished_from_open_ended_draw():
    assert describe_hand(cards("5h 7d"), cards("8c 9s Jh")) == "High Card with Double Gutshot Straight Draw"


def test_duplicate_ranks_do_not_make_a_straight_draw():
    assert describe_hand(cards("Ah Ad"), cards("2c 4s 9h")) == "Pair"


def test_made_straights_and_stronger_hands_do_not_get_straight_draw_labels():
    for hand, board in [("6h 7d", "8c 9s 10h"), ("Ah 2d", "3c 4s 5h"),
                        ("Ah Kh", "Qh Jh 2h 10d")]:
        assert "Straight Draw" not in describe_hand(cards(hand), cards(board))


def test_flush_and_river_descriptions_do_not_claim_impossible_draws():
    assert describe_hand(cards("Ah Kh"), cards("2h 7h 9h Js")) == "Flush"
    assert describe_hand(cards("Ah Kh"), cards("2h 7h 9c Js 4d")) == "High Card"
