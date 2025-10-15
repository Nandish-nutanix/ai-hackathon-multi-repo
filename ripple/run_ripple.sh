#!/bin/bash

# RIPPLE Quick Run Script
# ========================
# This script provides a convenient way to run RIPPLE with proper environment setup

set -e  # Exit on error

echo "🌊 RIPPLE - Repository Impact Prediction & Propagation LLM Engine"
echo "=================================================================="
echo ""

# Check if GITHUB_TOKEN is set
if [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ Error: GITHUB_TOKEN environment variable is not set!"
    echo ""
    echo "Please set your GitHub token:"
    echo "  export GITHUB_TOKEN='your_token_here'"
    echo ""
    echo "Generate a token at: https://github.com/settings/tokens"
    echo "Required scope: repo"
    echo ""
    exit 1
fi

echo "✅ GITHUB_TOKEN is set"

# Check if NAI_API_KEY is set
if [ -z "$NAI_API_KEY" ]; then
    echo "⚠️  Warning: NAI_API_KEY not set (LLM features will be limited)"
else
    echo "✅ NAI_API_KEY is set"
fi

echo ""

# Parse arguments or use defaults
REPOS="${1:-lcm-framework ntnx-api-lcm}"
DAYS="${2:-5}"

echo "📊 Configuration:"
echo "   Repositories: $REPOS"
echo "   Time range: Last $DAYS days"
echo ""
echo "=================================================================="
echo ""

# Run RIPPLE
python3 ripple.py --repos $REPOS --days $DAYS

echo ""
echo "=================================================================="
echo "✅ Analysis complete!"
echo "   View report: open lcm_impact_report.html"
echo "=================================================================="

