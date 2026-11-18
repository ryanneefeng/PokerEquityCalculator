from src.deck import Deck, Card, RANKS, SUITS
from src.evaluator import best_hand

def validate_equity_inputs(player_hand, board, num_players, known_opponents, dead_cards, simulations=10000):
    if len(player_hand) != 2:
        raise ValueError("Your hand must contain exactly two cards.")
    if len(board) not in (0, 3, 4, 5):
        raise ValueError("The board must contain 0, 3, 4, or 5 cards.")
    if type(num_players) is not int or not 2 <= num_players <= 10:
        raise ValueError("The number of active players must be between 2 and 10.")
    if len(known_opponents) > num_players - 1 or any(len(hand) != 2 for hand in known_opponents):
        raise ValueError("Known opponents must have two cards each and fit the active player count.")
    if type(simulations) is not int or simulations <= 0:
        raise ValueError("Simulations must be a positive integer.")
    cards = list(player_hand) + list(board) + list(dead_cards)
    for hand in known_opponents:
        cards.extend(hand)
    if any(not isinstance(card, Card) or card.rank not in RANKS or card.suit not in SUITS for card in cards):
        raise ValueError("All cards must have a valid rank and suit.")
    if len(set(cards)) != len(cards):
        raise ValueError("A card cannot appear more than once in the hand, board, opponents, or dead cards.")
    needed = 5 - len(board) + 2 * (num_players - 1 - len(known_opponents))
    if 52 - len(cards) < needed:
        raise ValueError("Not enough cards remain to complete the board and opponent hands.")


def exact_equity_river(player_hand, board, num_players, known_opponents, dead_cards):
    validate_equity_inputs(player_hand, board, num_players, known_opponents, dead_cards)
    if len(board) != 5:
        raise ValueError("Exact river equity requires five board cards.")
    if num_players - 1 - len(known_opponents) > 1:
        raise ValueError("Exact equity supports at most one unknown opponent; use calculate_equity for multiway hands.")
    deck = Deck()
    known_cards = player_hand + board + dead_cards
    for opp_hand in known_opponents:
        known_cards += opp_hand
    deck.remove(known_cards)

    remaining = deck.cards
    wins = 0
    ties = 0
    total = 0

    # Generate all possible opponent hand combinations
    unknown_opponents = num_players - 1 - len(known_opponents)

    from itertools import combinations as combs
    for opp_combo in combs(remaining, unknown_opponents * 2):
        # Split combo into hands of 2
        opponents = []
        valid = True
        used = set()
        for i in range(unknown_opponents):
            c1 = opp_combo[i * 2]
            c2 = opp_combo[i * 2 + 1]
            if c1 in used or c2 in used:
                valid = False
                break
            used.add(c1)
            used.add(c2)
            opponents.append([c1, c2])

        if not valid:
            continue

        for opp_hand in known_opponents:
            opponents.append(opp_hand)

        your_best = best_hand(player_hand + board)
        you_win = True
        tied_players = 1

        for opponent_hand in opponents:
            opp_best = best_hand(opponent_hand + board)
            if opp_best > your_best:
                you_win = False
                tied_players = 0
                break
            elif opp_best == your_best:
                you_win = False
                tied_players += 1

        if you_win:
            wins += 1
        elif tied_players > 1:
            ties += 1
            wins += 1 / tied_players
        total += 1

    if total == 0:
        return 0.0, 0.0
    return wins / total, ties / total


def exact_equity_turn(player_hand, board, num_players, known_opponents, dead_cards):
    validate_equity_inputs(player_hand, board, num_players, known_opponents, dead_cards)
    if len(board) != 4:
        raise ValueError("Exact turn equity requires four board cards.")
    if num_players - 1 - len(known_opponents) > 1:
        raise ValueError("Exact equity supports at most one unknown opponent; use calculate_equity for multiway hands.")
    deck = Deck()
    known_cards = player_hand + board + dead_cards
    for opp_hand in known_opponents:
        known_cards += opp_hand
    deck.remove(known_cards)

    remaining = deck.cards
    wins = 0
    ties = 0
    total = 0

    for river_card in remaining:
        full_board = board + [river_card]
        new_remaining = [c for c in remaining if c != river_card]

        unknown_opponents = num_players - 1 - len(known_opponents)
        from itertools import combinations as combs
        for opp_combo in combs(new_remaining, unknown_opponents * 2):
            opponents = []
            valid = True
            used = set()
            for i in range(unknown_opponents):
                c1 = opp_combo[i * 2]
                c2 = opp_combo[i * 2 + 1]
                if c1 in used or c2 in used:
                    valid = False
                    break
                used.add(c1)
                used.add(c2)
                opponents.append([c1, c2])

            if not valid:
                continue

            for opp_hand in known_opponents:
                opponents.append(opp_hand)

            your_best = best_hand(player_hand + full_board)
            you_win = True
            tied_players = 1

            for opponent_hand in opponents:
                opp_best = best_hand(opponent_hand + full_board)
                if opp_best > your_best:
                    you_win = False
                    tied_players = 0
                    break
                elif opp_best == your_best:
                    you_win = False
                    tied_players += 1

            if you_win:
                wins += 1
            elif tied_players > 1:
                ties += 1
                wins += 1 / tied_players
            total += 1

    if total == 0:
        return 0.0, 0.0
    return wins / total, ties / total

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
    wins = 0
    ties = 0

    for i in range(simulations):
        deck = Deck()
        known_cards = player_hand + board + dead_cards
        for opp_hand in known_opponents:
            known_cards += opp_hand
        deck.remove(known_cards)
        deck.shuffle()

        cards_needed = 5 - len(board)
        simulated_board = board + deck.deal(cards_needed)

        opponents = []
        for opp_hand in known_opponents:
            opponents.append(opp_hand)

        unknown_count = num_players - 1 - len(known_opponents)
        for j in range(unknown_count):
            opponents.append(deck.deal(2))

        your_best = best_hand(player_hand + simulated_board)

        you_win = True
        tied_players = 1
        for opponent_hand in opponents:
            opp_best = best_hand(opponent_hand + simulated_board)
            if opp_best > your_best:
                you_win = False
                tied_players = 0
                break
            elif opp_best == your_best:
                you_win = False
                tied_players += 1

        if you_win:
            wins += 1
        elif tied_players > 1:
            ties += 1
            wins += 1 / tied_players

    return wins / simulations, ties / simulations

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
