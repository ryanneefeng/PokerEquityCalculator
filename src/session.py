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

def get_stats():
    session = load_session()
    if not session:
        return None

    total_hands = len(session)
    wins = sum(1 for hand in session if hand["won"])
    win_rate = wins / total_hands

    followed = sum(1 for hand in session if hand["followed_recommendation"])
    follow_rate = followed / total_hands

    avg_equity = sum(hand["final_equity"] for hand in session) / total_hands

    # When followed recommendation
    followed_hands = [hand for hand in session if hand["followed_recommendation"]]
    followed_wins = sum(1 for hand in followed_hands if hand["won"])
    followed_win_rate = followed_wins / len(followed_hands) if followed_hands else 0

    # When deviated from recommendation
    deviated_hands = [hand for hand in session if not hand["followed_recommendation"]]
    deviated_wins = sum(1 for hand in deviated_hands if hand["won"])
    deviated_win_rate = deviated_wins / len(deviated_hands) if deviated_hands else 0

    return {
        "total_hands": total_hands,
        "wins": wins,
        "win_rate": round(win_rate * 100, 1),
        "follow_rate": round(follow_rate * 100, 1),
        "avg_equity": round(avg_equity, 1),
        "followed_win_rate": round(followed_win_rate * 100, 1),
        "deviated_win_rate": round(deviated_win_rate * 100, 1)
    }