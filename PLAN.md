# Plan: Manual Translation Entry on Missing Translation

## Context

Currently, when `get_translation()` returns `"Translation not found"`, the word is still saved to the database with that placeholder text. The user wants a conversation flow where the bot prompts them to enter their own translation instead. Also adding `/cancel` and `/c` commands to abort the conversation flow.

## Approach

Use `context.user_data` to track pending words when a translation is not found. The flow:

1. User sends a Hebrew word (via `/add` or plain text)
2. Bot tries to translate it
3. If translation is found → save and confirm (existing behavior)
4. If translation is NOT found → store the word in `context.user_data['pending_word']` and prompt:
   - Bot: "Translation not found for '{word}'. Please enter the translation:"
5. When user replies:
   - Bot checks if `pending_word` exists → if yes, saves the word with the manual translation
   - User sends `/cancel` or `/c` → clears `pending_word` and aborts

This only affects the "translation not found" case — all existing behavior is preserved.

## Implementation Details

Initially attempted using `ConversationHandler`, but encountered API compatibility issues with `telegram-ext-bot` v20.5 where custom filter classes had signature mismatches. Switched to a simpler stateless approach using `context.user_data` to track pending words.

### `app.py`
- Added `cancel_translation` handler that clears `pending_word` and sends confirmation
- Modified `handle_text()` to check for `pending_word` at the top (manual translation mode)
- Modified `handle_text()` to set `pending_word` when translation is not found
- Modified `add_word_command()` similarly
- Added `/cancel` and `/c` command handlers

### `test_app.py`
- Added comprehensive async tests for the manual translation flow:
  - `test_handle_text_with_translation` - normal flow
  - `test_handle_text_without_translation` - prompts for manual entry
  - `test_handle_text_manual_translation` - saves manual translation
  - `test_cancel_translation` - cancels and clears pending word
  - `test_add_word_command_without_translation` - /add command flow

## Reuse

- `add_word(word, translation)` — already exists, just needs to be called with user-provided translation
- `get_translation(hebrew_word)` — already returns `"Translation not found"`, which we check against
- All other handlers remain unchanged

## Steps

- [x] Added `cancel_translation` handler that clears `pending_word` and sends confirmation
- [x] Modified `handle_text()` to check for `pending_word` (manual translation mode)
- [x] Modified `handle_text()` to set `pending_word` when translation is not found
- [x] Modified `add_word_command()` with the same logic
- [x] Added `/cancel` and `/c` command handlers
- [x] Verified tests pass

## Verification

- Run `python test_app.py` to ensure existing functionality works ✅
- Manual test: Send a Hebrew word that won't translate → verify bot asks for manual translation → verify user input is saved correctly ✅
- Manual test: Send a Hebrew word that does translate → verify existing behavior is unchanged ✅
- Manual test: Use `/add` command with a non-translatable word → verify same conversation flow ✅
- Manual test: Use `/cancel` or `/c` to abort manual translation entry ✅

## Verification

- Run `python test_app.py` to ensure existing functionality works
- Manual test: Send a Hebrew word that won't translate → verify bot asks for manual translation → verify user input is saved correctly
- Manual test: Send a Hebrew word that does translate → verify existing behavior is unchanged
- Manual test: Use `/add` command with a non-translatable word → verify same conversation flow
