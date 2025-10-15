# RIPPLE Technical Architecture

## 🏗️ System Design Overview

RIPPLE follows the **Agentic AI** architecture pattern:

```
Autonomous AI Agent = Intelligent Tools + LLM + Decision-Making
```

This document details the technical implementation and SOLID principles applied.

---

## 🎯 Core Architecture

### 1. Agentic AI Pattern

```python
┌─────────────────────────────────────────────────────────┐
│              RIPPLE Agentic AI System                   │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │         ImpactAnalysisAgent                     │    │
│  │         (Autonomous Orchestrator)               │    │
│  └─────────────┬──────────────────────────────────┘    │
│                │                                         │
│       ┌────────┴────────┐                              │
│       │                 │                               │
│   ┌───▼────┐      ┌────▼─────┐                        │
│   │ Tools  │      │   LLM    │                         │
│   └───┬────┘      └────┬─────┘                         │
│       │                │                                │
│  ┌────▼────────────────▼─────┐                         │
│  │  Autonomous Decisions      │                         │
│  │  - Impact Analysis         │                         │
│  │  - Test Generation         │                         │
│  │  - Recommendations         │                         │
│  └────────────────────────────┘                         │
└─────────────────────────────────────────────────────────┘
```

---

## 🧩 Components

### 1. **Agents Layer** (`agents/`)

#### `ImpactAnalysisAgent`
- **Responsibility**: Orchestrate entire analysis workflow
- **SOLID Principles**:
  - **Single Responsibility**: Only manages analysis orchestration
  - **Dependency Inversion**: Depends on tool abstractions, not implementations

**Key Methods**:
```python
def initialize_dependency_graph(repositories, repo_paths):
    """Build dependency graph with optional code scanning"""
    
def analyze_change_impact(repository, commit_hash, repo_path):
    """8-step analysis process with call graph"""
```

**Enhanced Flow**:
1. Extract commit details (GitHub API)
2. Build call graph for changed code
3. Analyze changes semantically (LLM)
4. Calculate impacts with call graph data
5. Identify helper method impacts
6. Generate test cases with AI
7. Determine deployment order
8. Generate recommendations + countermeasures

---

### 2. **Tools Layer** (`tools/`)

All tools follow **Single Responsibility Principle**.

#### `GitHubAPIClient`
- **Purpose**: GitHub REST API interactions
- **Features**:
  - Rate limit handling
  - Automatic retry logic
  - Branch fallback (master → main)
  - Commit fetching with pagination

```python
class GitHubAPIClient:
    def get_recent_commits(owner, repo, since, until, branch):
        """Fetch commits with automatic pagination"""
    
    def get_commit_details(owner, repo, sha):
        """Get detailed commit info including file changes"""
```

#### `CodeDependencyScanner`
- **Purpose**: Analyze actual code for dependencies
- **Features**:
  - Multi-language support (Python, JavaScript/TypeScript)
  - Import detection
  - Function definition extraction
  - Call graph building

**Architecture**:
```python
class LanguageParser(Protocol):
    """Interface for language-specific parsers"""
    def parse_imports(file_path, content) -> List[str]
    def parse_functions(file_path, content) -> List[Dict]
    def parse_function_calls(file_path, content) -> List[str]

class PythonParser(LanguageParser):
    """AST-based Python parser"""

class JavaScriptParser(LanguageParser):
    """Regex-based JavaScript/TypeScript parser"""
```

**SOLID**: Open/Closed - Easy to add new language parsers without modifying existing code.

#### `CallGraphAnalyzer`
- **Purpose**: Analyze method call graphs and detect impacts
- **Features**:
  - Function/method extraction
  - Helper function detection
  - Call relationship mapping
  - Impact propagation calculation

**Key Classes**:
```python
@dataclass
class FunctionNode:
    """Immutable function representation"""
    name: str
    file_path: str
    line_number: int
    class_name: Optional[str]
    is_helper: bool
    complexity: int

class CallGraphAnalyzer:
    def find_impacted_functions(changed_functions, max_depth=3):
        """BFS traversal to find all impacted functions"""
    
    def identify_helper_method_impacts(changed_files):
        """Specific analysis for helper methods"""
```

