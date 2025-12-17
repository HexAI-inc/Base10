# Deployment Monitoring Scripts

## Quick Start

### 1. Install Digital Ocean CLI (`doctl`)

```bash
# macOS
brew install doctl

# Linux (Ubuntu/Debian)
snap install doctl

# Or download from: https://docs.digitalocean.com/reference/doctl/how-to/install/
```

### 2. Authenticate

```bash
doctl auth init
# Follow the prompts to enter your API token
# Get token from: https://cloud.digitalocean.com/account/api/tokens
```

### 3. Run the Monitor

```bash
./monitor-deployment.sh
```

## What the Monitor Shows

```
════════════════════════════════════════════════════════════════
  Digital Ocean Deployment Monitor - 2025-12-17 08:45:00
════════════════════════════════════════════════════════════════

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 Deployment: abc123def456
🔨 Status: BUILDING (3/10 steps)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 Recent Build Logs:
────────────────────────────────────────────────────────────────
Step 5/12 : RUN pip install --no-cache-dir -r requirements.txt
Successfully built image
Running database migrations...
INFO [alembic.runtime.migration] Running upgrade...

📝 Recent Runtime Logs:
────────────────────────────────────────────────────────────────
INFO: Starting application...
✅ Database ready!
INFO: Uvicorn running on http://0.0.0.0:8000
```

## Manual Commands

If you prefer manual control, here are the `doctl` commands:

### List Your Apps
```bash
doctl apps list
```

### Get App Info
```bash
# Replace with your app ID
APP_ID="your-app-id"
doctl apps get $APP_ID
```

### View Recent Deployments
```bash
doctl apps list-deployments $APP_ID
```

### View Build Logs
```bash
# Get latest deployment ID
DEPLOYMENT_ID=$(doctl apps list-deployments $APP_ID --format ID --no-header | head -n 1)

# View build logs
doctl apps logs $APP_ID $DEPLOYMENT_ID --type build
```

### View Runtime Logs (Live)
```bash
# Follow runtime logs in real-time
doctl apps logs $APP_ID --type run --follow

# Last 100 lines
doctl apps logs $APP_ID --type run --tail 100
```

### Trigger Manual Deployment
```bash
doctl apps create-deployment $APP_ID
```

### Check Deployment Status
```bash
doctl apps get-deployment $APP_ID $DEPLOYMENT_ID
```

## Monitoring Options

### Option 1: Automated Monitor (Recommended)
```bash
./monitor-deployment.sh
```
- Auto-refreshes every 5 seconds
- Shows build progress
- Displays recent logs
- Colored output for easy reading

### Option 2: Follow Logs Manually
```bash
# Build logs (during deployment)
doctl apps logs $APP_ID --type build --follow

# Runtime logs (after deployment)
doctl apps logs $APP_ID --type run --follow
```

### Option 3: Digital Ocean Dashboard
Visit: https://cloud.digitalocean.com/apps
- Visual progress bars
- Full log history
- Deployment controls
- Metrics and analytics

## Troubleshooting

### Error: "doctl: command not found"
Install doctl:
```bash
# macOS
brew install doctl

# Linux
snap install doctl
```

### Error: "Not authenticated"
Run:
```bash
doctl auth init
```
Then enter your API token from: https://cloud.digitalocean.com/account/api/tokens

### Error: "App not found"
1. List your apps:
   ```bash
   doctl apps list
   ```
2. Update `APP_NAME` in `monitor-deployment.sh`:
   ```bash
   APP_NAME="your-actual-app-name"
   ```

### Can't see logs
Wait 10-30 seconds after deployment starts. Logs may be delayed.

## Advanced Usage

### Watch Specific Deployment
```bash
# Get deployment ID from DO dashboard or:
doctl apps list-deployments $APP_ID

# Monitor specific deployment
DEPLOYMENT_ID="abc123"
watch -n 2 "doctl apps get-deployment $APP_ID $DEPLOYMENT_ID --format Phase,Progress.SuccessSteps,Progress.TotalSteps"
```

### Export Logs to File
```bash
# Build logs
doctl apps logs $APP_ID $DEPLOYMENT_ID --type build > build-logs.txt

# Runtime logs
doctl apps logs $APP_ID --type run --tail 500 > runtime-logs.txt
```

### Monitor Multiple Apps
Edit `monitor-deployment.sh` and change:
```bash
APP_NAME="base10-backend"  # Change this
```

Or pass as environment variable:
```bash
APP_NAME="my-other-app" ./monitor-deployment.sh
```

## Integration with CI/CD

### GitHub Actions Notification
Add to `.github/workflows/notify-deployment.yml`:
```yaml
- name: Check Deployment
  run: |
    doctl auth init --access-token ${{ secrets.DO_TOKEN }}
    doctl apps logs ${{ secrets.APP_ID }} --type run --tail 50
```

## Keyboard Shortcuts

- **Ctrl+C** - Exit monitor
- **Ctrl+Z** - Pause (use `fg` to resume)

## What to Look For

### ✅ Success Indicators
```
Running database migrations...
INFO [alembic.runtime.migration] Running upgrade 20251216_merge_heads -> 2bf57f65397a
✅ Database ready!
INFO: Uvicorn running on http://0.0.0.0:8000
```

### ❌ Error Indicators
```
ERROR: Failed to build image
sqlalchemy.exc.ProgrammingError
ModuleNotFoundError: No module named 'X'
Port 8000 already in use
```

### ⚠️ Warning Indicators
```
⚠️ Redis unavailable
WARNING: Deprecated feature
```

## Quick Reference Card

| Task | Command |
|------|---------|
| Monitor deployment | `./monitor-deployment.sh` |
| Follow runtime logs | `doctl apps logs $APP_ID --type run --follow` |
| View last 100 logs | `doctl apps logs $APP_ID --type run --tail 100` |
| List deployments | `doctl apps list-deployments $APP_ID` |
| Trigger deployment | `doctl apps create-deployment $APP_ID` |
| Check app status | `doctl apps get $APP_ID` |

## Support

- **Digital Ocean Docs**: https://docs.digitalocean.com/products/app-platform/
- **doctl Reference**: https://docs.digitalocean.com/reference/doctl/
- **Community Forum**: https://www.digitalocean.com/community/
