from src.deck import Card, RANKS, SUITS
from src.equity import calculate_equity, project_next_street
from src.decision import get_recommendation, min_raise
from math import isfinite
from src.evaluator import describe_hand, best_hand_cards
from src.session import log_hand, get_stats
from src.pots import create_players, add_chips, get_call_amount, get_opponent_limit
from src.pots import build_side_pots, return_uncalled_chips, calculate_pot_equity, calculate_call_equity

def display_projections(projections, base_equity):
    if not projections:
        return
    print("  Key cards next street:")
    for card, equity in projections:
        change = equity - base_equity
        direction = "+" if change >= 0 else ""
        print(f"    {card} -> {equity*100:.1f}% ({direction}{change*100:.1f}%)")

def display_results(equity, tie_rate, pot_size, bet_to_call, stack_size, hole_cards=None, board=None, projections=None, base_equity=None,
                    current_contribution=0, last_raise=None, big_blind=1, can_raise=True, opponent_limit=None, call_cost=None):
    action, explanation = get_recommendation(equity, tie_rate, pot_size, bet_to_call, stack_size,
                                            current_contribution, last_raise, big_blind, can_raise,
                                            opponent_limit=opponent_limit, call_cost=call_cost)
    print("\n===========================================")
    if hole_cards is not None and board is not None:
        hand_desc = describe_hand(hole_cards, board)
        print(f"  Hand:       {hand_desc}")
        if len(board) >= 3:
            best_cards = best_hand_cards(hole_cards + board)
            best_str = ", ".join(str(c) for c in best_cards)
            print(f"  Best 5:     {best_str}")
    print(f"  Equity:     {equity * 100:.1f}%")
    print(f"  Tie Rate:   {tie_rate * 100:.1f}%")
    print(f"  Action:     {action}")
    print(f"  Reason:     {explanation}")
    print("===========================================")
    return action

def get_pot_info(all_in=False, remaining_stack=None):
    while True:
        try:
            pot_size = float(input("\nCurrent pot size: $"))
            if not isfinite(pot_size) or pot_size < 0:
                print("Please enter a finite, nonnegative pot size.")
                continue
            if all_in:
                return round(pot_size, 2), 0, 0
            bet_to_call = float(input("Bet to call ($0 if none): $"))
            if remaining_stack is None:
                stack_size = float(input("Your remaining stack size ($0 if all-in): $"))
            else:
                stack_size = remaining_stack
                print(f"  Your remaining stack: ${stack_size}")
            if not isfinite(bet_to_call) or not isfinite(stack_size) or bet_to_call < 0 or stack_size < 0:
                print("Please enter finite, nonnegative bet and stack amounts.")
                continue
            return round(pot_size, 2), round(bet_to_call, 2), round(stack_size, 2)
        except ValueError:
            print("Please enter a valid number.")

def get_money_input(prompt, minimum=0, maximum=None):
    while True:
        try:
            amount = float(input(prompt))
            if not isfinite(amount) or amount < minimum or (maximum is not None and amount > maximum):
                print("Please enter an amount within the allowed range.")
                continue
            return round(amount, 2)
        except ValueError:
            print("Please enter a valid number.")

def get_betting_info(bet_to_call, big_blind, current_contribution=None, previous_last_raise=None):
    if current_contribution is None:
        current_contribution = get_money_input("Your chips already committed this street (including blinds): $")
    current_bet = round(current_contribution + bet_to_call, 2)
    last_raise = big_blind
    if current_bet > big_blind:
        minimum = max(big_blind, previous_last_raise or big_blind)
        last_raise = get_money_input("Last full bet/raise increment (exclude short all-ins): $", minimum, current_bet)
    return current_contribution, last_raise

def get_raise_amount(current_bet, current_contribution, stack_size, last_raise, big_blind):
    minimum = min_raise(current_bet, 0, last_raise, big_blind)
    maximum = round(current_contribution + stack_size, 2)
    print(f"  Minimum bet/raise to ${minimum} total this street; all-in total ${maximum}.")
    while True:
        amount = get_money_input("Your bet/raise to (total this street): $", 0, maximum)
        if amount <= current_bet:
            print("A raise must exceed the current wager.")
            continue
        if amount < minimum and amount != maximum:
            print(f"Raise to at least ${minimum}, or put in your entire stack.")
            continue
        return amount

