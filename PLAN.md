# Plan: Fix "Message is too long" Error

## Problem
When `list_words` returns many vocabulary entries, the message exceeds Telegram's 4096 character limit, causing a `telegram.error.BadRequest: Message is too long` exception.

## Solution
Create a helper function to split long messages into chunks and send them sequentially.

## Steps
- [ ] Add `_send_long_message` helper function that:
  - Splits text into chunks of 4096 characters (Telegram's limit)
  - Sends each chunk as a separate message
- [ ] Update `list_words` to use `_send_long_message` instead of direct `reply_text`
- [ ] Add error handling for `telegram.error.BadRequest` in message sending
- [ ] Test with many words to verify splitting works
- [ ] Commit and push

## Verification
- Send `/list` with many words (>4096 chars total)
- Verify multiple messages are sent sequentially
- Verify no errors in logs
