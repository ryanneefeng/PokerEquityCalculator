import random
from src.deck import Deck, Card, RANKS, SUITS
from src.evaluator import best_hand

def calculate_equity(player_hand, board, num_players, known_opponents=None, dead_cards=None, simulations=10000):
    if known_opponents is None:
        known_opponents = []
    if dead_cards is None:
        dead_cards = []

    wins = 0
    ties = 0

    for i in range(simulations):
        deck = Deck()

        # Remove all known cards from deck
        known_cards = player_hand + board + dead_cards
        for opp_hand in known_opponents:
            known_cards += opp_hand
        deck.remove(known_cards)
        deck.shuffle()

        # Deal remaining board cards
        cards_needed = 5 - len(board)
        simulated_board = board + deck.deal(cards_needed)

        # Build opponent hands
        opponents = []
        for opp_hand in known_opponents:
            opponents.append(opp_hand)

        # Deal random hands to unknown opponents
        unknown_count = num_players - 1 - len(known_opponents)
        for j in range(unknown_count):
            opponents.append(deck.deal(2))

        # Evaluate hands
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

    equity = wins / simulations
    tie_rate = ties / simulations
    return equity, tie_rate