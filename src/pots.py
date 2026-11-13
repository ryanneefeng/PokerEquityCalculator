from math import isfinite
from src.equity import calculate_equity

def create_players(num_players):
    players = {}
    for position in range(1, num_players + 1):
        players[position] = {
            "stack": None, "contribution": 0, "street_contribution": 0,
            "folded": False, "seen": False, "needs_update": False,
        }
    return players

def add_chips(player, amount):
    amount = round(amount, 2)
    if not isfinite(amount) or amount < 0 or amount > player["stack"]:
        raise ValueError("A contribution must fit the player's remaining stack.")
    player["stack"] = round(player["stack"] - amount, 2)
    player["contribution"] = round(player["contribution"] + amount, 2)
    player["street_contribution"] = round(player["street_contribution"] + amount, 2)

def get_call_amount(players, position, big_blind=0, preflop=False):
    live_players = [p for p in players if not players[p]["folded"]]
    current_bet = max((players[p]["street_contribution"] for p in live_players), default=0)
    funded_players = [p for p in live_players if (players[p]["stack"] or 0) > 0]
    if preflop and len(funded_players) >= 2:
        current_bet = max(current_bet, big_blind)
    return round(max(0, current_bet - players[position]["street_contribution"]), 2)

def get_opponent_limit(players, position):
    limits = []
    for opponent, player in players.items():
        if opponent != position and not player["folded"] and (player["stack"] or 0) > 0:
            limits.append(round(player["street_contribution"] + player["stack"], 2))
    return max(limits, default=0)

def build_side_pots(players, dead_money=0):
    if not isfinite(dead_money) or dead_money < 0:
        raise ValueError("Dead money must be finite and nonnegative.")
    contributions = {}
    for position, player in players.items():
        amount = player["contribution"]
        if not isfinite(amount) or amount < 0:
            raise ValueError("Contributions must be finite and nonnegative.")
        contributions[position] = round(amount * 100)

    levels = sorted(set(amount for amount in contributions.values() if amount > 0))
    pots = []
    live_players = [p for p in players if not players[p]["folded"]]
    if len(live_players) == 1:
        amounts = sorted(contributions.values(), reverse=True)
        excess = amounts[0] - (amounts[1] if len(amounts) > 1 else 0)
        refunds = {}
        if excess:
            owner = max(contributions, key=contributions.get)
            refunds[owner] = excess / 100
        contested = round(sum(contributions.values()) / 100 + dead_money - excess / 100, 2)
        return ([{"amount": contested, "eligible": live_players}] if contested else []), refunds
    if dead_money:
        eligible = [p for p in players if not players[p]["folded"]]
        if not eligible:
            raise ValueError("The pot needs a live eligible player.")
        pots.append({"amount": round(dead_money, 2), "eligible": eligible})
    refunds = {}
    previous = 0
    for level in levels:
        contributors = [p for p in players if contributions[p] >= level]
        amount = (level - previous) * len(contributors)
        previous = level
        if len(contributors) == 1:
            refunds[contributors[0]] = amount / 100
            continue
        eligible = [p for p in contributors if not players[p]["folded"]]
        if not eligible:
            raise ValueError("A pot has no live eligible player. Check the recorded folds and contributions.")
        if pots and pots[-1]["eligible"] == eligible:
            pots[-1]["amount"] = round(pots[-1]["amount"] + amount / 100, 2)
        else:
            pots.append({"amount": amount / 100, "eligible": eligible})
    return pots, refunds

def return_uncalled_chips(players):
    pots, refunds = build_side_pots(players)
    for position, amount in refunds.items():
        player = players[position]
        if amount > player["street_contribution"]:
            raise ValueError("An uncalled wager must belong to the current street.")
        player["contribution"] = round(player["contribution"] - amount, 2)
        player["street_contribution"] = round(player["street_contribution"] - amount, 2)
        player["stack"] = round((player["stack"] or 0) + amount, 2)
    return refunds

def calculate_pot_equity(player_hand, board, players, position, dead_cards=None, simulations=10000, dead_money=0):
    if dead_cards is None:
        dead_cards = []
    pots, refunds = build_side_pots(players, dead_money)
    eligible_pot = 0
    expected_return = 0
    weighted_ties = 0
    for pot in pots:
        equity, tie_rate = 0, 0
        if position in pot["eligible"]:
            eligible_pot += pot["amount"]
            if len(pot["eligible"]) == 1:
                equity = 1
            else:
                known_opponents = []
                removed_cards = list(dead_cards)
                for opponent, player in players.items():
                    if opponent == position or not player.get("hand"):
                        continue
                    if opponent in pot["eligible"]:
                        known_opponents.append(player["hand"])
                    else:
                        removed_cards.extend(player["hand"])
                equity, tie_rate = calculate_equity(
                    player_hand, board, len(pot["eligible"]), known_opponents=known_opponents,
                    dead_cards=list(set(removed_cards)), simulations=simulations
                )
            expected_return += pot["amount"] * equity
            weighted_ties += pot["amount"] * tie_rate
        pot["equity"] = equity
        pot["tie_rate"] = tie_rate
    return {
        "pots": pots, "refunds": refunds, "eligible_pot": round(eligible_pot, 2),
        "expected_return": expected_return,
        "equity": expected_return / eligible_pot if eligible_pot else 0,
        "tie_rate": weighted_ties / eligible_pot if eligible_pot else 0,
    }

def calculate_call_equity(player_hand, board, players, position, bet_to_call, dead_cards=None, simulations=10000, dead_money=0):
    pots, previous_refunds = build_side_pots(players, dead_money)
    projected = {p: dict(player) for p, player in players.items()}
    call_amount = min(bet_to_call, projected[position]["stack"])
    add_chips(projected[position], call_amount)
    result = calculate_pot_equity(player_hand, board, projected, position, dead_cards, simulations, dead_money)
    result["call_amount"] = call_amount
    refund_added = max(0, result["refunds"].get(position, 0) - previous_refunds.get(position, 0))
    result["call_refund"] = round(min(call_amount, refund_added), 2)
    result["call_cost"] = round(call_amount - result["call_refund"], 2)
    # Only matched chips are at risk if no further opponent adds money.
    result["decision_pot"] = round(result["eligible_pot"] - result["call_cost"], 2)
    return result