def get_player_updates(players, position, expected_pot=None, dead_money=0, ask_folds=False):
    while True:
        updated = {p: dict(player) for p, player in players.items()}
        for seat, player in updated.items():
            if seat == position:
                if not player["seen"]:
                    earlier = get_money_input("Your contributions before this street (exclude antes/dead money): $")
                    player["contribution"] = round(earlier + player["street_contribution"], 2)
                    player["seen"] = True
                continue
            print(f"\n  Seat {seat}:")
            if ask_folds and not player["folded"] and (player["stack"] is None or player["stack"] > 0):
                while True:
                    live = input("Still in the hand? (y/n): ").lower().strip()
                    if live in ["y", "n"]:
                        player["folded"] = live == "n"
                        if player["folded"]:
                            player["needs_update"] = True
                        break
                    print("Please enter y or n.")
            if player["folded"]:
                if not player["seen"] or player["needs_update"]:
                    maximum = player["contribution"] + player["stack"] if player["seen"] else None
                    amount = get_money_input("Total contributed before folding (exclude antes/dead money): $", player["contribution"], maximum)
                    extra = round(amount - player["contribution"], 2)
                    player["contribution"] = amount
                    player["street_contribution"] = round(player["street_contribution"] + extra, 2)
                    player["stack"] = round((player["stack"] or extra) - extra, 2)
                    player["seen"] = True
                    player["needs_update"] = False
                continue
            if not player["seen"]:
                player["street_contribution"] = get_money_input("Chips committed this street (including blinds): $")
                earlier = get_money_input("Contributions before this street (exclude antes/dead money): $")
                player["contribution"] = round(earlier + player["street_contribution"], 2)
                player["stack"] = get_money_input("Remaining stack ($0 if all-in): $")
                player["seen"] = True
            elif player["stack"] > 0:
                maximum = round(player["street_contribution"] + player["stack"], 2)
                if get_opponent_limit(updated, seat) == 0:
                    wager = max((other["street_contribution"] for p, other in updated.items()
                                 if p != seat and not other["folded"]), default=0)
                    maximum = min(maximum, max(player["street_contribution"], wager))
                amount = get_money_input("Chips committed this street now: $", player["street_contribution"],
                                         maximum)
                add_chips(player, round(amount - player["street_contribution"], 2))
            else:
                print("  Already all-in; still eligible for matching pots.")
        total = round(sum(player["contribution"] for player in updated.values()) + dead_money, 2)
        if expected_pot is not None and total != round(expected_pot, 2):
            print(f"Contributions total ${total}, but the entered pot was ${expected_pot}. Please re-enter the player information.")
            continue
        try:
            pots, refunds = build_side_pots(updated, dead_money)
            if any(amount > updated[p]["street_contribution"] for p, amount in refunds.items()):
                raise ValueError("Remove uncalled wagers from earlier streets before entering contributions.")
        except ValueError as error:
            print(error)
            continue
        players.clear()
        players.update(updated)
        return total

def finish_betting_round(players, position, dead_money=0):
    print("\nUpdate the other players up to your next decision or the end of this betting round.")
    ask_folds = False
    while True:
        funded = [p for p, player in players.items() if not player["folded"] and (player["stack"] or 0) > 0]
        if len(funded) <= 1 and not any(get_call_amount(players, p) for p in funded) and not any(
            not player["seen"] or player["needs_update"] for player in players.values()
        ):
            break
        total = get_player_updates(players, position, dead_money=dead_money, ask_folds=ask_folds)
        if players[position]["stack"] > 0 and get_call_amount(players, position) > 0:
            return total, players[position]["stack"]
        current_bet = max(player["street_contribution"] for player in players.values() if not player["folded"])
        pending = [p for p, player in players.items() if p != position and not player["folded"] and
                   player["stack"] > 0 and player["street_contribution"] < current_bet]
        if not pending:
            break
        print(f"Seats {pending} still owe chips. Record their call or fold before continuing.")
        ask_folds = True
    for seat, amount in return_uncalled_chips(players).items():
        print(f"  Uncalled ${amount} returned to seat {seat}.")
    pots, refunds = build_side_pots(players, dead_money)
    for i, pot in enumerate(pots):
        label = "Main pot" if i == 0 else f"Side pot {i}"
        print(f"  {label}: ${pot['amount']} -- eligible seats {pot['eligible']}")
    return round(sum(player["contribution"] for player in players.values()) + dead_money, 2), players[position]["stack"]

def display_pots(result, position):
    eligible_count = 0
    for i, pot in enumerate(result["pots"]):
        label = "Main pot" if i == 0 else f"Side pot {i}"
        if position in pot["eligible"]:
            eligible_count += 1
            print(f"  {label}: ${pot['amount']} -- your equity {pot['equity']*100:.1f}%")
        else:
            print(f"  {label}: ${pot['amount']} -- you are not eligible")
    suffix = " after calling" if result.get("call_amount", 0) else ""
    print(f"  Eligible pot{suffix}: ${result['eligible_pot']}")
    if eligible_count > 1:
        print("  Overall equity and tie rate are weighted by your eligible pot amounts.")
    if result.get("call_refund", 0):
        print(f"  ${result['call_refund']} of this call is currently unmatched and excluded from the call cost.")

