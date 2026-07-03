import os
import psycopg2
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
from bs4 import BeautifulSoup
import logging
import time
import genanki
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
DB_HOST = os.getenv("DB_HOST", "postgres")
DB_NAME = os.getenv("DB_NAME", "vocabulary_db")
DB_USER = os.getenv("DB_USER", "vocabulary_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "vocabulary_password")

def init_db():
    max_retries = 5
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD
            )
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS vocabulary (
                    id SERIAL PRIMARY KEY,
                    word TEXT UNIQUE NOT NULL,
                    translation TEXT NOT NULL
                )
            ''')
            conn.commit()
            conn.close()
            logger.info("Database initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize database (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                raise

def add_word(word, translation):
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO vocabulary (word, translation) VALUES (%s, %s) ON CONFLICT (word) DO NOTHING", (word, translation))
        conn.commit()
        # Check if any rows were actually inserted
        return cursor.rowcount > 0
    except psycopg2.Error as e:
        logger.error(f"Error adding word: {e}")
        return False
    finally:
        conn.close()

def get_all_words():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cursor = conn.cursor()
    cursor.execute("SELECT word, translation FROM vocabulary")
    words = cursor.fetchall()
    conn.close()
    return words

def remove_word(word):
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cursor = conn.cursor()
    cursor.execute("DELETE FROM vocabulary WHERE word = %s", (word,))
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
        # Make sure we're sending the correct encoding
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        # Try to decode with different encodings
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
        except:
            # If that fails, try with encoding detection
            soup = BeautifulSoup(response.content, 'html.parser', from_encoding='utf-8')
            
        translation_div = soup.find('span', {'id': 'ctl00_ctl00_ContentPlaceHolder1_ContentMiddle_TranslationPanel1_lblReverso'})
        if translation_div:
            # Clean up the text
            text = translation_div.get_text(strip=True)
            # Remove extra whitespace
            return ' '.join(text.split())
        return "Translation not found"
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error fetching translation: {e}")
        return "Network error fetching translation"
    except Exception as e:
        logger.error(f"Error fetching translation: {e}")
        return "Error fetching translation"


async def cancel_translation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop('pending_word', None)
    await update.message.reply_text("Cancelled. Word was not added.")
    return


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to Hebrew Vocabulary Bot! Use /help to see available commands.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
Available commands:
/list or /l - Show all saved words
/add or /a - Add a Hebrew word (send word directly)
/remove or /r - Remove a Hebrew word
/deck or /d - Generate and send Anki deck
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
    
    # Join all arguments to handle multi-word Hebrew phrases
    hebrew_word = ' '.join(context.args)
    translation = get_translation(hebrew_word)
    
    # Check if translation is an error message
    if translation.startswith("Error") or translation.startswith("Network error"):
        await update.message.reply_text(f"Could not translate '{hebrew_word}'. Please check the word and try again.")
        return
    
    if translation == "Translation not found":
        context.user_data['pending_word'] = hebrew_word
        await update.message.reply_text(f"Translation not found for '{hebrew_word}'. Please enter the translation:")
        return
    
    if add_word(hebrew_word, translation):
        await update.message.reply_text(f"Added: {hebrew_word} - {translation}")
    else:
        await update.message.reply_text(f"Word '{hebrew_word}' already exists in the database.")

async def remove_word_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Please provide a Hebrew word to remove.")
        return
    
    # Join all arguments to handle multi-word Hebrew phrases
    hebrew_word = ' '.join(context.args)
    remove_word(hebrew_word)
    await update.message.reply_text(f"Removed: {hebrew_word}")

async def generate_anki_deck(update: Update, context: ContextTypes.DEFAULT_TYPE):
    words = get_all_words()
    if not words:
        await update.message.reply_text("No words to generate deck.")
        return
    
    # Create Anki deck using genanki
    deck_id = uuid.uuid4().int & (1<<31)-1  # Generate a unique deck ID
    deck = genanki.Deck(deck_id, 'Hebrew Vocabulary')
    
    # Define the model for the cards
    model = genanki.Model(
        1607392319,
        'Hebrew Vocabulary Model',
        fields=[
            {'name': 'Hebrew'},
            {'name': 'Translation'},
        ],
        templates=[
            {
                'name': 'Card 1',
                'qfmt': '{{Hebrew}}',
                'afmt': '{{FrontSide}}<hr id="answer">{{Translation}}',
            },
            {
                'name': 'Card 2',
                'qfmt': '{{Translation}}',
                'afmt': '{{FrontSide}}<hr id="answer">{{Hebrew}}',
            },
        ]
    )
    
    # Add cards to the deck
    for word, translation in words:
        note = genanki.Note(
            model=model,
            fields=[word, translation]
        )
        deck.add_note(note)
    
    # Generate the .apkg file
    filename = "hebrew_vocabulary.apkg"
    genanki.Package(deck).write_to_file(filename)
    
    # Send file to user
    try:
        with open(filename, "rb") as f:
            await update.message.reply_document(document=f, filename=filename)
    except Exception as e:
        logger.error(f"Error sending file: {e}")
        await update.message.reply_text("Error generating or sending deck file.")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    # Check if we're waiting for a manual translation
    if context.user_data.get('pending_word'):
        hebrew_word = context.user_data.pop('pending_word')
        translation = text.strip()
        
        if add_word(hebrew_word, translation):
            await update.message.reply_text(f"Added: {hebrew_word} - {translation}")
        else:
            await update.message.reply_text(f"Word '{hebrew_word}' already exists in the database.")
        return
    
    # Normal flow: assume any text input is a Hebrew phrase to add
    translation = get_translation(text)
    
    # Check if translation is an error message
    if translation.startswith("Error") or translation.startswith("Network error"):
        await update.message.reply_text(f"Could not translate '{text}'. Please check the word and try again.")
        return
    
    if translation == "Translation not found":
        context.user_data['pending_word'] = text
        await update.message.reply_text(f"Translation not found for '{text}'. Please enter the translation:")
        return
    
    if add_word(text, translation):
        await update.message.reply_text(f"Added: {text} - {translation}")
    else:
        await update.message.reply_text(f"Word '{text}' already exists in the database.")

def main():
    # Test database connection
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        return
    
    # Create application
    application = Application.builder().token(os.getenv("TELEGRAM_TOKEN")).build()
    
    # Add handlers with shorthand commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("list", list_words))
    application.add_handler(CommandHandler("add", add_word_command))
    application.add_handler(CommandHandler("remove", remove_word_command))
    application.add_handler(CommandHandler("deck", generate_anki_deck))
    # Shorthand commands
    application.add_handler(CommandHandler("l", list_words))
    application.add_handler(CommandHandler("a", add_word_command))
    application.add_handler(CommandHandler("r", remove_word_command))
    application.add_handler(CommandHandler("d", generate_anki_deck))
    # Cancel command
    application.add_handler(CommandHandler("cancel", cancel_translation))
    application.add_handler(CommandHandler("c", cancel_translation))
    # Text handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    # Run the bot
    logger.info("Starting bot...")
    application.run_polling()

if __name__ == "__main__":
    main()
