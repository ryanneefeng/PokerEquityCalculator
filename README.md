# Poker Hand Equity Calculator

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-Active-success.svg)]()

A Texas Hold'em poker equity calculator built in Python that uses Monte Carlo
simulation to estimate a player's probability of winning a hand and recommends
the optimal move based on pot odds, stack size, and equity. Built out of an
interest in probability and quantitative decision making.

> This project is an expansion of my CS50P final project, rebuilt from scratch
> with proper software architecture, object oriented design, and additional
> features beyond the scope of the original submission.

## Features

- **Monte Carlo Simulation** - 10,000 simulations pre-flop and flop, exact enumeration on turn and river in heads up play for perfect accuracy. Multi-street projections always use Monte Carlo for speed.
- **Full Hand Evaluator** - detects all hand types from High Card to Straight Flush including ace-low straights with correct tiebreaker logic
- **Hand Descriptor** - identifies your current hand or draw at each street and shows the exact 5 cards making your best hand
- **Multi-Street Projection** - shows how equity shifts if specific cards hit next street, highlighting the biggest gainers and losers
- **Decision Engine** - recommends fold, call, raise, or all-in based on pot odds, equity, and remaining stack with stack-aware raise sizing
- **Continuous Game Mode** - follows a full hand from pre-flop through the river with live equity updates, fold tracking, dead card removal, and action logging
- **Input Safety** - duplicate card prevention, pot and stack sanity checks between streets, and full input validation throughout
- **Session Logging** - automatically logs every continuous mode hand to a JSON file including hole cards, board, equity, recommendation, action taken, and outcome
- **Position Awareness** - tracks your seat position and displays acting order at each street, distinguishing between folds that occurred before and after your action so equity is calculated with accurate information

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

Mode:
1 = Single calculation
2 = Full game mode (pre-flop to river)
3 = View session stats

Select mode (1, 2, or 3): 1

How many players at the table (including you)? 4

Enter your 2 hole cards (e.g. A Hearts, 10 Spades):
Card 1: Q spades
Card 2: 10 clubs

How many cards are on the board?
0 = Pre-flop, 3 = Flop, 4 = Turn, 5 = River
Number of board cards: 3
Board card 1: 10 diamonds
Board card 2: 5 clubs
Board card 3: 4 clubs

Have any players revealed their cards (folded and shown)? (y/n): n

Current pot size: $120
Bet to call ($0 if none): $30
Your remaining stack size: $500

Running simulation...

===========================================
  Hand:       Pair with Backdoor Flush Draw
  Best 5:     Q of Spades, 10 of Clubs, 10 of Diamonds, 5 of Clubs, 4 of Clubs
  Equity:     44.1%
  Tie Rate:   1.6%
  Action:     Call
  Reason:     Equity 44.1% beats pot odds 20.0%. Call $30.0
===========================================

Play another hand? (y/n): n

Thanks for playing!
```
### Continuous Game Mode
```
===========================================
      Poker Hand Equity Calculator
===========================================

Mode:
1 = Single calculation
2 = Full game mode (pre-flop to river)
3 = View session stats

Select mode (1, 2, or 3): 2

How many players at the table (including you)? 5

Enter your 2 hole cards (e.g. A Hearts, 10 Spades):
Card 1: 8 spades
Card 2: 8 clubs

What is your seat position at the table?
1 = Small Blind, 2 = Big Blind, 3 to 5 = UTG to Dealer
Your position (1-5): 3

You are playing from: UTG

-- PRE-FLOP --
  Position: UTG
  Acting order: UTG (YOU) → Cutoff → Dealer → SB → BB
  You act 1 of 5
  You are not a blind -- you can fold, call, or raise freely.

Current pot size: $60
Bet to call ($0 if none): $40
Your remaining stack size ($0 if all-in): $500 

===========================================
  Hand:       Pocket 8s
  Equity:     23.9%
  Tie Rate:   1.0%
  Action:     Fold
  Reason:     Equity 23.9% well below pot odds 40.0%
===========================================

What did you do? (fold, call, raise, check): call
Risky call. I hope luck is on your side!

Did anyone fold this round? (y/n): n
Press Enter to continue to the Flop...

Enter the 3 Flop cards:
Flop card 1: A hearts
Flop card 2: 10 diamonds
Flop card 3: 8 diamonds

