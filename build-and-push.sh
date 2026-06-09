#!/bin/bash

# Manual build and push script for Anki Hebrew Vocabulary Assistant

echo "=== Building and Pushing to GitHub Container Registry ==="

# Build the Docker image
echo "Building Docker image..."
docker build -t ghcr.io/kirisoraa/anki-hebrew-vocabulary-assistant:latest .

# Login to GitHub Container Registry
echo "Logging into GitHub Container Registry..."
echo $GITHUB_TOKEN | docker login ghcr.io -u kirisoraa --password-stdin

# Push the image
echo "Pushing image to GitHub Container Registry..."
docker push ghcr.io/kirisoraa/anki-hebrew-vocabulary-assistant:latest

echo "=== Deployment Ready ==="
echo "Your image is now available at:"
echo "ghcr.io/kirisoraa/anki-hebrew-vocabulary-assistant:latest"
echo ""
echo "Use this image in your TrueNAS Scale deployment."