def get_player_action(recommendation, bet_to_call=0, stack_size=None, can_raise=True):
    valid_actions = ["fold", "call", "raise", "check"]
    while True:
        action = input("\nWhat did you do? (fold, call, raise, check): ").lower().strip()
        if action not in valid_actions:
            print("Invalid action. Please enter fold, call, raise, or check.")
            continue
        if action == "check" and bet_to_call > 0:
            print("You cannot check while facing a bet. Call, raise, or fold.")
            continue
        if action == "call" and bet_to_call == 0:
            print("There is no bet to call. Check, raise, or fold.")
            continue
        if action == "raise" and not can_raise:
            print("Raising is not available. Call or fold if facing a bet, otherwise check.")
            continue
        if action == "raise" and stack_size is not None and stack_size <= bet_to_call:
            print("You do not have enough chips to raise. Call all-in or fold.")
            continue
        if action == "fold":
            if recommendation.lower().startswith("fold"):
                print("Good fold, hand over")
            else:
                print("You folded, hand over")
            return "fold"
        if action == "check":
            return "check"
        if action == "call" and "call" in recommendation.lower():
            return action
        if action != recommendation.split()[0].lower():
            if action == "raise" and "call" in recommendation.lower():
                print("Bold move. I hope luck is on your side!")
            elif action == "call" and "raise" in recommendation.lower():
                print("Playing it safe. I hope you don't regret that later!")
            elif action == "call" and "fold" in recommendation.lower():
                print("Risky call. I hope luck is on your side!")
            else:
                print(f"You chose to {action} instead of the recommended action: {recommendation}. I hope luck is on your side!")
        return action

def remove_folded_positions(num_folded, active_positions, position, players=None):
    if active_positions is None:
        return
    if players is not None:
        foldable = [p for p in active_positions if p != position and
                    (players[p]["stack"] is None or players[p]["stack"] > 0)]
        if num_folded > len(foldable):
            raise ValueError("An all-in player cannot fold.")
    if num_folded == len(active_positions) - 1:
        if players is not None:
            for p in active_positions:
                if p != position:
                    players[p]["folded"] = True
                    players[p]["needs_update"] = True
        active_positions[:] = [position]
        return

    for i in range(num_folded):
        while True:
            available = [p for p in active_positions if p != position and
                         (players is None or players[p]["stack"] is None or players[p]["stack"] > 0)]
            print(f"  Active opponent seats: {', '.join(str(p) for p in available)}")
            try:
                folded_position = int(input(f"Seat number of folded player {i + 1}: "))
                if folded_position not in available:
                    print("Please enter an active opponent's seat number.")
                    continue
                active_positions.remove(folded_position)
                if players is not None:
                    players[folded_position]["folded"] = True
                    players[folded_position]["needs_update"] = True
                break
            except ValueError:
                print("Please enter a valid number.")

def handle_folds_before(num_players, known_opponents, dead_cards, used_cards, active_positions=None, position=None, players=None):
    foldable = num_players - 1
    if players is not None:
        foldable = sum(p != position and not player["folded"] and
                       (player["stack"] is None or player["stack"] > 0) for p, player in players.items())
        if foldable == 0:
            return num_players, known_opponents, dead_cards
    while True:
        folded = input("\nDid anyone fold or reveal cards before your turn this street? (y/n): ").lower().strip()
        if folded in ["y", "n"]:
            break
        print("Please enter y or n.")

    if folded == "n":
        return num_players, known_opponents, dead_cards

    while True:
        try:
            num_folded = int(input("How many players folded? "))
            if num_folded < 1 or num_folded > foldable:
                print(f"Please enter a number between 1 and {foldable}.")
                continue
            break
        except ValueError:
            print("Please enter a valid number.")

    remove_folded_positions(num_folded, active_positions, position, players)
    num_players -= num_folded

    if num_players == 1:
        return num_players, known_opponents, dead_cards

    while True:
        showed = input("Did any of them show their hand? (y/n): ").lower().strip()
        if showed in ["y", "n"]:
            break
        print("Please enter y or n.")

    if showed == "y":
        if num_folded == 1:
            num_showed = 1
        else:
            while True:
                try:
                    num_showed = int(input("How many showed their hand? "))
                    if num_showed < 1 or num_showed > num_folded:
                        print(f"Please enter a number between 1 and {num_folded}.")
                        continue
                    break
                except ValueError:
                    print("Please enter a valid number.")

        for i in range(num_showed):
            print(f"\nEnter the 2 cards for the player who showed hand {i + 1}:")
            card1 = get_card_input("Card 1: ", used_cards)
            card2 = get_card_input("Card 2: ", used_cards)
            dead_cards.append(card1)
            dead_cards.append(card2)

    return num_players, known_opponents, dead_cards

