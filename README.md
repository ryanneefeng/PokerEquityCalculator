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
How many players at the table (including you)? 4
Enter your 2 hole cards (e.g. A Hearts, 10 Spades):
Card 1: A Hearts
Card 2: A Diamonds
How many cards are on the board?
0 = Pre-flop, 3 = Flop, 4 = Turn, 5 = River
Number of board cards: 3
Board card 1: K Hearts
Board card 2: A Clubs
Board card 3: 2 Spades
Current pot size: $1000
Bet to call ($0 if none): $200
Your remaining stack size: $800
Running simulation...
===========================================
Equity:     91.2%
Tie Rate:   0.3%
Action:     Raise (All-In consideration)
Reason:     Equity 91.2% vs pot odds 16.7%. Consider all-in or raise to $600.0 total
```
### Continuous Game Mode
```
===========================================
Poker Hand Equity Calculator
How many players at the table (including you)? 4
Enter your 2 hole cards (e.g. A Hearts, 10 Spades):
Card 1: A Hearts
Card 2: K Hearts
Mode:
1 = Single calculation, 2 = Full game mode (pre-flop to river)
Select mode (1 or 2): 2
-- PRE-FLOP --
Current pot size: $750
Bet to call ($0 if none): $250
Your remaining stack size: $5000
===========================================
Equity:     41.0%
Tie Rate:   2.1%
Action:     Call
Reason:     Equity 41.0% beats pot odds 25.0%. Call $250.0
What did you do? (fold, call, raise, check): call
Press Enter to add the flop...
Flop card 1: 10 Hearts
Flop card 2: K Clubs
Flop card 3: J Hearts
-- FLOP --
Current pot size: $3250
Bet to call ($0 if none): $750
Your remaining stack size: $4000
===========================================
Equity:     72.4%
Tie Rate:   4.6%
Action:     Raise
Reason:     Equity 72.4% is strong regardless of pot odds. Raise to $1200.0 total
What did you do? (fold, call, raise, check): raise
Press Enter to add the turn...
Turn card: A Spades
-- TURN --
Current pot size: $10150
Bet to call ($0 if none): $1000
Your remaining stack size: $1000
===========================================
Equity:     59.9%
Tie Rate:   7.0%
Action:     Call (All-In)
Reason:     Equity 59.9% with tie rate 7.0%. Call all-in of $1000.0
What did you do? (fold, call, raise, check): call
Press Enter to add the river...
River card: Q Hearts
-- RIVER --
Current pot size: $12000
Bet to call ($0 if none): $0
Your remaining stack size: $0
Equity: 100.0% (you are all-in, no action needed)
Hand complete!
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
- Known opponent cards - if an opponent shows their hand, factor those cards into the equity calculation directly
- Play again - option to run another hand after completing a full game without restarting the program

**Phase 2**
- Hand strength descriptor - identify and display the player's current hand or
  draw such as flush draw, gutshot straight draw, or top pair
- Exact enumeration on turn and river - switch from Monte Carlo to exact
  enumeration when few cards remain for a perfect result
- Multi-street projection - show how equity changes if a specific card hits on
  the next street

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
