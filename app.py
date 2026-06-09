import os
import sqlite3
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
from bs4 import BeautifulSoup
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
DB_PATH = "vocabulary.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vocabulary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word TEXT UNIQUE NOT NULL,
            translation TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_word(word, translation):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT OR IGNORE INTO vocabulary (word, translation) VALUES (?, ?)", (word, translation))
        conn.commit()
        return True
    except sqlite3.Error as e:
        logger.error(f"Error adding word: {e}")
        return False
    finally:
        conn.close()

def get_all_words():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT word, translation FROM vocabulary")
    words = cursor.fetchall()
    conn.close()
    return words

def remove_word(word):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM vocabulary WHERE word = ?", (word,))
    conn.commit()
    conn.close()

def get_translation(hebrew_word):
    url = "https://doitinhebrew.com/translate/default.aspx"
    params = {
        'kb': 'IL+Hebrew+Phonetic',
        'l1': 'iw',
        'l2': 'en',
        'txt': hebrew_word
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        translation_div = soup.find('div', {'id': 'ctl00_ctl00_ContentPlaceHolder1_ContentMiddle_TranslationPanel1_div_right'})
        if translation_div:
            return translation_div.get_text(strip=True)
        return "Translation not found"
    except Exception as e:
        logger.error(f"Error fetching translation: {e}")
        return "Error fetching translation"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to Hebrew Vocabulary Bot! Use /help to see available commands.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
Available commands:
/list - Show all saved words
/add - Add a Hebrew word (send word directly)
/remove - Remove a Hebrew word
/deck - Generate and send Anki deck
/help - Show this help message

To add a word, simply send the Hebrew word.
"""
    await update.message.reply_text(help_text)

async def list_words(update: Update, context: ContextTypes.DEFAULT_TYPE):
    words = get_all_words()
    if not words:
        await update.message.reply_text("No words saved yet.")
        return
    
    message = "Saved words:\n"
    for word, translation in words:
        message += f"• {word} - {translation}\n"
    
    await update.message.reply_text(message)

async def add_word_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Please provide a Hebrew word to add.")
        return
    
    hebrew_word = context.args[0]
    translation = get_translation(hebrew_word)
    
    if add_word(hebrew_word, translation):
        await update.message.reply_text(f"Added: {hebrew_word} - {translation}")
    else:
        await update.message.reply_text("Error adding word.")

async def remove_word_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Please provide a Hebrew word to remove.")
        return
    
    hebrew_word = context.args[0]
    remove_word(hebrew_word)
    await update.message.reply_text(f"Removed: {hebrew_word}")

async def generate_anki_deck(update: Update, context: ContextTypes.DEFAULT_TYPE):
    words = get_all_words()
    if not words:
        await update.message.reply_text("No words to generate deck.")
        return
    
    # Create Anki deck content
    deck_content = ""
    for word, translation in words:
        # Add word -> translation card
        deck_content += f"{word}\t{translation}\n"
        # Add translation -> word card
        deck_content += f"{translation}\t{word}\n"
    
    # Save to file
    with open("anki_deck.txt", "w", encoding="utf-8") as f:
        f.write(deck_content)
    
    # Send file to user
    with open("anki_deck.txt", "rb") as f:
        await update.message.reply_document(document=f, filename="anki_deck.txt")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    # Assume any text input is a Hebrew word to add
    translation = get_translation(text)
    
    if add_word(text, translation):
        await update.message.reply_text(f"Added: {text} - {translation}")
    else:
        await update.message.reply_text("Error adding word.")

def main():
    # Initialize database
    init_db()
    
    # Create application
    application = Application.builder().token(os.getenv("TELEGRAM_TOKEN")).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("list", list_words))
    application.add_handler(CommandHandler("add", add_word_command))
    application.add_handler(CommandHandler("remove", remove_word_command))
    application.add_handler(CommandHandler("deck", generate_anki_deck))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    # Run the bot
    application.run_polling()

if __name__ == "__main__":
    main()