def handle_folds(num_players, known_opponents, dead_cards, used_cards, active_positions=None, position=None, players=None):
    foldable = num_players - 1
    if players is not None:
        foldable = sum(p != position and not player["folded"] and
                       (player["stack"] is None or player["stack"] > 0) for p, player in players.items())
        if foldable == 0:
            return num_players, known_opponents, dead_cards
    while True:
        folded = input("\nDid anyone fold this round? (y/n): ").lower().strip()
        if folded in ["y", "n"]:
            break
        print("Please enter y or n.")

    if folded == "n":
        return num_players, known_opponents, dead_cards

    while True:
        try:
            num_folded = int(input("How many players folded? "))
            if num_folded < 1 or num_folded > foldable:
                print(f"Please enter a number between 1 and {foldable}.")
                continue
            break
        except ValueError:
            print("Please enter a valid number.")

    remove_folded_positions(num_folded, active_positions, position, players)
    num_players -= num_folded

    # If everyone else folded, no need to ask about shown cards
    if num_players == 1:
        return num_players, known_opponents, dead_cards

    while True:
        showed = input("Did any of them show their hand? (y/n): ").lower().strip()
        if showed in ["y", "n"]:
            break
        print("Please enter y or n.")

    if showed == "y":
        if num_folded == 1:
            num_showed = 1
        else:
            while True:
                try:
                    num_showed = int(input("How many showed their hand? "))
                    if num_showed < 1 or num_showed > num_folded:
                        print(f"Please enter a number between 1 and {num_folded}.")
                        continue
                    break
                except ValueError:
                    print("Please enter a valid number.")

        for i in range(num_showed):
            print(f"\nEnter the 2 cards for the player who showed hand {i + 1}:")
            card1 = get_card_input("Card 1: ", used_cards)
            card2 = get_card_input("Card 2: ", used_cards)
            dead_cards.append(card1)
            dead_cards.append(card2)

    return num_players, known_opponents, dead_cards

def get_position(num_players):
    print("\nWhat is your seat position at the table?")
    print("1 = Small Blind, 2 = Big Blind", end="")
    if num_players > 2:
        print(f", 3 to {num_players} = UTG to Dealer", end="")
    print()

    while True:
        try:
            position = int(input(f"Your position (1-{num_players}): "))
            if position < 1 or position > num_players:
                print(f"Please enter a number between 1 and {num_players}.")
                continue
            break
        except ValueError:
            print("Please enter a valid number.")

    if position == 1:
        label = "Small Blind"
    elif position == 2:
        label = "Big Blind"
    elif position == 3:
        label = "UTG"
    elif position == num_players:
        label = "Dealer (Button)"
    elif position == num_players - 1 and num_players >= 5:
        label = "Cutoff"
    elif position > 3:
        label = f"UTG+{position - 3}"
    else:
        label = "UTG"

    print(f"\nYou are playing from: {label}")
    return position, label

def ask_action_reopened():
    while True:
        reopened = input("\nAfter your action, did anyone bet or raise so you owe more chips? (y/n): ").lower().strip()
        if reopened in ["y", "n"]:
            return reopened == "y"
        print("Please enter y or n.")

