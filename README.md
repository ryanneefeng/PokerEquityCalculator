# Poker Hand Equity Calculator

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)

A command-line Texas Hold'em equity calculator for 2-10 players, built in Python.
It estimates your expected share of the pot, including ties, and suggests actions
using equity, pot odds, and the recorded betting state.

This project expands on my CS50P final project, rebuilt out of an interest in
probability and quantitative decision making.

## Getting Started

Requires Python 3.10 or newer. No external packages are needed; the application
and test runner use the standard library.

The current development branch is `fix/hand-evaluation`:

```bash
git clone --branch fix/hand-evaluation https://github.com/ryanneefeng/PokerEquityCalculator.git
cd PokerEquityCalculator
python main.py
```

## Modes

| Mode | Behavior |
| --- | --- |
| **1 - Single calculation** | Analyze one pre-flop, flop, turn, or river state, including contributions, stacks, folds, exposed cards, and eligible pots. Does not save a session hand. |
| **2 - Full game** | Follow a hand through successive streets and repeated betting decisions, then save its history and outcome. |
| **3 - Session stats** | View recorded hand results, recommendation follow rates, splits, and net profit where costs and payouts are known. |

## Features

- **Hand evaluation:** all nine hand categories, category-specific tiebreakers,
  ace-low straights, and the best five cards from the available cards.
- **Hand descriptions:** made hands, flush draws, flop-only backdoor flush draws,
  open-ended straight draws, gutshots, and double gutshots.
- **Betting state:** fixed seats, position and acting order, remaining stacks,
  street and total contributions, folds, all-ins, and returning action after bets
  or raises. All-in players stay eligible without receiving another betting turn.
- **Legal actions and sizing:** reject checks facing a bet, calls with nothing
  owed, unavailable raises, and raises below the minimum unless they are all-in.
  Reopening rights use the recorded full raise increment.
- **Main and side pots:** retain folded money, separate eligibility by matched
  contributions, return uncalled wagers, and weight equity by pots you can win.
- **Exposed cards:** track one or two cards by opponent seat, including live,
  all-in, and folded opponents. Partial live hands receive random legal completions.
- **Next-card projections:** show the five largest estimated equity changes on
  the flop and turn in both modes, including all-in runouts.
- **Session history:** save every player decision, including multiple decisions
  on one street, plus final seat snapshots and optional payout details.

## Entering a Hand

Enter cards as a rank and suit, such as `A Hearts` or `10 Spades`. Input is
case-insensitive. Ranks are `2` through `10`, `J`, `Q`, `K`, and `A`; suits are
`Hearts`, `Diamonds`, `Clubs`, and `Spades`. Duplicate cards are rejected.

Your hand requires two cards. The board contains 0, 3, 4, or 5 cards. In full game
mode, add the flop, turn, and river when prompted.

### Bets, stacks, and folds

- The pot includes all committed bets, including chips still in front of players.
  Each seat's total contributions plus separately entered antes/dead money must
  match the entered pot.
- Give each seat's current-street contribution, earlier contributions, and
  remaining stack on first entry. Later updates use new street totals and debit
  the extra chips automatically.
- Enter the big blind and last **full** bet/raise increment. Short all-ins do not
  lower that increment. A short raise can require another call or fold without
  restoring the right to raise.
- Enter a raise as the **total commitment on that street**, including chips
  already committed. Use `raise` for an opening bet as well; a shove is a raise
  to your full available total, or a call when your stack cannot cover the wager.
- Seat numbers stay fixed throughout full game mode. Report the actual folded
  seats. In single calculation mode, you are seat 1; the folded-and-shown
  shortcut assigns folders to seats 2 onward before the remaining seat updates.
- After acting, update opponents through your next decision or the end of the
  round. A funded player who still owes chips must call or fold before advancing.

Showing cards does not fold a player. To record one or two newly exposed cards,
type `cards` at a pot-size prompt, either fold prompt, the single-mode
folded-and-shown prompt, or a between-street continuation prompt:

```text
Current pot size (or 'cards' to record exposed cards): $cards
Seat showing cards (2): 2
How many NEW exposed cards (1-2)? 1
Exposed card 1: A Hearts
```

You can add the second card later. Known live cards stay attached to that seat;
a folded seat's exposed cards remain unavailable to the board and other hands.

## Equity and Recommendations

| Calculation | Default method |
| --- | --- |
| Pre-flop or flop | 10,000 Monte Carlo trials |
| Turn or river with two players eligible for a pot | Exact enumeration of legal remaining cards |
| Turn or river with three or more eligible players | 10,000 Monte Carlo trials |
| Next-card projections | 300 Monte Carlo trials per candidate and a separate 300-trial baseline |

Equity includes the appropriate share of tied pots. For example, a three-way
board split gives each player one-third equity and a 100% tie rate. When several
pots are eligible, displayed overall equity and tie rate are weighted by their
amounts. A player contributing $50 against two $200 contributions can win the
$150 main pot; the opponents' $300 side pot is excluded from that player's equity.

