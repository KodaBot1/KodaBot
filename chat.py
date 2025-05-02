# chat.py
from run import run_bot

restaurant = "xtreme-pizza-ottawa"
print(f"💬 Chat with {restaurant}. Type 'exit' to quit.\n")

conversation = []

while True:
    user_input = input("You: ")
    if user_input.lower() in ["exit", "quit"]:
        break

    conversation.append({"role": "user", "content": user_input})
    response = run_bot(restaurant, user_input, conversation=conversation)
    conversation.append({"role": "assistant", "content": response})

    print(f"Bot: {response}\n")
