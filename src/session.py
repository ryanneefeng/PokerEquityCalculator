import sqlite3
from datetime import datetime

DB_FILE = "session.db"

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    return conn

def initialize_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            hole_cards TEXT,
            board TEXT,
            num_players INTEGER,
            final_equity REAL,
            recommendation TEXT,
            player_action TEXT,
            followed_recommendation INTEGER,
            won INTEGER
        )
    """)
    conn.commit()
    conn.close()

def log_hand(hole_cards, board, num_players, final_equity, recommendation, player_action, won):
    initialize_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO hands (date, hole_cards, board, num_players, final_equity, recommendation, player_action, followed_recommendation, won)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M"),
        ", ".join(str(c) for c in hole_cards),
        ", ".join(str(c) for c in board),
        num_players,
        round(final_equity * 100, 1),
        recommendation,
        player_action,
        1 if player_action.lower() in recommendation.lower() else 0,
        1 if won else 0
    ))
    conn.commit()
    conn.close()

def get_stats():
    initialize_db()
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM hands")
    total_hands = cursor.fetchone()[0]

    if total_hands == 0:
        conn.close()
        return None

    cursor.execute("SELECT COUNT(*) FROM hands WHERE won = 1")
    wins = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(final_equity) FROM hands")
    avg_equity = round(cursor.fetchone()[0], 1)

    cursor.execute("SELECT COUNT(*) FROM hands WHERE followed_recommendation = 1")
    followed = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM hands WHERE followed_recommendation = 1 AND won = 1")
    followed_wins = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM hands WHERE followed_recommendation = 0")
    deviated = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM hands WHERE followed_recommendation = 0 AND won = 1")
    deviated_wins = cursor.fetchone()[0]

    conn.close()

    return {
        "total_hands": total_hands,
        "wins": wins,
        "win_rate": round(wins / total_hands * 100, 1),
        "avg_equity": avg_equity,
        "follow_rate": round(followed / total_hands * 100, 1),
        "followed_win_rate": round(followed_wins / followed * 100, 1) if followed > 0 else 0,
        "deviated_win_rate": round(deviated_wins / deviated * 100, 1) if deviated > 0 else 0
    }