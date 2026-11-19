from src.deck import Deck, Card, RANKS, SUITS
from src.evaluator import best_hand

def validate_equity_inputs(player_hand, board, num_players, known_opponents, dead_cards, simulations=10000):
    if len(player_hand) != 2:
        raise ValueError("Your hand must contain exactly two cards.")
    if len(board) not in (0, 3, 4, 5):
        raise ValueError("The board must contain 0, 3, 4, or 5 cards.")
    if type(num_players) is not int or not 2 <= num_players <= 10:
        raise ValueError("The number of active players must be between 2 and 10.")
    if len(known_opponents) > num_players - 1 or any(len(hand) not in (1, 2) for hand in known_opponents):
        raise ValueError("Known opponents must have one or two exposed cards each and fit the active player count.")
    if type(simulations) is not int or simulations <= 0:
        raise ValueError("Simulations must be a positive integer.")
    cards = list(player_hand) + list(board) + list(dead_cards)
    for hand in known_opponents:
        cards.extend(hand)
    if any(not isinstance(card, Card) or card.rank not in RANKS or card.suit not in SUITS for card in cards):
        raise ValueError("All cards must have a valid rank and suit.")
    if len(set(cards)) != len(cards):
        raise ValueError("A card cannot appear more than once in the hand, board, opponents, or dead cards.")
    needed = 5 - len(board) + 2 * (num_players - 1) - sum(map(len, known_opponents))
    if 52 - len(cards) < needed:
        raise ValueError("Not enough cards remain to complete the board and opponent hands.")


def _remaining_cards(player_hand, board, known_opponents, dead_cards):
    deck = Deck()
    deck.remove(player_hand + board + dead_cards + [card for hand in known_opponents for card in hand])
    return deck.cards


def _showdown_share(player_hand, board, opponents):
    your_best = best_hand(player_hand + board)
    tied_players = 1
    for hand in opponents:
        opponent_best = best_hand(hand + board)
        if opponent_best > your_best:
            return 0.0, 0
        if opponent_best == your_best:
            tied_players += 1
    return 1 / tied_players, int(tied_players > 1)


def _exact_equity(player_hand, board, num_players, known_opponents, dead_cards, board_size):
    from itertools import combinations
    validate_equity_inputs(player_hand, board, num_players, known_opponents, dead_cards)
    if len(board) != board_size:
        raise ValueError(f"Exact equity requires {board_size} board cards.")
    templates = [list(hand) for hand in known_opponents] + [[] for _ in range(num_players - 1 - len(known_opponents))]
    incomplete = [i for i, hand in enumerate(templates) if len(hand) < 2]
    if len(incomplete) > 1:
        raise ValueError("Exact equity supports at most one unknown opponent; use calculate_equity for multiway hands.")
    remaining = _remaining_cards(player_hand, board, known_opponents, dead_cards)
    shares = ties = total = 0
    for runout in combinations(remaining, 5 - len(board)):
        full_board = board + list(runout)
        available = [card for card in remaining if card not in runout]
        missing = 2 - len(templates[incomplete[0]]) if incomplete else 0
        for completion in combinations(available, missing):
            opponents = list(templates)
            if incomplete:
                i = incomplete[0]
                opponents[i] = templates[i] + list(completion)
            share, tie = _showdown_share(player_hand, full_board, opponents)
            shares += share
            ties += tie
            total += 1
    return shares / total, ties / total


def exact_equity_river(player_hand, board, num_players, known_opponents, dead_cards):
    return _exact_equity(player_hand, board, num_players, known_opponents, dead_cards, 5)


def exact_equity_turn(player_hand, board, num_players, known_opponents, dead_cards):
    return _exact_equity(player_hand, board, num_players, known_opponents, dead_cards, 4)


def project_next_street(player_hand, board, num_players, known_opponents=None, dead_cards=None, simulations=300,
                        *, equity_calculator=None):
    """Estimate next-card changes, optionally using a pot-aware board callback."""
    if known_opponents is None:
        known_opponents = []
    if dead_cards is None:
        dead_cards = []

    if len(board) not in [3, 4]:
        return []
    validate_equity_inputs(player_hand, board, num_players, known_opponents, dead_cards, simulations)

    deck = Deck()
    known_cards = player_hand + board + dead_cards
    for opp_hand in known_opponents:
        known_cards += opp_hand
    deck.remove(known_cards)
    remaining = deck.cards

    if equity_calculator is None:
        def equity_calculator(candidate_board):
            return monte_carlo_equity(player_hand, candidate_board, num_players, known_opponents, dead_cards, simulations)[0]
    base_equity = equity_calculator(board)

    results = []
    for card in remaining:
        new_board = board + [card]
        equity = equity_calculator(new_board)
        results.append((card, equity))

    results.sort(key=lambda x: abs(x[1] - base_equity), reverse=True)
    return results[:5], base_equity

def monte_carlo_equity(player_hand, board, num_players, known_opponents, dead_cards, simulations=10000):
    validate_equity_inputs(player_hand, board, num_players, known_opponents, dead_cards, simulations)
    remaining = _remaining_cards(player_hand, board, known_opponents, dead_cards)
    templates = [list(hand) for hand in known_opponents] + [[] for _ in range(num_players - 1 - len(known_opponents))]
    shares = ties = 0
    for _ in range(simulations):
        deck = Deck()
        deck.cards = remaining.copy()
        deck.shuffle()
        simulated_board = board + deck.deal(5 - len(board))
        opponents = [hand + deck.deal(2 - len(hand)) for hand in templates]
        share, tie = _showdown_share(player_hand, simulated_board, opponents)
        shares += share
        ties += tie
    return shares / simulations, ties / simulations


def calculate_equity(player_hand, board, num_players, known_opponents=None, dead_cards=None, simulations=10000):
    # Equity includes your share of tied pots; tie rate counts how often you split.
    if known_opponents is None:
        known_opponents = []
    if dead_cards is None:
        dead_cards = []
    validate_equity_inputs(player_hand, board, num_players, known_opponents, dead_cards, simulations)

    if len(board) == 5 and num_players == 2:
        return exact_equity_river(player_hand, board, num_players, known_opponents, dead_cards)
    elif len(board) == 4 and num_players == 2:
        return exact_equity_turn(player_hand, board, num_players, known_opponents, dead_cards)

    return monte_carlo_equity(player_hand, board, num_players, known_opponents, dead_cards, simulations)
