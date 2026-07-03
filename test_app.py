#!/usr/bin/env python3
"""
Test script to verify the Hebrew vocabulary bot functionality
"""
import os
import sys
import asyncio
import psycopg2
import requests
from bs4 import BeautifulSoup
from unittest.mock import MagicMock, AsyncMock, patch

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import (
    init_db, add_word, get_all_words, remove_word, get_translation,
    handle_text, add_word_command, cancel_translation
)

def test_database():
    """Test database functionality"""
    print("Testing database functionality...")
    
    # Initialize database
    init_db()
    print("✓ Database initialized")
    
    # Test adding a word
    result = add_word("שלום", "Hello")
    print(f"✓ Added word: {result}")
    
    # Test getting all words
    words = get_all_words()
    print(f"✓ Retrieved {len(words)} words")
    
    # Test removing a word
    remove_word("שלום")
    print("✓ Removed word")
    
    return True

def test_translation():
    """Test translation functionality"""
    print("Testing translation functionality...")
    
    # Test translation
    translation = get_translation("שלום")
    print(f"✓ Translation for 'שלום': {translation}")
    
    return True

async def test_handle_text_with_translation():
    """Test handle_text when translation is found"""
    print("Testing handle_text with translation found...")
    
    # Create mock update and context
    mock_update = MagicMock()
    mock_update.message.text = "שלום"
    mock_update.message.reply_text = AsyncMock()
    
    mock_context = MagicMock()
    mock_context.user_data = {}
    
    # Call handle_text
    await handle_text(mock_update, mock_context)
    
    # Verify reply_text was called with the correct message
    mock_update.message.reply_text.assert_called_once()
    call_args = mock_update.message.reply_text.call_args[0][0]
    assert "Added:" in call_args and "שלום" in call_args
    print("✓ handle_text works when translation is found")
    
    # Verify pending_word was NOT set
    assert 'pending_word' not in mock_context.user_data
    print("✓ pending_word not set when translation found")

async def test_handle_text_without_translation():
    """Test handle_text when translation is not found"""
    print("Testing handle_text with translation not found...")
    
    # Create mock update and context
    mock_update = MagicMock()
    mock_update.message.text = "nonexistentword123"
    mock_update.message.reply_text = AsyncMock()
    
    mock_context = MagicMock()
    mock_context.user_data = {}
    
    # Mock get_translation to return "Translation not found"
    with patch('app.get_translation', return_value="Translation not found"):
        await handle_text(mock_update, mock_context)
    
    # Verify reply_text was called with the prompt
    mock_update.message.reply_text.assert_called_once()
    call_args = mock_update.message.reply_text.call_args[0][0]
    assert "Translation not found" in call_args and "Please enter the translation" in call_args
    print("✓ handle_text prompts for manual translation when not found")
    
    # Verify pending_word WAS set
    assert mock_context.user_data.get('pending_word') == "nonexistentword123"
    print("✓ pending_word set correctly")

async def test_handle_text_manual_translation():
    """Test handle_text when receiving manual translation"""
    print("Testing handle_text with manual translation input...")
    
    # Create mock update and context
    mock_update = MagicMock()
    mock_update.message.text = "Hello (manual)"
    mock_update.message.reply_text = AsyncMock()
    
    mock_context = MagicMock()
    mock_context.user_data = {'pending_word': 'nonexistentword123'}
    
    # Mock add_word to return True
    with patch('app.add_word', return_value=True):
        await handle_text(mock_update, mock_context)
    
    # Verify reply_text was called with the confirmation
    mock_update.message.reply_text.assert_called_once()
    call_args = mock_update.message.reply_text.call_args[0][0]
    assert "Added:" in call_args and "Hello (manual)" in call_args
    print("✓ handle_text saves manual translation correctly")
    
    # Verify pending_word was removed
    assert 'pending_word' not in mock_context.user_data
    print("✓ pending_word removed after saving")

async def test_cancel_translation():
    """Test cancel_translation handler"""
    print("Testing cancel_translation...")
    
    # Create mock update and context
    mock_update = MagicMock()
    mock_update.message.reply_text = AsyncMock()
    
    mock_context = MagicMock()
    mock_context.user_data = {'pending_word': 'some_word'}
    
    # Call cancel_translation
    await cancel_translation(mock_update, mock_context)
    
    # Verify pending_word was removed
    assert 'pending_word' not in mock_context.user_data
    print("✓ pending_word removed after cancel")
    
    # Verify reply_text was called
    mock_update.message.reply_text.assert_called_once()
    call_args = mock_update.message.reply_text.call_args[0][0]
    assert "Cancelled" in call_args
    print("✓ cancel message sent")

async def test_add_word_command_without_translation():
    """Test add_word_command when translation is not found"""
    print("Testing add_word_command with translation not found...")
    
    # Create mock update and context
    mock_update = MagicMock()
    mock_update.message.reply_text = AsyncMock()
    
    mock_context = MagicMock()
    mock_context.args = ["nonexistentword456"]
    mock_context.user_data = {}
    
    # Mock get_translation to return "Translation not found"
    with patch('app.get_translation', return_value="Translation not found"):
        await add_word_command(mock_update, mock_context)
    
    # Verify reply_text was called with the prompt
    mock_update.message.reply_text.assert_called_once()
    call_args = mock_update.message.reply_text.call_args[0][0]
    assert "Translation not found" in call_args and "Please enter the translation" in call_args
    print("✓ add_word_command prompts for manual translation when not found")
    
    # Verify pending_word WAS set
    assert mock_context.user_data.get('pending_word') == "nonexistentword456"
    print("✓ pending_word set correctly in add_word_command")

async def run_all_tests():
    """Run all async tests"""
    print("\n" + "="*60)
    print("Running Manual Translation Flow Tests...")
    print("="*60 + "\n")
    
    try:
        await test_handle_text_with_translation()
        print()
        await test_handle_text_without_translation()
        print()
        await test_handle_text_manual_translation()
        print()
        await test_cancel_translation()
        print()
        await test_add_word_command_without_translation()
        print()
        print("✓ All manual translation tests passed!")
        return 0
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

def main():
    """Run all tests"""
    print("Running Hebrew Vocabulary Bot Tests...\n")
    
    # Run sync tests
    try:
        test_database()
        print()
        test_translation()
        print("\n✓ Sync tests passed!")
    except Exception as e:
        print(f"\n✗ Sync test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Run async tests
    print()
    result = asyncio.run(run_all_tests())
    return result

if __name__ == "__main__":
    sys.exit(main())
