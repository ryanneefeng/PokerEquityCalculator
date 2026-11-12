def cap_raise(raise_amount, stack_size):
    if raise_amount >= stack_size:
        return stack_size, True
    return raise_amount, False

def min_raise(current_bet, raise_amount, last_raise=None, big_blind=1):
    if last_raise is None:
        last_raise = max(current_bet, big_blind)
    minimum = round(current_bet + max(last_raise, big_blind), 2)
    return max(raise_amount, minimum)

def get_recommendation(equity, tie_rate, pot_size, bet_to_call, stack_size,
                       current_contribution=0, last_raise=None, big_blind=1, can_raise=True):
    call_amount = min(bet_to_call, stack_size)
    total_pot = pot_size + call_amount
    current_bet = round(current_contribution + bet_to_call, 2)
    minimum_raise = min_raise(current_bet, 0, last_raise, big_blind)
    total_stack = round(current_contribution + stack_size, 2)
    
    if bet_to_call == 0:
        if not can_raise:
            return "Check", f"Equity {equity*100:.1f}%. You cannot raise on this action."
        if tie_rate == 1:
            return "Check", f"A split pot is certain in the simulation. Equity {equity*100:.1f}%"
        if equity >= 0.85:
            raise_amount, is_all_in = cap_raise(max(minimum_raise, current_contribution + min(round(pot_size * 0.75, 2), round(stack_size * 0.80, 2))), total_stack)
            label = "All-In" if (is_all_in and equity >= 0.65) else f"${raise_amount}"
            return "Raise (All-In consideration)", f"Equity {equity*100:.1f}%. Consider going all-in or raise to {label} total"
        elif equity >= 0.70:
            raise_amount, is_all_in = cap_raise(max(minimum_raise, current_contribution + min(round(pot_size * 0.60, 2), round(stack_size * 0.30, 2))), total_stack)
            label = "All-In" if is_all_in else f"${raise_amount}"
            return "Raise", f"Equity {equity*100:.1f}%. Raise to {label} total (60% of pot)"
        elif equity >= 0.60:
            raise_amount, is_all_in = cap_raise(max(minimum_raise, current_contribution + min(round(pot_size * 0.35, 2), round(stack_size * 0.20, 2))), total_stack)
            label = "All-In" if is_all_in else f"${raise_amount}"
            return "Raise Small", f"Equity {equity*100:.1f}%. Raise to {label} total (35% of pot)"
        elif equity >= 0.40:
            return "Raise if confident or Check", f"Equity {equity*100:.1f}%"
        else:
            return "Check", f"Equity {equity*100:.1f}%"

    pot_odds = call_amount / total_pot

    # ALL-IN
    if bet_to_call >= stack_size:
        if equity >= pot_odds:
            return "Call (All-In)", f"Equity {equity*100:.1f}% meets pot odds {pot_odds*100:.1f}%. Call all-in of ${call_amount}"
        else:
            return "Fold", f"Equity {equity*100:.1f}% below pot odds {pot_odds*100:.1f}%. Fold against all-in of ${call_amount}"

    if equity < pot_odds:
        return "Fold", f"Equity {equity*100:.1f}% below pot odds {pot_odds*100:.1f}%"
    if not can_raise:
        return "Call", f"Equity {equity*100:.1f}% meets pot odds {pot_odds*100:.1f}%. Call ${bet_to_call}; the betting has not reopened for a raise."
    if tie_rate == 1:
        return "Call", f"A split pot is certain in the simulation. Equity {equity*100:.1f}% meets pot odds {pot_odds*100:.1f}%. Call ${bet_to_call}"

    #Equity override
    if equity >= 0.75:
        raise_amount, is_all_in = cap_raise(max(minimum_raise, current_contribution + min(round(pot_size * 0.75, 2), round(stack_size * 0.80, 2))), total_stack)
        label = "All-In" if is_all_in else f"${raise_amount}"
        return "Raise (All-In consideration)", f"Equity {equity*100:.1f}% is dominant. Raise to {label} total"
    elif equity >= 0.65:
        raise_amount, is_all_in = cap_raise(max(minimum_raise, current_contribution + min(round(pot_size * 0.60, 2), round(stack_size * 0.30, 2))), total_stack)
        label = "All-In" if is_all_in else f"${raise_amount}"
        return "Raise", f"Equity {equity*100:.1f}% is strong regardless of pot odds. Raise to {label} total"

    if equity >= 0.55 and equity >= pot_odds + 0.20:
        raise_amount, is_all_in = cap_raise(max(minimum_raise, current_contribution + min(round(pot_size * 0.60, 2), round(stack_size * 0.30, 2))), total_stack)
        label = "All-In" if is_all_in else f"${raise_amount}"
        return "Raise", f"Equity {equity*100:.1f}% far exceeds pot odds {pot_odds*100:.1f}%. Raise to {label} total"
    elif equity >= 0.45 and equity >= pot_odds + 0.10:
        raise_amount, is_all_in = cap_raise(max(minimum_raise, current_contribution + min(round(pot_size * 0.35, 2), round(stack_size * 0.20, 2))), total_stack)
        label = "All-In" if is_all_in else f"${raise_amount}"
        return "Raise Small or Call", f"Equity {equity*100:.1f}% beats pot odds {pot_odds*100:.1f}%. Raise to {label} total or just call ${bet_to_call}"
    else:
        return "Call", f"Equity {equity*100:.1f}% meets pot odds {pot_odds*100:.1f}%. Call ${bet_to_call}"