def run_betting_round(street_label, num_players, known_opponents, dead_cards, used_cards,
                       player_hand, board, is_all_in, prev_pot, prev_stack,
                       show_projections=False, skip_first_folds_before=False,
                       active_positions=None, position=None, big_blind=1, players=None, dead_money=0):
    """
    Runs the user's decision(s) for a single street.

    A street isn't always one decision. A later bet or raise can require
    another call or fold, even if a short all-in does not reopen raising.
    Keep the user's contribution so each new decision uses the extra amount
    owed, and compare it with the last full increment to determine raising rights.
    """
    equity, tie_rate = 0.0, 0.0
    action, player_action = "", ""
    action_returned = False
    current_contribution = None
    last_raise = None
    recorded_state = False
    if players is not None:
        if active_positions is None:
            active_positions = [p for p in players if not players[p]["folded"]]
        if players[position]["seen"]:
            current_contribution = players[position]["street_contribution"]

    while True:
        if not recorded_state and not (skip_first_folds_before and not action_returned):
            num_players, known_opponents, dead_cards = handle_folds_before(
                num_players, known_opponents, dead_cards, used_cards, active_positions, position, players
            )
            if num_players == 1:
                return {
                    "status": "won_by_fold", "num_players": num_players,
                    "known_opponents": known_opponents, "dead_cards": dead_cards,
                    "is_all_in": is_all_in, "prev_pot": prev_pot, "prev_stack": prev_stack,
                    "equity": equity, "action": action, "player_action": player_action,
                }

        if action_returned:
            print(f"\n  Action returns on the {street_label} -- another player bet or raised.")
            print("  Pot odds have changed, so let's get an updated read before you act again.")

        auto_runout = False
        if players is not None and players[position]["seen"]:
            auto_runout = players[position]["stack"] == 0 or (
                get_opponent_limit(players, position) == 0 and get_call_amount(players, position) == 0
            )
        if auto_runout:
            pot_size, stack_size = finish_betting_round(players, position, dead_money)
            bet_to_call = 0
        elif recorded_state:
            pot_size = round(sum(player["contribution"] for player in players.values()) + dead_money, 2)
            stack_size = players[position]["stack"]
            bet_to_call = get_call_amount(players, position, big_blind, street_label == "Pre-Flop")
        else:
            remaining_stack = players[position]["stack"] if players is not None and players[position]["seen"] else None
            pot_size, bet_to_call, stack_size = get_pot_info(
                all_in=is_all_in, remaining_stack=remaining_stack if players is not None else (prev_stack if action_returned else None)
            )
            if players is not None:
                if current_contribution is None:
                    current_contribution = get_money_input("Your chips already committed this street (including blinds): $")
                players[position]["street_contribution"] = current_contribution
                players[position]["stack"] = stack_size
                get_player_updates(players, position, pot_size, dead_money)
                bet_to_call = get_call_amount(players, position, big_blind, street_label == "Pre-Flop")
                print(f"  Bet to call from recorded contributions: ${bet_to_call}")
                auto_runout = stack_size == 0 or (get_opponent_limit(players, position) == 0 and bet_to_call == 0)
                if auto_runout:
                    pot_size, stack_size = finish_betting_round(players, position, dead_money)
                    bet_to_call = 0
        if players is not None:
            active_positions[:] = [p for p in players if not players[p]["folded"]]
            num_players = len(active_positions)
            is_all_in = stack_size == 0
        if action_returned and bet_to_call == 0:
            break

        if not is_all_in:
            if prev_pot is not None and pot_size < prev_pot:
                print(f"Warning: pot size decreased from ${prev_pot} to ${pot_size}. Please ensure you entered the correct pot size.")
            if prev_stack is not None and stack_size > prev_stack:
                print(f"Warning: stack size increased from ${prev_stack} to ${stack_size}. Please ensure you entered the correct stack size.")
            if stack_size == 0:
                is_all_in = True

        prev_pot, prev_stack = pot_size, stack_size

        pot_result = None
        decision_pot = pot_size
        opponent_limit = None
        if players is not None:
            if auto_runout:
                pot_result = calculate_pot_equity(player_hand, board, players, position, dead_cards, dead_money=dead_money)
            else:
                pot_result = calculate_call_equity(player_hand, board, players, position, bet_to_call, dead_cards, dead_money=dead_money)
                decision_pot = pot_result["decision_pot"]
            equity, tie_rate = pot_result["equity"], pot_result["tie_rate"]
            opponent_limit = get_opponent_limit(players, position)
        else:
            equity, tie_rate = calculate_equity(
                player_hand, board, num_players, known_opponents=known_opponents, dead_cards=dead_cards
            )

        if is_all_in or auto_runout:
            hand_desc = describe_hand(player_hand, board)
            print("\n===========================================")
            print(f"  Hand:       {hand_desc}")
            if len(board) >= 3:
                best_cards = best_hand_cards(player_hand + board)
                best_str = ", ".join(str(c) for c in best_cards)
                print(f"  Best 5:     {best_str}")
            status = "you are all-in" if is_all_in else "no opponent can bet; running out the board"
            print(f"  Equity:     {equity * 100:.1f}% ({status})")
            if pot_result is not None:
                display_pots(pot_result, position)
            print("===========================================")
            # No more decisions once you're all-in, but others can still
            # fold among themselves before the next card is dealt.
            if players is None:
                num_players, known_opponents, dead_cards = handle_folds(
                    num_players, known_opponents, dead_cards, used_cards, active_positions, position
                )
            if num_players == 1:
                return {
                    "status": "won_by_fold", "num_players": num_players,
                    "known_opponents": known_opponents, "dead_cards": dead_cards,
                    "is_all_in": is_all_in, "prev_pot": prev_pot, "prev_stack": prev_stack,
                    "equity": equity, "action": action, "player_action": player_action,
                }
            return {
                "status": "continue", "num_players": num_players, "known_opponents": known_opponents,
                "dead_cards": dead_cards, "is_all_in": is_all_in, "prev_pot": prev_pot, "prev_stack": prev_stack,
                "equity": equity, "action": action, "player_action": player_action,
            }

        current_contribution, last_raise = get_betting_info(bet_to_call, big_blind, current_contribution, last_raise)
        can_raise = not action_returned or bet_to_call >= last_raise
        if not can_raise:
            print("  The extra amount is less than a full raise. You can call or fold, but cannot raise.")
        if opponent_limit is not None and opponent_limit <= current_contribution + bet_to_call:
            can_raise = False
            print("  No opponent has chips to contest another raise.")
        if pot_result is not None:
            display_pots(pot_result, position)
        if show_projections and players is None:
            projections, base_equity = project_next_street(
                player_hand, board, num_players, known_opponents=known_opponents, dead_cards=dead_cards
            )
            action = display_results(equity, tie_rate, pot_size, bet_to_call, stack_size, player_hand, board, projections, base_equity,
                                     current_contribution, last_raise, big_blind, can_raise)
        else:
            action = display_results(equity, tie_rate, decision_pot, bet_to_call, stack_size, player_hand, board,
                                     current_contribution=current_contribution, last_raise=last_raise, big_blind=big_blind,
                                     can_raise=can_raise, opponent_limit=opponent_limit,
                                     call_cost=pot_result["call_cost"] if pot_result is not None else None)

        player_action = get_player_action(action, bet_to_call, stack_size, can_raise)
        if player_action == "fold":
            if players is not None:
                players[position]["folded"] = True
            return {
                "status": "folded", "num_players": num_players, "known_opponents": known_opponents,
                "dead_cards": dead_cards, "is_all_in": is_all_in, "prev_pot": prev_pot, "prev_stack": prev_stack,
                "equity": equity, "action": action, "player_action": player_action,
            }

        chips_added = 0
        if player_action == "raise":
            current_bet = round(current_contribution + bet_to_call, 2)
            raise_amount = get_raise_amount(current_bet, current_contribution, stack_size, last_raise, big_blind)
            last_raise = max(last_raise, round(raise_amount - current_bet, 2))
            chips_added = round(raise_amount - current_contribution, 2)
        elif player_action == "call":
            chips_added = min(bet_to_call, stack_size)
        current_contribution = round(current_contribution + chips_added, 2)
        if players is not None:
            add_chips(players[position], chips_added)
        prev_pot = round(pot_size + chips_added, 2)
        prev_stack = round(stack_size - chips_added, 2)
        if prev_stack == 0:
            is_all_in = True

        num_players, known_opponents, dead_cards = handle_folds(num_players, known_opponents, dead_cards, used_cards, active_positions, position, players)
        if num_players == 1:
            if players is not None:
                prev_pot, prev_stack = finish_betting_round(players, position, dead_money)
            return {
                "status": "won_by_fold", "num_players": num_players, "known_opponents": known_opponents,
                "dead_cards": dead_cards, "is_all_in": is_all_in, "prev_pot": prev_pot, "prev_stack": prev_stack,
                "equity": equity, "action": action, "player_action": player_action,
            }

        if players is not None:
            prev_pot, prev_stack = finish_betting_round(players, position, dead_money)
            active_positions[:] = [p for p in players if not players[p]["folded"]]
            num_players = len(active_positions)
            is_all_in = prev_stack == 0
            if num_players == 1:
                return {
                    "status": "won_by_fold", "num_players": num_players,
                    "known_opponents": known_opponents, "dead_cards": dead_cards,
                    "is_all_in": is_all_in, "prev_pot": prev_pot, "prev_stack": prev_stack,
                    "equity": equity, "action": action, "player_action": player_action,
                }
            if is_all_in or get_call_amount(players, position) == 0:
                break
            action_returned = True
            recorded_state = True
            continue
        if is_all_in or not ask_action_reopened():
            break
        action_returned = True

    return {
        "status": "continue", "num_players": num_players, "known_opponents": known_opponents,
        "dead_cards": dead_cards, "is_all_in": is_all_in, "prev_pot": prev_pot, "prev_stack": prev_stack,
        "equity": equity, "action": action, "player_action": player_action,
    }

