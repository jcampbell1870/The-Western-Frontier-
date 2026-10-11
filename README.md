# The Western Frontier - Python Flask Web Game

## Overview

A playable web-based recreation of the classic 1971 Oregon Trail game, built with Python 3 and Flask. Players manage resources, make strategic decisions, and survive the journey from Missouri to Oregon. Completed journeys earn Arcade1870 tokens from the shared reward vault.

## Features

- **Full Oregon Trail Gameplay**: Journey progression, resource management, random events
- **Profession Selection**: Start as Banker, Carpenter, or Farmer with different resources
- **Strategic Decisions**: Hunt for food, rest to recover, cross rivers, manage supplies
- **Random Events**: Weather, illness, wagon damage, successful hunting opportunities
- **Win/Lose Conditions**: Reach Oregon City to win; lose with party death or wagon failure
- **Blockchain Integration**: Completed journeys eligible for 5 A1870 token rewards
- **Persistent Game State**: Session-based game storage
- **Responsive Web UI**: Works on desktop and mobile
- **Modern Flask Stack**: Python 3, Flask-CORS, Gunicorn, environment-based config

## Local Development

### Prerequisites

- Python 3.8+
- pip or poetry

### Setup

```bash
# Clone the repository
git clone https://github.com/jcampbell1870/The-Western-Frontier-.git
cd The-Western-Frontier-

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

Visit `http://localhost:5000` in your browser.

## Deployment to Render

### Step 1: Connect GitHub Repository

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **New +** > **Web Service**
3. Connect your GitHub account and select `The-Western-Frontier-` repository
4. Render will auto-detect the `render.yaml` configuration

### Step 2: Configure Service

Render will read from `render.yaml` and auto-configure:

```yaml
name: The Western Frontier
services:
  - type: web
    name: western-frontier
    env: python
    pythonVersion: 3.12
    buildCommand: "pip install -r requirements.txt"
    startCommand: "gunicorn app:app"
```

### Step 3: Deploy

1. Click **Create Web Service**
2. Render will automatically build and deploy
3. Your app will be live at: `https://your-render-service-name.onrender.com`

### Environment Variables (Set in Render Dashboard)

- `FLASK_ENV`: production
- `SECRET_KEY`: Your secret key (Render auto-generates)
- `PORT`: Automatically set by Render (default 5000)

## Game Mechanics

### Starting Resources (by Profession)

| Profession | Money | Food | Ammo | Clothing | Difficulty |
|------------|-------|------|------|----------|-------------|
| Farmer     | $400  | 220  | 80   | 10       | Easy        |
| Carpenter  | $800  | 180  | 90   | 8        | Medium      |
| Banker     | $1600 | 200  | 120  | 8        | Hard        |

### Actions

- **Next Day**: Advance time, consume food, move distance, face random events
- **Hunt**: Spend ammunition for food (stochastic success)
- **Rest**: Restore party health, gain morale points
- **Cross River**: Risk-based river crossing with potential losses
- **Claim A1870**: Claim reward if journey completed

### Random Events

- Storm: Wagon damage, distance loss
- Safe crossing: Morale boost, score gain
- Illness: Party member health loss
- Wildlife: Extra distance on favorable encounter

### Winning Conditions

- Reach 2000+ miles to Oregon City
- Keep party alive (at least 1 member)
- Maintain wagon integrity (health > 0)

### Reward System

**Arcade1870 Token Rewards:**
- Contract: `0x8eddD4edea39c5B5f77662453600F53A202EE47C`
- Vault: `0x1e4f6e4a382adbdb662733a19ae773d3ab8f497d`
- Per Completed Journey: **5 A1870 tokens**

Shared vault with Crypto Hockey and other games in the ecosystem.

## API Endpoints

### `POST /api/new-game`
Create a new game session.

**Request:**
```json
{
  "player_name": "John Smith",
  "profession": "Farmer"
}
```

**Response:**
```json
{
  "success": true,
  "game": { /* GameState */ },
  "config": {
    "vault": "0x1e4f6e4a382adbdb662733a19ae773d3ab8f497d",
    "contract": "0x8eddD4edea39c5B5f77662453600F53A202EE47C",
    "reward_amount": "5"
  }
}
```

### `GET /api/state`
Get current game state.

**Response:**
```json
{
  "player_name": "John Smith",
  "distance": 450,
  "max_distance": 2000,
  "has_won": false,
  "game_over": false,
  "journal": [/* journey log */],
  "members": [/* party */],
  /* ... other state fields ... */
}
```

### `POST /api/action`
Execute a game action.

**Request:**
```json
{
  "action": "advance-day"
}
```

Actions: `advance-day`, `hunt`, `rest`, `cross-river`, `claim-reward`

### `GET /api/health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "The Western Frontier",
  "timestamp": "2024-01-01T12:00:00"
}
```

## Technology Stack

- **Framework**: Flask 3.0.3
- **WSGI Server**: Gunicorn 22.0.0
- **Language**: Python 3.12
- **CORS Support**: Flask-CORS 4.0.0
- **Deployment**: Render (Docker-ready)

## File Structure

```
The-Western-Frontier-/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── Procfile               # Deployment configuration
├── render.yaml            # Render service config
├── config.json            # Blockchain configuration
├── templates/
│   └── index.html         # Game UI (HTML/CSS/JS)
└── README.md             # This file
```

## Performance

- Session-based state (no database required)
- Lightweight Flask app (~5-10MB memory)
- Render free tier: Up to 750 hours/month
- Auto-sleep after 15 minutes of inactivity
- Response time: <100ms typical

## Troubleshooting

### App won't start

```bash
# Check Python version
python --version  # Should be 3.8+

# Verify dependencies
pip install -r requirements.txt

# Test locally
python app.py
```

### Game state lost after deployment

- Session data is stored in-memory; redeploys will clear sessions
- This is by design for stateless web deployment
- For persistence, implement database (PostgreSQL on Render)

### Reward claim not working

- Ensure you've completed the journey (reached 2000+ miles)
- Check browser console for API errors
- Verify blockchain config in `config.json`

## Future Enhancements

- [ ] Database persistence (PostgreSQL)
- [ ] User authentication & leaderboard
- [ ] WebSocket multiplayer journey
- [ ] NFT milestone rewards
- [ ] Advanced trading post UI
- [ ] Mobile native app (React Native)
- [ ] Seasonal events & challenges

## License

Provided as-is for educational and entertainment purposes.

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to GitHub
5. Open a Pull Request

## Support

For issues or questions:

1. Check [GitHub Issues](https://github.com/jcampbell1870/The-Western-Frontier-/issues)
2. Review [Render Documentation](https://render.com/docs)
3. Open a new issue with details

## Acknowledgments

- Original game: Carleton College (1971) - Don Rawitsch, Bill Heinemann, Paul Dillenberger
- Producer: Minnesota Educational Computing Consortium (MECC)
- Built with Flask and Python 3
- Deployed on Render
- Blockchain integration: Arcade1870 token & reward vault

---

**🤠 Ready to blaze a trail to Oregon? Play now!**

*The Western Frontier - Where History Meets Web3*
