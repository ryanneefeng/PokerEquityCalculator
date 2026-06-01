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
- **Full Hand Evaluator** - detects all hand types from High Card to Straight Flush with correct tiebreaker logic
- **Pot Odds Engine** - compares equity against pot odds to recommend fold, call, raise small, raise, or all-in
- **Stack-Aware Raise Sizing** - raise recommendations account for both pot size and remaining stack
- **Tie Rate Tracking** - tracks split pot scenarios and factors them into effective equity
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
Reason:     Equity 91.2% vs pot odds 16.7%. Consider all-in or raise $600.0 total
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
└── requirements.txt
```
## Design Decisions

**Monte Carlo over exact enumeration** - pre-flop there are over 1.7 million
possible board runouts. Monte Carlo trades perfect accuracy for speed and
scales easily to any number of players. 10,000 simulations gives results
accurate to within 1-2% in practice.

**Tuple return from evaluate_hand** - returning (hand_rank, tiebreaker)
instead of just a number means Python's built-in tuple comparison handles all
tiebreaking automatically with no additional logic needed.

**Raise sizing based on both pot and stack** - a raise recommendation based
only on pot size can suggest amounts larger than a safe fraction of the
player's remaining chips. Sizing off the minimum of pot-based and stack-based
amounts keeps recommendations realistic.

**Absolute equity floors** - pot odds alone can justify aggressive action with
weak hands if the pot is large relative to the bet. Absolute equity floors
ensure the program never recommends raising below a minimum win probability
regardless of pot odds.

## Planned Enhancements

**Phase 1**
- Continuous game mode - follow a single hand from pre-flop through the river,
  updating equity and recommendations in real time as each street is revealed
- Known opponent cards - if an opponent shows their hand, factor those cards
  into the equity calculation directly

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
