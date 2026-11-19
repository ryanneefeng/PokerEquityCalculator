from src.deck import RANKS, SUITS
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

def best_hand_cards(all_cards):
    best = None
    best_combo = None
    for combo in combinations(all_cards, 5):
        result = evaluate_hand(list(combo))
        if best is None or result > best:
            best = result
            best_combo = list(combo)
    return best_combo

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
        indices = [-1, 0, 1, 2, 3]  # treat ace as below 2
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
    if counts[0] > 1:
        # Compare matching ranks before kickers
        tiebreaker = []
        for count in sorted(set(counts), reverse=True):
            matching_ranks = []
            for rank in rank_counts:
                if rank_counts[rank] == count:
                    matching_ranks.append(RANKS.index(rank))
            tiebreaker.extend(sorted(matching_ranks, reverse=True))
    return (hand_rank, tiebreaker)


def best_hand(all_cards):
    best = None
    for combo in combinations(all_cards, 5):
        result = evaluate_hand(list(combo))
        if best is None or result > best:
            best = result
    return best

def describe_hand(hole_cards, board):
    all_cards = hole_cards + board
    num_board_cards = len(board)

    # If we have 5+ cards evaluate the made hand
    if num_board_cards >= 3:
        hand_rank = best_hand(all_cards)[0]
        made_hands = {
            9: "Straight Flush",
            8: "Four of a Kind",
            7: "Full House",
            6: "Flush",
            5: "Straight",
            4: "Three of a Kind",
            3: "Two Pair",
            2: "Pair",
            1: "High Card"
        }
        made = made_hands[hand_rank]

        # On the river no draws possible
        if num_board_cards == 5:
            return made

        # Check for draws on top of made hand
        draws = []
        all_suits = [card.suit for card in all_cards]

        # Flush draw - 4 cards of same suit
        for suit in SUITS:
            if all_suits.count(suit) == 4:
                draws.append("Flush Draw")
                break

        # Backdoor flush draw - 3 cards of same suit
        if num_board_cards == 3 and hand_rank < HAND_RANKINGS["Flush"] and "Flush Draw" not in draws:
            for suit in SUITS:
                if all_suits.count(suit) == 3:
                    draws.append("Backdoor Flush Draw")
                    break

        # Find ranks that complete a straight, including the wheel. Counting
        # completion ranks also distinguishes double gutshots from open ends.
        if hand_rank < HAND_RANKINGS["Straight"]:
            ranks = {RANKS.index(card.rank) + 2 for card in all_cards}
            straights = [{14, 2, 3, 4, 5}] + [set(range(low, low + 5)) for low in range(2, 11)]
            outs = set()
            for straight in straights:
                missing = straight - ranks
                if len(missing) == 1:
                    outs.update(missing)
            if len(outs) >= 2:
                open_ended = any(set(range(low, low + 4)) <= ranks for low in range(2, 11))
                draws.append("Open Ended Straight Draw" if open_ended else "Double Gutshot Straight Draw")
            elif outs:
                draws.append("Gutshot Straight Draw")

        if draws:
            return f"{made} with {' and '.join(draws)}"
        return made

    # Pre-flop -- just describe hole cards
    ranks = [card.rank for card in hole_cards]
    suits = [card.suit for card in hole_cards]
    if ranks[0] == ranks[1]:
        return f"Pocket {ranks[0]}s"
    elif suits[0] == suits[1]:
        return f"{ranks[0]}-{ranks[1]} Suited"
    else:
        return f"{ranks[0]}-{ranks[1]} Offsuit"
