#!/bin/bash

# Digital Ocean Runtime Logs Monitor
# Watches live application logs in real-time
#
# Prerequisites:
# 1. Install doctl: brew install doctl (macOS) or snap install doctl (Linux)
# 2. Authenticate: doctl auth init
# 3. Get your App ID from DO dashboard URL or run: doctl apps list

# Configuration
APP_NAME="base10-backend"
TAIL_LINES=50  # Number of historical lines to show initially

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
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
print_status "$CYAN" "🔍 Finding app: $APP_NAME..."
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

# Print header
clear
echo "════════════════════════════════════════════════════════════════"
print_status "$CYAN" "  📝 Live Runtime Logs - $(date '+%Y-%m-%d %H:%M:%S')"
echo "════════════════════════════════════════════════════════════════"
print_status "$YELLOW" "App: $APP_NAME"
print_status "$YELLOW" "Press Ctrl+C to exit"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Color coding function
colorize_log() {
    while IFS= read -r line; do
        # Timestamp in cyan
        if [[ $line =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2} ]] || [[ $line =~ ^[A-Z][a-z]{2}[[:space:]]+[0-9]+ ]]; then
            timestamp=$(echo "$line" | awk '{print $1" "$2" "$3}')
            message=$(echo "$line" | cut -d' ' -f4-)
            echo -ne "${CYAN}$timestamp${NC} "
            line="$message"
        fi
        
        # Color based on content
        if echo "$line" | grep -qi "error\|exception\|failed\|traceback\|❌"; then
            print_status "$RED" "$line"
        elif echo "$line" | grep -qi "warning\|⚠️"; then
            print_status "$YELLOW" "$line"
        elif echo "$line" | grep -qi "success\|complete\|✅\|ready"; then
            print_status "$GREEN" "$line"
        elif echo "$line" | grep -qi "info\|starting\|running\|🚀"; then
            print_status "$BLUE" "$line"
        elif echo "$line" | grep -qi "debug"; then
            print_status "$MAGENTA" "$line"
        elif echo "$line" | grep -qi "GET\|POST\|PUT\|DELETE\|PATCH"; then
            # HTTP requests
            if echo "$line" | grep -qi "200\|201\|204"; then
                print_status "$GREEN" "$line"
            elif echo "$line" | grep -qi "400\|401\|403\|404"; then
                print_status "$YELLOW" "$line"
            elif echo "$line" | grep -qi "500\|502\|503"; then
                print_status "$RED" "$line"
            else
                echo "$line"
            fi
        else
            echo "$line"
        fi
    done
}

# Follow logs with color coding
print_status "$CYAN" "📡 Streaming live logs..."
echo "────────────────────────────────────────────────────────────────"
echo ""

# Stream logs and colorize
doctl apps logs "$APP_ID" --type run --follow 2>&1 | colorize_log
