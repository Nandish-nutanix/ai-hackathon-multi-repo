"""
RIPPLE Configuration
═══════════════════════════════════════════════════════════════════
Repository Impact Prediction & Propagation LLM Engine

An Agentic AI Solution for Cross-Repository Impact Analysis
Powered by Autonomous AI Agents + Intelligent Tools
"""
import os
from typing import List, Dict

# NAI LLM Configuration
# IMPORTANT: Set NAI_API_KEY environment variable before running
NAI_ENDPOINT_API_KEY = os.getenv("NAI_API_KEY")
NAI_LLM_ENDPOINT_URL = os.getenv("NAI_LLM_ENDPOINT_URL", "https://10.35.30.155/api/v1/chat/completions")
NAI_LLM_ENDPOINT_NAME = os.getenv("NAI_LLM_MODEL", "pg-llama-33")

# GitHub Configuration
# IMPORTANT: Set GITHUB_TOKEN environment variable before running
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME", "raj.bundela")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# Validate required environment variables
if not GITHUB_TOKEN:
    raise EnvironmentError(
        "GITHUB_TOKEN environment variable is required!\n"
        "Please set it using: export GITHUB_TOKEN='your_token_here'"
    )

if not NAI_ENDPOINT_API_KEY:
    print("⚠️  Warning: NAI_API_KEY not set. LLM features will be limited.")
    print("   To enable full features: export NAI_API_KEY='your_api_key_here'\n")

# Nutanix LCM Ecosystem Repositories
NUTANIX_REPOSITORIES = [
    {
        "name": "lcm-framework",
        "url": "https://github.com/nutanix-core/lcm-framework",
        "language": "Python",
        "components": ["core", "api", "inventory", "upgrade_engine"],
        "deployment_layer": "core",
        "user_facing": True,
        "ui_endpoints": ["/lcm/api/v1/inventory", "/lcm/api/v1/upgrade"],
        "operations": ["inventory_scan", "upgrade_initiate", "upgrade_status", "module_discovery"]
    },
    {
        "name": "ntnx-api-lcm",
        "url": "https://github.com/nutanix-core/ntnx-api-lcm",
        "language": "Python",
        "components": ["api_gateway", "rest_handlers", "authentication"],
        "deployment_layer": "api",
        "user_facing": True,
        "ui_endpoints": ["/api/lcm/v1/", "/api/lcm/v2/"],
        "operations": ["api_request", "auth_verify", "endpoint_routing"]
    },
    {
        "name": "lcm-networking",
        "url": "https://github.com/nutanix-core/lcm-networking",
        "language": "Python",
        "components": ["network_manager", "connectivity", "proxy"],
        "deployment_layer": "core",
        "user_facing": False,
        "ui_endpoints": [],
        "operations": ["network_check", "proxy_config", "connectivity_test"]
    },
    {
        "name": "prism-ui-lcm-ui",
        "url": "https://github.com/nutanix-core/prism-ui-lcm-ui",
        "language": "JavaScript",
        "components": ["ui_components", "lcm_dashboard", "upgrade_wizard"],
        "deployment_layer": "ui",
        "user_facing": True,
        "ui_endpoints": ["/console/#/page/lcm", "/console/#/page/lcm/upgrade"],
        "operations": ["display_inventory", "trigger_upgrade", "show_status"]
    },
]

# Note: USER_FLOWS and DEPLOYMENT_CONFIG are now dynamically generated
# based on the repositories provided at runtime.
# See utils/dynamic_config_builder.py for the implementation.

# Analysis Configuration
ANALYSIS_CONFIG = {
    "max_depth": 3,
    "risk_threshold": 0.7,
    "include_indirect": True,
    "test_coverage_target": 0.85,
    "days_to_analyze": 5,  # Default: 5 days (configurable via CLI)
    "max_commits_per_repo": 50,  # Maximum commits per repository
    "max_tokens": 4096,  # Enhanced for detailed analysis
    "enable_code_scanning": True,  # Enable real code dependency scanning
    "enable_call_graph": True,  # Enable method call graph analysis
}

# Tool Definitions for LLM
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "analyze_code_changes",
            "description": "Analyze code changes in a commit to identify modified functions, classes, and APIs.",
            "parameters": {
                "type": "object",
                "properties": {
                    "repository": {"type": "string", "description": "Repository name"},
                    "commit_hash": {"type": "string", "description": "Git commit hash"},
                    "file_paths": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["repository", "commit_hash"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_impact_score",
            "description": "Calculate the impact score of a change on dependent repositories.",
            "parameters": {
                "type": "object",
                "properties": {
                    "source_repo": {"type": "string"},
                    "changed_components": {"type": "array", "items": {"type": "string"}},
                    "change_type": {"type": "string", "enum": ["breaking", "enhancement", "bugfix", "refactor"]}
                },
                "required": ["source_repo", "changed_components", "change_type"]
            }
        }
    }
]