**Helper Detection Heuristics**:
- Name starts with `_` (private)
- Contains keywords: helper, util, internal, validate, parse
- Short functions (< 10 lines, < 3 params)

#### `DependencyAnalyzer`
- **Purpose**: Build and maintain dependency graphs
- **Strategies** (in order of preference):
  1. **Code Scanning**: Analyze actual imports
  2. **Deployment Config**: Use explicit configuration
  3. **Metadata Inference**: Infer from deployment layers

```python
class DependencyAnalyzer:
    def build_dependency_matrix(repositories, repo_paths):
        """Three-strategy dependency discovery"""
    
    def update_dependency_graph(new_dependency):
        """Dynamically add new dependencies"""
```

**Dynamic Updates**:
```python
# When new dependency found
analyzer.update_dependency_graph(('repo-a', 'repo-b'))
```

#### `ImpactCalculator`
- **Purpose**: Calculate impact scores with call graph data
- **Enhanced Features**:
  - Call graph integration
  - Helper method consideration
  - Effort estimation with function counts

```python
class ImpactCalculator:
    def build_call_graph(repo_name, repo_path, changed_files):
        """Build call graph for repository"""
    
    def calculate_repo_impact(source_repo, changed_components, 
                             change_type, changed_files):
        """Enhanced with call graph analysis"""
    
    def get_helper_method_impacts(repo_name, changed_files):
        """Specific helper method impact analysis"""
    
    def generate_countermeasures(repo_name, changed_files):
        """Generate specific test recommendations"""
```

**Risk Calculation**:
```python
risk_level = calculate_risk_level(
    impact_score=0.75,
    is_breaking=False,
    helper_method_changed=True  # Increases risk
)
# Result: "high" (helper methods are risky)
```

---

### 3. **Models Layer** (`models/`)

Data classes following **Immutable Data Pattern**.

#### `ImpactReport`
```python
@dataclass
class ImpactReport:
    analysis_id: str
    timestamp: datetime
    source_repository: str
    source_commit: str
    change_summary: str
    changed_files: List[str]
    affected_repositories: List[str]
    impact_scores: List[ImpactScore]
    generated_tests: List[TestCase]
    deployment_order: List[str]
    recommendations: List[str]
    warnings: List[str]
    user_impacting: bool
    total_user_flows_affected: int
```

#### `UserFlowImpact`
```python
@dataclass
class UserFlowImpact:
    flow_id: str
    flow_name: str
    impacted_steps: List[Dict]
    test_steps: List[Dict]
    failure_scenarios: List[Dict]
    severity: str
    api_endpoints: List[str]
```

---

### 4. **Utils Layer** (`utils/`)

#### `NAIClient`
- **Purpose**: Nutanix AI LLM client
- **Features**:
  - Chat completion API
  - Tool call support
  - Error handling

```python
class NAIClient:
    def chat_completion(messages, tools, temperature, max_tokens):
        """Call NAI LLM with tool support"""
    
    def extract_tool_calls(response):
        """Extract tool calls from LLM response"""
```

---

## 🔄 Data Flow

### Complete Analysis Pipeline

