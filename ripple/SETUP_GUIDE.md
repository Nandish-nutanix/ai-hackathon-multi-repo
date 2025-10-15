# RIPPLE Setup and Usage Guide

## 🌊 Overview

**RIPPLE** (Repository Impact Prediction & Propagation LLM Engine) is an agentic AI system that analyzes code changes across multiple repositories to predict and assess their impact using:

- **Real GitHub API Integration**: Fetch commits directly from GitHub
- **Code Dependency Scanning**: Analyze actual imports and dependencies
- **Call Graph Analysis**: Track method callers and impact propagation
- **Helper Method Detection**: Identify impacts of helper method changes
- **Dynamic Dependency Discovery**: Update dependency graph as new relations are found
- **AI-Powered Analysis**: Use Nutanix AI (pg-llama-33) for semantic understanding

---

## 📋 Prerequisites

1. **Python 3.8+** installed
2. **GitHub Personal Access Token** (classic token with `repo` scope)
3. **Access to Nutanix AI Platform** (NAI endpoint)
4. **Git** installed on your system

---

## 🚀 Installation

### Step 1: Navigate to RIPPLE Directory

```bash
cd /Users/raj.bundela/Desktop/Nutest/Iris/nutest-py3-tests/experimental/mahadev-agasar/ripple
```

### Step 2: Create Virtual Environment (Recommended)

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Dependencies include:**
- `requests>=2.31.0` - HTTP client
- `PyGithub>=2.1.1` - GitHub API wrapper
- `gitpython>=3.1.40` - Git operations
- `networkx>=3.2` - Graph algorithms
- `python-dotenv>=1.0.0` - Environment variables

---

## ⚙️ Configuration

### 1. GitHub Token (REQUIRED)

**IMPORTANT**: The GitHub token must be set as an environment variable for security.

```bash
# Set your GitHub token
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

**Never hardcode tokens in source code!** RIPPLE will automatically read from the environment variable.

#### Generate a GitHub Token

1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scope: `repo` (Full control of private repositories)
4. Copy the token and set it as an environment variable

### 2. NAI API Key (OPTIONAL)

For full LLM features, set the NAI API key:

```bash
export NAI_API_KEY="your_nai_api_key_here"
```

If not set, basic analysis will still work but LLM features will be limited.

### 2. Repositories

Four repositories are pre-configured in `config.py`:
1. **lcm-framework** - Core LCM framework
2. **ntnx-api-lcm** - LCM API layer
3. **lcm-networking** - Network management
4. **prism-ui-lcm-ui** - UI components

### 3. Analysis Configuration

Configure analysis behavior in `config.py`:
```python
ANALYSIS_CONFIG = {
    "days_to_analyze": 5,          # Default time range (override with --days)
    "max_commits_per_repo": 50,    # Maximum commits to analyze
    "max_tokens": 4096,            # LLM token limit
    "enable_code_scanning": True,  # Scan actual code for dependencies
    "enable_call_graph": True,     # Analyze method call graphs
}
```

---

## 📖 Usage

### Basic Usage

Analyze commits from the last 5 days (default):
```bash
python ripple.py --repos lcm-framework ntnx-api-lcm --days 5
```

### Advanced Usage

#### 1. Analyze Single Repository (7 days)
```bash
python ripple.py --repos lcm-framework --days 7
```

#### 2. Analyze All Repositories (2 days)
```bash
python ripple.py --repos lcm-framework ntnx-api-lcm lcm-networking prism-ui-lcm-ui --days 2
```

#### 3. Custom Output Files
```bash
python ripple.py --repos lcm-framework --days 5 \
  --output-html my_analysis.html \
  --output-json my_analysis.json
```

#### 4. Fast Mode (Disable Code Scanning)
```bash
python ripple.py --repos lcm-networking --days 3 --disable-code-scan
```

#### 5. Without Call Graph Analysis
```bash
python ripple.py --repos prism-ui-lcm-ui --days 2 --disable-call-graph
```

### Command-Line Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--repos` | List | Required | Repository names to analyze |
| `--days` | Integer | 5 | Number of days to analyze |
| `--output-html` | String | lcm_impact_report.html | HTML output file |
| `--output-json` | String | lcm_impact_report.json | JSON output file |
| `--disable-code-scan` | Flag | False | Disable code dependency scanning |
| `--disable-call-graph` | Flag | False | Disable call graph analysis |

---

## 🔍 What RIPPLE Analyzes

### 1. **Commit Collection**
- Fetches commits from GitHub for specified time range
- Filters by repository and branch
- Extracts file changes and diffs

### 2. **Dependency Discovery**
- **Static Analysis**: Infers from deployment layers (API → Core → UI)
- **Code Scanning**: Analyzes actual imports and dependencies
- **Dynamic Updates**: Updates graph when new dependencies found

### 3. **Impact Analysis**
- **Direct Impact**: Repositories that depend on changed code
- **Call Graph Impact**: Functions that call changed methods
- **Helper Method Detection**: Identifies all callers of helper methods
- **User Flow Impact**: Which user workflows are affected

### 4. **Test Generation**
- AI generates test case recommendations
- Prioritizes based on impact score
- Includes integration tests for helper methods
- Provides test coverage estimates

### 5. **Deployment Planning**
- Topological sort for safe deployment order
- Risk assessment (Critical/High/Medium/Low)
- Effort estimation in hours
- Specific countermeasures for each change

---

## 📊 Understanding the Output

### HTML Report

The HTML report (`lcm_impact_report.html`) includes:

1. **Executive Dashboard**
   - Total commits analyzed
   - Repositories affected
   - Risk distribution
   - Test coverage metrics

