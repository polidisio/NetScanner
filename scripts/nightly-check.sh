#!/bin/bash
# ============================================
# OpenClaw Nightly Health Check
# Runs daily at 3:00 AM
# ============================================

DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M)
LOG_DIR="$HOME/.openclaw/workspace/logs"
MEMORY_DIR="$HOME/.openclaw/workspace/memory"
WORKSPACE="$HOME/.openclaw/workspace"
EMAIL_TO="jmaudisio@outlook.com"
UPDATES_AVAILABLE=false
OPENCLAW_UPDATE=false

# Create log directory
mkdir -p "$LOG_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_DIR/nightly-$DATE.log"
}

# Notify functions
send_resend_alert() {
    local subject="$1"
    local body="$2"
    
    curl -s -X POST "https://api.resend.com/emails" \
      -H "Authorization: Bearer e_BNZqQcAu_CXy8q5qscoZ8XcwoehfVdZfx" \
      -H "Content-Type: application/json" \
      -d @- <<EOF
{
  "from": "Aria Agent <aria.agent@saraiba.eu>",
  "to": ["aspontes@saraiba.eu"],
  "subject": "⚠️ $subject",
  "text": "$body"
}
EOF
}

notify_issue() {
    local issue="$1"
    local details="$2"
    
    MESSAGE="⚠️ OpenClaw Alert - $issue
    
Fecha: $DATE $TIME
Detalles: $details"
    
    # Send via Resend
    send_resend_alert "OpenClaw Alert - $issue" "$MESSAGE"
    
    # Log for now
    log "   🔔 ALERT: $issue - Email sent"
}

# Track issues
ISSUES=""

log "=========================================="
log "OpenClaw Nightly Health Check"
log "=========================================="

# ------------------------------------------
# 1. MEMORY CHECK & BACKUP
# ------------------------------------------
log "📝 Checking memory..."

# Check today's memory file exists
TODAY_FILE="$MEMORY_DIR/$DATE.md"
if [ -f "$TODAY_FILE" ]; then
    log "   ✅ Today's memory exists: $DATE.md"
else
    log "   ⚠️ Creating today's memory file"
    echo "# $DATE" > "$TODAY_FILE"
    echo "" >> "$TODAY_FILE"
    echo "## Daily Summary" >> "$TODAY_FILE"
    echo "- (pendiente)" >> "$TODAY_FILE"
fi

# Check yesterday's memory
YESTERDAY=$(date -v-1d +%Y-%m-%d)
YESTERDAY_FILE="$MEMORY_DIR/$YESTERDAY.md"
if [ -f "$YESTERDAY_FILE" ]; then
    log "   ✅ Yesterday's memory exists: $YESTERDAY.md"
else
    log "   ⚠️ Yesterday's memory missing: $YESTERDAY.md"
    notify_issue "Memory missing" "Yesterday's memory file not found: $YESTERDAY.md"
fi

