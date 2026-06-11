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
        if action == "call" and "call" in reccomendation.lower():
            return action
        if action != reccomendation.split()[0].lower():
            print(f"You chose to {action}, instead of the recommended action: {reccomendation}. I hope luck is on your side!")
        return action

def continuous_game(num_players, player_hand, known_opponents=None):
    if known_opponents is None:
        known_opponents = []

    prev_pot = None
    prev_stack = None

    print ("\n-- PRE-FLOP --")
    pot_size, bet_to_call, stack_size = get_pot_info()
    equity, tie_rate = calculate_equity(player_hand, [], num_players, known_opponents=known_opponents)
    action = display_results(equity, tie_rate, pot_size, bet_to_call, stack_size)
    
    player_action = get_player_action(action)
    if player_action == "fold":
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

    equity, tie_rate = calculate_equity(player_hand, board, num_players, known_opponents=known_opponents)
    
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

    equity, tie_rate = calculate_equity(player_hand, board, num_players, known_opponents=known_opponents)
    
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
    
    equity, tie_rate = calculate_equity(player_hand, board, num_players, known_opponents=known_opponents)

    if stack_size == 0:
        print(f"Equity: {equity * 100:.1f}% (you are all-in, no action needed)")
    else:
        action = display_results(equity, tie_rate, pot_size, bet_to_call, stack_size)
        player_action = get_player_action(action)

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

def get_known_opponents(num_players):
    known_opponents = []
    while True:
        has_known = input("\nDo any opponents have known cards? (y/n): ").lower().strip()
        if has_known == 'y':
            while True:
                try:
                    num_known = int(input("How many opponents have known cards? "))
                    if num_known < 1 or num_known >= num_players:
                        print(f"Please enter a number between 1 and {num_players - 1}.")
                        continue
                    break
                except ValueError:
                    print("Please enter a valid number.")
            for i in range(num_known):
                print(f"\nEnter the 2 hole cards for opponent {i + 1}:")
                opp_card1 = get_card_input("Card 1: ")
                opp_card2 = get_card_input("Card 2: ")
                known_opponents.append([opp_card1, opp_card2])
            return known_opponents
        elif has_known == 'n':
            return known_opponents
        else:
            print("Please enter 'y' or 'n'.")

def main():
    while True:
        print("\n===========================================")
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
        known_opponents = get_known_opponents(num_players)

        print("\nMode:")
        print("1 = Single calculation, 2 = Full game mode (pre-flop to river)")
        while True:
            mode = input("Select mode (1 or 2): ")
            if mode in ["1", "2"]:
                break
            print("Invalid mode. Please enter 1 or 2.")

        if mode == '2':
            continuous_game(num_players, player_hand, known_opponents=known_opponents)
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
            equity, tie_rate = calculate_equity(player_hand, board, num_players, known_opponents=known_opponents)
            display_results(equity, tie_rate, pot_size, bet_to_call, stack_size)

        #play again
        again = input("Play another hand? (y/n): ").lower().strip()
        if again != 'y':
            print("\nThanks for playing!")
            break

if __name__ == "__main__":
    main()