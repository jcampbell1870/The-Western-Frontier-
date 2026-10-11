#!/usr/bin/env python3
"""
The Western Frontier - A web-based Oregon Trail game
Built with Flask and deployed to Render
"""

import os
import json
import random
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Optional
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from functools import wraps

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = os.getenv('SECRET_KEY', 'western-frontier-secret-key-change-in-production')
CORS(app)

# Game configuration
class Profession(Enum):
    BANKER = "Banker"
    CARPENTER = "Carpenter"
    FARMER = "Farmer"

@dataclass
class BlockchainConfig:
    arcade1870_contract_address: str = "0x8eddD4edea39c5B5f77662453600F53A202EE47C"
    reward_vault_address: str = "0x1e4f6e4a382adbdb662733a19ae773d3ab8f497d"
    reward_issuer_url: str = "https://www.cryptohockey.org/api/reward-claim"
    reward_signer_private_key: str = ""
    reward_signer_address: str = ""
    reward_amount: str = "5"
    reward_token_decimals: int = 18
    reward_claim_ttl_seconds: int = 600
    ethereum_rpc_url: str = "https://eth-mainnet.g.alchemy.com/v2/YOUR_ALCHEMY_KEY"
    sepolia_rpc_url: str = "https://eth-sepolia.g.alchemy.com/v2/YOUR_ALCHEMY_KEY"
    polygon_rpc_url: str = "https://polygon-rpc.com"
    default_network_chain_id: int = 1
    supported_chain_ids: List[int] = field(default_factory=lambda: [1, 11155111, 137])

@dataclass
class PartyMember:
    name: str
    health: int = 100
    alive: bool = True

@dataclass
class GameState:
    player_name: str = "Traveler"
    profession: str = Profession.FARMER.value
    money: int = 0
    food: int = 0
    oxen: int = 0
    bullets: int = 0
    clothing: int = 0
    wagon_health: int = 100
    party_members: int = 5
    distance: int = 0
    max_distance: int = 2000
    month: int = 3
    day: int = 1
    year: int = 1848
    location: str = "Independence, Missouri"
    has_won: bool = False
    reward_claimed: bool = False
    score: int = 0
    journal: List[str] = field(default_factory=list)
    members: List[PartyMember] = field(default_factory=list)
    current_weather: str = "Clear"
    river_risk: int = 0
    miles_per_day: int = 20
    game_over: bool = False