-- FLOP --
  Acting order: SB → BB → UTG (YOU) → Cutoff → Dealer
  You act 3 of 5

Current pot size: $300
Bet to call ($0 if none): $60
Your remaining stack size ($0 if all-in): $460

Did anyone fold or reveal cards before your turn this street? (y/n): n

===========================================
  Hand:       Three of a Kind
  Best 5:     8 of Spades, 8 of Clubs, A of Hearts, 10 of Diamonds, 8 of Diamonds
  Equity:     73.6%
  Tie Rate:   0.1%
  Key cards next street:
    8 of Hearts -> 100.0% (+25.3%)
    9 of Diamonds -> 51.0% (-23.7%)
    J of Diamonds -> 51.7% (-23.0%)
    7 of Diamonds -> 53.0% (-21.7%)
    Q of Diamonds -> 54.0% (-20.7%)
  Action:     Raise
  Reason:     Equity 73.6% is strong regardless of pot odds. Raise to $138.0 total
===========================================

What did you do? (fold, call, raise, check): raise

Did anyone fold this round? (y/n): y
How many players folded? 1
Did any of them show their hand? (y/n): n
Press Enter to continue to the Turn...

Turn card: A spades

-- TURN --
  Acting order: SB → BB → UTG (YOU) → Dealer
  You act 3 of 4

Current pot size: $650
Bet to call ($0 if none): $75 
Your remaining stack size ($0 if all-in): $322

Did anyone fold or reveal cards before your turn this street? (y/n): y
How many players folded? 1
Did any of them show their hand? (y/n): y

Enter the 2 cards for the player who showed hand 1:
Card 1: J spades
Card 2: 4 clubs

===========================================
  Hand:       Full House
  Best 5:     8 of Spades, 8 of Clubs, A of Hearts, 8 of Diamonds, A of Spades
  Equity:     91.9%
  Tie Rate:   0.3%
  Key cards next street:
    A of Clubs -> 57.3% (-32.3%)
    A of Diamonds -> 61.0% (-28.7%)
    10 of Spades -> 63.7% (-26.0%)
    10 of Clubs -> 68.3% (-21.3%)
    10 of Hearts -> 68.7% (-21.0%)
  Action:     Raise (All-In consideration)
  Reason:     Equity 91.9% is dominant. Raise to $257.6 total
===========================================

What did you do? (fold, call, raise, check): raise

Did anyone fold this round? (y/n): n
Press Enter to continue to the River...

River card: J hearts

-- RIVER --
  Acting order: SB → BB → Dealer (YOU)
  You act 3 of 3

Current pot size: $1100
Bet to call ($0 if none): $75
Your remaining stack size ($0 if all-in): $175

Did anyone fold or reveal cards before your turn this street? (y/n): n

===========================================
  Hand:       Full House
  Best 5:     8 of Spades, 8 of Clubs, A of Hearts, 8 of Diamonds, A of Spades
  Equity:     96.5%
  Tie Rate:   0.0%
  Action:     Raise (All-In consideration)
  Reason:     Equity 96.5% is dominant. Raise to $150.0 total
===========================================

What did you do? (fold, call, raise, check): raise

Did you win this hand? (y/n): y

Hand complete!
Hand logged.

Play another hand? (y/n): n

Thanks for playing!
```
### Session Stats Mode
```
===========================================
      Poker Hand Equity Calculator
===========================================

Mode:
1 = Single calculation
2 = Full game mode (pre-flop to river)
3 = View session stats

Select mode (1, 2, or 3): 3

===========================================
           Session Statistics
===========================================
  Total hands played:       6
  Wins:                     3
  Win rate:                 50.0%
  Average final equity:     49.5%
  Followed recommendation:  66.7%
  Win rate when followed:   50.0%
  Win rate when deviated:   50.0%
