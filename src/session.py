import json
import os
from datetime import datetime

SESSION_FILE = "session.json"

def load_session():
    if not os.path.exists(SESSION_FILE):
        return []
    with open(SESSION_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_session(data):
    with open(SESSION_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def log_hand(hole_cards, board, num_players, final_equity, recommendation, player_action, won):
    session = load_session()
    hand = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "hole_cards": [str(card) for card in hole_cards],
        "board": [str(card) for card in board],
        "num_players": num_players,
        "final_equity": round(final_equity * 100, 1),
        "recommendation": recommendation,
        "player_action": player_action,
        "followed_recommendation": player_action.lower() in recommendation.lower(),
        "won": won
    }
    session.append(hand)
    save_session(session)