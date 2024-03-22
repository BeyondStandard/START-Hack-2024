#!/bin/bash

# Define the path of the .env file
ENV_FILE=".env"

# Check if the .env file exists
if [ ! -f "$ENV_FILE" ]; then
    # Prompt the user for input as the file doesn't exist
    read -rp "Enter your OpenAI API Key: " user_input
    echo "OPENAI_API_KEY=\"$user_input\"" > "$ENV_FILE"

    read -rp "Enter your ElevelLabs API Key: " user_input
    echo "ELEVENLABS_KEY=\"$user_input\"" >> "$ENV_FILE"

    read -rp "Enter your LangChain API Key: " user_input
    echo "LANGCHAIN_API_KEY=\"$user_input\"" >> "$ENV_FILE"

    read -rp "Enter your PlayHT UID Key: " user_input
    echo "PLAYHT_UID=\"$user_input\"" >> "$ENV_FILE"

    read -rp "Enter your PlayHT API Key: " user_input
    echo "PLAYHT_KEY=\"$user_input\"" >> "$ENV_FILE"

    echo "Your API key has been saved to $ENV_FILE."
else
    echo "$ENV_FILE already exists."
fi