Call advice uses eligible pots after the current call and the matched cost of
calling, excluding money expected to return as uncalled. Its break-even threshold
is `call cost / eligible pot after calling`. Raise suggestions use heuristic
equity thresholds, pot/stack sizing, the minimum legal raise, raising rights,
and funded opponents' capacity.

Projections assume the current call is paid and hold contributions fixed. Their
changes are **percentage points from the displayed sampled baseline**, which may
differ from the main equity estimate. Sampling noise can affect both values and
ranking; they do not predict future bets, calls, or folds.

### Python API example

One opponent has exposed an ace on the river. The unknown second card is
uniformly distributed over the remaining legal cards:

```python
from src.deck import Card
from src.equity import calculate_equity

hero = [Card("K", "Clubs"), Card("K", "Diamonds")]
board = [Card(rank, suit) for rank, suit in [
    ("2", "Hearts"), ("3", "Diamonds"), ("7", "Clubs"),
    ("8", "Spades"), ("9", "Hearts"),
]]
equity, tie_rate = calculate_equity(
    hero, board, 2, known_opponents=[[Card("A", "Hearts")]]
)
print(f"Equity: {equity:.1%}; tie rate: {tie_rate:.1%}")
# Equity: 93.2%; tie rate: 0.0%
```

The API validates cards, player counts, simulation counts, hand/board lengths,
and remaining-deck capacity. Known opponents accept one or two exposed cards.
Use `calculate_equity` for normal dispatch; direct exact-turn/river helpers
support at most one incomplete opponent hand.

## Session History and Results

Full game mode saves to `session.db` in the working directory. Existing databases
migrate automatically while preserving old hands.

- **`hands`:** cards, final equity, last real action/recommendation, outcome,
  optional costs and payouts, net profit, pot details, and final seat snapshots.
- **`decisions`:** each decision in order, with street, board, equity,
  recommendation, action, chips added, raise total, stack, and seat snapshot.

At showdown, enter `win`, `loss`, or `split` (`y`/`n` also work). For a win or
split, optionally enter your actual payout from each eligible pot. Exclude
returned wagers. Leave unknown amounts blank. If antes/dead money were recorded
separately, enter your share of that cost or leave it unknown.

Net profit is payout minus your matched contributions and known ante cost. It is
reported only when both cost and payout are known. Winning a small pot can still
produce a net loss. Uncalled refunds count as neither winnings nor chips at risk.

Statistics count a hand winning **any pot share**, including splits, as a win.
Hand follow rate means all recorded decisions matched advice; decision follow
rate counts individual decisions. Empty actions receive no following credit.
Profit totals show how many hands have complete cost/payout records. Older
summary-only hands retain their limited history; missing decisions and payouts
cannot be reconstructed. These statistics are descriptive, not evidence that
following the recommendations improves results.

## Tests

```bash
python run_tests.py
```

The standard-library runner discovers the plain test functions in `tests/`,
uses a fixed random seed, and redirects session tests to temporary databases so
your saved history is untouched. Coverage includes hand comparisons, split
shares, partial hands, betting legality, reopening rights, side pots, database
migration, decision history, payouts, and CLI flows.

## Scope and Limitations

The calculator models standard 52-card Texas Hold'em with no-limit betting inputs
and chip value as the baseline. Unknown cards are uniformly random; opponent
ranges and action-based range updates are not implemented. Position affects
acting order, but does not adjust the strategy heuristic.

Recommendations do not model future betting costs, implied or reverse implied
odds, fold probabilities, rake, tournament ICM, or payout structure. They are
heuristics rather than optimal-play or GTO solutions. Exact results are exact
under the entered card assumptions; Monte Carlo results have sampling error.

Potential next steps include opponent ranges, a richer betting-response model,
position-aware strategy, and higher-precision projections.

## Project Structure

```text
PokerEquityCalculator/
|-- main.py          # CLI, input validation, and hand flow
|-- run_tests.py     # Standard-library test runner
|-- src/
|   |-- deck.py      # Cards and deck operations
|   |-- evaluator.py # Hand comparisons, best five, and descriptions
|   |-- equity.py    # Exact/Monte Carlo equity and projections
|   |-- pots.py      # Contributions, refunds, eligibility, and pot equity
|   |-- decision.py  # Pot odds and action/sizing heuristics
|   `-- session.py   # SQLite migration, history, and statistics
|-- tests/           # Regression and CLI-flow tests
|-- requirements.txt # Empty: no external dependencies
|-- README.md
`-- LICENSE
```

## AI Usage

AI assistance was used for code cleanup, major debugging, regression tests, and
documentation updates.

## Author

**Ryan Feng**
Cornell University | B.A. Mathematics | Class of 2029

- LinkedIn: [linkedin.com/in/ryanneefeng](https://linkedin.com/in/ryanneefeng)
- Email: ryanneefeng@gmail.com
- GitHub: [@ryanneefeng](https://github.com/ryanneefeng)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
