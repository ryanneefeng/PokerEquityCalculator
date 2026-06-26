import sys
import os
import sqlite3
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.deck import Card
from src.session import log_hand, get_stats, DB_FILE, initialize_db

def make_cards(card_list):
    return [Card(rank, suit) for rank, suit in card_list]

def teardown_test_session():
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)

def setup_test_session(hands):
    teardown_test_session()
    initialize_db()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    for hand in hands:
        cursor.execute("""
            INSERT INTO hands (date, hole_cards, board, num_players, final_equity, recommendation, player_action, followed_recommendation, won)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            hand["date"],
            str(hand["hole_cards"]),
            str(hand["board"]),
            hand["num_players"],
            hand["final_equity"],
            hand["recommendation"],
            hand["player_action"],
            1 if hand["followed_recommendation"] else 0,
            1 if hand["won"] else 0
        ))
    conn.commit()
    conn.close()

def test_log_hand_adds_entry():
    teardown_test_session()
    player_hand = make_cards([("A", "Hearts"), ("K", "Diamonds")])
    board = make_cards([("2", "Clubs"), ("3", "Spades"), ("4", "Hearts")])
    log_hand(player_hand, board, 2, 0.65, "Raise", "raise", True)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM hands")
    count = cursor.fetchone()[0]
    cursor.execute("SELECT won, final_equity FROM hands")
    row = cursor.fetchone()
    conn.close()
    assert count == 1
    assert row[0] == 1
    assert row[1] == 65.0
    teardown_test_session()

def test_get_stats_win_rate():
    setup_test_session([
        {"date": "2026-01-01", "hole_cards": [], "board": [], "num_players": 2, "final_equity": 60.0, "recommendation": "Raise", "player_action": "raise", "followed_recommendation": True, "won": True},
        {"date": "2026-01-01", "hole_cards": [], "board": [], "num_players": 2, "final_equity": 40.0, "recommendation": "Fold", "player_action": "fold", "followed_recommendation": True, "won": False},
        {"date": "2026-01-01", "hole_cards": [], "board": [], "num_players": 2, "final_equity": 50.0, "recommendation": "Call", "player_action": "raise", "followed_recommendation": False, "won": True},
    ])
    stats = get_stats()
    assert stats["total_hands"] == 3
    assert stats["wins"] == 2
    assert stats["win_rate"] == 66.7
    assert stats["follow_rate"] == 66.7
    assert stats["followed_win_rate"] == 50.0
    assert stats["deviated_win_rate"] == 100.0
    teardown_test_session()

def test_get_stats_empty_session():
    teardown_test_session()
    stats = get_stats()
    assert stats is None