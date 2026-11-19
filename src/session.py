import json
import re
import sqlite3
from contextlib import closing
from datetime import datetime
from math import isfinite

DB_FILE = "session.db"


def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_db():
    with closing(get_connection()) as conn, conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS hands (
                id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, hole_cards TEXT,
                board TEXT, num_players INTEGER, final_equity REAL,
                recommendation TEXT, player_action TEXT,
                followed_recommendation INTEGER, won INTEGER
            )
        """)
        columns = {row[1] for row in conn.execute("PRAGMA table_info(hands)")}
        for name, kind in {"outcome": "TEXT", "contribution": "REAL", "payout": "REAL",
                           "net_profit": "REAL", "pots_json": "TEXT", "history_complete": "INTEGER",
                           "players_json": "TEXT"}.items():
            if name not in columns:
                conn.execute(f"ALTER TABLE hands ADD COLUMN {name} {kind}")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hand_id INTEGER NOT NULL REFERENCES hands(id) ON DELETE CASCADE,
                sequence INTEGER NOT NULL, street TEXT, board TEXT, equity REAL,
                recommendation TEXT, player_action TEXT, followed_recommendation INTEGER,
                pot_size REAL, bet_to_call REAL, stack_before REAL,
                contribution_before REAL, chips_added REAL, raise_to REAL,
                stack_after REAL, players_json TEXT,
                UNIQUE(hand_id, sequence)
            )
        """)
        # Old all-in runouts wrote empty actions as successfully followed advice.
        conn.execute("""UPDATE hands SET followed_recommendation = NULL
                        WHERE TRIM(COALESCE(player_action, '')) = ''
                           OR TRIM(COALESCE(recommendation, '')) = ''""")


def recommendation_followed(recommendation, player_action):
    action = (player_action or "").strip().lower()
    choices = set(re.findall(r"\b(fold|call|raise|check)\b", (recommendation or "").lower()))
    if action not in {"fold", "call", "raise", "check"} or not choices:
        return None
    return int(action in choices)


def log_hand(hole_cards, board, num_players, final_equity, recommendation, player_action, won,
             *, history=None, outcome=None, contribution=None, payout=None, pots=None, players=None):
    for value in (contribution, payout):
        if value is not None and (not isfinite(value) or value < 0):
            raise ValueError("Contributions and payouts must be finite and nonnegative.")
    if outcome not in {None, "won", "lost", "split", "folded", "won_by_fold"}:
        raise ValueError("Invalid hand outcome.")
    if outcome is not None:
        won = outcome in {"won", "split", "won_by_fold"}
    if history:
        recommendation = history[-1]["recommendation"]
        player_action = history[-1]["player_action"]
    followed = recommendation_followed(recommendation, player_action)
    if history is not None:
        flags = [recommendation_followed(d["recommendation"], d["player_action"]) for d in history]
        flags = [flag for flag in flags if flag is not None]
        followed = int(all(flags)) if flags else None
    contribution = round(contribution, 2) if contribution is not None else None
    payout = round(payout, 2) if payout is not None else None
    if outcome in {"lost", "folded"} and payout not in (None, 0):
        raise ValueError("A lost or folded hand cannot have a positive payout.")
    if outcome in {"won", "split", "won_by_fold"} and payout == 0:
        raise ValueError("A win or split must have a positive payout or an unknown payout.")
    if pots is not None:
        for pot in pots:
            amount, share = pot["amount"], pot.get("payout")
            if not isfinite(amount) or amount < 0 or (share is not None and (
                not isfinite(share) or share < 0 or share > amount
            )):
                raise ValueError("A pot payout must be within the finite pot amount.")
        if payout is not None and all(pot.get("payout") is not None for pot in pots):
            if round(sum(pot["payout"] for pot in pots), 2) != payout:
                raise ValueError("Total payout must equal the recorded per-pot payouts.")
    net_profit = round(payout - contribution, 2) if payout is not None and contribution is not None else None
    initialize_db()
    with closing(get_connection()) as conn, conn:
        cursor = conn.execute("""
            INSERT INTO hands (date, hole_cards, board, num_players, final_equity,
                               recommendation, player_action, followed_recommendation, won,
                               outcome, contribution, payout, net_profit, pots_json, history_complete, players_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (datetime.now().isoformat(timespec="seconds"), ", ".join(map(str, hole_cards)),
              ", ".join(map(str, board)), num_players, round(final_equity * 100, 1),
              recommendation, player_action, followed, int(won), outcome, contribution,
              payout, net_profit, json.dumps(pots) if pots is not None else None,
              int(history is not None), json.dumps(players, default=str) if players is not None else None))
        hand_id = cursor.lastrowid
        for sequence, decision in enumerate(history or [], 1):
            conn.execute("""
                INSERT INTO decisions (hand_id, sequence, street, board, equity, recommendation,
                    player_action, followed_recommendation, pot_size, bet_to_call, stack_before,
                    contribution_before, chips_added, raise_to, stack_after, players_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (hand_id, sequence, decision["street"], ", ".join(map(str, decision["board"])),
                  decision["equity"] * 100, decision["recommendation"], decision["player_action"],
                  recommendation_followed(decision["recommendation"], decision["player_action"]),
                  decision["pot_size"], decision["bet_to_call"], decision["stack_before"],
                  decision["contribution_before"], decision["chips_added"], decision.get("raise_to"),
                  decision["stack_after"], json.dumps(decision.get("players"))))
    return hand_id


def get_stats():
    initialize_db()
    with closing(get_connection()) as conn:
        total_hands, wins, avg_equity = conn.execute(
            "SELECT COUNT(*), COALESCE(SUM(won), 0), AVG(final_equity) FROM hands"
        ).fetchone()
        if not total_hands:
            return None
        evaluated, followed, followed_wins, deviated, deviated_wins = conn.execute("""
            SELECT COUNT(followed_recommendation),
                   COALESCE(SUM(followed_recommendation = 1), 0),
                   COALESCE(SUM(followed_recommendation = 1 AND won = 1), 0),
                   COALESCE(SUM(followed_recommendation = 0), 0),
                   COALESCE(SUM(followed_recommendation = 0 AND won = 1), 0) FROM hands
        """).fetchone()
        decision_count, decision_followed = conn.execute(
            "SELECT COUNT(followed_recommendation), COALESCE(SUM(followed_recommendation), 0) FROM decisions"
        ).fetchone()
        measured, profit, splits = conn.execute("""
            SELECT COUNT(net_profit), SUM(net_profit), COALESCE(SUM(outcome = 'split'), 0) FROM hands
        """).fetchone()
    return {
        "total_hands": total_hands, "wins": wins,
        "win_rate": round(wins / total_hands * 100, 1), "avg_equity": round(avg_equity, 1),
        "follow_rate": round(followed / evaluated * 100, 1) if evaluated else 0,
        "followed_win_rate": round(followed_wins / followed * 100, 1) if followed else 0,
        "deviated_win_rate": round(deviated_wins / deviated * 100, 1) if deviated else 0,
        "evaluated_hands": evaluated, "decision_count": decision_count,
        "decision_follow_rate": round(decision_followed / decision_count * 100, 1) if decision_count else None,
        "measured_hands": measured, "net_profit": round(profit, 2) if profit is not None else None,
        "splits": splits,
    }
