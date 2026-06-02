from src.deck import RANKS
from itertools import combinations

HAND_RANKINGS = {
    "High Card": 1,
    "Pair": 2,
    "Two Pair": 3,
    "Three of a Kind": 4,
    "Straight": 5,
    "Flush": 6,
    "Full House": 7,
    "Four of a Kind": 8,
    "Straight Flush": 9
}

def evaluate_hand(cards):
    ranks = [card.rank for card in cards]
    suits = [card.suit for card in cards]

    is_flush = len(set(suits)) == 1

    indices = []
    for rank in ranks:
        indices.append(RANKS.index(rank))
    indices.sort()
    is_straight = (indices[-1] - indices[0] == 4) and (len(set(indices)) == 5)
    
    # Check for ace-low straight
    if not is_straight and set(indices) == {0, 1, 2, 3, 12}:
        is_straight = True
        indices = [0, 1, 2, 3, 4]  # treat ace as low
    rank_counts = {}
    
    for rank in ranks:
        if rank in rank_counts:
            rank_counts[rank] += 1
        else:
            rank_counts[rank] = 1
    counts = []
    for rank in rank_counts:
        counts.append(rank_counts[rank])
    counts.sort(reverse=True)

    if is_flush and is_straight:
        hand_rank = HAND_RANKINGS["Straight Flush"]
    elif counts[0] == 4:
        hand_rank = HAND_RANKINGS["Four of a Kind"]
    elif counts[0] == 3 and counts[1] == 2:
        hand_rank = HAND_RANKINGS["Full House"]
    elif is_flush:
        hand_rank = HAND_RANKINGS["Flush"]
    elif is_straight:
        hand_rank = HAND_RANKINGS["Straight"]
    elif counts[0] == 3:
        hand_rank = HAND_RANKINGS["Three of a Kind"]
    elif counts[0] == 2 and counts[1] == 2:
        hand_rank = HAND_RANKINGS["Two Pair"]
    elif counts[0] == 2:
        hand_rank = HAND_RANKINGS["Pair"]
    else:
        hand_rank = HAND_RANKINGS["High Card"]

    tiebreaker = sorted(indices, reverse=True)
    return (hand_rank, tiebreaker)


def best_hand(all_cards):
    best = None
    for combo in combinations(all_cards, 5):
        result = evaluate_hand(list(combo))
        if best is None or result > best:
            best = result
    return best