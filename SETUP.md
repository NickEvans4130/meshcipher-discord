# MeshCipher Bot Setup Guide

## 1. Create a Discord Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application", name it "MeshCipher Bot"
3. Go to the "Bot" tab
4. Click "Reset Token" and copy it - you'll need this for `.env`
5. Enable these Privileged Gateway Intents:
   - Message Content Intent
   - Server Members Intent
6. Go to "OAuth2" > "URL Generator"
7. Select scopes: `bot`, `applications.commands`
8. Select permissions: Send Messages, Embed Links, Add Reactions, Manage Messages, Read Message History, Use Slash Commands
9. Copy the generated URL and open it to invite the bot to your server

## 2. Set Up Your Discord Server

Create these channels (or use existing ones):

| Channel | Purpose |
|---------|---------|
| #announcements | Release announcements |
| #bug-reports | Bug report submissions |
| #feature-requests | Feature voting |
| #getting-started | New user onboarding + FAQ |
| #troubleshooting | Support + FAQ |

Create these roles:

| Role | Purpose |
|------|---------|
| Beta Tester | Auto-assigned to new members |
| Developer | Access to admin commands |

## 3. Get Channel and Role IDs

1. Enable Developer Mode in Discord: User Settings > Advanced > Developer Mode
2. Right-click each channel and select "Copy Channel ID"
3. Right-click each role and select "Copy Role ID"

## 4. Configure the Bot

```bash
cp .env.example .env
```

Edit `.env` and fill in all values:

```
DISCORD_TOKEN=your_bot_token_here
CHANNEL_ANNOUNCEMENTS=123456789
CHANNEL_BUG_REPORTS=123456789
CHANNEL_FEATURE_REQUESTS=123456789
CHANNEL_GETTING_STARTED=123456789
CHANNEL_TROUBLESHOOTING=123456789
ROLE_BETA_TESTER=123456789
ROLE_DEVELOPER=123456789
```

## 5. GitHub Integration (Optional)

To enable `/gh-issue`:

1. Create a GitHub Personal Access Token at https://github.com/settings/tokens
2. Give it `repo` scope
3. Add to `.env`:
   ```
   GITHUB_TOKEN=ghp_your_token_here
   GITHUB_REPO=NickEvans4130/MeshCipher
   ```

## 6. Run the Bot

```bash
chmod +x start.sh
./start.sh
```

The script will:
- Check Python version (3.11+ required)
- Create a virtual environment
- Install dependencies
- Initialize data files
- Start the bot

## 7. Verify

Once running, you should see:
```
Logged in as MeshCipher Bot#1234
Synced 5 slash commands
Bot is ready!
```

Test with `/help` in any channel to confirm slash commands are working.

## Troubleshooting

**"DISCORD_TOKEN not set"** - Make sure `.env` exists and contains your token.

**Slash commands not showing** - Commands sync on startup. Wait a few minutes or restart the bot. Guild-specific sync is faster than global.

**"Could not find bug reports channel"** - Check that the channel IDs in `.env` match your server.

**FAQ not responding** - FAQ only works in the getting-started and troubleshooting channels.
