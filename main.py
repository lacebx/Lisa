from config import client, persona_prompt
from conversation import load_conversation_from_file, chat
from termcolor import colored
import json

# Start the interactive conversation
conversation = load_conversation_from_file('conversation_history.json')

# Append the persona prompt if the conversation is empty or has been truncated
if not conversation or conversation[0]['content'] != persona_prompt:
    conversation = [{'role': 'system', 'content': persona_prompt}]

# Example usage
while True:
    try:
        user_input = input(colored("User: ", 'blue'))
    except (EOFError, KeyboardInterrupt):
        print("Unexpected input error.Goodbye!")
        break
    response, conversation = chat(user_input, conversation)
    print(colored("Lisa: ", 'green') + response)

    # Append the new conversation to the conversation history
    conversation.append({'role': 'user', 'content': user_input})
    conversation.append({'role': 'assistant', 'content': response})

    # Save the updated conversation history to the file
    try:
        with open('conversation_history.json', 'w') as file:
            json.dump(conversation, file)
    except IOError:
        print("Failed to save conversation history.")
