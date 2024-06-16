import json
import openai
import os
from termcolor import colored
from config import client, persona_prompt
from fileops import read_file, write_to_file, create_file
from errorhandlind import run_command_with_auto_resolve, simplify_error, generate_advice

# Load the conversation history from a file (or create an empty list)
def load_conversation_from_file(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            if not content:  # Check if the file is empty
                return []
            conversation = json.loads(content)
    except FileNotFoundError:
        conversation = []
    return conversation

# Function to send a user message and receive an assistant response
def chat(message, conversation):
    global spam_warning  # Use the global spam_warning variable
    # Truncate the conversation history to fit within the token limit
    while len(json.dumps(conversation)) > 3500:
        truncated_message = conversation.pop(0)

    # Check if the user asked Lisa to fall back in line
    if "stay in character" in message.lower():
        conversation = [{'role': 'system', 'content': persona_prompt}]
        return "My apologies sire, I will get back in character. Please, Let's proceed.", conversation

    # Check for spamming
    if len(conversation) >= 6 and conversation[-1]['content'] == conversation[-3]['content'] == conversation[-5]['content']:
        if spam_warning >= 2:
            return "Stop spamming or I will terminate this conversation!", conversation
        else:
            spam_warning += 1
            return "Please stop repeating yourself.", conversation
    else:
        spam_warning = 0  # Reset spam_warning count if the messages are not identical

    # Check if the user asked Lisa to read a file
    if "read file" in message.lower():
        file_path = message.split("read file ")[1]
        response = read_file(file_path)
        return response, conversation
    # Check if the user asked Lisa to write to a file
    if "write to file" in message.lower():
        file_path, file_content = message.split("write to file ")[1].split(" with content ")
        try:
            with open(file_path, 'a') as file:  # 'a' mode for appending to the file instead of overwriting
                file.write('\n' + file_content)  # Start from a new line
            return "File written successfully.", conversation
        except IOError:
            return "Failed to write to file.", conversation

    # Check if the user asked Lisa to create a file
    if "create file" in message.lower():
        file_path = message.split("create file ")[1]
        try:
            open(file_path, 'a').close()  # 'a' mode will create the file if it doesn't exist
            return "File created successfully.", conversation
        except IOError:
            return "Failed to create file.", conversation

    conversation.append({'role': 'user', 'content': message})

    # Check if the user asked Lisa to run a command
    if "run command" in message.lower():
        command = message.split("run command ")[1]
        output = run_command_with_auto_resolve(command)
        return output, conversation

    # Warn the user if the conversation is close to the token limit
    if len(json.dumps(conversation)) > 3800:
        print(colored("Warning: You are close to the token limit. The conversation history may be truncated.", 'red'))

    # Check if the user asked for the token count
    if "token count" in message.lower():
        token_count = len(json.dumps(conversation))
        conversation.append({'role': 'assistant', 'content': f"The current token count is {token_count}."})
        return f"The current token count is {token_count}.", conversation

    try:
        response = client.chat.completions.create(model="gpt-3.5-turbo",
        temperature=0.1,
        messages=conversation)
    except openai.RateLimitError:
        return "Sorry, I have exceeded my rate limit. Please try again later.", conversation
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}", conversation

    # Filter out responses that mention the AI model's limitations
    response_content = response['choices'][0]['message']['content']
    if "as an AI language model" in response_content:
        response_content = "I'm sorry, but I can't provide the information you're looking for."

    conversation.append({'role': 'assistant', 'content': response_content})
    return response_content, conversation