def continuous_game(num_players, player_hand, known_opponents=None, used_cards=None):
    if known_opponents is None:
        known_opponents = []
    if used_cards is None:
        used_cards = set()
    dead_cards = []
    is_all_in = False

    board = []
    equity = 0.0
    action = ""
    player_action = ""

    big_blind = get_money_input("Big blind size: $", 0.01)
    position, position_label = get_position(num_players)
    table_size = num_players
    active_positions = list(range(1, table_size + 1))
    players = create_players(table_size)
    dead_money = get_money_input("Antes/dead money included in the pot (exclude bets): $")
    for seat, hand in zip([p for p in players if p != position], known_opponents):
        players[seat]["hand"] = hand

    prev_pot = None
    prev_stack = None

    print("\n-- PRE-FLOP --")
    print(f"  Position: {position_label}")
    display_acting_order(table_size, position, "preflop", active_positions, players)

    if position == 1:
        print("  You are the Small Blind -- you must post the small blind before action begins.")
    elif position == 2:
        print("  You are the Big Blind -- you must post the big blind before action begins.")
    else:
        print("  You are not a blind -- you can fold, call, or raise freely.")

    preflop_order = get_acting_order(table_size, position, "preflop", active_positions)
    your_preflop_index = preflop_order.index(position)

    streets = [
        ("Pre-Flop", False, your_preflop_index == 0),
        ("Flop", True, False),
        ("Turn", True, False),
        ("River", False, False),
    ]

    for street_label, show_projections, skip_first_folds_before in streets:
        if street_label != "Pre-Flop":
            for player in players.values():
                player["street_contribution"] = 0
        if street_label == "Flop":
            input("Press Enter to continue to the Flop...")
            print("\nEnter the 3 Flop cards:")
            flop = [get_card_input(f"Flop card {i + 1}: ", used_cards) for i in range(3)]
            board = flop
            print("\n-- FLOP --")
            display_acting_order(table_size, position, "postflop", active_positions, players)
        elif street_label == "Turn":
            input("Press Enter to continue to the Turn...")
            turn = get_card_input("\nTurn card: ", used_cards)
            board = board + [turn]
            print("\n-- TURN --")
            display_acting_order(table_size, position, "postflop", active_positions, players)
        elif street_label == "River":
            input("Press Enter to continue to the River...")
            river = get_card_input("\nRiver card: ", used_cards)
            board = board + [river]
            print("\n-- RIVER --")
            display_acting_order(table_size, position, "postflop", active_positions, players)

        result = run_betting_round(
            street_label, num_players, known_opponents, dead_cards, used_cards,
            player_hand, board, is_all_in, prev_pot, prev_stack,
            show_projections=show_projections, skip_first_folds_before=skip_first_folds_before,
            active_positions=active_positions, position=position, big_blind=big_blind,
            players=players, dead_money=dead_money,
        )
        num_players = result["num_players"]
        known_opponents = result["known_opponents"]
        dead_cards = result["dead_cards"]
        is_all_in = result["is_all_in"]
        prev_pot = result["prev_pot"]
        prev_stack = result["prev_stack"]
        equity = result["equity"]
        action = result["action"]
        player_action = result["player_action"]

        if result["status"] == "won_by_fold":
            print("Everyone folded. You win the pot!")
            log_hand(player_hand, board, num_players, equity, action, player_action, True)
            print("\nHand logged.")
            return
        if result["status"] == "folded":
            log_hand(player_hand, board, num_players, equity, action, player_action, False)
            print("\nHand logged.")
            return

    while True:
        won_input = input("\nDid you win any share of a pot? (y/n): ").lower().strip()
        if won_input in ["y", "n"]:
            break
        print("Please enter y or n.")

    print("\nHand complete!")
    log_hand(player_hand, board, num_players, equity, action, player_action, won_input == "y")
    print("Hand logged.")

