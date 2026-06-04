from src.deck import Card, RANKS, SUITS
from src.equity import calculate_equity
from src.decision import get_recommendation

def display_results(equity, tie_rate, pot_size, bet_to_call, stack_size):
    action, explanation = get_recommendation(equity, tie_rate, pot_size, bet_to_call, stack_size)
    print("\n===========================================")
    print(f"  Equity:     {equity * 100:.1f}%")
    print(f"  Tie Rate:   {tie_rate * 100:.1f}%")
    print(f"  Action:     {action}")
    print(f"  Reason:     {explanation}")
    print("===========================================\n")
    return action

def get_pot_info():
    while True:
        try:
            pot_size = float(input("\nCurrent pot size: $"))
            bet_to_call = float(input("Bet to call ($0 if none): $"))
            stack_size = float(input("Your remaining stack size: $"))
            return pot_size, bet_to_call, stack_size
        except ValueError:
            print("Please enter a valid number.")

def get_player_action(reccomendation):
    valid_actions = ["fold", "call", "raise", "check"]
    while True:
        action = input("What did you do? (fold, call, raise, check): ").lower().strip()
        if action not in valid_actions:
            print("Invalid action. Please enter fold, call, raise, or check.")
            continue
        if action == "fold":
            if reccomendation.lower().startswith("fold"):
                print("Good fold, hand over")
            else:
                print(f"You folded, hand over")
            return "fold"
        if action == "check":
            return "check"
        if action != reccomendation.split()[0].lower():
            print(f"You chose to {action}, instead of the recommended action: {reccomendation}. I hope luck is on your side!")
        return action

def continuous_game(num_players, player_hand):
    prev_POT = None
    prev_stack = None

    print ("\n-- PRE-FLOP --")
    pot_size, bet_to_call, stack_size = get_pot_info()
    equity, tie_rate = calculate_equity(player_hand, [], num_players)
    action = display_results(equity, tie_rate, pot_size, bet_to_call, stack_size)
    
    playuer_action = get_player_action(action)
    if playuer_action == "fold":
        return
    
    prev_pot = pot_size
    prev_stack = stack_size

    #flop
    input("Press Enter to continue to the Flop...")
    print("\nEnter the 3 Flop cards:")
    flop = []
    for i in range(3):
        card = get_card_input(f"Flop card {i + 1}: ")
        flop.append(card)
    board = flop

    print ("\n-- FLOP --")
    pot_size, bet_to_call, stack_size = get_pot_info()

    if pot_size < prev_pot:
        print(f"Warning: pot size decreased from ${prev_pot} to ${pot_size}. Please ensure you entered the correct pot size.")
    if stack_size > prev_stack:
        print(f"Warning: stack size increased from ${prev_stack} to ${stack_size}. Please ensure you entered the correct stack size.")
    prev_pot = pot_size
    prev_stack = stack_size

    equity, tie_rate = calculate_equity(player_hand, board, num_players)
    
    if stack_size == 0:
        print(f"\n  Equity: {equity * 100:.1f}% (you are all-in, no action needed)")
    else:
        action = display_results(equity, tie_rate, pot_size, bet_to_call, stack_size)
        player_action = get_player_action(action)
        if player_action == "fold":
            return
    
    #turn
    input("Press Enter to continue to the Turn...")
    turn = get_card_input("Turn card: ")
    board = board + [turn]

    print ("\n-- TURN --")
    pot_size, bet_to_call, stack_size = get_pot_info()

    if pot_size < prev_pot:
        print(f"Warning: pot size decreased from ${prev_pot} to ${pot_size}. Please ensure you entered the correct pot size.")
    if stack_size > prev_stack:
        print(f"Warning: stack size increased from ${prev_stack} to ${stack_size}. Please ensure you entered the correct stack size.")
    prev_pot = pot_size
    prev_stack = stack_size

    equity, tie_rate = calculate_equity(player_hand, board, num_players)
    
    if stack_size == 0:
        print(f"\n  Equity: {equity * 100:.1f}% (you are all-in, no action needed)")
    else:
        action = display_results(equity, tie_rate, pot_size, bet_to_call, stack_size)
        player_action = get_player_action(action)
        if player_action == "fold":
            return
    
    #river
    input("Press Enter to continue to the River...")
    river = get_card_input("River card: ")
    board = board + [river]

    print ("\n-- RIVER --")
    pot_size, bet_to_call, stack_size = get_pot_info()
    if pot_size < prev_pot:
        print(f"Warning: pot size decreased from ${prev_pot} to ${pot_size}. Please ensure you entered the correct pot size.")
    if stack_size > prev_stack:
        print(f"Warning: stack size increased from ${prev_stack} to ${stack_size}. Please ensure you entered the correct stack size.")
    
    equity, tie_rate = calculate_equity(player_hand, board, num_players)

    if stack_size == 0:
        print(f"Equity: {equity * 100:.1f}% (you are all-in, no action needed)")
    else:
        action = display_results(equity, tie_rate, pot_size, bet_to_call, stack_size)
        get_player_action(action)

    print ("Hand complete!")
    
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

def get_card_input(prompt):
    while True:
        try:
            return parse_card(input(prompt))
        except ValueError as e:
            print(f"Error: {e}. Please try again.")

def main():
    print("===========================================")
    print("      Poker Hand Equity Calculator")
    print("===========================================\n")

    while True:
        try:
            num_players = int(input("How many players at the table (including you)? "))
            if num_players < 2 or num_players > 10:
                print("Please enter a number between 2 and 10.")
                continue
            break
        except ValueError:
            print("Please enter a valid number.")

    print("\nEnter your 2 hole cards (e.g. A Hearts, 10 Spades):")
    card1 = get_card_input("Card 1: ")
    card2 = get_card_input("Card 2: ")
    player_hand = [card1, card2]

    print("\nMode:")
    print("1 = Single calculation, 2 = Full game mode (pre-flop to river)")
    while True:
        mode = input("Select mode (1 or 2): ")
        if mode in ["1", "2"]:
            break
        print("Invalid mode. Please enter 1 or 2.")

    if mode == '2':
        continuous_game(num_players, player_hand)
        return
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
            card = get_card_input(f"Board card {i + 1}: ")
            board.append(card)

        while True:
            try:
                pot_size = float(input("\nCurrent pot size: $"))
                bet_to_call = float(input("Bet to call ($0 if none): $"))
                stack_size = float(input("Your remaining stack size: $"))
                break
            except ValueError:
                print("Please enter a valid number.")

        print("\nRunning simulation...")
        equity, tie_rate = calculate_equity(player_hand, board, num_players)
        action, explanation = get_recommendation(equity, tie_rate, pot_size, bet_to_call, stack_size)

    print("\n===========================================")
    print(f"  Equity:     {equity * 100:.1f}%")
    print(f"  Tie Rate:   {tie_rate * 100:.1f}%")
    print(f"  Action:     {action}")
    print(f"  Reason:     {explanation}")
    print("===========================================")

if __name__ == "__main__":
    main()