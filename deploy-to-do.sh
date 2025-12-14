#!/bin/bash

# Quick Deploy Script for Digital Ocean
# Run this after authenticating: doctl auth init

set -e

echo "🚀 Base10 - Digital Ocean Deployment Script"
echo "==========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if doctl is authenticated
if ! doctl account get > /dev/null 2>&1; then
    echo -e "${RED}❌ Not authenticated with Digital Ocean${NC}"
    echo "Run: doctl auth init"
    exit 1
fi

echo -e "${GREEN}✓${NC} Authenticated with Digital Ocean"
echo ""

# Step 1: Create PostgreSQL Database
echo "📊 Creating PostgreSQL database..."
DB_EXISTS=$(doctl databases list --format Name --no-header | grep -w "base10-db" || echo "")

if [ -z "$DB_EXISTS" ]; then
    doctl databases create base10-db \
        --engine pg \
        --version 15 \
        --size db-s-1vcpu-1gb \
        --region nyc3
    echo -e "${GREEN}✓${NC} Database created (takes ~5 minutes to provision)"
else
    echo -e "${YELLOW}⚠${NC} Database 'base10-db' already exists"
fi

# Step 2: SKIP Redis for MVP (Save $15/month!)
echo ""
echo -e "${YELLOW}⚠${NC} Skipping Redis for MVP - using in-memory cache (FREE!)"
echo "   Get free Redis later from: railway.app or render.com"

# Step 3: SKIP Spaces for MVP (Save $5/month!)
echo ""
echo -e "${YELLOW}⚠${NC} Skipping Spaces for MVP - using local storage (FREE!)"
echo "   App Platform has 5GB free disk space"
echo "   Can add Spaces later when you have users"

# Wait for databases to be ready
echo ""
echo "⏳ Waiting for databases to be ready (this may take a few minutes)..."
echo "   You can check status with: doctl databases list"
echo ""

# Step 5: Show connection details
echo ""
echo "📋 Resource Summary"
echo "==================="
echo ""

echo "Databases:"
doctl databases list --format Name,Status,Engine,Region,Size

echo ""
echo "=========================================="
echo -e "${GREEN}✓ Infrastructure setup complete!${NC}"
echo "=========================================="
echo ""

echo "Next steps:"
echo ""
echo "1. Get database connection strings:"
echo "   doctl databases connection base10-db"
echo "   doctl databases connection base10-redis"
echo ""
echo "2. Update app-spec.yaml with the connection strings"
echo ""
echo "3. Deploy the app:"
echo "   doctl apps create --spec app-spec.yaml"
echo "1. Get database connection string:"
echo "   doctl databases connection base10-db"
echo ""
echo "2. Update app-spec.yaml with the connection string"
echo "   doctl apps logs <app-id> --follow"
echo ""
