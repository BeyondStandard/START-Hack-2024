#!/bin/bash

# Define the path of the .env file
ENV_FILE=".env"

# Check if the .env file exists
if [ ! -f "$ENV_FILE" ]; then
    # Prompt the user for input as the file doesn't exist
    read -p "Enter your OpenAI API Key: " user_input
    echo "OPENAI_API_KEY=\"$user_input\"" > "$ENV_FILE"

    read -p "Enter your ElevelLabs API Key: " user_input
    echo "ELEVENLABS_KEY=\"$user_input\"" >> "$ENV_FILE"

    echo "Your API key has been saved to $ENV_FILE."
else
    echo "$ENV_FILE already exists."
fi