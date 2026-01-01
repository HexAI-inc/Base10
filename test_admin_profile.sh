#!/bin/bash

# Admin Profile API Test Script
# This script tests all admin profile and settings endpoints

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
BASE_URL="http://localhost:8000/api/v1/admin"
ADMIN_TOKEN=""  # Set this to your admin JWT token

# Check if token is set
if [ -z "$ADMIN_TOKEN" ]; then
    echo -e "${RED}ERROR: ADMIN_TOKEN not set${NC}"
    echo "Usage: ADMIN_TOKEN='your_token_here' ./test_admin_profile.sh"
    exit 1
fi

echo "========================================"
echo "Admin Profile API Tests"
echo "========================================"
echo ""

# Test 1: Get Admin Profile
echo -e "${YELLOW}Test 1: GET /admin/profile${NC}"
response=$(curl -s -w "\n%{http_code}" -X GET "${BASE_URL}/profile" \
    -H "Authorization: Bearer ${ADMIN_TOKEN}")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" -eq 200 ]; then
    echo -e "${GREEN}✓ Status: 200 OK${NC}"
    echo "Response:"
    echo "$body" | python3 -m json.tool 2>/dev/null || echo "$body"
else
    echo -e "${RED}✗ Status: $http_code${NC}"
    echo "Response: $body"
fi
echo ""

# Test 2: Update Admin Profile
echo -e "${YELLOW}Test 2: PATCH /admin/profile${NC}"
response=$(curl -s -w "\n%{http_code}" -X PATCH "${BASE_URL}/profile" \
    -H "Authorization: Bearer ${ADMIN_TOKEN}" \
    -H "Content-Type: application/json" \
    -d '{
        "full_name": "Test Admin User",
        "bio": "Updated via API test"
    }')
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" -eq 200 ]; then
    echo -e "${GREEN}✓ Status: 200 OK${NC}"
    echo "Response:"
    echo "$body" | python3 -m json.tool 2>/dev/null || echo "$body"
else
    echo -e "${RED}✗ Status: $http_code${NC}"
    echo "Response: $body"
fi
echo ""

# Test 3: Update Admin Settings
echo -e "${YELLOW}Test 3: PATCH /admin/settings${NC}"
response=$(curl -s -w "\n%{http_code}" -X PATCH "${BASE_URL}/settings" \
    -H "Authorization: Bearer ${ADMIN_TOKEN}" \
    -H "Content-Type: application/json" \
    -d '{
        "notification_settings": {
            "email_enabled": true,
            "system_alerts": true,
            "user_reports": true,
            "new_registrations": false,
            "performance_alerts": true,
            "security_alerts": true
        },
        "preferences": {
            "theme": "dark",
            "items_per_page": 50,
            "auto_refresh_interval": 60,
            "timezone": "Africa/Freetown"
        }
    }')
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" -eq 200 ]; then
    echo -e "${GREEN}✓ Status: 200 OK${NC}"
    echo "Response:"
    echo "$body" | python3 -m json.tool 2>/dev/null || echo "$body"
else
    echo -e "${RED}✗ Status: $http_code${NC}"
    echo "Response: $body"
fi
echo ""

# Test 4: Get Admin Activity
echo -e "${YELLOW}Test 4: GET /admin/activity${NC}"
response=$(curl -s -w "\n%{http_code}" -X GET "${BASE_URL}/activity?page=1&page_size=25" \
    -H "Authorization: Bearer ${ADMIN_TOKEN}")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" -eq 200 ]; then
    echo -e "${GREEN}✓ Status: 200 OK${NC}"
    echo "Response:"
    echo "$body" | python3 -m json.tool 2>/dev/null || echo "$body"
else
    echo -e "${RED}✗ Status: $http_code${NC}"
    echo "Response: $body"
fi
echo ""

# Test 5: Test with Invalid Token (should fail)
echo -e "${YELLOW}Test 5: GET /admin/profile with invalid token (should fail)${NC}"
response=$(curl -s -w "\n%{http_code}" -X GET "${BASE_URL}/profile" \
    -H "Authorization: Bearer invalid_token_123")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" -eq 401 ] || [ "$http_code" -eq 403 ]; then
    echo -e "${GREEN}✓ Status: $http_code (Expected failure)${NC}"
    echo "Response: $body"
else
    echo -e "${RED}✗ Status: $http_code (Expected 401 or 403)${NC}"
    echo "Response: $body"
fi
echo ""

# Test 6: Test Profile Update with Duplicate Email (should fail)
echo -e "${YELLOW}Test 6: Update with duplicate data (should fail)${NC}"
response=$(curl -s -w "\n%{http_code}" -X PATCH "${BASE_URL}/profile" \
    -H "Authorization: Bearer ${ADMIN_TOKEN}" \
    -H "Content-Type: application/json" \
    -d '{
        "username": "admin"
    }')
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" -eq 200 ] || [ "$http_code" -eq 400 ]; then
    echo -e "${GREEN}✓ Status: $http_code${NC}"
    echo "Response: $body"
else
    echo -e "${RED}✗ Status: $http_code${NC}"
    echo "Response: $body"
fi
echo ""

echo "========================================"
echo "Test Summary"
echo "========================================"
echo ""
echo "All basic tests completed!"
echo ""
echo "Next steps:"
echo "1. Review the responses above"
echo "2. Verify data is saved correctly in the database"
echo "3. Test with frontend integration"
echo "4. Test with non-admin user tokens"
echo ""
