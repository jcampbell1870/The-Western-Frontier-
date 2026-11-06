# The Western Frontier - Python Flask Web Game

## Overview

A playable web-based recreation of the classic 1971 Oregon Trail game, built with Python 3 and Flask. Players manage resources, make strategic decisions, and survive the journey from Missouri to Oregon.

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

## Deployment to Railway

Railway is the recommended host for this project because it supports Python web apps natively, provides environment variables, and keeps deployment simple without needing Render-specific YAML.

### Step 1: Prepare the repository

1. Push this repository to GitHub.
2. Ensure the project contains:
   - `requirements.txt`
   - `app.py`
   - `railway.json` (included in this repo)
   - `runtime.txt` (included in this repo)

### Step 2: Create a Railway project

1. Go to [Railway](https://railway.com/)
2. Sign in with GitHub
3. Click **New Project**
4. Select **Deploy from GitHub repo**
5. Choose `The-Western-Frontier-`

Railway will automatically detect the Python app and use the settings in `railway.json`.

### Step 3: Configure environment variables

Set these in the Railway dashboard:

- `FLASK_ENV`: `production`
- `SECRET_KEY`: any long random value

`PORT` is provided automatically by Railway.

### Step 4: Deploy

Railway will run the project with:

```bash
gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
```

Once the build completes, Railway will provide a public URL such as:

```text
https://your-project-name.up.railway.app
```

### Optional: custom domain

After deployment:

1. Open your Railway project
2. Go to **Settings**
3. Select **Domains**
4. Add your custom domain and follow the DNS instructions

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
- **Deployment**: Railway

## File Structure

```
The-Western-Frontier-/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── railway.json            # Railway deployment configuration
├── runtime.txt             # Python version pin
├── Procfile                # Legacy Render compatibility
├── render.yaml             # Legacy Render config
├── config.json             # Blockchain configuration
├── templates/
│   └── index.html         # Game UI (HTML/CSS/JS)
└── README.md              # This file
```

## Performance

- Session-based state (no database required)
- Lightweight Flask app (~5-10MB memory)
- Railway free tier: suitable for small hobby deployments
- Auto-sleep after inactivity may apply depending on the Railway plan
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
- For persistence, implement database (PostgreSQL on Railway)

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
2. Review [Railway Documentation](https://docs.railway.com/)
3. Open a new issue with details

## Acknowledgments

- Original game: Carleton College (1971) - Don Rawitsch, Bill Heinemann, Paul Dillenberger
- Producer: Minnesota Educational Computing Consortium (MECC)
- Built with Flask and Python 3
- Deployed on Railway
- Blockchain integration: Arcade1870 token & reward vault

---

**🤠 Ready to blaze a trail to Oregon? Play now!**

*The Western Frontier - Where History Meets Web3*
