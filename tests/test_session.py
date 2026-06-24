import sys
import os
import json
import tempfile
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.deck import Card
from src.session import log_hand, get_stats, SESSION_FILE

def make_cards(card_list):
    return [Card(rank, suit) for rank, suit in card_list]

def setup_test_session(hands):
    with open(SESSION_FILE, "w", encoding="utf-8") as f:
        json.dump(hands, f)

def teardown_test_session():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)

def test_log_hand_adds_entry():
    teardown_test_session()
    player_hand = make_cards([("A", "Hearts"), ("K", "Diamonds")])
    board = make_cards([("2", "Clubs"), ("3", "Spades"), ("4", "Hearts")])
    log_hand(player_hand, board, 2, 0.65, "Raise", "raise", True)
    with open(SESSION_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert len(data) == 1
    assert data[0]["won"] == True
    assert data[0]["final_equity"] == 65.0
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