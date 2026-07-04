# Hebrew Vocabulary Assistant

A Telegram bot that helps with Hebrew vocabulary practice by saving words and generating Anki decks.

## Features

- Add Hebrew words with translations from doitinhebrew.com
- Manual translation entry when automatic translation fails
- Long messages are automatically split (e.g. `/list` with many words)
- Store words in a PostgreSQL database
- Generate Anki decks with reverse flashcards
- Telegram commands: /list, /add, /remove, /deck, /help, /cancel

## Disclaimer

This project was shamelessly vibecoded. 🫶

## Architecture

- Telegram bot in Python using python-telegram-bot
- PostgreSQL database for storing vocabulary
- Docker Compose for containerization
- Web scraping for translations from doitinhebrew.com

## Setup

1. Add your Telegram bot token to `.env` file
2. Run with Docker Compose:
   ```bash
   docker-compose up
   ```

## Commands

- `/start` - Start the bot
- `/help` - Show help message
- `/list` - Show all saved words
- `/add <word>` - Add a Hebrew word
- `/remove <word>` - Remove a Hebrew word
- `/deck` - Generate and send Anki deck

## Usage

1. Send a Hebrew word to add it to your vocabulary
2. If automatic translation fails, you'll be prompted to enter the translation manually
3. Use `/cancel` or `/c` to cancel manual translation entry
4. Use `/list` to see all saved words
5. Use `/deck` to generate and download an Anki deck