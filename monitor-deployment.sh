#!/bin/bash

# Digital Ocean App Deployment Monitor
# Monitors build, deploy, and runtime logs in real-time
#
# Prerequisites:
# 1. Install doctl: https://docs.digitalocean.com/reference/doctl/how-to/install/
#    - macOS: brew install doctl
#    - Linux: snap install doctl
# 2. Authenticate: doctl auth init
# 3. Get your App ID from DO dashboard URL or run: doctl apps list

# Configuration
APP_NAME="base10-backend"
REFRESH_INTERVAL=5  # seconds

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Check if doctl is installed
if ! command -v doctl &> /dev/null; then
    print_status "$RED" "❌ Error: doctl is not installed"
    echo ""
    echo "Install doctl:"
    echo "  macOS:  brew install doctl"
    echo "  Linux:  snap install doctl"
    echo "  Other:  https://docs.digitalocean.com/reference/doctl/how-to/install/"
    echo ""
    echo "Then authenticate:"
    echo "  doctl auth init"
    exit 1
fi

# Check if authenticated
if ! doctl account get &> /dev/null; then
    print_status "$RED" "❌ Error: Not authenticated with Digital Ocean"
    echo ""
    echo "Run: doctl auth init"
    exit 1
fi

# Get App ID
print_status "$BLUE" "🔍 Finding app: $APP_NAME..."
APP_ID=$(doctl apps list --format ID,Spec.Name --no-header | grep "$APP_NAME" | awk '{print $1}')

if [ -z "$APP_ID" ]; then
    print_status "$RED" "❌ Error: App '$APP_NAME' not found"
    echo ""
    echo "Available apps:"
    doctl apps list --format ID,Spec.Name
    echo ""
    echo "Update APP_NAME in this script or run:"
    echo "  export APP_ID=your-app-id"
    echo "  $0"
    exit 1
fi

print_status "$GREEN" "✅ Found app: $APP_NAME (ID: $APP_ID)"
echo ""

# Function to get latest deployment
get_latest_deployment() {
    doctl apps list-deployments "$APP_ID" --format ID,Created --no-header | head -n 1 | awk '{print $1}'
}

# Function to get deployment status
get_deployment_status() {
    local deployment_id=$1
    doctl apps get-deployment "$APP_ID" "$deployment_id" --format Phase,Progress.SuccessSteps,Progress.TotalSteps,Progress.Steps --no-header
}

# Function to get build logs
get_build_logs() {
    local deployment_id=$1
    doctl apps logs "$APP_ID" "$deployment_id" --type build 2>/dev/null | tail -n 20
}

# Function to get runtime logs
get_runtime_logs() {
    doctl apps logs "$APP_ID" --type run 2>/dev/null | tail -n 20
}

# Main monitoring loop
print_status "$YELLOW" "📊 Monitoring deployment..."
print_status "$YELLOW" "Press Ctrl+C to exit"
echo ""

LAST_DEPLOYMENT=""

while true; do
    clear
    echo "════════════════════════════════════════════════════════════════"
    print_status "$BLUE" "  Digital Ocean Deployment Monitor - $(date '+%Y-%m-%d %H:%M:%S')"
    echo "════════════════════════════════════════════════════════════════"
    echo ""
    
    # Get latest deployment
    DEPLOYMENT_ID=$(get_latest_deployment)
    
    if [ -z "$DEPLOYMENT_ID" ]; then
        print_status "$YELLOW" "⏳ Waiting for deployment..."
    else
        if [ "$DEPLOYMENT_ID" != "$LAST_DEPLOYMENT" ]; then
            print_status "$GREEN" "🚀 New deployment detected: $DEPLOYMENT_ID"
            LAST_DEPLOYMENT="$DEPLOYMENT_ID"
        fi
        
        # Get deployment status
        STATUS=$(get_deployment_status "$DEPLOYMENT_ID")
        PHASE=$(echo "$STATUS" | awk '{print $1}')
        PROGRESS=$(echo "$STATUS" | awk '{print $2}')
        TOTAL=$(echo "$STATUS" | awk '{print $3}')
        
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        print_status "$YELLOW" "📦 Deployment: $DEPLOYMENT_ID"
        echo ""
        
        case "$PHASE" in
            "PENDING")
                print_status "$YELLOW" "⏳ Status: PENDING - Waiting to start"
                ;;
            "BUILDING")
                print_status "$BLUE" "🔨 Status: BUILDING ($PROGRESS/$TOTAL steps)"
                ;;
            "DEPLOYING")
                print_status "$BLUE" "🚀 Status: DEPLOYING ($PROGRESS/$TOTAL steps)"
                ;;
            "ACTIVE")
                print_status "$GREEN" "✅ Status: ACTIVE - Deployment successful!"
                ;;
            "ERROR"|"FAILED")
                print_status "$RED" "❌ Status: $PHASE - Deployment failed"
                ;;
            *)
                print_status "$YELLOW" "📊 Status: $PHASE"
                ;;
        esac
        
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        
        # Show build logs if building
        if [ "$PHASE" = "BUILDING" ] || [ "$PHASE" = "DEPLOYING" ]; then
            print_status "$BLUE" "📋 Recent Build Logs:"
            echo "────────────────────────────────────────────────────────────────"
            BUILD_LOGS=$(get_build_logs "$DEPLOYMENT_ID")
            if [ -n "$BUILD_LOGS" ]; then
                echo "$BUILD_LOGS"
            else
                echo "  (waiting for logs...)"
            fi
            echo ""
        fi
        
        # Always show runtime logs
        print_status "$GREEN" "📝 Recent Runtime Logs:"
        echo "────────────────────────────────────────────────────────────────"
        RUNTIME_LOGS=$(get_runtime_logs)
        if [ -n "$RUNTIME_LOGS" ]; then
            echo "$RUNTIME_LOGS"
        else
            echo "  (no runtime logs yet)"
        fi
        echo ""
        
        # Show helpful commands
        if [ "$PHASE" = "ACTIVE" ]; then
            echo "════════════════════════════════════════════════════════════════"
            print_status "$GREEN" "✅ Deployment Complete!"
            echo ""
            echo "Test your API:"
            echo "  curl https://your-api-url/health"
            echo ""
            echo "View full logs:"
            echo "  doctl apps logs $APP_ID --type run --follow"
            echo "════════════════════════════════════════════════════════════════"
        fi
    fi
    
    echo ""
    print_status "$YELLOW" "🔄 Refreshing in ${REFRESH_INTERVAL}s... (Ctrl+C to exit)"
    
    sleep $REFRESH_INTERVAL
done