2. **Commit Analysis**
   - Each commit with detailed impact
   - Changed files and components
   - Affected repositories with scores
   - User flows impacted

3. **Helper Method Impacts**
   - List of changed helper methods
   - All callers identified
   - Impact level (High/Medium)
   - Recommended tests

4. **Test Recommendations**
   - Prioritized test cases
   - Test types (unit/integration)
   - Estimated duration
   - Code templates

5. **Deployment Plan**
   - Deployment order
   - Dependencies visualization
   - Risk warnings
   - Countermeasures

### JSON Report

The JSON report (`lcm_impact_report.json`) contains:
- Structured data for programmatic access
- All analysis metadata
- Impact scores and risk levels
- Test case details
- Deployment ordering

---

## 🛠️ Architecture

### Components

```
ripple/
├── ripple.py                      # Main entry point
├── config.py                      # Configuration
│
├── agents/                        # 🤖 AI Agents
│   └── impact_analysis_agent.py   # Core orchestrator
│
├── tools/                         # 🛠️ Intelligent Tools
│   ├── github_api_client.py       # GitHub REST API
│   ├── github_tools.py            # Git operations
│   ├── code_dependency_scanner.py # Code analysis
│   ├── call_graph_analyzer.py     # Call graph
│   ├── dependency_analyzer.py     # Dependencies
│   ├── impact_calculator.py       # Impact scoring
│   └── user_flow_analyzer.py      # User flows
│
├── models/                        # 📊 Data Models
│   ├── repository.py              # Repository info
│   ├── dependency.py              # Dependency graph
│   └── impact_report.py           # Report schema
│
└── utils/                         # 🔧 Utilities
    ├── llm_client.py              # NAI client
    ├── simple_html_reporter.py    # HTML generation
    └── dynamic_config_builder.py  # Config builder
```

### Analysis Flow

```
1. Initialize System
   ├── Load repositories from config
   ├── Check GitHub access
   └── Build dependency graph (with code scanning)

2. For Each Repository
   ├── Fetch commits from GitHub API
   ├── Clone/update local copy
   └── Analyze each commit

3. For Each Commit
   ├── Extract changed files
   ├── Build call graph
   ├── Analyze with LLM
   ├── Calculate impact scores
   ├── Identify helper method impacts
   ├── Generate test cases
   ├── Create countermeasures
   └── Generate recommendations

4. Generate Reports
   ├── Aggregate all analyses
   ├── Create HTML dashboard
   └── Save JSON data
```

---

## 🎯 Use Cases

### 1. Pre-Merge Analysis
Before merging a PR, analyze its impact:
```bash
# Analyze last 2 days (typical PR lifetime)
python ripple.py --repos lcm-framework --days 2
```

### 2. Release Planning
Understand impact of all changes in a release:
```bash
# Analyze last 14 days (typical sprint)
python ripple.py --repos lcm-framework ntnx-api-lcm lcm-networking --days 14
```

### 3. Helper Method Refactoring
After refactoring helper methods, identify all impacts:
```bash
# Enable call graph for detailed analysis
python ripple.py --repos lcm-framework --days 1
```

### 4. Cross-Repo Dependency Tracking
Monitor dependencies between repositories:
```bash
# Analyze all repos with code scanning
python ripple.py --repos lcm-framework ntnx-api-lcm lcm-networking prism-ui-lcm-ui --days 7
```

---

## 🐛 Troubleshooting

### Issue: "Invalid GitHub token"
**Solution**: Verify token has `repo` scope and is not expired
```bash
# Test token
curl -H "Authorization: token ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" \
  https://api.github.com/user
```

### Issue: "Repository not found"
**Solution**: Ensure you have access to the repository
```bash
# Check access
python -c "from tools.github_api_client import GitHubAPIClient; \
  client = GitHubAPIClient('YOUR_TOKEN'); \
  print(client.get_repository_info('nutanix-core', 'lcm-framework'))"
```

### Issue: "Rate limit exceeded"
**Solution**: GitHub API has rate limits (5000/hour for authenticated requests)
- Wait for rate limit reset
- Reduce number of repositories analyzed
- Use `--disable-code-scan` for faster analysis

### Issue: "LLM request failed"
**Solution**: Check NAI endpoint connectivity
```bash
# Verify NAI endpoint
curl -k https://10.35.30.155/api/v1/chat/completions
```

### Issue: "No commits found"
**Solution**: Adjust time range or check repository activity
```bash
# Increase time range
python ripple.py --repos lcm-framework --days 30
```

---

## 📈 Performance Tips

1. **Start Small**: Begin with 2-3 days, then expand
2. **Selective Repos**: Analyze related repos together
3. **Disable Features**: Use `--disable-code-scan` for speed
4. **Cached Clones**: Repositories are cached in `/tmp/`
5. **Parallel Analysis**: Run multiple RIPPLE instances for different repos

---

## 🔒 Security Notes

- GitHub token is stored in `config.py` (keep secure!)
- Use environment variables for production
- HTTPS verification can be disabled for NAI (dev environment)
- No sensitive data is logged

---

## 📞 Support

For issues or questions:
1. Check this guide
2. Review error messages
3. Check GitHub API status
4. Verify NAI endpoint connectivity

---

## 🎓 Example Workflow

```bash
# 1. Activate virtual environment
source .venv/bin/activate

# 2. Analyze recent changes
python ripple.py --repos lcm-framework ntnx-api-lcm --days 5

# 3. Review HTML report
open lcm_impact_report.html

# 4. Check high-risk changes
grep "high risk" lcm_impact_report.html

# 5. Review helper method impacts
grep "helper_method" lcm_impact_report.json

# 6. Plan deployment based on recommendations
```

---

**Happy Analyzing! 🌊**

