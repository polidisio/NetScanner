#!/bin/bash
# ============================================
# Remote Mac Cleaner - Mole
# Target: 192.168.1.201
# ============================================

REMOTE_HOST="192.168.1.201"
REMOTE_USER="clot"
REMOTE_KEY="$HOME/.ssh/id_rsa_remote"
LOG_DIR="$HOME/.openclaw/workspace/logs"

mkdir -p "$LOG_DIR"
DATE=$(date +%Y-%m-%d)

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Function to run remote command
remote_exec() {
    ssh -i "$REMOTE_KEY" -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$REMOTE_USER@$REMOTE_HOST" "$1" 2>/dev/null
}

log "=========================================="
log "Remote Mac Cleaner - Mole"
log "=========================================="

# Check connection
if ! remote_exec "echo ok" > /dev/null 2>&1; then
    log "❌ Cannot connect to $REMOTE_HOST"
    exit 1
fi

# Get disk space BEFORE
BEFORE_DISK=$(remote_exec "df -h / | tail -1 | awk '{print \$5}'")
log "💾 Disk before: $BEFORE_DISK"

# Run Mole clean (dry-run first)
log "🧹 Running Mole clean (preview)..."
DRY_RUN=$(remote_exec "mo clean --dry-run 2>&1")
CLEAN_SIZE=$(echo "$DRY_RUN" | grep -oP '\d+\.\d+ [GM]B' | head -1)

if [ -n "$CLEAN_SIZE" ]; then
    log "   Can clean: $CLEAN_SIZE"
    
    # Run actual clean
    log "🧹 Running Mole clean (actual)..."
    CLEAN_RESULT=$(remote_exec "mo clean 2>&1" | tail -20)
    log "   Result: $CLEAN_RESULT"
    
    # Get disk space AFTER
    AFTER_DISK=$(remote_exec "df -h / | tail -1 | awk '{print \$5}'")
    log "💾 Disk after: $AFTER_DISK"
    
    log "✅ Cleanup complete: $CLEAN_SIZE freed"
else
    log "✅ System is clean, no cleanup needed"
fi

log "=========================================="