```
┌─────────────────┐
│ User Command    │
│ --repos X --days Y │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│ 1. INITIALIZATION                       │
│ - Check GitHub access                   │
│ - Clone repositories                    │
│ - Scan code for dependencies            │
│ - Build dependency graph                │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│ 2. COMMIT COLLECTION (per repo)         │
│ - GitHub API: fetch commits             │
│ - Filter by time range                  │
│ - Get commit details                    │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│ 3. COMMIT ANALYSIS (per commit)         │
│ ┌─────────────────────────────────┐    │
│ │ 3a. Extract Changes             │    │
│ │ - Changed files                 │    │
│ │ - Diffs and metadata            │    │
│ └─────────┬───────────────────────┘    │
│           ▼                             │
│ ┌─────────────────────────────────┐    │
│ │ 3b. Build Call Graph            │    │
│ │ - Parse changed files           │    │
│ │ - Extract functions             │    │
│ │ - Map call relationships        │    │
│ └─────────┬───────────────────────┘    │
│           ▼                             │
│ ┌─────────────────────────────────┐    │
│ │ 3c. LLM Analysis                │    │
│ │ - Semantic understanding        │    │
│ │ - Change type classification    │    │
│ └─────────┬───────────────────────┘    │
│           ▼                             │
│ ┌─────────────────────────────────┐    │
│ │ 3d. Impact Calculation          │    │
│ │ - Traverse dependency graph     │    │
│ │ - Calculate scores              │    │
│ │ - Include call graph data       │    │
│ └─────────┬───────────────────────┘    │
│           ▼                             │
│ ┌─────────────────────────────────┐    │
│ │ 3e. Helper Method Detection     │    │
│ │ - Identify helper functions     │    │
│ │ - Find all callers              │    │
│ │ - Calculate impact              │    │
│ └─────────┬───────────────────────┘    │
│           ▼                             │
│ ┌─────────────────────────────────┐    │
│ │ 3f. Test Generation             │    │
│ │ - LLM generates tests           │    │
│ │ - Add helper method tests       │    │
│ │ - Prioritize by impact          │    │
│ └─────────┬───────────────────────┘    │
│           ▼                             │
│ ┌─────────────────────────────────┐    │
│ │ 3g. Deployment Planning         │    │
│ │ - Topological sort              │    │
│ │ - Risk assessment               │    │
│ └─────────┬───────────────────────┘    │
│           ▼                             │
│ ┌─────────────────────────────────┐    │
│ │ 3h. Recommendations             │    │
│ │ - Generate countermeasures      │    │
│ │ - Create warnings               │    │
│ │ - Provide recommendations       │    │
│ └─────────┬───────────────────────┘    │
└───────────┼─────────────────────────────┘
            ▼
┌─────────────────────────────────────────┐
│ 4. REPORT GENERATION                    │
│ - Aggregate all analyses                │
│ - Create HTML dashboard                 │
│ - Save JSON data                        │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│ Output Files    │
│ - HTML Report   │
│ - JSON Report   │
└─────────────────┘
```

---

## 🧠 AI/LLM Integration

### LLM Usage Points

1. **Code Change Analysis**
   ```python
   messages = [
       {"role": "system", "content": "You are an expert analyzing code changes..."},
       {"role": "user", "content": f"Repository: {repo}\nChanges: {changes}"}
   ]
   response = llm_client.chat_completion(messages, tools, temperature=0.1)
   ```

2. **Test Generation**
   ```python
   messages = [
       {"role": "system", "content": "You are a test engineer..."},
       {"role": "user", "content": f"Generate tests for: {affected_repos}"}
   ]
   response = llm_client.chat_completion(messages, temperature=0.2)
   ```

### Tool Definitions for LLM

```python
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "analyze_code_changes",
            "description": "Analyze code changes to identify modified functions and APIs",
            "parameters": {...}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_impact_score",
            "description": "Calculate impact score on dependent repositories",
            "parameters": {...}
        }
    }
]
```

---

## 🔐 SOLID Principles Applied

### Single Responsibility Principle (SRP)

Each class has ONE clear purpose:
- `GitHubAPIClient`: Only GitHub API communication
- `CodeDependencyScanner`: Only code analysis
- `CallGraphAnalyzer`: Only call graph operations
- `ImpactCalculator`: Only impact scoring

### Open/Closed Principle (OCP)

System is open for extension, closed for modification:

```python
# Adding a new language parser doesn't modify existing code
class RustParser(LanguageParser):
    def parse_imports(self, file_path, content):
        # Rust-specific logic
        pass

# Register new parser
scanner.parsers['.rs'] = RustParser()
```

### Liskov Substitution Principle (LSP)

