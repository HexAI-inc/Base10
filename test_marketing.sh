#!/bin/bash

# Test script for Base10 Marketing API
# This script tests the public waitlist endpoint

API_URL="http://localhost:8000/api/v1/marketing"

echo "🚀 Testing Marketing API..."

# 1. Join Waitlist
echo -e "\n1. Joining Waitlist..."
curl -X POST "$API_URL/waitlist" \
     -H "Content-Type: application/json" \
     -d '{
       "full_name": "Test Student",
       "phone_number": "+2201234567",
       "email": "test@example.com",
       "school_name": "Indaba High School",
       "education_level": "Grade 10",
       "location": "Banjul",
       "device_type": "Android",
       "referral_source": "Facebook"
     }'

# 2. Join Waitlist again (Idempotency check)
echo -e "\n\n2. Joining Waitlist again (should be idempotent)..."
curl -X POST "$API_URL/waitlist" \
     -H "Content-Type: application/json" \
     -d '{
       "full_name": "Test Student",
       "phone_number": "+2201234567",
       "email": "test@example.com",
       "school_name": "Indaba High School",
       "education_level": "Grade 10",
       "location": "Banjul",
       "device_type": "Android",
       "referral_source": "Facebook"
     }'

# 3. Join with different phone
echo -e "\n\n3. Joining with another lead..."
curl -X POST "$API_URL/waitlist" \
     -H "Content-Type: application/json" \
     -d '{
       "full_name": "Another Lead",
       "phone_number": "+2207654321",
       "device_type": "iPhone",
       "school_name": "Marina International"
     }'

echo -e "\n\n✅ Marketing API tests complete (Public endpoints)."
echo "Note: Admin endpoints (/leads, /stats, /broadcast) require an admin token."
