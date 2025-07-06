# Discord Bot

This is a Discord bot with various utility and AI-powered commands.

## Features

*   **Team Randomizer**: Randomly assigns players to two teams.
*   **Option Chooser**: Randomly selects an option from a given list.
*   **Ask Users**: Sends a question to mentioned users via DM and reports their answers back to the channel.
*   **Prompt with Audio**: Collects input from mentioned users based on a prompt, sends it to Google Gemini, and returns the generated content as both text and an audio file.
*   **Gemini Chat**: Allows users to directly ask questions to Google Gemini.
*   **Help Command**: Displays information about all available commands.

## Setup

### Prerequisites

*   Python 3.8+
*   `pip` (Python package installer)

### Installation

1.  **Clone the repository (if applicable) or navigate to your project directory:**
    ```bash
    cd ....\DiscordBot
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv .venv
    ```

3.  **Activate the virtual environment:**
    *   **Windows:**
        ```bash
        .venv\Scripts\activate
        ```
    *   **macOS/Linux:**
        ```bash
        source .venv/bin/activate
        ```

4.  **Install the required Python packages:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Create a `.env` file:**
    In the root directory of your project, create a file named `.env` and add your Discord Bot Token and Google Gemini API Key:
    ```
    DISCORD_TOKEN=YOUR_DISCORD_BOT_TOKEN_HERE
    GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE
    ```
    *   Replace `YOUR_DISCORD_BOT_TOKEN_HERE` with your actual Discord bot token from the Discord Developer Portal.
    *   Replace `YOUR_GEMINI_API_KEY_HERE` with your actual Google Gemini API Key.

6.  **Enable Server Members Intent:**
    Go to your bot's page in the Discord Developer Portal, navigate to the "Bot" section, and enable the "Server Members Intent" under "Privileged Gateway Intents". This is crucial for commands like `!ask` and `!poem` to function correctly.

7.  **Enable Generative Language API:**
    Ensure that the "Generative Language API" is enabled for your Google Cloud project where you obtained your Gemini API key. You can check this in the Google Cloud Console under "APIs & Services" -> "Enabled APIs & services".

## Running the Bot

Once you have completed the setup, you can run the bot using the following command from your project directory (with the virtual environment activated):

```bash
python main.py
```

## Commands

Here are the commands you can use with the bot:

*   **`!hello`**
    *   **Description**: Greets the user.
    *   **Usage**: `!hello`

*   **`!teams <player1> <player2> ...`**
    *   **Description**: Randomizes players into two teams.
    *   **Usage**: `!teams Player1 Player2 "Player With Space"`
    *   **Note**: If a player's name contains spaces, enclose it in double quotes.

*   **`!which <option1> <option2> ...`**
    *   **Description**: Chooses a game (or anything) from given options.
    *   **Usage**: `!which OptionA OptionB "Option C"`
    *   **Note**: If an option contains spaces, enclose it in double quotes.

*   **`!ask @User1 @User2 ... <Your question here>`**
    *   **Description**: Asks mentioned users a question via DM and reports their answers back to the channel.
    *   **Usage**: `!ask @JohnDoe @JaneDoe What is your favorite color?`

*   **`!prompt_audio @User1 @User2 ... <Your prompt for the content>`**
    *   **Description**: Collects input from mentioned users based on a prompt, sends it to Google Gemini, and returns the generated content as both text and an audio file.
    *   **Usage**: `!prompt_audio @User1 @User2 Write a poem about nature using these words`

*   **`!gemini <Your question here>`**
    *   **Description**: Allows you to directly ask questions to Google Gemini.
    *   **Usage**: `!gemini Tell me a fun fact about cats.`

*   **`!help`**
    *   **Description**: Displays a list of all available commands and their usage.
    *   **Usage**: `!help`