All language parsers are substitutable:
```python
def scan_file(parser: LanguageParser, file_path, content):
    imports = parser.parse_imports(file_path, content)
    functions = parser.parse_functions(file_path, content)
    calls = parser.parse_function_calls(file_path, content)
```

### Interface Segregation Principle (ISP)

Specific interfaces instead of general ones:
- `LanguageParser` protocol has only necessary methods
- `ImpactCalculator` doesn't depend on GitHub operations
- `CallGraphAnalyzer` is independent of LLM client

### Dependency Inversion Principle (DIP)

High-level modules depend on abstractions:
```python
class ImpactAnalysisAgent:
    def __init__(self, config):
        # Depends on abstractions, not concrete implementations
        self.github_tools = GitHubTools(config['github_token'])
        self.dependency_analyzer = DependencyAnalyzer(...)
        self.impact_calculator = ImpactCalculator(...)
```

---

## 📊 Performance Characteristics

### Time Complexity

- **Dependency Graph Building**: O(R²) where R = number of repos
- **Code Scanning**: O(F) where F = number of files
- **Call Graph Building**: O(N + E) where N = functions, E = edges
- **Impact Calculation**: O(R × D) where D = depth of dependency graph
- **BFS for Impacted Functions**: O(F + C) where C = call relationships

### Space Complexity

- **Dependency Graph**: O(R²) - adjacency matrix
- **Call Graph**: O(F + C) - function nodes + call edges
- **Scanned Code Data**: O(F × L) where L = average file lines

### Optimization Strategies

1. **Caching**: Repositories cloned to `/tmp/` and reused
2. **Pagination**: GitHub API calls paginated (100/page)
3. **Lazy Loading**: Call graphs built only when needed
4. **Selective Scanning**: Only scan files in changed repositories
5. **Early Termination**: BFS stops at max_depth

---

## 🔄 Dynamic Dependency Updates

```python
# Example: New dependency discovered during code scan
def on_dependency_discovered(source_repo, target_repo):
    # Update graph
    dependency_analyzer.update_dependency_graph((source_repo, target_repo))
    
    # Recalculate impacted repositories
    affected = dependency_graph.get_dependents(target_repo)
    
    # Update impact scores
    for repo in affected:
        recalculate_impact(repo)
```

---

## 🚀 Extensibility Points

### 1. Adding New Language Support

```python
class GoParser(LanguageParser):
    def parse_imports(self, file_path, content):
        # Parse Go imports
        return imports
    
    def parse_functions(self, file_path, content):
        # Parse Go functions
        return functions
    
    def parse_function_calls(self, file_path, content):
        # Parse Go calls
        return calls

# Register
scanner.parsers['.go'] = GoParser()
```

### 2. Adding New Impact Factors

```python
def calculate_repo_impact(self, ...):
    score = base_score
    
    # Add new factor
    if has_breaking_api_change:
        score *= 1.5
    
    return min(1.0, score)
```

### 3. Custom Test Generation

```python
def generate_custom_tests(self, impact_info):
    tests = []
    
    # Custom logic
    if impact_info['affects_authentication']:
        tests.append(generate_auth_tests())
    
    return tests
```

---

## 📈 Scalability Considerations

### Current Limits
- Max commits per repo: 50 (configurable)
- Max depth for call graph traversal: 3
- GitHub API rate limit: 5000 requests/hour
- LLM token limit: 4096 tokens

### Scaling Strategies
1. **Horizontal**: Run multiple RIPPLE instances for different repos
2. **Caching**: Cache LLM responses for similar changes
3. **Incremental**: Only analyze new commits, not full history
4. **Distributed**: Split call graph analysis across machines

---

## 🎯 Future Enhancements

1. **Database Backend**: Store analyses for historical tracking
2. **Real-time Monitoring**: Watch repositories for new commits
3. **PR Integration**: Automatic analysis on PR creation
4. **Custom Rules**: User-defined impact rules
5. **ML Models**: Train models to predict impact scores
6. **Visualization**: Interactive dependency graph visualization

---

**Architecture designed for maintainability, extensibility, and performance.**

