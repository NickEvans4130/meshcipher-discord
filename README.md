# MeshCipher Discord Bot

Beta testing support bot for the MeshCipher Discord server. Handles bug reports, release announcements, FAQ auto-responses, feature request voting, and GitHub integration.

## Features

### Bug Report System
- `/bug` - Opens a structured modal for reporting bugs (device, Android version, description, steps to reproduce)
- Reports are posted to the bug reports channel with tracking reactions
- Reaction-based status tracking (seen, investigating, fixed, can't reproduce)

### Release Announcements
- `/release` - Developer-only command to announce new versions
- Pings beta testers with changelog and download link

### FAQ Auto-Responder
- Monitors support channels for common questions
- Keyword-based matching against a configurable FAQ database
- Covers: adding contacts, connection modes, battery usage, troubleshooting, encryption details

### Feature Request Voting
- Automatic reaction voting on feature requests (upvote, downvote, fire)
- Vote tracking persisted to JSON

### GitHub Integration
- `/gh-issue` - Creates a GitHub issue from a Discord bug report
- Links the Discord message to the GitHub issue

### Onboarding
- Welcomes new members with a setup guide DM
- Auto-assigns the beta tester role

## Project Structure

```
meshcipher-bot/
  config/
    config.py          # Environment variables and constants
    faq_data.json      # FAQ knowledge base
  src/
    bot.py             # Main entry point
    commands.py        # Slash commands and modals
    events.py          # Event handlers (join, reactions, voting)
    faq.py             # FAQ auto-responder
    github_sync.py     # GitHub issue integration
  data/                # Runtime data (gitignored)
    bugs.json
    features.json
  logs/                # Log files (gitignored)
  .env                 # Bot token and config (gitignored)
  .env.example         # Template for .env
  requirements.txt     # Python dependencies
  start.sh             # Startup script
```

## Requirements

- Python 3.11+
- Discord bot token with Message Content, Members, and Reactions intents enabled
- GitHub personal access token (optional, for `/gh-issue`)

## Quick Start

```bash
# Clone the repo
git clone <repo-url>
cd meshcipher-bot

# Copy and configure environment
cp .env.example .env
# Edit .env with your values

# Run the bot
chmod +x start.sh
./start.sh
```

See [SETUP.md](SETUP.md) for detailed setup instructions.

## Commands

| Command | Access | Description |
|---------|--------|-------------|
| `/bug` | Everyone | Report a bug via structured modal |
| `/stats` | Everyone | Show beta testing statistics |
| `/help` | Everyone | Show available commands |
| `/release` | Developers | Announce a new version |
| `/gh-issue` | Developers | Create GitHub issue from bug report |

## Configuration

All configuration is done through environment variables in `.env`. See `.env.example` for all available options.

### Required
- `DISCORD_TOKEN` - Bot token from Discord Developer Portal

### Channel IDs
Set these to match your server's channel structure:
- `CHANNEL_ANNOUNCEMENTS`
- `CHANNEL_BUG_REPORTS`
- `CHANNEL_FEATURE_REQUESTS`
- `CHANNEL_GETTING_STARTED`
- `CHANNEL_TROUBLESHOOTING`

### Role IDs
- `ROLE_BETA_TESTER` - Auto-assigned to new members
- `ROLE_DEVELOPER` - Required for admin commands

### Optional
- `GITHUB_TOKEN` - For GitHub issue integration
- `GITHUB_REPO` - Repository in `owner/repo` format

## License

Apache 2.0
