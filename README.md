# Poker Hand Equity Calculator

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-Active-success.svg)]()

A Texas Hold'em poker equity calculator built in Python that uses Monte Carlo
simulation to estimate a player's probability of winning a hand and recommends
the optimal move based on pot odds, stack size, and equity.

> This project is an expansion of my CS50P final project, rebuilt from scratch
> with proper software architecture, object oriented design, and additional
> features beyond the scope of the original submission.

## Features

- **Monte Carlo Simulation** - 10,000 simulations per calculation for accurate equity estimation
- **Full Hand Evaluator** - detects all hand types from High Card to Straight Flush including ace-low straights, with correct tiebreaker logic
- **Pot Odds Engine** - compares equity against pot odds to recommend fold, call, raise small, raise, or all-in
- **Stack-Aware Raise Sizing** - raise recommendations account for both pot size and remaining stack, never suggesting more than a safe fraction of remaining chips
- **Equity Override** - strong hands (65%+ equity) receive aggressive recommendations regardless of pot odds
- **All-In Detection** - automatically detects when bet equals stack and simplifies to call all-in or fold
- **Tie Rate Tracking** - tracks split pot scenarios and factors them into effective equity
- **Continuous Game Mode** - follow a full hand from pre-flop through the river, with equity and recommendations updating live at each street
- **Fold Tracking** - after each street, log who folded and update player count and dead cards accordingly
- **Dead Card Removal** - cards revealed by folded players are removed from the deck, directly affecting equity calculations
- **Win by Fold Detection** - if all opponents fold the program ends the hand immediately
- **Action Tracking** - prompts the user for their decision after each recommendation and notes when they deviate
- **Input Sanity Checks** - warns the user if pot decreases or stack increases between streets
- **Duplicate Card Prevention** - rejects any card already entered in the current hand
- **Input Validation** - handles all invalid input gracefully without crashing

## How It Works

The program offers two modes. In single calculation mode the user inputs their hole cards, the current board state, any revealed cards from folded players, pot size, bet to call, and remaining stack. The program runs 10,000 Monte Carlo simulations and outputs an equity percentage, tie rate, and recommended action with a suggested raise amount.

In continuous game mode the program follows a full hand from pre-flop through the river. At each street the user enters the new board cards, pot info, and what action they took. After each street the program asks if anyone folded and whether they showed their cards. Folded players are removed from the simulation and any shown cards are treated as dead cards that cannot appear in future simulated boards or opponent hands. If all opponents fold at any point the hand ends immediately. Equity and recommendations update in real time at each street so the user can see how their position changes as the hand develops.

## Installation

```bash
git clone https://github.com/ryanneefeng/PokerEquityCalculator.git
cd PokerEquityCalculator
python main.py
```

No external libraries required.

## Example Session