def parse_card(card_str):
    parts = card_str.title().split()
    if len(parts) != 2:
        raise ValueError("Invalid card format. Use format: A Hearts")
    rank, suit = parts
    if rank not in RANKS:
        raise ValueError(f"Invalid rank: {rank}. Must be one of {RANKS}")
    if suit not in SUITS:
        raise ValueError(f"Invalid suit: {suit}. Must be one of {SUITS}")
    return Card(rank, suit)

def get_card_input(prompt, used_cards=None):
    while True:
        try:
            card = parse_card(input(prompt))
            if used_cards is not None and card in used_cards:
                print(f"{card} is already in play. Please enter a different card.")
                continue
            if used_cards is not None:
                used_cards.add(card)
            return card
        except ValueError as e:
            print(f"Error: {e}. Please try again.")

def get_acting_order(num_players, position, street, active_positions=None, players=None):
    positions = list(range(1, num_players + 1))
    if street == "preflop":
        # UTG first, blinds last
        order = positions[2:] + positions[:2]
    else:
        # SB first, dealer last
        order = [2, 1] if num_players == 2 else positions
    if active_positions is not None:
        order = [p for p in order if p in active_positions]
    if players is not None:
        order = [p for p in order if not players[p]["folded"] and
                 (players[p]["stack"] is None or players[p]["stack"] > 0)]
    return order

def display_acting_order(num_players, position, street, active_positions=None, players=None):
    order = get_acting_order(num_players, position, street, active_positions, players)
    position_labels = {1: "SB", 2: "BB", 3: "UTG", num_players: "Dealer"}
    if num_players == 2:
        position_labels = {1: "SB/Dealer", 2: "BB"}
    if num_players >= 5:
        position_labels[num_players - 1] = "Cutoff"
    for i in range(4, num_players - 1 if num_players >= 5 else num_players):
        position_labels[i] = f"UTG+{i-3}"

    order_str = " → ".join([position_labels.get(p, str(p)) + f" [seat {p}]" + (" (YOU)" if p == position else "") for p in order])
    print(f"  Acting order: {order_str if order else 'No players have chips left to bet'}")
    if position in order:
        print(f"  You act {order.index(position) + 1} of {len(order)}")
    else:
        print("  You are all-in and have no betting turn.")
    if players is not None:
        all_in = [p for p in players if not players[p]["folded"] and players[p]["stack"] == 0]
        if all_in:
            print(f"  All-in seats still in the hand: {all_in}")

