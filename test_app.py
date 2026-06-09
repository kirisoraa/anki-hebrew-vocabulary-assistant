#!/usr/bin/env python3
"""
Test script to verify the Hebrew vocabulary bot functionality
"""
import os
import sys
import psycopg2
import requests
from bs4 import BeautifulSoup

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import init_db, add_word, get_all_words, remove_word, get_translation

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

def main():
    """Run all tests"""
    print("Running Hebrew Vocabulary Bot Tests...\n")
    
    try:
        test_database()
        print()
        test_translation()
        print("\n✓ All tests passed!")
        return 0
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())