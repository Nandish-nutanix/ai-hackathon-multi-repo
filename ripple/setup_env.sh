#!/bin/bash

# RIPPLE Environment Setup Script
# ================================
# This script helps you set up environment variables for RIPPLE

echo "🌊 RIPPLE Environment Setup"
echo "======================================"
echo ""

# Check if already configured
if [ ! -z "$GITHUB_TOKEN" ]; then
    echo "✅ GITHUB_TOKEN is already set"
else
    echo "⚠️  GITHUB_TOKEN is not set"
    echo ""
    echo "Please set your GitHub token:"
    echo "  export GITHUB_TOKEN='your_token_here'"
    echo ""
    echo "Generate a token at: https://github.com/settings/tokens"
    echo "Required scopes: repo (full control of private repositories)"
    echo ""
fi

if [ ! -z "$NAI_API_KEY" ]; then
    echo "✅ NAI_API_KEY is already set"
else
    echo "ℹ️  NAI_API_KEY is not set (optional, but recommended for full features)"
    echo ""
    echo "To enable LLM features:"
    echo "  export NAI_API_KEY='your_api_key_here'"
    echo ""
fi

echo ""
echo "======================================"
echo "Quick Setup Commands:"
echo "======================================"
echo ""
echo "# Set GitHub token:"
echo "export GITHUB_TOKEN='ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'"
echo ""
echo "# Set NAI API key (optional):"
echo "export NAI_API_KEY='your_nai_api_key_here'"
echo ""
echo "# Run RIPPLE:"
echo "python3 ripple.py --repos lcm-framework ntnx-api-lcm --days 2"
echo ""
echo "======================================"
echo ""
echo "💡 Tip: Add these export commands to your ~/.bashrc or ~/.zshrc"
echo "   to make them permanent."
echo ""

