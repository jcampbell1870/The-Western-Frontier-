# 🤠 The Western Frontier

A Windows desktop homage to the classic 1971 Oregon Trail, rebuilt as a playable 2D strategy game with a retro frontier feel, party management, resource survival, and Arcade1870 rewards.

## What is included

- A playable Windows Forms game inspired by the original Oregon Trail mechanics
- Journey progression across a frontier trail
- Profession selection, wagon supplies, and party health management
- Random events including weather, river crossings, illness, and broken wagon parts
- Hunting, resting, and trail decisions
- Reward logic tied to the same Arcade1870 vault/reward treasury used by Crypto Hockey

## Run on Windows

1. Install .NET 8 SDK.
2. Open a terminal in the repository root.
3. Run:

```powershell
dotnet restore
```

4. Then:

```powershell
dotnet build
```

5. Launch the game:

```powershell
dotnet run --project .\src\TheWesternFrontierGame\TheWesternFrontierGame.csproj
```

## Reward treasury configuration

The game uses the same Arcade1870 reward addresses as Crypto Hockey:

```json
"Arcade1870ContractAddress": "0x8eddD4edea39c5B5f77662453600F53A202EE47C",
"RewardVaultAddress": "0x1e4f6e4a382adbdb662733a19ae773d3ab8f497d",
"RewardAmount": "5"
```

## Notes

This is intentionally designed to be a faithful but modernized 1971-inspired Windows experience rather than a literal text-only clone, while keeping the classic Oregon Trail rhythm of survival, planning, and consequences.
