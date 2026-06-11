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
- **Full Hand Evaluator** - detects all hand types from High Card to Straight Flush with correct tiebreaker logic including ace-low straights
- **Pot Odds Engine** - compares equity against pot odds to recommend fold, call, raise small, raise, or all-in
- **Stack-Aware Raise Sizing** - raise recommendations account for both pot size and remaining stack
- **Equity Override** - strong hands (65%+ equity) receive aggressive recommendations regardless of pot odds
- **All-In Detection** - automatically detects when bet equals stack and simplifies to call all-in or fold
- **Tie Rate Tracking** - tracks split pot scenarios and factors them into effective equity
- **Continuous Game Mode** - follow a full hand from pre-flop through the river, with equity and recommendations updating live at each street
- **Action Tracking** - prompts the user for their decision after each recommendation and notes when they deviate
- **Input Sanity Checks** - warns the user if pot decreases or stack increases between streets
- **Input Validation** - handles invalid card input gracefully without crashing

## How It Works

The program walks the user through a poker hand step by step. The user inputs
their hole cards, the cards currently on the board, the number of players at
the table, the current pot size, the bet they need to call, and their remaining
stack size. The program then runs 10,000 Monte Carlo simulations to estimate
win probability and outputs a recommendation along with a suggested raise amount
that accounts for both pot size and remaining stack.

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
Card 1: A hearts
Card 2: A spades
Do any opponents have known cards? (y/n): y
How many opponents have known cards? 1

Enter the 2 hole cards for opponent 1:
Card 1: 2 clubs
Card 2: 10 spades

Mode:
1 = Single calculation, 2 = Full game mode (pre-flop to river)
Select mode (1 or 2): 1

How many cards are on the board?
0 = Pre-flop, 3 = Flop, 4 = Turn, 5 = River
Number of board cards: 3
Board card 1: a clubs
Board card 2: 10 hearts
Board card 3: 10 clubs

Current pot size: $10000
Bet to call ($0 if none): $4200
Your remaining stack size: $12000

Running simulation...

===========================================
  Equity:     95.7%
  Tie Rate:   0.0%
  Action:     Raise (All-In consideration)
  Reason:     Equity 95.7% is dominant. Raise to $8400.0 total
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
Card 1: A hearts
Card 2: A clubs

Do any opponents have known cards? (y/n): n

Mode:
1 = Single calculation, 2 = Full game mode (pre-flop to river)
Select mode (1 or 2): 2

-- PRE-FLOP --

Current pot size: $10
Bet to call ($0 if none): $10
Your remaining stack size: $100

===========================================
  Equity:     63.1%
  Tie Rate:   0.8%
  Action:     Raise Small or Call
  Reason:     Equity 63.1% beats pot odds 50.0%. Raise to $20.0 total or just call $10.0
===========================================

What did you do? (fold, call, raise, check): raise
Press Enter to continue to the Flop...

Enter the 3 Flop cards:
Flop card 1: 10 spades
Flop card 2: J spades
Flop card 3: A spades

-- FLOP --

Current pot size: $40 
Bet to call ($0 if none): $30
Your remaining stack size: $90

===========================================
  Equity:     59.7%
  Tie Rate:   2.6%
  Action:     Raise Small or Call
  Reason:     Equity 59.7% beats pot odds 42.9%. Raise to $60.0 total or just call $30.0
===========================================

What did you do? (fold, call, raise, check): call
Press Enter to continue to the Turn...
Turn card: 5 spades

-- TURN --

Current pot size: $130
Bet to call ($0 if none): $30
Your remaining stack size: $60

===========================================
  Equity:     33.1%
  Tie Rate:   8.3%
  Action:     Call
  Reason:     Equity 33.1% beats pot odds 18.8%. Call $30.0
===========================================

What did you do? (fold, call, raise, check): call
Press Enter to continue to the River...
River card: A diamonds

-- RIVER --

Current pot size: $220
Bet to call ($0 if none): $30
Your remaining stack size: $30

===========================================
  Equity:     99.8%
  Tie Rate:   0.0%
  Action:     Call (All-In)
  Reason:     Equity 99.8% with tie rate 0.0%. Call all-in of $30.0
===========================================

What did you do? (fold, call, raise, check): call
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

**Phase 1**
- Fold tracking - after each street ask if any opponents folded, update the player count, and if they showed their hand add those cards to known opponents. If all opponents fold, end the hand and award the pot
- Known opponent card memory - in continuous game mode, track which opponents have already shown cards across streets so the user is never asked for the same information twice

**Phase 2**
- Hand strength descriptor - identify and display the player's current hand or draw such as flush draw, gutshot straight draw, or top pair
- Exact enumeration on turn and river - switch from Monte Carlo to exact enumeration when few cards remain for a perfect result
- Multi-street projection - show how equity changes if a specific card hits on the next street

**Phase 3**
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
