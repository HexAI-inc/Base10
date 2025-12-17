# 🔍 Monitoring Scripts

Quick access to deployment and runtime monitoring tools.

## 🚀 Quick Commands

### Watch Deployment Build
```bash
./watch-deployment.sh
```
Monitors: Docker builds, migrations, deployment status

### Watch Live Application Logs  
```bash
./watch-logs.sh
```
Monitors: HTTP requests, errors, performance

## 📖 Full Documentation
See [MONITORING_GUIDE.md](./MONITORING_GUIDE.md) for complete setup and usage instructions.

## ⚙️ Setup (First Time Only)

1. **Install doctl:**
   ```bash
   # macOS
   brew install doctl
   
   # Linux
   snap install doctl
   ```

2. **Authenticate:**
   ```bash
   doctl auth init
   ```
   Get token from: https://cloud.digitalocean.com/account/api/tokens

## 🎨 Color Legend

- 🔴 **Red** - Errors, failures, exceptions
- 🟡 **Yellow** - Warnings, 4xx HTTP codes
- 🟢 **Green** - Success, 2xx HTTP codes
- 🔵 **Blue** - Info, starting processes
- 🔷 **Cyan** - Timestamps, headers

## 🆘 Troubleshooting

**Error: "doctl: command not found"**
```bash
brew install doctl  # macOS
snap install doctl  # Linux
```

**Error: "Not authenticated"**
```bash
doctl auth init
```

**Error: "App not found"**
Edit script and update `APP_NAME="base10-backend"` to match your app name.
