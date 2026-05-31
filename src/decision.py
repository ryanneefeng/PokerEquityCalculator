def cap_raise(raise_amount, stack_size):
    if raise_amount >= stack_size:
        return stack_size, True
    return raise_amount, False


def get_recommendation(equity, tie_rate, pot_size, bet_to_call, stack_size):
    total_pot = pot_size + bet_to_call
    effective_equity = equity + (tie_rate / 2)

    if bet_to_call == 0:
        if equity >= 0.85:
            raise_amount, is_all_in = cap_raise(min(round(pot_size * 0.75, 2), round(stack_size * 0.80, 2)), stack_size)
            label = "All-In" if (is_all_in and equity >= 0.65) else f"${raise_amount}"
            return "Raise (All-In consideration)", f"Equity {equity*100:.1f}%. Consider going all-in or raise to {label} total"
        elif equity >= 0.70:
            raise_amount, is_all_in = cap_raise(min(round(pot_size * 0.60, 2), round(stack_size * 0.30, 2)), stack_size)
            label = f"${raise_amount}"
            return "Raise", f"Equity {equity*100:.1f}%. Raise to {label} total (60% of pot)"
        elif equity >= 0.60:
            raise_amount, is_all_in = cap_raise(min(round(pot_size * 0.35, 2), round(stack_size * 0.20, 2)), stack_size)
            label = f"${raise_amount}"
            return "Raise Small", f"Equity {equity*100:.1f}%. Raise to {label} total (35% of pot)"
        elif equity >= 0.40:
            return "Raise if confident or Check", f"Equity {equity*100:.1f}%"
        else:
            return "Check", f"Equity {equity*100:.1f}%"

    pot_odds = bet_to_call / total_pot

    if equity >= 0.65 and effective_equity >= pot_odds + 0.20:
        raise_amount, is_all_in = cap_raise(min(round(pot_size * 0.75, 2), round(stack_size * 0.80, 2)), stack_size)
        label = "All-In" if is_all_in else f"${raise_amount}"
        return "Raise (All-In consideration)", f"Equity {equity*100:.1f}% vs pot odds {pot_odds*100:.1f}%. Raise to {label} total"
    elif equity >= 0.60 and effective_equity >= pot_odds + 0.20:
        raise_amount, is_all_in = cap_raise(min(round(pot_size * 0.60, 2), round(stack_size * 0.30, 2)), stack_size)
        label = f"${raise_amount}"
        return "Raise", f"Equity {equity*100:.1f}% far exceeds pot odds {pot_odds*100:.1f}%. Raise to {label} total"
    elif equity >= 0.45 and effective_equity >= pot_odds + 0.10:
        raise_amount, is_all_in = cap_raise(min(round(pot_size * 0.35, 2), round(stack_size * 0.20, 2)), stack_size)
        label = f"${raise_amount}"
        return "Raise Small or Call", f"Equity {equity*100:.1f}% beats pot odds {pot_odds*100:.1f}%. Raise to {label} total or just call ${bet_to_call}"
    elif equity >= 0.30 and effective_equity >= pot_odds:
        return "Call", f"Equity {equity*100:.1f}% beats pot odds {pot_odds*100:.1f}%. Call ${bet_to_call}"
    elif equity >= 0.20 and effective_equity >= pot_odds - 0.05:
        return "Call or Fold", f"Equity {equity*100:.1f}% close to pot odds {pot_odds*100:.1f}%. Call ${bet_to_call} or fold"
    else:
        return "Fold", f"Equity {equity*100:.1f}% well below pot odds {pot_odds*100:.1f}%"