def main():
    while True:
        print("\n===========================================")
        print("      Poker Hand Equity Calculator")
        print("===========================================\n")

        print("Mode:")
        print("1 = Single calculation")
        print("2 = Full game mode (pre-flop to river)")
        print("3 = View session stats")
        while True:
            mode = input("\nSelect mode (1, 2, or 3): ")
            if mode in ["1", "2", "3"]:
                break
            print("Invalid mode. Please enter 1, 2, or 3.")

        if mode == '3':
            stats = get_stats()
            if stats is None:
                print("\nNo hands logged yet. Play some hands in continuous mode first.")
            else:
                print("\n===========================================")
                print("           Session Statistics")
                print("===========================================")
                print(f"  Total hands played:       {stats['total_hands']}")
                print(f"  Wins:                     {stats['wins']}")
                print(f"  Win rate:                 {stats['win_rate']}%")
                print(f"  Average final equity:     {stats['avg_equity']}%")
                print(f"  Followed recommendation:  {stats['follow_rate']}%")
                print(f"  Win rate when followed:   {stats['followed_win_rate']}%")
                print(f"  Win rate when deviated:   {stats['deviated_win_rate']}%")
                print("===========================================\n")
            again = input("Play another hand? (y/n): ").lower().strip()
            if again != 'y':
                print("\nThanks for playing!")
                break
            continue

        while True:
            try:
                num_players = int(input("\nHow many players at the table (including you)? "))
                if num_players < 2 or num_players > 10:
                    print("Please enter a number between 2 and 10.")
                    continue
                break
            except ValueError:
                print("Please enter a valid number.")

        print("\nEnter your 2 hole cards (e.g. A Hearts, 10 Spades):")
        used_cards = set()
        card1 = get_card_input("Card 1: ", used_cards)
        card2 = get_card_input("Card 2: ", used_cards)
        player_hand = [card1, card2]

        if mode == '2':
            continuous_game(num_players, player_hand, used_cards=used_cards)
        else:
            players = create_players(num_players)
            print("\nHow many cards are on the board?")
            print("0 = Pre-flop, 3 = Flop, 4 = Turn, 5 = River")
            while True:
                try:
                    num_board_cards = int(input("Number of board cards: "))
                    if num_board_cards not in [0, 3, 4, 5]:
                        print("Must be 0, 3, 4, or 5.")
                        continue
                    break
                except ValueError:
                    print("Please enter a valid number.")

            board = []
            for i in range(num_board_cards):
                card = get_card_input(f"Board card {i + 1}: ", used_cards)
                board.append(card)

            dead_cards = []
            known_opponents = []
            won_by_fold = False
            while True:
                has_revealed = input("\nHave any players revealed their cards (folded and shown)? (y/n): ").lower().strip()
                if has_revealed == "y":
                    while True:
                        try:
                            num_revealed = int(input("\nHow many players revealed their cards? "))
                            if num_revealed < 1 or num_revealed >= num_players:
                                print(f"Please enter a number between 1 and {num_players - 1}.")
                                continue
                            break
                        except ValueError:
                            print("Please enter a valid number.")

                    if num_revealed >= num_players - 1:
                        print("All opponents have folded. You win the pot!")
                        won_by_fold = True
                        break

                    num_players -= num_revealed
                    for seat in range(2, num_revealed + 2):
                        players[seat]["folded"] = True
                    for i in range(num_revealed):
                        print(f"\nEnter the 2 cards for player {i + 1} who revealed:")
                        card1 = get_card_input("Card 1: ", used_cards)
                        card2 = get_card_input("Card 2: ", used_cards)
                        dead_cards.append(card1)
                        dead_cards.append(card2)
                    break
                elif has_revealed == "n":
                    break
                else:
                    print("Please enter y or n.")

            if not won_by_fold:
                pot_size, bet_to_call, stack_size = get_pot_info()
                big_blind = get_money_input("Big blind size: $", 0.01)
                current_contribution = get_money_input("Your chips already committed this street (including blinds): $")
                dead_money = get_money_input("Antes/dead money included in the pot (exclude bets): $")
                print("  You are seat 1; use the other seat numbers consistently for this calculation.")
                players[1]["stack"] = stack_size
                players[1]["street_contribution"] = current_contribution
                get_player_updates(players, 1, pot_size, dead_money, ask_folds=True)
                bet_to_call = get_call_amount(players, 1, big_blind, len(board) == 0)
                last_raise = big_blind
                if stack_size > 0 and get_opponent_limit(players, 1) > 0:
                    current_contribution, last_raise = get_betting_info(bet_to_call, big_blind, current_contribution)

                print("\nRunning simulation...")
                if sum(not player["folded"] for player in players.values()) == 1:
                    print("All opponents have folded. You win the pot!")
                else:
                    result = calculate_call_equity(player_hand, board, players, 1, bet_to_call, dead_cards, dead_money=dead_money)
                    display_pots(result, 1)
                    display_results(result["equity"], result["tie_rate"], result["decision_pot"], bet_to_call, stack_size, player_hand, board,
                                     current_contribution=current_contribution, last_raise=last_raise, big_blind=big_blind,
                                     opponent_limit=get_opponent_limit(players, 1), call_cost=result["call_cost"])

        again = input("\nPlay another hand? (y/n): ").lower().strip()
        if again != 'y':
            print("\nThanks for playing!")
            break

if __name__ == "__main__":
    main()
