from src.deck import Card, RANKS, SUITS
from src.equity import calculate_equity, project_next_street
from src.decision import get_recommendation
from src.evaluator import describe_hand, best_hand_cards
from src.session import log_hand, get_stats

def display_projections(projections, base_equity):
    if not projections:
        return
    print("  Key cards next street:")
    for card, equity in projections:
        change = equity - base_equity
        direction = "+" if change >= 0 else ""
        print(f"    {card} -> {equity*100:.1f}% ({direction}{change*100:.1f}%)")

def display_results(equity, tie_rate, pot_size, bet_to_call, stack_size, hole_cards=None, board=None, projections=None, base_equity=None):
    action, explanation = get_recommendation(equity, tie_rate, pot_size, bet_to_call, stack_size)
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

def get_pot_info(all_in=False):
    while True:
        try:
            pot_size = float(input("\nCurrent pot size: $"))
            if all_in:
                return pot_size, 0, 0
            bet_to_call = float(input("Bet to call ($0 if none): $"))
            stack_size = float(input("Your remaining stack size ($0 if all-in): $"))
            return pot_size, bet_to_call, stack_size
        except ValueError:
            print("Please enter a valid number.")
            
def get_player_action(recommendation):
    valid_actions = ["fold", "call", "raise", "check"]
    while True:
        action = input("\nWhat did you do? (fold, call, raise, check): ").lower().strip()
        if action not in valid_actions:
            print("Invalid action. Please enter fold, call, raise, or check.")
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

def remove_folded_positions(num_folded, active_positions, position):
    if active_positions is None:
        return
    if num_folded == len(active_positions) - 1:
        active_positions[:] = [position]
        return

    for i in range(num_folded):
        while True:
            available = [p for p in active_positions if p != position]
            print(f"  Active opponent seats: {', '.join(str(p) for p in available)}")
            try:
                folded_position = int(input(f"Seat number of folded player {i + 1}: "))
                if folded_position not in available:
                    print("Please enter an active opponent's seat number.")
                    continue
                active_positions.remove(folded_position)
                break
            except ValueError:
                print("Please enter a valid number.")

def handle_folds_before(num_players, known_opponents, dead_cards, used_cards, active_positions=None, position=None):
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
            if num_folded < 1 or num_folded >= num_players:
                print(f"Please enter a number between 1 and {num_players - 1}.")
                continue
            break
        except ValueError:
            print("Please enter a valid number.")

    remove_folded_positions(num_folded, active_positions, position)
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

def handle_folds(num_players, known_opponents, dead_cards, used_cards, active_positions=None, position=None):
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
            if num_folded < 1 or num_folded >= num_players:
                print(f"Please enter a number between 1 and {num_players - 1}.")
                continue
            break
        except ValueError:
            print("Please enter a valid number.")

    remove_folded_positions(num_folded, active_positions, position)
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
        reopened = input("\nAfter your action, did a player still to act raise (reopening the betting)? (y/n): ").lower().strip()
        if reopened in ["y", "n"]:
            return reopened == "y"
        print("Please enter y or n.")

