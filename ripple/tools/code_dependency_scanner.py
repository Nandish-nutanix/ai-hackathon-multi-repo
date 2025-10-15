"""
Code Dependency Scanner
Analyzes actual code to discover cross-repository dependencies

Follows SOLID Principles:
- Single Responsibility: Each class handles one type of analysis
- Open/Closed: Easy to add new language parsers
- Dependency Inversion: Depends on abstract interfaces
"""
import os
import re
import ast
from typing import List, Dict, Set, Optional, Protocol
from pathlib import Path
from collections import defaultdict


class LanguageParser(Protocol):
    """
    Interface for language-specific parsers.
    
    Dependency Inversion: High-level modules depend on this abstraction
    """
    
    def parse_imports(self, file_path: str, content: str) -> List[str]:
        """Parse imports from source code"""
        ...
    
    def parse_functions(self, file_path: str, content: str) -> List[Dict]:
        """Parse function/method definitions"""
        ...
    
    def parse_function_calls(self, file_path: str, content: str) -> List[str]:
        """Parse function calls in the code"""
        ...


class PythonParser:
    """
    Python code parser using AST.
    
    Single Responsibility: Parse Python code
    """
    
    def parse_imports(self, file_path: str, content: str) -> List[str]:
        """
        Extract all imports from Python code.
        
        Returns:
            List of imported module names
        """
        imports = []
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
        except SyntaxError:
            # Fallback to regex if AST parsing fails
            imports = self._regex_parse_imports(content)
        
        return imports
    
    def _regex_parse_imports(self, content: str) -> List[str]:
        """Fallback regex-based import parsing"""
        imports = []
        
        # Match: import xyz
        for match in re.finditer(r'^import\s+([\w.]+)', content, re.MULTILINE):
            imports.append(match.group(1))
        
        # Match: from xyz import ...
        for match in re.finditer(r'^from\s+([\w.]+)\s+import', content, re.MULTILINE):
            imports.append(match.group(1))
        
        return imports
    
    def parse_functions(self, file_path: str, content: str) -> List[Dict]:
        """
        Extract function and method definitions.
        
        Returns:
            List of function metadata
        """
        functions = []
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                    functions.append({
                        'name': node.name,
                        'line_number': node.lineno,
                        'is_async': isinstance(node, ast.AsyncFunctionDef),
                        'args': [arg.arg for arg in node.args.args],
                        'file': file_path
                    })
        except SyntaxError:
            pass
        
        return functions
    
    def parse_function_calls(self, file_path: str, content: str) -> List[str]:
        """
        Extract function calls from code.
        
        Returns:
            List of function names being called
        """
        calls = []
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        calls.append(node.func.id)
                    elif isinstance(node.func, ast.Attribute):
                        calls.append(node.func.attr)
        except SyntaxError:
            pass
        
        return calls


class JavaScriptParser:
    """
    JavaScript/TypeScript code parser.
    
    Single Responsibility: Parse JavaScript/TypeScript code
    """
    
    def parse_imports(self, file_path: str, content: str) -> List[str]:
        """Extract imports from JavaScript/TypeScript"""
        imports = []
        
        # ES6 imports: import ... from 'module'
        for match in re.finditer(r"import\s+.*?from\s+['\"]([^'\"]+)['\"]", content):
            imports.append(match.group(1))
        
        # CommonJS: require('module')
        for match in re.finditer(r"require\(['\"]([^'\"]+)['\"]\)", content):
            imports.append(match.group(1))
        
        return imports
    
    def parse_functions(self, file_path: str, content: str) -> List[Dict]:
        """Extract function definitions from JavaScript/TypeScript"""
        functions = []
        
        # Function declarations: function name() {}
        for match in re.finditer(r"function\s+(\w+)\s*\(([^)]*)\)", content):
            functions.append({
                'name': match.group(1),
                'args': [a.strip() for a in match.group(2).split(',') if a.strip()],
                'file': file_path
            })
        
        # Arrow functions: const name = () => {}
        for match in re.finditer(r"(?:const|let|var)\s+(\w+)\s*=\s*\([^)]*\)\s*=>", content):
            functions.append({
                'name': match.group(1),
                'file': file_path
            })
        
        return functions
    
    def parse_function_calls(self, file_path: str, content: str) -> List[str]:
        """Extract function calls from JavaScript/TypeScript"""
        calls = []
        
        # Function calls: functionName(
        for match in re.finditer(r"(\w+)\s*\(", content):
            calls.append(match.group(1))
        
        return calls


