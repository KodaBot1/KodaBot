import os
import sys
import yaml
import pandas as pd
from openai import OpenAI
from string import Template
import random
import csv
from dotenv import load_dotenv
import re

# === Load local .env ONLY if running locally ===
if os.environ.get("RENDER") != "true":
    load_dotenv()

# === Initialize OpenAI client once ===
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    project=os.environ.get("OPENAI_PROJECT_ID")
)

def run_bot(restaurant, message, conversation=None, name_hint=None):
    base_path = f"restaurants/{restaurant}"
    config_file = f"{base_path}/{restaurant}.config.yaml"

    with open(config_file) as f:
        config = yaml.safe_load(f)
    with open(f"{base_path}/faq.yaml") as f:
        faq_data = yaml.safe_load(f)
    with open(f"{base_path}/menu.txt") as f:
        menu_text = f.read()
    with open(f"{base_path}/website.txt") as f:
        website_text = f.read()

    faq_block = "\n".join([
        f"Q: {item['question']}\nA: {item['answer']}"
        for item in faq_data.get("faq", [])
    ])

    flavor = "😎 Friendly suggestion"
    templates = config["mode"]["outbound_templates"].get(flavor, [])
    template = Template(random.choice(templates))
    user_input = template.safe_substitute({"name": name_hint or "Customer"})

    flavor_style = config.get("flavor_styles", {}).get(flavor, {})
    tone_description = flavor_style.get("tone", "")
    max_items = flavor_style.get("max_items", 2)
    bullet_style = flavor_style.get("bullet_style", True)
    closer = random.choice(config.get("closers", []))

    contains_intro = any(
        phrase in user_input.lower()
        for phrase in ["xtreme pizza texting", "xtreme pizza ottawa", "xtreme pizza here"]
    )

    intro_line = (
        "Avoid repeating the business name if the message already includes it."
        if contains_intro else
        "Always introduce yourself naturally (e.g., 'It’s Xtreme Pizza Ottawa', 'Xtreme Pizza here')"
    )

    system_prompt = f"""
You are a fast, helpful, and friendly team member from Xtreme Pizza Ottawa.

Customer name: {name_hint or 'Customer'}
Today's tone: {flavor}
Style guide: {tone_description}
Max combos: {max_items} | Bullet style: {bullet_style}

RESPONSE RULES:
- Quick hits: Mention just one best-seller and end quickly.
- Bundle push: Recommend 2–3 deals with bold prices and short bullets.
- Friendly suggestion: Keep it casual and natural, like texting a friend.
- Call-to-action heavy: Guide to checkout or phone clearly, but avoid sounding pushy.

GENERAL RULES:
- {intro_line}
- Keep responses short and tight — no essay-length replies
- Do NOT stack hype, emojis, and CTAs in one sentence.
- Sound like a real teammate texting between orders.
- Use bullets if listing items and bullet_style = True
- Always use: https://mottawa.xtremepizzaottawa.com/menu
- End with: {closer}

Menu:
{menu_text}

FAQs:
{faq_block}
"""

    lower_msg = message.lower()
    if any(term in lower_msg for term in config["safety"].get("profanity_triggers", [])):
        return config["safety"].get("abusive_response", "We’ll stop messaging you now.") + " ::exit"
    if any(term in lower_msg for term in config["safety"].get("negative_keywords", [])):
        return config["safety"].get("polite_opt_out", "No problem! We won’t message again.") + " ::exit"

    messages = [{"role": "system", "content": system_prompt}]
    messages.append({"role": "user", "content": message})

    if conversation:
        messages = messages[:1] + conversation

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )

    assistant_reply = response.choices[0].message.content.strip()

    MAX_LENGTH = 500
    if len(assistant_reply) > MAX_LENGTH:
        assistant_reply = assistant_reply[:MAX_LENGTH].rsplit('.', 1)[0] + "."

    emoji_count = assistant_reply.count("😎") + assistant_reply.count("🍕") + assistant_reply.count("🔥")
    if emoji_count > 2:
        assistant_reply = re.sub(r"[😎🍕🔥]", "", assistant_reply, count=emoji_count - 1)

    return assistant_reply

# === CLI Testing ===
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Usage: python3 run.py [restaurant-folder-name]")
        sys.exit(1)

    restaurant = sys.argv[1]
    base_path = f"restaurants/{restaurant}"
    config_path = f"{base_path}/{restaurant}.config.yaml"

    try:
        df = pd.read_csv("test_cases.csv", encoding="utf-8")
    except Exception as e:
        print(f"❌ Error reading test_cases.csv: {e}")
        sys.exit(1)

    with open(config_path) as f:
        config = yaml.safe_load(f)

    NEGATIVE_TRIGGERS = config["safety"].get("negative_keywords", [])
    ABUSIVE_TRIGGERS = config["safety"].get("profanity_triggers", [])

    output_rows = []

    for _, row in df.iterrows():
        if "name" not in row or pd.isna(row["name"]):
            print("⚠️ Skipping row — missing 'name'")
            continue

        name = row["name"].strip()
        if any(trigger in name.lower() for trigger in NEGATIVE_TRIGGERS):
            print(f"⛔ Skipping {row['name']} due to opt-out keyword detected.")
            continue
        if any(trigger in name.lower() for trigger in ABUSIVE_TRIGGERS):
            print(f"⛔ Skipping {row['name']} due to abusive language.")
            continue

        flavor = random.choice(config.get("flavors", []))
        outbound_templates = config["mode"]["outbound_templates"].get(flavor, [])

        if not outbound_templates:
            print(f"⚠️ No outbound templates defined for flavor: {flavor}")
            continue

        template = Template(random.choice(outbound_templates))
        user_input = template.safe_substitute({"name": name})

        print("\nSending:", user_input)
        print("Tone Flavor:", flavor)

        response = run_bot(restaurant, user_input, name_hint=name)

        print("Response:\n", response)

        output_rows.append({
            "Name": name,
            "Flavor": flavor,
            "User_Input": user_input,
            "Bot_Response": response
        })

    if output_rows:
        output_df = pd.DataFrame(output_rows)
        output_df.to_csv("output_responses.csv", index=False, encoding="utf-8")
        print("\n✅ All responses saved to output_responses.csv")
    else:
        print("\n⚠️ No responses were generated.")
