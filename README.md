# Post Button 🔘

Separate Telegram bot for building posts with inline buttons.

Location requested by the owner:
D:\Post Button

Current build includes:
- 5 languages: Uzbek, Turkish, Russian, Arabic, English
- mandatory membership for configured channels/groups
- user destinations (channels/groups)
- post builder: media + text + buttons
- button add/delete and row placement
- preview
- test/publish
- free attribution
- premium $1 / 30 days
- manual premium grants
- user and premium lists
- balance top-up flow
- BEP20/TRC20 USDT TxID verification adapters
- admin-editable attribution/support
- SQLite storage

IMPORTANT:
1. The real BotFather token and API keys are not included.
2. Copy .env.example to .env and enter secrets locally.
3. The bot must be an admin in destinations and in required channels/groups.
4. For BEP20/TRC20, the configured token contracts are USDT mainnet contracts.
5. Test payments on a safe/test environment before enabling real-money crediting.

Run on Windows:
  cd /d "D:\Post Button"
  py -m venv .venv
  .venv\Scripts\activate
  pip install -r requirements.txt
  copy .env.example .env
  python bot.py


Admin panel additions in this build:
- 📢 Post joylash entry directly inside the admin panel
- 📡 Separate admin-managed post destinations (channels/groups)
- Manual Premium list with revoke action
- Button editing (text + URL), not only deletion
- Mandatory membership is checked immediately after language selection
- .env is loaded from the bot.py directory, so running from D:\Post Button is reliable

Telegram limitation:
- Telegram inline keyboard buttons do not expose arbitrary background-color controls to bots. The project therefore does not pretend to support real button color changes; button appearance is controlled by Telegram.
