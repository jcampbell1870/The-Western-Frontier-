#!/usr/bin/env python3
"""
The Western Frontier - A web-based Oregon Trail game
Built with Flask and deployed to Render
"""

import os
import json
import random
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = os.environ.get('SECRET_KEY', 'western-frontier-secret-key-2024')
CORS(app)

# Game configuration
class Profession:
    BANKER = "Banker"
    CARPENTER = "Carpenter"
    FARMER = "Farmer"

class GameState:
    def __init__(self, player_name="Traveler", profession=Profession.FARMER):
        self.player_name = player_name
        self.profession = profession
        self.money = 0
        self.food = 0
        self.oxen = 0
        self.bullets = 0
        self.clothing = 0
        self.wagon_health = 100
        self.party_members = 5
        self.distance = 0
        self.max_distance = 2000
        self.month = 3
        self.day = 1
        self.year = 1848
        self.location = "Independence, Missouri"
        self.has_won = False
        self.game_over = False
        self.reward_claimed = False
        self.score = 0
        self.current_weather = "Clear"
        self.journal = [
            "The wagon rolls west from Independence, Missouri.",
            "Your party is ready for the long frontier journey."
        ]
        self.members = [
            {"name": f"Traveler {i+1}", "health": 100, "alive": True}
            for i in range(self.party_members)
        ]

        # Set profession-based starting resources
        if profession == Profession.BANKER:
            self.money = 1600
            self.food = 200
            self.oxen = 2
            self.bullets = 120
            self.clothing = 8
        elif profession == Profession.CARPENTER:
            self.money = 800
            self.food = 180
            self.oxen = 2
            self.bullets = 90
            self.clothing = 8
        else:  # Farmer
            self.money = 400
            self.food = 220
            self.oxen = 2
            self.bullets = 80
            self.clothing = 10

    def as_dict(self):
        return {
            "player_name": self.player_name,
            "profession": self.profession,
            "money": self.money,
            "food": self.food,
            "oxen": self.oxen,
            "bullets": self.bullets,
            "clothing": self.clothing,
            "wagon_health": self.wagon_health,
            "party_members": self.party_members,
            "distance": self.distance,
            "max_distance": self.max_distance,
            "month": self.month,
            "day": self.day,
            "year": self.year,
            "location": self.location,
            "has_won": self.has_won,
            "game_over": self.game_over,
            "reward_claimed": self.reward_claimed,
            "score": self.score,
            "current_weather": self.current_weather,
            "journal": self.journal[-20:],  # Keep last 20 journal entries
            "members": self.members
        }

def load_state_from_session():
    """Load game state from session"""
    state_data = session.get("game")
    if not state_data:
        return None
    
    state = GameState(
        player_name=state_data["player_name"],
        profession=state_data["profession"]
    )
    
    # Restore all attributes
    for key in ["money", "food", "oxen", "bullets", "clothing", "wagon_health", 
                "party_members", "distance", "max_distance", "month", "day", "year",
                "location", "has_won", "game_over", "reward_claimed", "score", 
                "current_weather", "journal", "members"]:
        if key in state_data and hasattr(state, key):
            setattr(state, key, state_data[key])
    
    return state

def save_state_to_session(state):
    """Save game state to session"""
    session["game"] = state.as_dict()
    session.modified = True

# Game logic functions
def advance_day(state):
    """Advance the game by one day"""
    if state.has_won or state.game_over:
        return

    # Weather roll
    weather_roll = random.randint(0, 100)
    if weather_roll < 25:
        state.current_weather = "Clear"
    elif weather_roll < 50:
        state.current_weather = "Rain"
    elif weather_roll < 70:
        state.current_weather = "Wind"
    elif weather_roll < 85:
        state.current_weather = "Snow"
    else:
        state.current_weather = "Extreme Heat"

    # Movement
    movement = random.randint(18, 36)
    state.distance += movement

    # Date advancement
    state.day += 1
    if state.day > 30:
        state.day = 1
        state.month += 1
    if state.month > 12:
        state.month = 1
        state.year += 1

    # Food consumption
    food_use = state.party_members * 2
    state.food -= food_use

    # Random events
    event_roll = random.randint(0, 100)
    if event_roll < 18:
        state.journal.append("A sudden storm damages the wagon and slows your progress.")
        state.wagon_health -= 10
        state.distance -= 10
    elif event_roll < 34:
        state.journal.append("You find a safe river crossing and restock morale.")
        state.score += 10
    elif event_roll < 48:
        state.journal.append("A member falls ill from harsh conditions.")
        for member in state.members:
            if member["alive"]:
                member["health"] -= 10
                if member["health"] <= 0:
                    member["alive"] = False
                    state.party_members -= 1
                break
    elif event_roll < 65:
        state.journal.append("You spot grazing animals and make better time on the trail.")
        state.distance += 8

    # Check failure conditions
    if state.wagon_health <= 0:
        state.journal.append("Your wagon is broken beyond repair. The journey ends here.")
        state.has_won = False
        state.game_over = True

    if state.food < 0:
        state.journal.append("The party is starving! Survival becomes desperate.")
        for member in state.members:
            if member["alive"]:
                member["health"] -= 15
                if member["health"] <= 0:
                    member["alive"] = False
                    state.party_members -= 1

    # Check win condition
    if state.distance >= state.max_distance:
        state.has_won = True
        state.score += 200
        state.location = "Oregon City, Oregon"
        state.journal.append("🎉 You reach the promised land on the frontier. Your journey is complete!")

    # Check party wipe
    if state.party_members <= 0:
        state.has_won = False
        state.game_over = True
        state.journal.append("❌ The wagon party is lost. The journey fails.")