class TrailGameEngine:
    def __init__(self, game_state: GameState):
        self.state = game_state
        self.random = random.Random()

    @staticmethod
    def create_new_game(player_name: str, profession: str) -> GameState:
        """Create a new game with initial state"""
        state = GameState(player_name=player_name, profession=profession)

        # Set starting resources based on profession
        if profession == Profession.BANKER.value:
            state.money = 1600
            state.food = 200
            state.oxen = 2
            state.bullets = 120
            state.clothing = 8
        elif profession == Profession.CARPENTER.value:
            state.money = 800
            state.food = 180
            state.oxen = 2
            state.bullets = 90
            state.clothing = 8
        else:  # Farmer
            state.money = 400
            state.food = 220
            state.oxen = 2
            state.bullets = 80
            state.clothing = 10

        state.party_members = 5
        state.members = [
            PartyMember(name=f"Traveler {i + 1}", health=100, alive=True)
            for i in range(state.party_members)
        ]

        state.journal = [
            "The wagon rolls west from Independence, Missouri.",
            "Your party is ready for the long frontier journey."
        ]

        return state

    def advance_day(self):
        """Advance the game by one day"""
        if self.state.has_won or self.state.game_over:
            return

        # Weather roll
        weather_roll = self.random.randint(0, 100)
        if weather_roll < 25:
            self.state.current_weather = "Clear"
        elif weather_roll < 50:
            self.state.current_weather = "Rain"
        elif weather_roll < 70:
            self.state.current_weather = "Wind"
        elif weather_roll < 85:
            self.state.current_weather = "Snow"
        else:
            self.state.current_weather = "Extreme Heat"

        # Movement
        movement = self.random.randint(18, 36)
        self.state.distance += movement

        # Date advancement
        self.state.day += 1
        if self.state.day > 30:
            self.state.day = 1
            self.state.month += 1
        if self.state.month > 12:
            self.state.month = 1
            self.state.year += 1

        # Food consumption
        food_use = self.state.party_members * 2
        self.state.food -= food_use

        # Random events
        event_roll = self.random.randint(0, 100)
        if event_roll < 18:
            self.state.journal.append("A sudden storm damages the wagon and slows your progress.")
            self.state.wagon_health -= 10
            self.state.distance -= 10
        elif event_roll < 34:
            self.state.journal.append("You find a safe river crossing and restock morale.")
            self.state.score += 10
        elif event_roll < 48:
            self.state.journal.append("A member falls ill from harsh conditions.")
            for member in self.state.members:
                if member.alive:
                    member.health -= 10
                    if member.health <= 0:
                        member.alive = False
                        self.state.party_members -= 1
        elif event_roll < 65:
            self.state.journal.append("You spot grazing animals and make better time on the trail.")
            self.state.distance += 8

        # Check failure conditions
        if self.state.wagon_health <= 0:
            self.state.journal.append("Your wagon is broken beyond repair. The journey ends here.")
            self.state.has_won = False
            self.state.game_over = True

        if self.state.food <= 0:
            self.state.journal.append("The party is running low on food. Survival becomes desperate.")
            for member in self.state.members:
                if member.alive:
                    member.health -= 15
                    if member.health <= 0:
                        member.alive = False
                        self.state.party_members -= 1

        # Check win condition
        if self.state.distance >= self.state.max_distance:
            self.state.has_won = True
            self.state.score += 200
            self.state.location = "Oregon City, Oregon"
            self.state.journal.append("You reach the promised land on the frontier. Your journey is complete.")

        # Check party loss
        if self.state.party_members <= 0:
            self.state.has_won = False
            self.state.game_over = True
            self.state.journal.append("The wagon party is lost. The journey fails.")

    def hunt(self):
        """Hunt for food"""
        if self.state.bullets <= 0:
            self.state.journal.append("You have no ammunition left to hunt.")
            return

        self.state.bullets -= 10
        success = self.random.randint(0, 100) > 25
        if success:
            meat = self.random.randint(30, 80)
            self.state.food += meat
            self.state.score += 15
            self.state.journal.append(f"A successful hunt yields {meat} pounds of food.")
        else:
            self.state.journal.append("The hunt fails, but the party remains determined.")

    def rest(self):
        """Rest and recover"""
        self.state.journal.append("The party rests and recovers from the trail.")
        for member in self.state.members:
            if member.alive and member.health < 100:
                member.health = min(100, member.health + 15)
        self.state.score += 5

    def cross_river(self):
        """Cross a river"""
        if self.state.distance >= self.state.max_distance:
            return

        danger = self.random.randint(0, 100)
        if danger < 35:
            self.state.journal.append("The river crossing is smooth and the wagon makes it through safely.")
            self.state.score += 10
        elif danger < 70:
            self.state.journal.append("The river is dangerous. A few supplies are lost in the crossing.")
            self.state.food -= 20
            self.state.money -= 20
            self.state.score += 5
        else:
            self.state.journal.append("The crossing turns tragic. The wagon suffers damage and a traveler is injured.")
            self.state.wagon_health -= 15
            for member in self.state.members:
                if member.alive:
                    member.health -= 15
                    if member.health <= 0:
                        member.alive = False
                        self.state.party_members -= 1

    def build_summary(self) -> Dict:
        """Build game state summary"""
        return {
            'player_name': self.state.player_name,
            'profession': self.state.profession,
            'date': f"{self.state.month}/{self.state.day}/{self.state.year}",
            'location': self.state.location,
            'distance': self.state.distance,
            'max_distance': self.state.max_distance,
            'weather': self.state.current_weather,
            'food': self.state.food,
            'money': self.state.money,
            'oxen': self.state.oxen,
            'bullets': self.state.bullets,
            'clothing': self.state.clothing,
            'wagon_health': self.state.wagon_health,
            'party_alive': self.state.party_members,
            'party_total': len(self.state.members),
            'score': self.state.score,
            'has_won': self.state.has_won,
            'game_over': self.state.game_over,
            'reward_ready': self.state.has_won and not self.state.reward_claimed,
            'journal': self.state.journal[-15:] if self.state.journal else []
        }

# Load blockchain configuration
def load_blockchain_config() -> BlockchainConfig:
    """Load blockchain configuration from environment or file"""
    try:
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                data = json.load(f)
                return BlockchainConfig(**data.get('BlockchainConfig', {}))
    except Exception as e:
        print(f"Warning: Could not load config file: {e}")
    return BlockchainConfig()