# Backup memory to OneDrive
log "   💾 Backing up memory..."
if [ -d "$HOME/OneDrive/Documents" ]; then
    BACKUP_DIR="$HOME/OneDrive/Documents/OpenClaw-Backups"
    mkdir -p "$BACKUP_DIR"
    cp -r "$MEMORY_DIR"/*.md "$BACKUP_DIR/" 2>/dev/null
    log "   ✅ Memory backed up to OneDrive"
else
    log "   ⚠️ OneDrive not available for backup"
    notify_issue "OneDrive unavailable" "Cannot backup memory to OneDrive"
fi

# ------------------------------------------
# 2. SERVICES CHECK
# ------------------------------------------
log "🔧 Checking services..."

# Check Dashboard
if lsof -i :5007 >/dev/null 2>&1; then
    log "   ✅ Dashboard running on port 5007"
else
    log "   ⚠️ Dashboard not running on port 5007"
fi

# Check OpenClaw gateway
if openclaw gateway status >/dev/null 2>&1; then
    log "   ✅ OpenClaw gateway is active"
else
    log "   ⚠️ OpenClaw gateway may not be running"
fi

# Check Skills
SKILLS_DIR="$WORKSPACE/skills"
if [ -d "$SKILLS_DIR" ]; then
    SKILL_COUNT=$(find "$SKILLS_DIR" -maxdepth 1 -type d | wc -l | tr -d ' ')
    SKILL_COUNT=$((SKILL_COUNT - 1))
    log "   ✅ Skills directory exists ($SKILL_COUNT skills)"
else
    log "   ⚠️ Skills directory not found"
fi

# ------------------------------------------
# 3. MEMORY MAINTENANCE
# ------------------------------------------
log "🧠 Memory maintenance..."

# Update MEMORY.md if needed
MEMORY_FILE="$WORKSPACE/MEMORY.md"
if [ -f "$MEMORY_FILE" ]; then
    # Check if MEMORY.md was updated this week
    LAST_UPDATE=$(stat -f "%Sm" -t "%Y-%m-%d" "$MEMORY_FILE" 2>/dev/null || stat -c "%y" "$MEMORY_FILE" | cut -d' ' -f1)
    log "   📅 MEMORY.md last updated: $LAST_UPDATE"
else
    log "   ⚠️ MEMORY.md not found"
fi

# Clean old logs (keep last 30 days)
find "$LOG_DIR" -name "nightly-*.log" -mtime +30 -delete 2>/dev/null
log "   🗑️ Old logs cleaned (keeping 30 days)"

# ------------------------------------------
# 4. DISK & SYSTEM INFO
# ------------------------------------------
log "💻 System info..."

# Disk usage
DISK_USAGE=$(df -h ~ | tail -1 | awk '{print $5}' | tr -d '%')
log "   💾 Disk usage: ${DISK_USAGE}%"

# Memory usage
MEM_USAGE=$(vm_stat | head -4 | grep "Pages active" | awk '{print $3}' | tr -d '.')
log "   🧊 Memory active: ~$((MEM_USAGE * 4096 / 1024 / 1024)) MB"

# ------------------------------------------
# 6. OPENCLAW UPDATES CHECK
# ------------------------------------------
log "🔄 Checking OpenClaw updates..."

# Get current version
CURRENT_VERSION=$(openclaw --version 2>/dev/null | grep -oP '\d+\.\d+\.\d+' | head -1)
LATEST_VERSION=$(npm show openclaw version 2>/dev/null)

if [ -n "$LATEST_VERSION" ] && [ "$CURRENT_VERSION" != "$LATEST_VERSION" ]; then
    log "   ⚠️ OpenClaw update available!"
    log "      Current: $CURRENT_VERSION"
    log "      Latest: $LATEST_VERSION"
    notify_issue "OpenClaw Update Available" "Current: $CURRENT_VERSION | Latest: $LATEST_VERSION"
    OPENCLAW_UPDATE=true
else
    log "   ✅ OpenClaw up to date ($CURRENT_VERSION)"
    OPENCLAW_UPDATE=false
fi

# ------------------------------------------
# 7. SYSTEM UPDATES CHECK
# ------------------------------------------
log "🔄 Checking system updates..."

# Check for macOS updates
UPDATE_OUTPUT=$(softwareupdate -l 2>&1)
if echo "$UPDATE_OUTPUT" | grep -q "No new"; then
    log "   ✅ System up to date"
    UPDATES_AVAILABLE=false
else
    # Extract available updates
    UPDATES=$(echo "$UPDATE_OUTPUT" | grep -E "^\s+\*" | head -5)
    if [ -n "$UPDATES" ]; then
        log "   ⚠️ Updates available:"
        echo "$UPDATES" | while read update; do
            log "      $update"
        done
        notify_issue "System Updates Available" "Updates found: $UPDATES"
        UPDATES_AVAILABLE=true
    else
        log "   ✅ System up to date"
        UPDATES_AVAILABLE=false
    fi
fi

# ------------------------------------------
# 8. REMOTE MAC MONITOR (192.168.1.201)
# ------------------------------------------
log "🖥️ Monitoring remote Mac 192.168.1.201..."

REMOTE_KEY="$HOME/.ssh/id_rsa_remote"
REMOTE_HOST="192.168.1.201"
REMOTE_USER="clot"

REMOTE_CHECK=$(ssh -i "$REMOTE_KEY" -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$REMOTE_USER@$REMOTE_HOST" "echo ok" 2>/dev/null)

if [ "$REMOTE_CHECK" = "ok" ]; then
    log "   ✅ Remote Mac reachable"
    
    REMOTE_UPTIME=$(ssh -i "$REMOTE_KEY" -o ConnectTimeout=10 "$REMOTE_USER@$REMOTE_HOST" "uptime | cut -d',' -f1" 2>/dev/null)
    REMOTE_CPU=$(ssh -i "$REMOTE_KEY" -o ConnectTimeout=10 "$REMOTE_USER@$REMOTE_HOST" "top -l 1 -n 0 | grep 'CPU usage'" 2>/dev/null | cut -d',' -f1)
    REMOTE_DISK=$(ssh -i "$REMOTE_KEY" -o ConnectTimeout=10 "$REMOTE_USER@$REMOTE_HOST" "df -h / | tail -1" 2>/dev/null | awk '{print $5}')
    
    log "      Uptime: $REMOTE_UPTIME"
    log "      CPU: $REMOTE_CPU"
    log "      Disk: $REMOTE_DISK"
    
    # Alert if disk is low
    DISK_NUM=$(echo "$REMOTE_DISK" | tr -d '%')
    if [ "$DISK_NUM" -gt 85 ]; then
        notify_issue "Remote Mac Low Disk" "Disk usage: $REMOTE_DISK"
    fi
else
    log "   ❌ Cannot reach remote Mac"
    notify_issue "Remote Mac Offline" "Cannot connect to 192.168.1.201"
fi

# ------------------------------------------
# 9. SUMMARY & NOTIFICATIONS
# ------------------------------------------
log ""
log "=========================================="
log "✅ Nightly check complete"
log "=========================================="

# Send summary email if there were issues or updates
if [ "$UPDATES_AVAILABLE" = true ] || [ "$OPENCLAW_UPDATE" = true ]; then
    send_resend_alert "OpenClaw - Resumen + Actualizaciones" "Todo OK + Hay actualizaciones disponibles"
fi

# Check if there were any issues and send notifications
if [ -f "$LOG_DIR/alerts queue.txt" ]; then
    ALERT_MSG=$(cat "$LOG_DIR/alerts queue.txt")
    
    # Send Telegram notification via OpenClaw (would need webhook/bot)
    # For now, log the alert
    log "🔔 Sending alert..."
    
    # Clean up alert queue
    rm -f "$LOG_DIR/alerts queue.txt"
fi

exit 0
