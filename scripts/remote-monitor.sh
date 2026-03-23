#!/bin/bash
# ============================================
# Remote Mac Monitor Script
# Target: 192.168.1.201 (Mac de Jose)
# ============================================

REMOTE_HOST="192.168.1.201"
REMOTE_USER="clot"
REMOTE_KEY="$HOME/.ssh/id_rsa_remote"
LOG_DIR="$HOME/.openclaw/workspace/logs"
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M)

mkdir -p "$LOG_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log "=========================================="
log "Remote Mac Monitor - $REMOTE_HOST"
log "=========================================="

# Function to run remote command
remote_exec() {
    ssh -i "$REMOTE_KEY" -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$REMOTE_USER@$REMOTE_HOST" "$1" 2>/dev/null
}

# Check if remote is reachable
if ! remote_exec "echo ok" > /dev/null 2>&1; then
    log "❌ Cannot connect to $REMOTE_HOST"
    exit 1
fi

log "✅ Connected to $REMOTE_HOST"

# System Info
log "📊 System Information:"
REMOTE_HOSTNAME=$(remote_exec "hostname")
log "   Hostname: $REMOTE_HOSTNAME"

REMOTE_UPTIME=$(remote_exec "uptime")
log "   Uptime: $REMOTE_UPTIME"

# CPU Usage
log "💻 CPU:"
remote_exec "top -l 1 -n 0 | grep 'CPU usage'" | while read line; do
    log "   $line"
done

# Memory
log "🧠 Memory:"
remote_exec "vm_stat" | while read line; do
    log "   $line"
done

# Disk Usage
log "💾 Disk:"
remote_exec "df -h /" | tail -1 | while read line; do
    log "   $line"
done

# Top Processes
log "🔝 Top 5 Processes:"
remote_exec "ps aux --sort=-%cpu | head -6" | tail -5 | while read line; do
    log "   $line"
done

log "=========================================="
log "Monitor complete"
log "=========================================="
