import os
import sys
import yaml
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
from string import Template
import random

# === Load API key from environment (Render & local .env)
load_dotenv(override=True)

# === Load restaurant folder name ===
if len(sys.argv) < 2:
    print("❌ Usage: python3 run.py [restaurant-folder-name]")
    sys.exit(1)

restaurant = sys.argv[1]
base_path = f"restaurants/{restaurant}"

# === Load brain files ===
with open(f"{base_path}/config.yaml") as f:
    config = yaml.safe_load(f)

with open(f"{base_path}/faq.yaml") as f:
    faq_data = yaml.safe_load(f)

with open(f"{base_path}/menu.txt") as f:
    menu_text = f.read()

with open(f"{base_path}/website.txt") as f:
    website_text = f.read()

# === Format FAQs into text block ===
faq_block = "\n".join([
    f"Q: {item['question']}\nA: {item['answer']}"
    for item in faq_data.get("faq", [])
])

# === Load test cases ===
try:
    df = pd.read_csv("test_cases.csv", encoding="utf-8")
except Exception as e:
    print(f"❌ Error reading test_cases.csv: {e}")
    sys.exit(1)

# === Safety filter keywords ===
NEGATIVE_TRIGGERS = config["safety"]["negative_keywords"]
ABUSIVE_TRIGGERS = config["safety"]["profanity_triggers"]

# === Run test cases ===
for _, row in df.iterrows():
    if "name" not in row:
        print("⚠️ Skipping row — missing 'name'")
        continue

    name = row["name"].lower()
    if any(trigger in name for trigger in NEGATIVE_TRIGGERS):
        print(f"⛔ Skipping {row['name']} due to opt-out keyword detected.")
        continue
    if any(trigger in name for trigger in ABUSIVE_TRIGGERS):
        print(f"⛔ Skipping {row['name']} due to abusive language.")
        continue

    # === Create OpenAI client here inside the loop ===
    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
        project=os.environ.get("OPENAI_PROJECT_ID")
    )

    # === Choose tone flavor and message ===
    flavor = random.choice(config.get("flavors", []))
    outbound_templates = config["mode"]["outbound_templates"].get(flavor, [])

    if not outbound_templates:
        print(f"⚠️ No outbound templates defined for flavor: {flavor}")
        continue

    template = Template(random.choice(outbound_templates))
    user_input = template.safe_substitute(row.to_dict())

    print("\nSending:", user_input)
    print("Tone Flavor:", flavor)

    # === Get flavor style ===
    flavor_style = config.get("flavor_styles", {}).get(flavor, {})
    tone_description = flavor_style.get("tone", "")
    max_items = flavor_style.get("max_items", 2)
    bullet_style = flavor_style.get("bullet_style", True)

    # === Optional closer ===
    closer = random.choice(config.get("closers", []))

    # === Craft system prompt ===
    system_prompt = f"""
You are a fast, helpful, and friendly team member from Xtreme Pizza Ottawa.

Today's tone: {flavor}
Style guide: {tone_description}
Max combos: {max_items} | Bullet style: {bullet_style}

RESPONSE RULES:
- Quick hits: Mention just one best-seller and end quickly. Do NOT say "Quick hit" in your message.
- Bundle push: Recommend 2–3 deals with bold prices and short bullets.
- Friendly suggestion: Keep it casual and natural, like texting a friend.
- Call-to-action heavy: Guide to checkout or phone clearly, but avoid sounding pushy.

GENERAL RULES:
- Always introduce yourself naturally (e.g., "It’s Xtreme Pizza Ottawa", "Xtreme Pizza here", "This is Xtreme Pizza texting you").
- Do NOT stack hype, emojis, and CTAs in one sentence. End shortly after the deal.
- Sound like a real teammate texting between orders.
- Keep replies short unless listing combos.
- Use bullets if bullet_style = True.
- Always use: https://mottawa.xtremepizzaottawa.com/menu
- End with: {closer}

Menu:
{menu_text}

FAQs:
{faq_block}
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
    )

    print("Response:\n", response.choices[0].message.content)
