from src.deck import Deck, Card, RANKS, SUITS
from src.evaluator import best_hand

def exact_equity_river(player_hand, board, num_players, known_opponents, dead_cards):
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
        you_tie = False

        for opponent_hand in opponents:
            opp_best = best_hand(opponent_hand + board)
            if opp_best > your_best:
                you_win = False
                you_tie = False
                break
            elif opp_best == your_best:
                you_win = False
                you_tie = True

        if you_win:
            wins += 1
        elif you_tie:
            ties += 1
        total += 1

    if total == 0:
        return 0.0, 0.0
    return wins / total, ties / total


def exact_equity_turn(player_hand, board, num_players, known_opponents, dead_cards):
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
            you_tie = False

            for opponent_hand in opponents:
                opp_best = best_hand(opponent_hand + full_board)
                if opp_best > your_best:
                    you_win = False
                    you_tie = False
                    break
                elif opp_best == your_best:
                    you_win = False
                    you_tie = True

            if you_win:
                wins += 1
            elif you_tie:
                ties += 1
            total += 1

    if total == 0:
        return 0.0, 0.0
    return wins / total, ties / total

def project_next_street(player_hand, board, num_players, known_opponents=None, dead_cards=None, simulations=300):
    if known_opponents is None:
        known_opponents = []
    if dead_cards is None:
        dead_cards = []

    if len(board) not in [3, 4]:
        return []

    deck = Deck()
    known_cards = player_hand + board + dead_cards
    for opp_hand in known_opponents:
        known_cards += opp_hand
    deck.remove(known_cards)
    remaining = deck.cards

    base_equity, _ = monte_carlo_equity(player_hand, board, num_players, known_opponents, dead_cards, simulations)

    results = []
    for card in remaining:
        new_board = board + [card]
        equity, _ = monte_carlo_equity(player_hand, new_board, num_players, known_opponents, dead_cards, simulations)
        results.append((card, equity))

    results.sort(key=lambda x: abs(x[1] - base_equity), reverse=True)
    return results[:5], base_equity

def monte_carlo_equity(player_hand, board, num_players, known_opponents, dead_cards, simulations=10000):
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
        you_tie = False
        for opponent_hand in opponents:
            opp_best = best_hand(opponent_hand + simulated_board)
            if opp_best > your_best:
                you_win = False
                you_tie = False
                break
            elif opp_best == your_best:
                you_win = False
                you_tie = True

        if you_win:
            wins += 1
        elif you_tie:
            ties += 1

    return wins / simulations, ties / simulations

def calculate_equity(player_hand, board, num_players, known_opponents=None, dead_cards=None, simulations=10000):
    if known_opponents is None:
        known_opponents = []
    if dead_cards is None:
        dead_cards = []

    if len(board) == 5 and num_players == 2:
        return exact_equity_river(player_hand, board, num_players, known_opponents, dead_cards)
    elif len(board) == 4 and num_players == 2:
        return exact_equity_turn(player_hand, board, num_players, known_opponents, dead_cards)

    return monte_carlo_equity(player_hand, board, num_players, known_opponents, dead_cards, simulations)