===========================================

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
│   ├── decision.py    # Pot odds and recommendation engine
│   └── session.py     # Session logging and statistics
│
├── tests/
│   ├── test_evaluator.py
│   ├── test_equity.py
│   └── test_session.py
│   └── test_position.py
│
├── main.py            # Entry point and user input handling
├── README.md
├── LICENSE
├── .gitignore
└── requirements.txt
```

## Files

### src/deck.py
Defines the `Card` and `Deck` classes. Each card is represented as an object
with a rank and suit attribute. The Deck class handles building a 52 card deck,
removing known cards, shuffling, and dealing. `__eq__` and `__hash__` are
implemented so cards can be compared correctly and stored in sets for O(1)
lookup.

### src/evaluator.py
Contains `evaluate_hand`, `best_hand`, `best_hand_cards`, and `describe_hand`.
`evaluate_hand` takes exactly 5 cards and returns a tuple of (hand rank,
tiebreaker) where hand rank is a number from 1 (High Card) to 9 (Straight
Flush) and tiebreaker is a list of card indices sorted highest to lowest.
Returning a tuple means two hands of the same type are compared correctly
through Python's built-in tuple comparison. `best_hand` tries every possible
5 card combination from 7 available cards to find the strongest. `best_hand_cards`
returns the actual 5 cards making that hand. `describe_hand` identifies the
current hand type or draw in plain English.

### src/equity.py
Runs the equity calculation. Pre-flop and flop use Monte Carlo simulation with
10,000 runs. Turn and river in heads up play switch to exact enumeration for
a perfect result. Dead cards from folded players and known opponent hands are
both removed from the deck before any simulation runs so they cannot appear
in simulated boards or opponent hands.

### src/decision.py
Takes equity, tie rate, pot size, bet to call, and stack size and returns an
action and explanation. Pot odds are calculated as bet / (pot + bet). Raise
amounts are calculated as the minimum of a pot-based amount and a stack-based
amount. Absolute equity floors are enforced so the program never recommends
raising on a weak hand regardless of pot odds. All-in is only suggested when
equity clears 65%.

### src/session.py
Handles session logging and statistics using SQLite via Python's built-in `sqlite3` module. `log_hand` inserts each completed continuous mode hand into a local `session.db` database. `get_stats` queries the database to return win rate, recommendation follow rate, average equity, and a breakdown of win rate when following vs deviating from recommendations.

### main.py
Entry point for the program. Handles all user input with validation loops,
duplicate card prevention, and pot and stack sanity checks between streets.
Manages both single calculation and continuous game mode, including fold
tracking, dead card memory, and all-in detection across streets.

## Design Decisions

**Monte Carlo over exact enumeration pre-flop and flop** - pre-flop there are over 1.7 million possible board runouts. Monte Carlo trades perfect accuracy for speed and scales easily to any number of players. 10,000 simulations gives results accurate to within 1-2% in practice. Exact enumeration is used on the turn and river in heads up play where the number of combinations is small enough to compute perfectly.

**Tuple return from evaluate_hand** - returning `(hand_rank, tiebreaker)` instead of just a number means Python's built-in tuple comparison handles all tiebreaking automatically. An Ace high flush beats a King high flush without any additional comparison logic needed.

**Raise sizing based on both pot and stack** - a raise recommendation based only on pot size can suggest amounts larger than a safe fraction of the player's remaining chips. Sizing off the minimum of pot-based and stack-based amounts keeps recommendations realistic. The minimum raise is also enforced so the suggested raise never falls below the size of the current bet to call.

**Absolute equity floors** - pot odds alone can justify aggressive action with weak hands if the pot is large relative to the bet. Absolute equity floors ensure the program never recommends raising below a minimum win probability regardless of pot odds.

**Dead cards vs known opponents** - cards shown by folded players are tracked separately from active known opponent hands. Folded cards are removed from the deck as dead cards but the folder is not simulated as an active opponent. This correctly models two separate effects: fewer cards available in the deck, and fewer players competing for the pot.

## Future Ideas

- Position-based recommendation adjustments - factor in acting position when suggesting raise sizes and aggression levels, since acting last provides an informational advantage worth exploiting
- SQL query interface - expose session data for custom queries and deeper hand history analysis

## Requirements

No external libraries required. Uses only Python built-in modules: random
and itertools.

## Author

**Ryan Feng**
Cornell University | B.A. Mathematics, Minor: Computer Science, Actuarial Studies | Class of 2029

- LinkedIn: [linkedin.com/in/ryanneefeng](https://linkedin.com/in/ryanneefeng)
- Email: ryanneefeng@gmail.com
- GitHub: [@ryanneefeng](https://github.com/ryanneefeng)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
