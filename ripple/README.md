# 🌊 RIPPLE

## **R**epository **I**mpact **P**rediction & **P**ropagation **L**LM **E**ngine

<div align="center">

**An Agentic AI Solution for Cross-Repository Impact Analysis**

*Where AI Agents Predict the Impact of Every Code Change*

[![Nutanix AI](https://img.shields.io/badge/Powered%20by-Nutanix%20AI-blue)](https://nutanix.com)
[![Agentic AI](https://img.shields.io/badge/Architecture-Agentic%20AI-green)](https://github.com)
[![LLM](https://img.shields.io/badge/LLM-pg--llama--33-orange)](https://github.com)

</div>

---

## 🎯 What is RIPPLE?

RIPPLE is an **agentic AI system** that autonomously analyzes code changes across multiple repositories to predict and assess their impact. Using autonomous AI agents that combine intelligent tools with large language models, RIPPLE identifies breaking changes, generates test cases, and provides actionable recommendations—all without human intervention.

### 🤖 Agentic AI Architecture

Following the **Agentic AI Pattern**:

```
Autonomous AI Agents = Intelligent Tools + LLM + Autonomous Decision-Making
```

Unlike traditional automation, RIPPLE's agents:
- 🧠 **Think autonomously** - Make intelligent decisions based on context
- 🔄 **Adapt dynamically** - Adjust analysis strategies based on code patterns
- 🎯 **Act with purpose** - Generate actionable insights and recommendations
- 🤝 **Collaborate intelligently** - Multiple agents work together seamlessly

### 🛠️ Intelligent Tools

RIPPLE's autonomous agents leverage these intelligent tools:

- 🔧 **GitHub Integration** - Clone repos, extract commits, analyze diffs
- 📊 **Dependency Analyzer** - Build cross-repo dependency graphs  
- 🔍 **Code Analyzer** - Detect breaking changes, API modifications
- 📈 **Impact Calculator** - Calculate risk scores and effort estimates
- 🔄 **User Flow Analyzer** - Track impacts through user journeys
- 🚀 **Deployment Planner** - Determine optimal deployment sequences

### 🧠 AI Agent Capabilities

Powered by **Nutanix AI (pg-llama-33)**, RIPPLE agents provide:

- 🤖 **Semantic Code Understanding** - Deep comprehension of code intent
- 🧪 **Autonomous Test Generation** - Create comprehensive test suites
- 💡 **Intelligent Recommendations** - Context-aware guidance
- 🎯 **Risk Assessment** - Predict potential breaking changes
- 📋 **Impact Propagation** - Track cascading effects across repositories

## 🎯 Features

- ✅ **Automated Change Detection**: Monitor commits across repositories
- 📊 **Dependency Graph Analysis**: Build and analyze cross-repo dependencies
- 🎯 **Impact Scoring**: Calculate risk scores for affected components
- 🧪 **Test Case Generation**: AI-powered test case creation
- 📋 **Deployment Planning**: Optimal deployment order based on dependencies
- 📈 **Beautiful HTML Reports**: Comprehensive visual reports
- 🔍 **Limited Token Usage**: Efficient with `max_tokens=512`

## 🚀 Quick Start

### 1. Installation

```bash
cd NAI_agent_workshop/multi_repo_impact_analysis
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configuration

**IMPORTANT: Set environment variables for security**

```bash
# Required: GitHub Personal Access Token
export GITHUB_TOKEN="your_github_token_here"

# Optional: Nutanix AI API Key (for full LLM features)
export NAI_API_KEY="your_nai_api_key_here"
```

Generate GitHub token at: https://github.com/settings/tokens (needs `repo` scope)

### 3. Run RIPPLE

Analyze the last 5 days of commits:
```bash
python ripple.py --repos lcm-framework ntnx-api-lcm --days 5
```

**That's it!** RIPPLE's autonomous agents will:
1. 🔍 Analyze commits across repositories
2. 🧠 Understand code changes semantically  
3. 📊 Calculate cross-repository impacts
4. 🧪 Generate test cases automatically
5. 📋 Create deployment recommendations
6. 📈 Produce comprehensive HTML reports

## 📊 Example Output

```
======================================================================
🌊 RIPPLE - Repository Impact Prediction & Propagation LLM Engine
   Powered by Agentic AI (Autonomous Agents = Tools + LLM)
   Nutanix AI Platform
======================================================================

📊 LLM Model: pg-llama-33
🔗 Endpoint: https://10.35.30.155/api/v1/chat/completions
🎯 Max Tokens per Request: 512

📦 Repositories: 2
   • lcm-framework: https://github.com/nutanix-core/lcm-framework
   • lcm-release-modules: https://github.com/nutanix-core/lcm-release-modules

🔧 Building dependency graph...
✅ Graph built: 2 repos, 1 dependencies

======================================================================
📂 Analyzing: lcm-framework
⏰ Time range: Last 15 days
======================================================================

📥 Cloning/updating to: /tmp/lcm-framework
✅ Found 23 commits, analyzing top 10

──────────────────────────────────────────────────────────────────────
📝 Commit 1/10: abc123de
   Update API endpoints for version 2.0...
──────────────────────────────────────────────────────────────────────
   📊 Impact: 1 repos affected
      • lcm-release-modules: high risk (0.75)
   🧪 Tests: 4 generated
   ⏱  Effort: 8.5h

...

======================================================================
✅ Analysis Complete!
======================================================================

📊 Summary:
   • Analyzed commits: 15
   • LLM Model: pg-llama-33
   • HTML report: lcm_impact_report.html
   • JSON report: lcm_impact_report.json

📈 Impact Analysis:
   • Total affected repos: 8
   • Total tests generated: 30
   • High/Critical risks: 3
```

## 📁 Project Structure

```
RIPPLE/
├── ripple.py                        # 🌊 Main entry point
├── config.py                        # ⚙️  Configuration
├── requirements.txt                 # 📦 Dependencies
├── README.md                        # 📖 Documentation
│
├── agents/                          # 🤖 Autonomous AI Agents
│   └── impact_analysis_agent.py    #    Core agentic AI orchestrator
│
├── tools/                           # 🛠️ Intelligent Tools
│   ├── github_tools.py              #    GitHub integration
│   ├── dependency_analyzer.py       #    Dependency graph builder
│   ├── code_analyzer.py             #    Code change detector
│   ├── impact_calculator.py         #    Impact & risk scorer
│   └── user_flow_analyzer.py        #    User journey tracker
│
├── models/                          # 📊 Data Models
│   ├── repository.py                #    Repository structures
│   ├── dependency.py                #    Dependency graphs
│   └── impact_report.py             #    Report schemas
│
└── utils/                           # 🔧 Utilities
    ├── llm_client.py                #    NAI LLM client
    ├── html_reporter.py             #    Report generators
    └── dynamic_config_builder.py    #    Dynamic configuration
```

## 🔧 Configuration

Edit `config.py` to customize:

```python
# Analysis Configuration
ANALYSIS_CONFIG = {
    "max_depth": 3,                  # Dependency traversal depth
    "risk_threshold": 0.7,           # Minimum risk score to flag
    "days_to_analyze": 15,           # Time range
    "max_commits_per_repo": 10,      # Limit commits per repo
    "max_tokens": 512,               # LLM token limit (efficient!)
}
```

## 🎨 HTML Report Features

The generated HTML report includes:

- 📊 **Executive Dashboard**: Summary statistics at a glance
- 🎯 **Impact Analysis**: Visual risk levels and scores
- 🧪 **Test Cases**: Prioritized test recommendations
- 🚀 **Deployment Plan**: Ordered deployment sequence
- 💡 **Recommendations**: AI-generated insights
- ⚠️ **Warnings**: Critical issues highlighted

## 🔍 How RIPPLE Works

### Agentic AI Flow (Autonomous Agents = Tools + LLM + Decision-Making)

RIPPLE's autonomous agents operate in an intelligent, self-directed manner:

1. **🔍 Discovery Phase** (Agent → Tools)
   - Agent identifies repositories to analyze
   - Extracts commits and code changes from GitHub
   - Builds dependency graphs automatically

2. **🧠 Analysis Phase** (Agent → LLM + Tools)
   - Agent sends code to LLM for semantic understanding
   - Identifies breaking changes, API modifications
   - Calculates impact scores across dependency graph
   - Detects affected user flows and journeys

3. **🧪 Generation Phase** (Agent → LLM)
   - Agent autonomously generates comprehensive test cases
   - Creates prioritized testing strategies
   - Designs validation scenarios

4. **📋 Planning Phase** (Agent → Tools + LLM)
   - Agent determines optimal deployment sequences
   - Generates intelligent recommendations
   - Produces actionable warnings and insights

5. **📈 Reporting Phase** (Agent → Tools)
   - Agent compiles all findings
   - Generates beautiful, interactive HTML reports
   - Saves structured JSON data for further processing

### 🎯 What Makes It "Agentic"?

Unlike traditional automation scripts, RIPPLE's agents:

- **Make autonomous decisions** about what to analyze and how deeply
- **Adapt their strategy** based on code complexity and patterns
- **Learn from context** to provide more accurate predictions
- **Collaborate intelligently** across multiple tools and data sources
- **Generate novel insights** beyond pre-programmed rules

### Tool Definitions

The system exposes these tools to the LLM:

- `analyze_code_changes`: Identify modified components
- `calculate_impact_score`: Compute cross-repo impact

## 📈 Use Cases

1. **Pre-Deployment Analysis**: Understand impact before merging
2. **Risk Assessment**: Identify high-risk changes
3. **Test Planning**: Generate comprehensive test suites
4. **Deployment Orchestration**: Determine safe deployment order
5. **Documentation**: Automatic change impact documentation

## 🛠️ Advanced Usage

### Custom Repository Configuration

Add repositories in `config.py`:

```python
NUTANIX_REPOSITORIES = [
    {
        "name": "your-repo",
        "url": "https://github.com/your-org/your-repo",
        "language": "Python",
        "components": ["component1", "component2"]
    },
]
```

### Use RIPPLE as a Library

Integrate RIPPLE's agentic AI into your own applications:

```python
from agents.impact_analysis_agent import ImpactAnalysisAgent
from config import NUTANIX_REPOSITORIES

# Initialize the autonomous agent
agent = ImpactAnalysisAgent(config)
agent.initialize_dependency_graph(NUTANIX_REPOSITORIES)

# Let the agent analyze autonomously
report = agent.analyze_change_impact(repo, commit, path)

# Access agent's findings
print(f"Agent found {len(report.affected_repositories)} impacted repos")
print(f"Agent generated {len(report.generated_tests)} test cases")
```

## 🧪 Testing RIPPLE

Run RIPPLE on test repositories:

```bash
# Quick test on a single repository
python ripple.py --repos lcm-framework --days 7

# Test with multiple repositories
python ripple.py --repos lcm-framework lcm-release-modules --days 15

# Full 60-day analysis
python ripple.py --repos lcm-framework --days 60
```

## 📝 LLM Model Information

**Model**: `pg-llama-33`  
**Endpoint**: Nutanix AI Platform  
**Max Tokens**: 512 (optimized for efficiency)  
**Temperature**: 0.01-0.2 (focused, deterministic outputs)

The system is designed to minimize token usage while maximizing insight quality.

## 🔒 Security

- GitHub tokens are read from environment variables
- HTTPS verification can be configured
- No sensitive data is logged

## 🌊 Why "RIPPLE"?

Just like a ripple in water, code changes propagate through interconnected systems. RIPPLE's agentic AI:

- 🌊 **Tracks the ripple effect** of every code change
- 🔮 **Predicts where impacts will propagate** before they happen  
- 🎯 **Prevents unexpected breakages** in downstream systems
- 🤖 **Does it all autonomously** using intelligent AI agents

## 🤝 Contributing

RIPPLE demonstrates cutting-edge agentic AI concepts:
- 🤖 Autonomous AI agent architecture
- 🛠️ Intelligent tool orchestration  
- 🧠 LLM-powered decision making
- 📊 Multi-repository dependency analysis
- 🧪 Autonomous test generation
- 🎯 Intelligent risk assessment

## 📄 License

Internal use - Nutanix AI Workshop

## 👥 Authors

**Nutanix AI Team**  
*Building the Future of Agentic AI for Enterprise Software*

---

<div align="center">

**🌊 Built with ❤️ using Nutanix AI Platform (pg-llama-33)**

*RIPPLE: Where Agentic AI Meets Repository Intelligence*

**Autonomous Agents = Intelligent Tools + LLM + Decision-Making**

</div>

