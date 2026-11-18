from src.deck import Card, Deck
from src.equity import calculate_equity, monte_carlo_equity, exact_equity_river, exact_equity_turn, project_next_street


HAND = [Card("A", "Hearts"), Card("K", "Diamonds")]
BOARD = [Card("2", "Hearts"), Card("3", "Diamonds"), Card("7", "Clubs"), Card("8", "Spades"), Card("9", "Hearts")]


def rejects(call):
    try:
        call()
    except ValueError:
        return
    raise AssertionError("Invalid equity input must raise ValueError")


def test_duplicate_cards_are_rejected_across_all_known_card_sources():
    for kwargs in [{"board": [HAND[0]] + BOARD[1:]},
                   {"dead_cards": [HAND[0]]},
                   {"known_opponents": [[HAND[0], Card("Q", "Clubs")]]},
                   {"dead_cards": [Card("Q", "Clubs")] * 2}]:
        args = {"player_hand": HAND, "board": BOARD, "num_players": 2}
        args.update(kwargs)
        rejects(lambda: calculate_equity(**args))


def test_invalid_card_shapes_ranks_and_suits_are_rejected():
    for hand in [[], HAND[:1], HAND + [BOARD[0]], [Card("1", "Hearts"), HAND[1]],
                 [Card("A", "Stars"), HAND[1]], ["Ah", HAND[1]]]:
        rejects(lambda: calculate_equity(hand, BOARD, 2))
    for board in [BOARD[:1], BOARD[:2], BOARD + [Card("J", "Clubs")]]:
        rejects(lambda: calculate_equity(HAND, board, 2))


def test_invalid_player_counts_and_known_hands_are_rejected():
    for count in [0, 1, 11, 2.5, True]:
        rejects(lambda: calculate_equity(HAND, BOARD, count))
    for opponents in [[[]], [BOARD[:3]], [BOARD[:2], BOARD[2:4]]]:
        rejects(lambda: calculate_equity(HAND, [], 2, known_opponents=opponents))


def test_invalid_simulation_counts_are_rejected_even_on_exact_paths():
    for count in [0, -1, 1.5, True, None, "100"]:
        rejects(lambda: calculate_equity(HAND, BOARD, 2, simulations=count))
        rejects(lambda: monte_carlo_equity(HAND, [], 2, [], [], simulations=count))
        rejects(lambda: project_next_street(HAND, BOARD[:3], 2, simulations=count))


def test_insufficient_remaining_cards_are_rejected():
    available = [card for card in Deck().cards if card not in HAND + BOARD]
    rejects(lambda: calculate_equity(HAND, BOARD[:3], 10, dead_cards=available[:30]))


def test_direct_exact_functions_validate_street_and_unknown_opponents():
    rejects(lambda: exact_equity_river(HAND, BOARD[:4], 2, [], []))
    rejects(lambda: exact_equity_turn(HAND, BOARD, 2, [], []))
    rejects(lambda: exact_equity_river(HAND, BOARD, 3, [], []))
    rejects(lambda: exact_equity_turn(HAND, BOARD[:4], 3, [], []))
    rejects(lambda: monte_carlo_equity(HAND, BOARD, 2, [], [HAND[0]], 1))
