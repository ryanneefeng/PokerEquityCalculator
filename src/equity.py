import random
from src.deck import Deck, Card, RANKS, SUITS
from src.evaluator import best_hand

def calculate_equity(player_hand, board, num_players, simulations=10000):
    wins = 0
    ties = 0

    for i in range(simulations):
        deck = Deck()
        known_cards = player_hand + board
        deck.remove(known_cards)
        deck.shuffle()

        cards_needed = 5 - len(board)
        simulated_board = board + deck.deal(cards_needed)

        opponents = []
        for j in range(num_players - 1):
            opponent_hand = deck.deal(2)
            opponents.append(opponent_hand)

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