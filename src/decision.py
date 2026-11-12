def cap_raise(raise_amount, stack_size):
    if raise_amount >= stack_size:
        return stack_size, True
    return raise_amount, False

def min_raise(bet_to_call, raise_amount):
    minimum = bet_to_call * 2
    return max(raise_amount, minimum)

def get_recommendation(equity, tie_rate, pot_size, bet_to_call, stack_size):
    call_amount = min(bet_to_call, stack_size)
    total_pot = pot_size + call_amount
    
    if bet_to_call == 0:
        if tie_rate == 1:
            return "Check", f"A split pot is certain in the simulation. Equity {equity*100:.1f}%"
        if equity >= 0.85:
            raise_amount, is_all_in = cap_raise(min_raise(0, min(round(pot_size * 0.75, 2), round(stack_size * 0.80, 2))), stack_size)
            label = "All-In" if (is_all_in and equity >= 0.65) else f"${raise_amount}"
            return "Raise (All-In consideration)", f"Equity {equity*100:.1f}%. Consider going all-in or raise to {label} total"
        elif equity >= 0.70:
            raise_amount, is_all_in = cap_raise(min_raise(0, min(round(pot_size * 0.60, 2), round(stack_size * 0.30, 2))), stack_size)
            label = "All-In" if is_all_in else f"${raise_amount}"
            return "Raise", f"Equity {equity*100:.1f}%. Raise to {label} total (60% of pot)"
        elif equity >= 0.60:
            raise_amount, is_all_in = cap_raise(min_raise(0, min(round(pot_size * 0.35, 2), round(stack_size * 0.20, 2))), stack_size)
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
    if tie_rate == 1:
        return "Call", f"A split pot is certain in the simulation. Equity {equity*100:.1f}% meets pot odds {pot_odds*100:.1f}%. Call ${bet_to_call}"

    #Equity override
    if equity >= 0.75:
        raise_amount, is_all_in = cap_raise(min_raise(bet_to_call, min(round(pot_size * 0.75, 2), round(stack_size * 0.80, 2))), stack_size)
        label = "All-In" if is_all_in else f"${raise_amount}"
        return "Raise (All-In consideration)", f"Equity {equity*100:.1f}% is dominant. Raise to {label} total"
    elif equity >= 0.65:
        raise_amount, is_all_in = cap_raise(min_raise(bet_to_call, min(round(pot_size * 0.60, 2), round(stack_size * 0.30, 2))), stack_size)
        label = "All-In" if is_all_in else f"${raise_amount}"
        return "Raise", f"Equity {equity*100:.1f}% is strong regardless of pot odds. Raise to {label} total"

    if equity >= 0.55 and equity >= pot_odds + 0.20:
        raise_amount, is_all_in = cap_raise(min_raise(bet_to_call, min(round(pot_size * 0.60, 2), round(stack_size * 0.30, 2))), stack_size)
        label = "All-In" if is_all_in else f"${raise_amount}"
        return "Raise", f"Equity {equity*100:.1f}% far exceeds pot odds {pot_odds*100:.1f}%. Raise to {label} total"
    elif equity >= 0.45 and equity >= pot_odds + 0.10:
        raise_amount, is_all_in = cap_raise(min_raise(bet_to_call, min(round(pot_size * 0.35, 2), round(stack_size * 0.20, 2))), stack_size)
        label = "All-In" if is_all_in else f"${raise_amount}"
        return "Raise Small or Call", f"Equity {equity*100:.1f}% beats pot odds {pot_odds*100:.1f}%. Raise to {label} total or just call ${bet_to_call}"
    else:
        return "Call", f"Equity {equity*100:.1f}% meets pot odds {pot_odds*100:.1f}%. Call ${bet_to_call}"
