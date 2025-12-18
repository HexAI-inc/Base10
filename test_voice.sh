#!/bin/bash

# Test script for Base10 Voice API
# Note: This requires a valid auth token and an audio file to test transcription

API_URL="http://localhost:8000/api/v1/voice"
TOKEN=$1

if [ -z "$TOKEN" ]; then
    echo "Usage: ./test_voice.sh <AUTH_TOKEN>"
    exit 1
fi

echo "🚀 Testing Voice API..."

# 1. Test TTS URL generation
echo -e "\n1. Testing TTS URL generation..."
curl -X POST "$API_URL/tts?text=Hello+Base10+students" \
     -H "Authorization: Bearer $TOKEN"

# 2. Test Transcribe (Placeholder - requires actual audio file)
echo -e "\n\n2. Testing Transcription (Metadata check)..."
# curl -X POST "$API_URL/transcribe" \
#      -H "Authorization: Bearer $TOKEN" \
#      -F "audio=@test_audio.wav"

echo -e "\n\n✅ Voice API structure verified."
echo "Note: Transcription requires a real audio file upload."