class CodeDependencyScanner:
    """
    Main scanner that discovers dependencies by analyzing actual code.
    
    Open/Closed Principle: Can add new parsers without modifying this class
    """
    
    def __init__(self):
        self.parsers = {
            '.py': PythonParser(),
            '.js': JavaScriptParser(),
            '.ts': JavaScriptParser(),
            '.jsx': JavaScriptParser(),
            '.tsx': JavaScriptParser(),
        }
    
    def scan_repository(self, repo_path: str, 
                       repo_name: str) -> Dict[str, any]:
        """
        Scan a repository to discover dependencies, functions, and calls.
        
        Args:
            repo_path: Local path to repository
            repo_name: Name of the repository
            
        Returns:
            Dictionary with scanned data
        """
        result = {
            'repo_name': repo_name,
            'imports': defaultdict(list),  # file -> list of imports
            'functions': [],  # List of all functions
            'function_calls': defaultdict(set),  # function_name -> set of callers
            'files_scanned': 0,
            'external_dependencies': set()
        }
        
        if not os.path.exists(repo_path):
            return result
        
        # Walk through repository
        for root, dirs, files in os.walk(repo_path):
            # Skip common non-source directories
            dirs[:] = [d for d in dirs if d not in {
                '.git', 'node_modules', '__pycache__', '.venv', 'venv',
                'dist', 'build', '.eggs', 'egg-info'
            }]
            
            for file in files:
                file_path = os.path.join(root, file)
                ext = os.path.splitext(file)[1]
                
                if ext in self.parsers:
                    self._scan_file(file_path, ext, result, repo_path)
        
        return result
    
    def _scan_file(self, file_path: str, ext: str, 
                   result: Dict, repo_path: str):
        """Scan a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            parser = self.parsers[ext]
            relative_path = os.path.relpath(file_path, repo_path)
            
            # Parse imports
            imports = parser.parse_imports(file_path, content)
            result['imports'][relative_path] = imports
            result['external_dependencies'].update(imports)
            
            # Parse functions
            functions = parser.parse_functions(file_path, content)
            result['functions'].extend(functions)
            
            # Parse function calls and build call graph
            calls = parser.parse_function_calls(file_path, content)
            for func in functions:
                func_name = func['name']
                # Track which functions call this function
                for call in calls:
                    if call != func_name:  # Don't count self-calls
                        result['function_calls'][call].add(func_name)
            
            result['files_scanned'] += 1
            
        except Exception as e:
            # Silently skip files that can't be read
            pass
    
    def find_cross_repo_dependencies(self, 
                                    scanned_repos: Dict[str, Dict]) -> Dict[str, Set[str]]:
        """
        Analyze scanned repositories to find cross-repo dependencies.
        
        Args:
            scanned_repos: Dict of repo_name -> scan_result
            
        Returns:
            Dict of repo_name -> set of repos it depends on
        """
        dependencies = defaultdict(set)
        
        # Build a map of module names to repositories
        module_to_repo = {}
        for repo_name, scan_result in scanned_repos.items():
            # Common patterns: repo name might be in imports
            repo_base = repo_name.replace('-', '_')
            module_to_repo[repo_base] = repo_name
            module_to_repo[repo_name] = repo_name
        
        # Find dependencies
        for repo_name, scan_result in scanned_repos.items():
            external_deps = scan_result['external_dependencies']
            
            for dep in external_deps:
                # Check if this import matches another repo
                dep_base = dep.split('.')[0]  # Get base module
                
                for module_name, target_repo in module_to_repo.items():
                    if target_repo != repo_name and module_name in dep_base:
                        dependencies[repo_name].add(target_repo)
        
        return dict(dependencies)
    
    def find_function_callers(self, function_name: str, 
                             scan_result: Dict) -> List[Dict]:
        """
        Find all places where a function is called.
        
        Args:
            function_name: Name of the function
            scan_result: Result from scan_repository
            
        Returns:
            List of caller information
        """
        callers = []
        
        # Find in call graph
        if function_name in scan_result['function_calls']:
            calling_functions = scan_result['function_calls'][function_name]
            
            # Find details of calling functions
            for caller in calling_functions:
                for func_info in scan_result['functions']:
                    if func_info['name'] == caller:
                        callers.append({
                            'caller': caller,
                            'file': func_info.get('file', 'unknown'),
                            'line': func_info.get('line_number', 0)
                        })
        
        return callers


class DependencyGraphBuilder:
    """
    Builds a dependency graph from scanned code.
    
    Single Responsibility: Graph construction
    """
    
    def __init__(self):
        self.graph = defaultdict(set)
    
    def add_dependency(self, source: str, target: str):
        """Add a dependency relationship"""
        self.graph[source].add(target)
    
    def get_dependents(self, repo: str) -> Set[str]:
        """Get all repositories that depend on this repo"""
        dependents = set()
        for source, targets in self.graph.items():
            if repo in targets:
                dependents.add(source)
        return dependents
    
    def get_dependencies(self, repo: str) -> Set[str]:
        """Get all repositories this repo depends on"""
        return self.graph.get(repo, set())
    
    def topological_sort(self) -> List[str]:
        """
        Get deployment order using topological sort.
        
        Returns:
            List of repositories in deployment order
        """
        from collections import deque
        
        # Calculate in-degrees
        in_degree = defaultdict(int)
        all_repos = set(self.graph.keys())
        for targets in self.graph.values():
            all_repos.update(targets)
        
        for repo in all_repos:
            in_degree[repo] = 0
        
        for targets in self.graph.values():
            for target in targets:
                in_degree[target] += 1
        
        # Start with repos that have no dependencies
        queue = deque([repo for repo in all_repos if in_degree[repo] == 0])
        result = []
        
        while queue:
            repo = queue.popleft()
            result.append(repo)
            
            # Reduce in-degree for dependents
            for dependent in self.get_dependents(repo):
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)
        
        return result