blockchain_config = load_blockchain_config()

# Routes

@app.route('/')
def index():
    """Serve the main game page"""
    return render_template('index.html')

@app.route('/api/game/new', methods=['POST'])
def new_game():
    """Create a new game"""
    data = request.get_json()
    player_name = data.get('player_name', 'Traveler')
    profession = data.get('profession', Profession.FARMER.value)

    game_state = TrailGameEngine.create_new_game(player_name, profession)
    session['game_state'] = asdict(game_state)
    session.modified = True

    engine = TrailGameEngine(game_state)
    return jsonify({
        'success': True,
        'game': engine.build_summary(),
        'config': {
            'vault': blockchain_config.reward_vault_address,
            'contract': blockchain_config.arcade1870_contract_address
        }
    })

@app.route('/api/game/state', methods=['GET'])
def get_game_state():
    """Get current game state"""
    if 'game_state' not in session:
        return jsonify({'error': 'No active game'}), 404

    game_dict = session.get('game_state')
    game_state = GameState(
        player_name=game_dict['player_name'],
        profession=game_dict['profession'],
        money=game_dict['money'],
        food=game_dict['food'],
        oxen=game_dict['oxen'],
        bullets=game_dict['bullets'],
        clothing=game_dict['clothing'],
        wagon_health=game_dict['wagon_health'],
        party_members=game_dict['party_members'],
        distance=game_dict['distance'],
        max_distance=game_dict['max_distance'],
        month=game_dict['month'],
        day=game_dict['day'],
        year=game_dict['year'],
        location=game_dict['location'],
        has_won=game_dict['has_won'],
        reward_claimed=game_dict['reward_claimed'],
        score=game_dict['score'],
        journal=game_dict['journal'],
        members=[PartyMember(**m) for m in game_dict['members']],
        current_weather=game_dict['current_weather'],
        game_over=game_dict['game_over']
    )

    engine = TrailGameEngine(game_state)
    return jsonify(engine.build_summary())

@app.route('/api/game/advance-day', methods=['POST'])
def advance_day():
    """Advance the game by one day"""
    if 'game_state' not in session:
        return jsonify({'error': 'No active game'}), 404

    game_dict = session.get('game_state')
    game_state = GameState(
        player_name=game_dict['player_name'],
        profession=game_dict['profession'],
        money=game_dict['money'],
        food=game_dict['food'],
        oxen=game_dict['oxen'],
        bullets=game_dict['bullets'],
        clothing=game_dict['clothing'],
        wagon_health=game_dict['wagon_health'],
        party_members=game_dict['party_members'],
        distance=game_dict['distance'],
        max_distance=game_dict['max_distance'],
        month=game_dict['month'],
        day=game_dict['day'],
        year=game_dict['year'],
        location=game_dict['location'],
        has_won=game_dict['has_won'],
        reward_claimed=game_dict['reward_claimed'],
        score=game_dict['score'],
        journal=game_dict['journal'],
        members=[PartyMember(**m) for m in game_dict['members']],
        current_weather=game_dict['current_weather'],
        game_over=game_dict['game_over']
    )

    engine = TrailGameEngine(game_state)
    engine.advance_day()

    session['game_state'] = asdict(game_state)
    session.modified = True

    return jsonify(engine.build_summary())

@app.route('/api/game/hunt', methods=['POST'])
def hunt():
    """Hunt for food"""
    if 'game_state' not in session:
        return jsonify({'error': 'No active game'}), 404

    game_dict = session.get('game_state')
    game_state = GameState(
        player_name=game_dict['player_name'],
        profession=game_dict['profession'],
        money=game_dict['money'],
        food=game_dict['food'],
        oxen=game_dict['oxen'],
        bullets=game_dict['bullets'],
        clothing=game_dict['clothing'],
        wagon_health=game_dict['wagon_health'],
        party_members=game_dict['party_members'],
        distance=game_dict['distance'],
        max_distance=game_dict['max_distance'],
        month=game_dict['month'],
        day=game_dict['day'],
        year=game_dict['year'],
        location=game_dict['location'],
        has_won=game_dict['has_won'],
        reward_claimed=game_dict['reward_claimed'],
        score=game_dict['score'],
        journal=game_dict['journal'],
        members=[PartyMember(**m) for m in game_dict['members']],
        current_weather=game_dict['current_weather'],
        game_over=game_dict['game_over']
    )

    engine = TrailGameEngine(game_state)
    engine.hunt()

    session['game_state'] = asdict(game_state)
    session.modified = True

    return jsonify(engine.build_summary())

