# 🤖 KodaBot — AI-Powered Messaging Engine for Restaurants

Built by **Koda Kid**, KodaBot is a real-time, config-driven AI engine that helps restaurants connect with customers over SMS, Instagram DMs, and beyond — with zero fluff and a human feel.

---

## 👀 What It Does
KodaBot runs outbound and inbound conversations that actually sound like a real teammate texting between orders — not a stiff, robotic assistant.

It’s made to:
- Send deal blasts that feel natural, not spammy
- Answer menu questions fast
- Handle "I'm in" replies with a clear call to action
- Avoid overuse of emojis, hype, or repetition

---

## 🧱 How It Works
Everything runs through a general-purpose Python engine — no restaurant-specific code. Each location has its own folder with a config file, menu, and optional website/FAQ content.

Spin up a new bot by duplicating a folder and updating a YAML file.

---

## 🗂️ Project Structure
```
KodaBot/
├── run.py               # Main engine (batch or real-time)
├── chat.py              # Real-time terminal testing
├── requirements.txt     # Dependencies
├── .gitignore           # Keeps secrets + junk out of Git
├── restaurants/
│   └── xtreme-pizza-ottawa/
│       ├── config.yaml
│       ├── menu.txt
│       ├── faq.yaml
│       └── website.txt
```

---

## 🧪 How to Test It Locally
Talk to your bot in real time:
```bash
python3 chat.py
```

Generate outbound deal messages using a CSV:
```bash
python3 run.py xtreme-pizza-ottawa
```

CSV example:
```csv
name
Liam
Noah
Sarah
```

---

## 🔐 .env Setup
Make a `.env` file in the root folder:
```env
OPENAI_API_KEY=your-key-here
```

> This file is ignored by Git — it’s just for local use.

---

## 🧠 How It Thinks
The bot’s tone, safety filters, and content rules are all in `config.yaml`.
You can set:
- How hype-y each message type should be
- How many combos to list
- Which emoji styles to use (or not)
- What to say when someone swears or says "stop"

It can:
- Respond differently based on intent (menu, deals, help)
- Pick from multiple opening styles to avoid repetition
- Always mention who’s messaging (“It’s Koda Pizza here!”)

---

## 🛡️ Smart Filters
Out of the box, KodaBot:
- Silently blocks abusive or profane replies
- Sends a polite opt-out if someone says "unsubscribe" or "stop"
- Doesn’t respond after ghosting (configurable)

---

## 🛠️ Scale It Up
To launch for a new restaurant:
1. Duplicate an existing folder
2. Replace the menu, FAQ, and update the config
3. Test it locally — done.

No need to touch the Python engine at all.

---

## 🚀 Ready to Deploy
You can host this with:
- Railway
- Replit
- Render

And trigger it using:
- Make.com
- GoHighLevel
- Webhooks from any platform

Coming next: webhook mode + hosted version

---

## Made by Maksim (Koda Kid)
Built to be flexible, fast, and sound like a real person — not a script.

Let’s get that order rolling. 🍕
