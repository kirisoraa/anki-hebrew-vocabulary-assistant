#!/bin/bash

# Deployment script for Anki Hebrew Vocabulary Assistant on TrueNAS Scale

echo "=== Anki Hebrew Vocabulary Assistant Deployment Guide ==="

echo "
1. First, you need to push this project to a Docker registry:

   Option A: Using GitHub (Free)
   - Create a new repository on GitHub
   - Run these commands:
     git remote add origin https://github.com/YOUR_USERNAME/anki-hebrew-vocabulary-assistant.git
     git branch -M main
     git push -u origin main

   Option B: Using your own Docker registry
   - Set up a registry on your TrueNAS Scale or another server
   - Tag your image accordingly

2. For TrueNAS Scale deployment:

   a. In TrueNAS Scale UI, go to Apps
   b. Click 'Catalog' and find 'Docker' or 'Helm' apps
   c. Install 'Portainer' or use the built-in Docker support
   d. Create a new container with:
      - Image: your-registry/anki-hebrew-vocabulary-assistant:latest
      - Environment variables from .env file
      - Volume mapping for PostgreSQL data
      - Port mapping for the bot

3. Configuration:
   - Make sure your .env file contains your Telegram bot token
   - Ensure PostgreSQL data persistence is configured
   - Set up health checks for the PostgreSQL service

4. After deployment:
   - Test the bot in Telegram
   - Verify database connectivity
   - Check logs for any errors

For more detailed instructions, refer to the project README.
"