@app.route('/api/game/rest', methods=['POST'])
def rest():
    """Rest and recover"""
    if 'game_state' not in session:
        return jsonify({'error': 'No active game'}), 404

    game_dict = session.get('game_state')
    game_state = GameState(
        player_name=game_dict['player_name'],
        profession=game_dict['profession'],
        money=game_dict['money'],
        food=game_dict['food'],
        oxen=game_dict['oxen'],
        bullets=game_dict['bullets'],
        clothing=game_dict['clothing'],
        wagon_health=game_dict['wagon_health'],
        party_members=game_dict['party_members'],
        distance=game_dict['distance'],
        max_distance=game_dict['max_distance'],
        month=game_dict['month'],
        day=game_dict['day'],
        year=game_dict['year'],
        location=game_dict['location'],
        has_won=game_dict['has_won'],
        reward_claimed=game_dict['reward_claimed'],
        score=game_dict['score'],
        journal=game_dict['journal'],
        members=[PartyMember(**m) for m in game_dict['members']],
        current_weather=game_dict['current_weather'],
        game_over=game_dict['game_over']
    )

    engine = TrailGameEngine(game_state)
    engine.rest()

    session['game_state'] = asdict(game_state)
    session.modified = True

    return jsonify(engine.build_summary())

@app.route('/api/game/cross-river', methods=['POST'])
def cross_river():
    """Cross a river"""
    if 'game_state' not in session:
        return jsonify({'error': 'No active game'}), 404

    game_dict = session.get('game_state')
    game_state = GameState(
        player_name=game_dict['player_name'],
        profession=game_dict['profession'],
        money=game_dict['money'],
        food=game_dict['food'],
        oxen=game_dict['oxen'],
        bullets=game_dict['bullets'],
        clothing=game_dict['clothing'],
        wagon_health=game_dict['wagon_health'],
        party_members=game_dict['party_members'],
        distance=game_dict['distance'],
        max_distance=game_dict['max_distance'],
        month=game_dict['month'],
        day=game_dict['day'],
        year=game_dict['year'],
        location=game_dict['location'],
        has_won=game_dict['has_won'],
        reward_claimed=game_dict['reward_claimed'],
        score=game_dict['score'],
        journal=game_dict['journal'],
        members=[PartyMember(**m) for m in game_dict['members']],
        current_weather=game_dict['current_weather'],
        game_over=game_dict['game_over']
    )

    engine = TrailGameEngine(game_state)
    engine.cross_river()

    session['game_state'] = asdict(game_state)
    session.modified = True

    return jsonify(engine.build_summary())

@app.route('/api/game/claim-reward', methods=['POST'])
def claim_reward():
    """Claim Arcade1870 reward"""
    if 'game_state' not in session:
        return jsonify({'error': 'No active game'}), 404

    game_dict = session.get('game_state')

    if not game_dict['has_won']:
        return jsonify({'error': 'Journey not completed'}), 400

    if game_dict['reward_claimed']:
        return jsonify({'error': 'Reward already claimed'}), 400

    game_dict['reward_claimed'] = True
    session['game_state'] = game_dict
    session.modified = True

    return jsonify({
        'success': True,
        'message': 'Reward claim prepared',
        'vault': blockchain_config.reward_vault_address,
        'contract': blockchain_config.arcade1870_contract_address,
        'amount': blockchain_config.reward_amount,
        'issuer_url': blockchain_config.reward_issuer_url
    })

@app.route('/api/config/blockchain', methods=['GET'])
def get_blockchain_config():
    """Get blockchain configuration"""
    return jsonify({
        'arcade1870_contract': blockchain_config.arcade1870_contract_address,
        'reward_vault': blockchain_config.reward_vault_address,
        'reward_amount': blockchain_config.reward_amount,
        'default_chain_id': blockchain_config.default_network_chain_id,
        'supported_chains': blockchain_config.supported_chain_ids
    })

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'The Western Frontier'})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.getenv('FLASK_ENV') == 'development')
