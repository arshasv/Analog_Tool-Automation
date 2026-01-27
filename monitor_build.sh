#!/bin/bash
# ============================================================================
# Docker Build Monitor Script
# Monitors the ongoing Docker build process
# ============================================================================

echo "╔════════════════════════════════════════════════════╗"
echo "║  Docker Build Monitor - Sky130 EDA Platform       ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""

# Check if build is running
if docker compose -f /home/user/analog-eda/docker/docker-compose.yml ps | grep -q "building"; then
    echo "✅ Build is in progress"
else
    echo "⚠️  No active build detected"
fi

echo ""
echo "📊 Current Docker Status:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Show docker images
echo ""
echo "Images:"
docker images | grep -E "sky130|ubuntu|REPOSITORY" || echo "No images yet"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💡 Monitoring Options:"
echo ""
echo "  1. Watch build logs:"
echo "     docker compose -f /home/user/analog-eda/docker/docker-compose.yml logs -f"
echo ""
echo "  2. Check disk usage:"
echo "     df -h | grep -E 'Filesystem|/dev/'"
echo ""
echo "  3. Check memory usage:"
echo "     free -h"
echo ""
echo "  4. View Docker stats:"
echo "     docker stats"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "⏰ Expected build time: 30-60 minutes"
echo "📚 See BUILD_GUIDE.md for detailed progress info"
echo ""