def run_betting_round(street_label, num_players, known_opponents, dead_cards, used_cards,
                       player_hand, board, is_all_in, prev_pot, prev_stack,
                       show_projections=False, skip_first_folds_before=False,
                       active_positions=None, position=None):
    """
    Runs the user's decision(s) for a single street.

    A street isn't always one decision. If a player who acts after the user
    raises, the action reopens: the pot just grew, the bet to call is new,
    and pot odds have to be recalculated -- the user needs a fresh
    recommendation and a real chance to act again, not stale numbers carried
    into the next street. This loops for exactly that case, and keeps looping
    through re-raise wars until action actually closes on the user (or
    everyone folds, or the user is all-in and has no more decisions to make).
    """
    equity, tie_rate = 0.0, 0.0
    action, player_action = "", ""
    reopened = False

    while True:
        if not (skip_first_folds_before and not reopened):
            num_players, known_opponents, dead_cards = handle_folds_before(
                num_players, known_opponents, dead_cards, used_cards, active_positions, position
            )
            if num_players == 1:
                return {
                    "status": "won_by_fold", "num_players": num_players,
                    "known_opponents": known_opponents, "dead_cards": dead_cards,
                    "is_all_in": is_all_in, "prev_pot": prev_pot, "prev_stack": prev_stack,
                    "equity": equity, "action": action, "player_action": player_action,
                }

        if reopened:
            print(f"\n  Action reopens on the {street_label} -- a player raised after your last action.")
            print("  Pot odds have changed, so let's get an updated read before you act again.")

        pot_size, bet_to_call, stack_size = get_pot_info(all_in=is_all_in)

        if not is_all_in:
            if prev_pot is not None and pot_size < prev_pot:
                print(f"Warning: pot size decreased from ${prev_pot} to ${pot_size}. Please ensure you entered the correct pot size.")
            if prev_stack is not None and stack_size > prev_stack:
                print(f"Warning: stack size increased from ${prev_stack} to ${stack_size}. Please ensure you entered the correct stack size.")
            if stack_size == 0:
                is_all_in = True

        prev_pot, prev_stack = pot_size, stack_size

        equity, tie_rate = calculate_equity(
            player_hand, board, num_players, known_opponents=known_opponents, dead_cards=dead_cards
        )

        if is_all_in:
            hand_desc = describe_hand(player_hand, board)
            print("\n===========================================")
            print(f"  Hand:       {hand_desc}")
            if len(board) >= 3:
                best_cards = best_hand_cards(player_hand + board)
                best_str = ", ".join(str(c) for c in best_cards)
                print(f"  Best 5:     {best_str}")
            print(f"  Equity:     {equity * 100:.1f}% (you are all-in)")
            print("===========================================")
            # No more decisions once you're all-in, but others can still
            # fold among themselves before the next card is dealt.
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

        if show_projections:
            projections, base_equity = project_next_street(
                player_hand, board, num_players, known_opponents=known_opponents, dead_cards=dead_cards
            )
            action = display_results(equity, tie_rate, pot_size, bet_to_call, stack_size, player_hand, board, projections, base_equity)
        else:
            action = display_results(equity, tie_rate, pot_size, bet_to_call, stack_size, player_hand, board)

        player_action = get_player_action(action)
        if player_action == "fold":
            return {
                "status": "folded", "num_players": num_players, "known_opponents": known_opponents,
                "dead_cards": dead_cards, "is_all_in": is_all_in, "prev_pot": prev_pot, "prev_stack": prev_stack,
                "equity": equity, "action": action, "player_action": player_action,
            }

        num_players, known_opponents, dead_cards = handle_folds(num_players, known_opponents, dead_cards, used_cards, active_positions, position)
        if num_players == 1:
            return {
                "status": "won_by_fold", "num_players": num_players, "known_opponents": known_opponents,
                "dead_cards": dead_cards, "is_all_in": is_all_in, "prev_pot": prev_pot, "prev_stack": prev_stack,
                "equity": equity, "action": action, "player_action": player_action,
            }

        if not ask_action_reopened():
            break
        reopened = True

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

    position, position_label = get_position(num_players)
    table_size = num_players
    active_positions = list(range(1, table_size + 1))

    prev_pot = None
    prev_stack = None

    print("\n-- PRE-FLOP --")
    print(f"  Position: {position_label}")
    display_acting_order(table_size, position, "preflop", active_positions)

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
        if street_label == "Flop":
            input("Press Enter to continue to the Flop...")
            print("\nEnter the 3 Flop cards:")
            flop = [get_card_input(f"Flop card {i + 1}: ", used_cards) for i in range(3)]
            board = flop
            print("\n-- FLOP --")
            display_acting_order(table_size, position, "postflop", active_positions)
        elif street_label == "Turn":
            input("Press Enter to continue to the Turn...")
            turn = get_card_input("\nTurn card: ", used_cards)
            board = board + [turn]
            print("\n-- TURN --")
            display_acting_order(table_size, position, "postflop", active_positions)
        elif street_label == "River":
            input("Press Enter to continue to the River...")
            river = get_card_input("\nRiver card: ", used_cards)
            board = board + [river]
            print("\n-- RIVER --")
            display_acting_order(table_size, position, "postflop", active_positions)

        result = run_betting_round(
            street_label, num_players, known_opponents, dead_cards, used_cards,
            player_hand, board, is_all_in, prev_pot, prev_stack,
            show_projections=show_projections, skip_first_folds_before=skip_first_folds_before,
            active_positions=active_positions, position=position,
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
        won_input = input("\nDid you win this hand? (y/n): ").lower().strip()
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

def get_acting_order(num_players, position, street, active_positions=None):
    positions = list(range(1, num_players + 1))
    if street == "preflop":
        # UTG first, blinds last
        order = positions[2:] + positions[:2]
    else:
        # SB first, dealer last
        order = [2, 1] if num_players == 2 else positions
    if active_positions is not None:
        order = [p for p in order if p in active_positions]
    return order

def display_acting_order(num_players, position, street, active_positions=None):
    order = get_acting_order(num_players, position, street, active_positions)
    position_labels = {1: "SB", 2: "BB", 3: "UTG", num_players: "Dealer"}
    if num_players == 2:
        position_labels = {1: "SB/Dealer", 2: "BB"}
    if num_players >= 5:
        position_labels[num_players - 1] = "Cutoff"
    for i in range(4, num_players - 1 if num_players >= 5 else num_players):
        position_labels[i] = f"UTG+{i-3}"

    order_str = " → ".join([position_labels.get(p, str(p)) + f" [seat {p}]" + (" (YOU)" if p == position else "") for p in order])
    acting_index = order.index(position) + 1
    print(f"  Acting order: {order_str}")
    print(f"  You act {acting_index} of {len(order)}")

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
                while True:
                    try:
                        pot_size = float(input("\nCurrent pot size: $"))
                        bet_to_call = float(input("Bet to call ($0 if none): $"))
                        stack_size = float(input("Your remaining stack size: $"))
                        break
                    except ValueError:
                        print("Please enter a valid number.")

                print("\nRunning simulation...")
                equity, tie_rate = calculate_equity(player_hand, board, num_players, known_opponents=known_opponents, dead_cards=dead_cards)
                display_results(equity, tie_rate, pot_size, bet_to_call, stack_size, player_hand, board)

        again = input("\nPlay another hand? (y/n): ").lower().strip()
        if again != 'y':
            print("\nThanks for playing!")
            break

if __name__ == "__main__":
    main()
