#!/bin/bash
# Check Base10 deployment status

echo "🔍 Checking Base10 deployment..."
echo ""

APP_ID="1a03ec26-533e-4611-8583-1be73d259a00"

# Get deployment status
echo "📊 Deployment Status:"
doctl apps get $APP_ID 2>/dev/null | head -3

echo ""
echo "🚀 Recent Deployments:"
doctl apps list-deployments $APP_ID --format ID,Phase,Progress,CreatedAt 2>/dev/null | head -5

echo ""
echo "📝 Latest Logs (last 50 lines):"
doctl apps logs $APP_ID --type build 2>/dev/null | tail -50

echo ""
echo "🌐 To get your API URL once deployed:"
echo "   doctl apps get $APP_ID"
echo ""
echo "📊 View live logs:"
echo "   doctl apps logs $APP_ID --follow --type run"