def hunt(state):
    """Hunt for food"""
    if state.bullets <= 0:
        state.journal.append("You have no ammunition left to hunt.")
        return

    state.bullets -= 10
    success = random.randint(0, 100) > 25
    if success:
        meat = random.randint(30, 80)
        state.food += meat
        state.score += 15
        state.journal.append(f"🦌 A successful hunt yields {meat} pounds of food.")
    else:
        state.journal.append("The hunt fails, but the party remains determined.")

def rest(state):
    """Rest and recover"""
    state.journal.append("The party rests and recovers from the trail.")
    for member in state.members:
        if member["alive"] and member["health"] < 100:
            member["health"] = min(100, member["health"] + 15)
    state.score += 5

def cross_river(state):
    """Cross a river"""
    if state.distance >= state.max_distance:
        return

    danger = random.randint(0, 100)
    if danger < 35:
        state.journal.append("🌊 The river crossing is smooth and the wagon makes it through safely.")
        state.score += 10
    elif danger < 70:
        state.journal.append("🌊 The river is dangerous. A few supplies are lost in the crossing.")
        state.food = max(0, state.food - 20)
        state.money = max(0, state.money - 20)
        state.score += 5
    else:
        state.journal.append("🌊 The crossing turns tragic. The wagon suffers damage and a traveler is injured.")
        state.wagon_health -= 15
        for member in state.members:
            if member["alive"]:
                member["health"] -= 15
                if member["health"] <= 0:
                    member["alive"] = False
                    state.party_members -= 1
                break

def claim_reward(state):
    """Claim Arcade1870 reward"""
    if not state.has_won:
        state.journal.append("❌ You must complete the journey to claim rewards.")
        return False
    if state.reward_claimed:
        state.journal.append("ℹ️ Reward already claimed for this journey.")
        return False
    state.reward_claimed = True
    state.journal.append("✅ Arcade1870 reward prepared: 5 A1870 tokens from the shared vault.")
    return True

# Routes

@app.route('/')
def index():
    """Serve the main game page"""
    return render_template('index.html')

@app.route('/api/new-game', methods=['POST'])
def new_game():
    """Create a new game"""
    data = request.get_json() or {}
    player_name = data.get('player_name', 'Traveler')
    profession = data.get('profession', Profession.FARMER)
    
    state = GameState(player_name=player_name, profession=profession)
    save_state_to_session(state)
    
    return jsonify({
        'success': True,
        'game': state.as_dict(),
        'config': {
            'vault': '0x1e4f6e4a382adbdb662733a19ae773d3ab8f497d',
            'contract': '0x8eddD4edea39c5B5f77662453600F53A202EE47C',
            'reward_amount': '5'
        }
    })

@app.route('/api/state', methods=['GET'])
def get_state():
    """Get current game state"""
    state = load_state_from_session()
    if not state:
        return jsonify({'error': 'No active game'}), 404
    return jsonify(state.as_dict())

@app.route('/api/action', methods=['POST'])
def execute_action():
    """Execute a game action"""
    state = load_state_from_session()
    if not state:
        return jsonify({'error': 'No active game'}), 404

    data = request.get_json() or {}
    action = data.get('action')

    if action == 'advance-day':
        advance_day(state)
    elif action == 'hunt':
        hunt(state)
    elif action == 'rest':
        rest(state)
    elif action == 'cross-river':
        cross_river(state)
    elif action == 'claim-reward':
        claim_reward(state)
    else:
        return jsonify({'error': 'Unknown action'}), 400

    save_state_to_session(state)
    return jsonify(state.as_dict())

@app.route('/api/config/blockchain', methods=['GET'])
def get_blockchain_config():
    """Get blockchain configuration"""
    return jsonify({
        'arcade1870_contract': '0x8eddD4edea39c5B5f77662453600F53A202EE47C',
        'reward_vault': '0x1e4f6e4a382adbdb662733a19ae773d3ab8f497d',
        'reward_amount': '5',
        'default_chain_id': 1,
        'supported_chains': [1, 11155111, 137]
    })

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'The Western Frontier', 'timestamp': datetime.utcnow().isoformat()})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