### Single Calculation Mode
```
===========================================
      Poker Hand Equity Calculator
===========================================

How many players at the table (including you)? 4

Enter your 2 hole cards (e.g. A Hearts, 10 Spades):
Card 1: 3 spades
Card 2: 10 clubs

Mode:
1 = Single calculation, 2 = Full game mode (pre-flop to river)
Select mode (1 or 2): 1

How many cards are on the board?
0 = Pre-flop, 3 = Flop, 4 = Turn, 5 = River
Number of board cards: 3
Board card 1: J spades
Board card 2: K clubs
Board card 3: 3 spades
3 of Spades is already in play. Please enter a different card.
Board card 3: 3 clubs

Have any players revealed their cards (folded and shown)? (y/n): y
How many players revealed their cards? 1

Enter the 2 cards for player 1 who revealed:
Card 1: 2 clubs
Card 2: 9 spades

Current pot size: $100
Bet to call ($0 if none): $20
Your remaining stack size: $200

Running simulation...

===========================================
  Equity:     27.6%
  Tie Rate:   3.9%
  Action:     Call or Fold
  Reason:     Equity 27.6% close to pot odds 16.7%. Call $20.0 or fold
===========================================

Play another hand? (y/n): n

Thanks for playing!
```
### Continuous Game Mode
```
===========================================
      Poker Hand Equity Calculator
===========================================

How many players at the table (including you)? 4

Enter your 2 hole cards (e.g. A Hearts, 10 Spades):
Card 1: A spades
Card 2: 2 clubs

Mode:
1 = Single calculation, 2 = Full game mode (pre-flop to river)
Select mode (1 or 2): 2

-- PRE-FLOP --

Current pot size: $60 
Bet to call ($0 if none): $20
Your remaining stack size: $100

===========================================
  Equity:     31.8%
  Tie Rate:   4.3%
  Action:     Call
  Reason:     Equity 31.8% beats pot odds 25.0%. Call $20.0
===========================================

What did you do? (fold, call, raise, check): call
Did anyone fold this round? (y/n): n
Press Enter to continue to the Flop...

Enter the 3 Flop cards:
Flop card 1: 4 clubs
Flop card 2: 10 spades
Flop card 3: J spades

-- FLOP --

Current pot size: $80
Bet to call ($0 if none): $40
Your remaining stack size: $80

===========================================
  Equity:     21.2%
  Tie Rate:   3.4%
  Action:     Fold
  Reason:     Equity 21.2% well below pot odds 33.3%
===========================================

What did you do? (fold, call, raise, check): call
Risky call. I hope luck is on your side!
Did anyone fold this round? (y/n): y
How many players folded? 1
Did any of them show their hand? (y/n): y

Enter the 2 cards for the player who showed hand 1:
Card 1: 3 spades
Card 2: K clubs 
Press Enter to continue to the Turn...
Turn card: A clubs

-- TURN --

Current pot size: $160
Bet to call ($0 if none): $20
Your remaining stack size: $40

===========================================
  Equity:     62.6%
  Tie Rate:   6.3%
  Action:     Raise
  Reason:     Equity 62.6% far exceeds pot odds 11.1%. Raise to $40.0 total
===========================================

What did you do? (fold, call, raise, check): raise
Did anyone fold this round? (y/n): n
Press Enter to continue to the River...
River card: 10 clubs

-- RIVER --

Current pot size: $280
Bet to call ($0 if none): $0
Your remaining stack size: $0
Equity: 58.5% (you are all-in, no action needed)
Hand complete!

Play another hand? (y/n): n

Thanks for playing!
```
## Project Structure
```
PokerEquityCalculator/
│
├── src/
│   ├── deck.py        # Card and Deck classes
│   ├── evaluator.py   # Hand evaluation and best hand logic
│   ├── equity.py      # Monte Carlo equity simulation
│   └── decision.py    # Pot odds and recommendation engine
│
├── tests/
│   ├── test_evaluator.py
│   └── test_equity.py
│
├── main.py            # Entry point and user input handling
├── README.md
├── LICENSE
└── requirements.txt
```
## Planned Enhancements

**Phase 2**
- Hand strength descriptor - identify and display the player's current hand or draw such as flush draw, gutshot straight draw, or top pair
- Exact enumeration on turn and river - switch from Monte Carlo to exact enumeration when few cards remain for a perfect result
- Multi-street projection - show how equity changes if a specific card hits on the next street

**Phase 3**
- Position awareness - track seat order and adjust available decisions and fold information based on when the player acts in each betting round
- Session tracker - log hands, recommendations, and outcomes across a full game
- SQL storage - persist session history for post-game decision analysis

## Requirements

No external libraries required. Uses only Python built-in modules: random
and itertools.

## Author

**Ryan Feng**
Cornell University | B.A. Mathematics, Minor: Computer Science, Statistics | Class of 2029

- LinkedIn: [linkedin.com/in/ryanneefeng](https://linkedin.com/in/ryanneefeng)
- Email: ryanneefeng@gmail.com
- GitHub: [@ryanneefeng](https://github.com/ryanneefeng)

## License
