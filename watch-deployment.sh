#!/bin/bash

# Digital Ocean Deployment Monitor - Build & Deploy Only
# Monitors build progress and deployment status
#
# Prerequisites:
# 1. Install doctl: brew install doctl (macOS) or snap install doctl (Linux)
# 2. Authenticate: doctl auth init
# 3. Get your App ID from DO dashboard URL or run: doctl apps list

# Configuration
APP_NAME="1a03ec26-533e-4611-8583-1be73d259a00 "
REFRESH_INTERVAL=60  # seconds

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
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
    echo "Update APP_NAME in this script"
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
    doctl apps get-deployment "$APP_ID" "$deployment_id" --format Phase,Progress.SuccessSteps,Progress.TotalSteps,Created --no-header 2>/dev/null
}

# Function to get build logs
get_build_logs() {
    local deployment_id=$1
    doctl apps logs "$APP_ID" "$deployment_id" --type build 2>/dev/null | tail -n 30
}

# Main monitoring loop
print_status "$YELLOW" "📊 Monitoring deployment build..."
print_status "$YELLOW" "Press Ctrl+C to exit"
echo ""

LAST_DEPLOYMENT=""
NOTIFIED_ACTIVE=false

while true; do
    clear
    echo "════════════════════════════════════════════════════════════════"
    print_status "$CYAN" "  🔨 Deployment Build Monitor - $(date '+%Y-%m-%d %H:%M:%S')"
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
            NOTIFIED_ACTIVE=false
        fi
        
        # Get deployment status
        STATUS=$(get_deployment_status "$DEPLOYMENT_ID")
        PHASE=$(echo "$STATUS" | awk '{print $1}')
        PROGRESS=$(echo "$STATUS" | awk '{print $2}')
        TOTAL=$(echo "$STATUS" | awk '{print $3}')
        CREATED=$(echo "$STATUS" | awk '{print $4" "$5}')
        
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        print_status "$CYAN" "📦 Deployment ID: $DEPLOYMENT_ID"
        print_status "$CYAN" "🕐 Started: $CREATED"
        echo ""
        
        case "$PHASE" in
            "PENDING")
                print_status "$YELLOW" "⏳ Status: PENDING - Waiting to start"
                print_status "$YELLOW" "   Waiting in build queue..."
                ;;
            "BUILDING")
                print_status "$BLUE" "🔨 Status: BUILDING ($PROGRESS/$TOTAL steps)"
                print_status "$BLUE" "   Docker image being created..."
                ;;
            "DEPLOYING")
                print_status "$BLUE" "🚀 Status: DEPLOYING ($PROGRESS/$TOTAL steps)"
                print_status "$BLUE" "   Running migrations and starting containers..."
                ;;
            "ACTIVE")
                if [ "$NOTIFIED_ACTIVE" = false ]; then
                    print_status "$GREEN" "✅ Status: ACTIVE - Deployment successful!"
                    NOTIFIED_ACTIVE=true
                else
                    print_status "$GREEN" "✅ Status: ACTIVE"
                fi
                print_status "$GREEN" "   Application is running"
                ;;
            "ERROR"|"FAILED")
                print_status "$RED" "❌ Status: $PHASE - Deployment failed"
                print_status "$RED" "   Check build logs below for errors"
                ;;
            "SUPERSEDED")
                print_status "$YELLOW" "⚠️  Status: SUPERSEDED - Replaced by newer deployment"
                ;;
            *)
                print_status "$YELLOW" "📊 Status: $PHASE"
                ;;
        esac
        
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        
        # Show build logs
        if [ "$PHASE" = "BUILDING" ] || [ "$PHASE" = "DEPLOYING" ] || [ "$PHASE" = "ERROR" ] || [ "$PHASE" = "FAILED" ]; then
            print_status "$CYAN" "📋 Build Logs (last 30 lines):"
            echo "────────────────────────────────────────────────────────────────"
            BUILD_LOGS=$(get_build_logs "$DEPLOYMENT_ID")
            if [ -n "$BUILD_LOGS" ]; then
                echo "$BUILD_LOGS" | while IFS= read -r line; do
                    if echo "$line" | grep -qi "error\|failed\|exception"; then
                        print_status "$RED" "$line"
                    elif echo "$line" | grep -qi "warning"; then
                        print_status "$YELLOW" "$line"
                    elif echo "$line" | grep -qi "success\|complete\|✅"; then
                        print_status "$GREEN" "$line"
                    else
                        echo "$line"
                    fi
                done
            else
                echo "  (waiting for logs...)"
            fi
            echo ""
        fi
        
        # Show next steps when active
        if [ "$PHASE" = "ACTIVE" ]; then
            echo "════════════════════════════════════════════════════════════════"
            print_status "$GREEN" "✅ Build Complete! Application is live."
            echo ""
            print_status "$CYAN" "📝 Next steps:"
            echo "   • View runtime logs: ./watch-logs.sh"
            echo "   • Test API endpoint: curl https://your-api-url/health"
            echo "   • View app dashboard: https://cloud.digitalocean.com/apps"
            echo ""
            print_status "$YELLOW" "   Monitoring will continue for new deployments..."
            echo "════════════════════════════════════════════════════════════════"
        fi
        
        # Show help for failed deployments
        if [ "$PHASE" = "ERROR" ] || [ "$PHASE" = "FAILED" ]; then
            echo "════════════════════════════════════════════════════════════════"
            print_status "$RED" "❌ Build Failed"
            echo ""
            print_status "$YELLOW" "🔍 Troubleshooting:"
            echo "   • Check build logs above for specific errors"
            echo "   • View full logs: doctl apps logs $APP_ID $DEPLOYMENT_ID --type build"
            echo "   • Common issues:"
            echo "     - Missing dependencies in requirements.txt"
            echo "     - Dockerfile syntax errors"
            echo "     - Migration failures"
            echo "     - Build timeout (increase resources)"
            echo "════════════════════════════════════════════════════════════════"
        fi
    fi
    
    echo ""
    print_status "$YELLOW" "🔄 Refreshing in ${REFRESH_INTERVAL}s... (Ctrl+C to exit)"
    
    sleep $REFRESH_INTERVAL
done
