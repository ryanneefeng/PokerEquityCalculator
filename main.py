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
    if projections and base_equity is not None:
        display_projections(projections, base_equity)
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
            
def get_player_action(reccomendation):
    valid_actions = ["fold", "call", "raise", "check"]
    while True:
        action = input("\nWhat did you do? (fold, call, raise, check): ").lower().strip()
        if action not in valid_actions:
            print("Invalid action. Please enter fold, call, raise, or check.")
            continue
        if action == "fold":
            if reccomendation.lower().startswith("fold"):
                print("Good fold, hand over")
            else:
                print("You folded, hand over")
            return "fold"
        if action == "check":
            return "check"
        if action == "call" and "call" in reccomendation.lower():
            return action
        if action != reccomendation.split()[0].lower():
            if action == "raise" and "call" in reccomendation.lower():
                print("Bold move. I hope luck is on your side!")
            elif action == "call" and "raise" in reccomendation.lower():
                print("Playing it safe. I hope you don't regret that later!")
            elif action == "call" and "fold" in reccomendation.lower():
                print("Risky call. I hope luck is on your side!")
            else:
                print(f"You chose to {action} instead of the recommended action: {reccomendation}. I hope luck is on your side!")
        return action

def handle_folds(num_players, known_opponents, dead_cards, used_cards):
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
    elif position == num_players:
        label = "Dealer (Button)"
    elif position == num_players - 1:
        label = "Cutoff"
    else:
        label = f"UTG+{position - 3}" if position > 3 else "UTG"

    print(f"\nYou are playing from: {label}")
    return position, label

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

    prev_pot = None
    prev_stack = None

    print("\n-- PRE-FLOP --")
    print(f"  Position: {position_label}")
    display_acting_order(num_players, position, "preflop")

    if position == 1:
        print("  You are the Small Blind -- you must post the small blind before action begins.")
    elif position == 2:
        print("  You are the Big Blind -- you must post the big blind before action begins.")
    else:
        print("  You are not a blind -- you can fold, call, or raise freely.")

    pot_size, bet_to_call, stack_size = get_pot_info()
    equity, tie_rate = calculate_equity(player_hand, [], num_players, known_opponents=known_opponents, dead_cards=dead_cards)
    action = display_results(equity, tie_rate, pot_size, bet_to_call, stack_size, player_hand, [])

    player_action = get_player_action(action)
    if player_action == "fold":
        log_hand(player_hand, board, num_players, equity, action, player_action, False)
        print("\nHand logged.")
        return

    num_players, known_opponents, dead_cards = handle_folds(num_players, known_opponents, dead_cards, used_cards)
    if num_players == 1:
        print("Everyone folded. You win the pot!")
        log_hand(player_hand, board, num_players, equity, action, player_action, True)
        print("\nHand logged.")
        return

    prev_pot = pot_size
    prev_stack = stack_size

    # Flop
    input("Press Enter to continue to the Flop...")
    print("\nEnter the 3 Flop cards:")
    flop = []
    for i in range(3):
        card = get_card_input(f"Flop card {i + 1}: ", used_cards)
        flop.append(card)
    board = flop

    print("\n-- FLOP --")
    display_acting_order(num_players, position, "postflop")
    pot_size, bet_to_call, stack_size = get_pot_info(all_in=is_all_in)

    if not is_all_in:
        if pot_size < prev_pot:
            print(f"Warning: pot size decreased from ${prev_pot} to ${pot_size}. Please ensure you entered the correct pot size.")
        if stack_size > prev_stack:
            print(f"Warning: stack size increased from ${prev_stack} to ${stack_size}. Please ensure you entered the correct stack size.")
        if stack_size == 0:
            is_all_in = True

    prev_pot = pot_size
    prev_stack = stack_size

    equity, tie_rate = calculate_equity(player_hand, board, num_players, known_opponents=known_opponents, dead_cards=dead_cards)

    if is_all_in:
        hand_desc = describe_hand(player_hand, board)
        best_cards = best_hand_cards(player_hand + board)
        best_str = ", ".join(str(c) for c in best_cards)
        print("\n===========================================")
        print(f"  Hand:       {hand_desc}")
        print(f"  Best 5:     {best_str}")
        print(f"  Equity:     {equity * 100:.1f}% (you are all-in)")
        print("===========================================\n")
    else:
        projections, base_equity = project_next_street(player_hand, board, num_players, known_opponents=known_opponents, dead_cards=dead_cards)
        action = display_results(equity, tie_rate, pot_size, bet_to_call, stack_size, player_hand, board, projections, base_equity)
        player_action = get_player_action(action)
        if player_action == "fold":
            log_hand(player_hand, board, num_players, equity, action, player_action, False)
            print("\nHand logged.")
            return

    num_players, known_opponents, dead_cards = handle_folds(num_players, known_opponents, dead_cards, used_cards)
    if num_players == 1:
        print("Everyone folded. You win the pot!")
        log_hand(player_hand, board, num_players, equity, action, player_action, True)
        print("\nHand logged.")
        return
    # Turn
    input("Press Enter to continue to the Turn...")
    turn = get_card_input("\nTurn card: ", used_cards)
    board = board + [turn]

    print("\n-- TURN --")
    display_acting_order(num_players, position, "postflop")
    pot_size, bet_to_call, stack_size = get_pot_info(all_in=is_all_in)

    if not is_all_in:
        if pot_size < prev_pot:
            print(f"Warning: pot size decreased from ${prev_pot} to ${pot_size}. Please ensure you entered the correct pot size.")
        if stack_size > prev_stack:
            print(f"Warning: stack size increased from ${prev_stack} to ${stack_size}. Please ensure you entered the correct stack size.")
        if stack_size == 0:
            is_all_in = True

    prev_pot = pot_size
    prev_stack = stack_size

    equity, tie_rate = calculate_equity(player_hand, board, num_players, known_opponents=known_opponents, dead_cards=dead_cards)

    if is_all_in:
        hand_desc = describe_hand(player_hand, board)
        best_cards = best_hand_cards(player_hand + board)
        best_str = ", ".join(str(c) for c in best_cards)
        print("\n===========================================")
        print(f"  Hand:       {hand_desc}")
        print(f"  Best 5:     {best_str}")
        print(f"  Equity:     {equity * 100:.1f}% (you are all-in)")
        print("===========================================\n")
    else:
        projections, base_equity = project_next_street(player_hand, board, num_players, known_opponents=known_opponents, dead_cards=dead_cards)
        action = display_results(equity, tie_rate, pot_size, bet_to_call, stack_size, player_hand, board, projections, base_equity)
        player_action = get_player_action(action)
        if player_action == "fold":
            log_hand(player_hand, board, num_players, equity, action, player_action, False)
            print("\nHand logged.")
            return

    num_players, known_opponents, dead_cards = handle_folds(num_players, known_opponents, dead_cards, used_cards)
    if num_players == 1:
        print("Everyone folded. You win the pot!")
        log_hand(player_hand, board, num_players, equity, action, player_action, True)
        print("\nHand logged.")
        return

    # River
    input("Press Enter to continue to the River...")
    river = get_card_input("\nRiver card: ", used_cards)
    board = board + [river]

    print("\n-- RIVER --")
    display_acting_order(num_players, position, "postflop")
    pot_size, bet_to_call, stack_size = get_pot_info(all_in=is_all_in)

    if not is_all_in:
        if pot_size < prev_pot:
            print(f"Warning: pot size decreased from ${prev_pot} to ${pot_size}. Please ensure you entered the correct pot size.")
        if stack_size > prev_stack:
            print(f"Warning: stack size increased from ${prev_stack} to ${stack_size}. Please ensure you entered the correct stack size.")
        if stack_size == 0:
            is_all_in = True

    equity, tie_rate = calculate_equity(player_hand, board, num_players, known_opponents=known_opponents, dead_cards=dead_cards)

    if is_all_in:
        hand_desc = describe_hand(player_hand, board)
        best_cards = best_hand_cards(player_hand + board)
        best_str = ", ".join(str(c) for c in best_cards)
        print("\n===========================================")
        print(f"  Hand:       {hand_desc}")
        print(f"  Best 5:     {best_str}")
        print(f"  Equity:     {equity * 100:.1f}% (you are all-in)")
        print("===========================================\n")
    else:
        action = display_results(equity, tie_rate, pot_size, bet_to_call, stack_size, player_hand, board)
        player_action = get_player_action(action)

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

def get_acting_order(num_players, position, street):
    positions = list(range(1, num_players + 1))
    if street == "preflop":
        # UTG first, blinds last
        order = positions[2:] + positions[:2]
    else:
        # SB first, dealer last
        order = positions
    return order

def display_acting_order(num_players, position, street):
    order = get_acting_order(num_players, position, street)
    position_labels = {1: "SB", 2: "BB"}
    if num_players >= 3:
        position_labels[num_players] = "Dealer"
    if num_players >= 4:
        position_labels[num_players - 1] = "Cutoff"
    for i in range(3, num_players - 1):
        if i == 3:
            position_labels[i] = "UTG"
        else:
            position_labels[i] = f"UTG+{i-3}"

    order_str = " → ".join([position_labels.get(p, str(p)) + (" (YOU)" if p == position else "") for p in order])
    acting_index = order.index(position) + 1
    print(f"  Acting order: {order_str}")
    print(f"  You act {acting_index} of {num_players}")

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