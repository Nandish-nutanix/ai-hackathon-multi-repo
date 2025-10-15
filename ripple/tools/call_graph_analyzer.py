"""
Call Graph Analyzer
Analyzes method call graphs to detect impact of changes

Follows SOLID Principles:
- Single Responsibility: Focus on call graph analysis
- Open/Closed: Extensible for different analysis strategies
"""
import ast
import re
from typing import List, Dict, Set, Optional, Tuple
from collections import defaultdict, deque
from dataclasses import dataclass


@dataclass
class FunctionNode:
    """
    Represents a function/method in the call graph.
    
    Immutable data class following Single Responsibility
    """
    name: str
    file_path: str
    line_number: int
    class_name: Optional[str] = None
    is_helper: bool = False
    complexity: int = 1
    
    def __hash__(self):
        return hash((self.name, self.file_path, self.line_number))
    
    def __eq__(self, other):
        return (self.name == other.name and 
                self.file_path == other.file_path and 
                self.line_number == other.line_number)


@dataclass
class CallEdge:
    """
    Represents a call relationship between functions.
    """
    caller: FunctionNode
    callee: FunctionNode
    call_count: int = 1
    
    def __hash__(self):
        return hash((self.caller, self.callee))


class CallGraphAnalyzer:
    """
    Analyzes call graphs to determine impact of code changes.
    
    Single Responsibility: Call graph analysis and impact detection
    """
    
    def __init__(self):
        self.functions: Dict[str, FunctionNode] = {}  # name -> FunctionNode
        self.call_graph: Dict[FunctionNode, Set[FunctionNode]] = defaultdict(set)  # caller -> callees
        self.reverse_graph: Dict[FunctionNode, Set[FunctionNode]] = defaultdict(set)  # callee -> callers
    
    def build_call_graph(self, repo_path: str, file_changes: List[str]) -> None:
        """
        Build call graph from repository code.
        
        Args:
            repo_path: Path to repository
            file_changes: List of changed file paths
        """
        import os
        
        # First pass: Collect all function definitions
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if d not in {'.git', 'node_modules', '__pycache__'}]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    self._parse_python_file(file_path)
        
        # Second pass: Build call relationships
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if d not in {'.git', 'node_modules', '__pycache__'}]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    self._build_calls_from_file(file_path)
    
    def _parse_python_file(self, file_path: str) -> None:
        """Parse Python file to extract function definitions"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    func_node = FunctionNode(
                        name=node.name,
                        file_path=file_path,
                        line_number=node.lineno,
                        class_name=self._get_class_name(node, tree),
                        is_helper=self._is_helper_function(node),
                        complexity=self._calculate_complexity(node)
                    )
                    
                    # Use fully qualified name for class methods
                    full_name = f"{func_node.class_name}.{func_node.name}" if func_node.class_name else func_node.name
                    self.functions[full_name] = func_node
                    
        except Exception as e:
            # Skip files that can't be parsed
            pass
    
    def _get_class_name(self, func_node, tree) -> Optional[str]:
        """Get the class name if function is a method"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for item in node.body:
                    if item == func_node:
                        return node.name
        return None
    
    def _is_helper_function(self, node: ast.FunctionDef) -> bool:
        """
        Determine if a function is a helper function.
        
        Heuristics:
        - Name starts with underscore (private)
        - Name contains 'helper', 'util', 'internal'
        - Short function with few parameters
        """
        name = node.name
        
        # Private functions
        if name.startswith('_') and not name.startswith('__'):
            return True
        
        # Common helper patterns
        helper_patterns = ['helper', 'util', 'internal', 'validate', 'parse', 'format']
        if any(pattern in name.lower() for pattern in helper_patterns):
            return True
        
        # Short utility functions (< 10 lines, < 3 params)
        if len(node.body) < 10 and len(node.args.args) <= 3:
            return True
        
        return False
    
    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity"""
        complexity = 1
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity
    
    def _build_calls_from_file(self, file_path: str) -> None:
        """Build call relationships from a Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Find all function definitions and their calls
            for func_def in [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
                caller_name = func_def.name
                caller_class = self._get_class_name(func_def, tree)
                full_caller_name = f"{caller_class}.{caller_name}" if caller_class else caller_name
                
                if full_caller_name not in self.functions:
                    continue
                
                caller_node = self.functions[full_caller_name]
                
                # Find all function calls within this function
                for node in ast.walk(func_def):
                    if isinstance(node, ast.Call):
                        callee_name = self._extract_call_name(node)
                        if callee_name and callee_name in self.functions:
                            callee_node = self.functions[callee_name]
                            self.call_graph[caller_node].add(callee_node)
                            self.reverse_graph[callee_node].add(caller_node)
                            
        except Exception as e:
            pass
    
    def _extract_call_name(self, call_node: ast.Call) -> Optional[str]:
        """Extract function name from a call node"""
        if isinstance(call_node.func, ast.Name):
            return call_node.func.id
        elif isinstance(call_node.func, ast.Attribute):
            # For self.method_name or obj.method_name
            return call_node.func.attr
        return None
    
    def find_impacted_functions(self, changed_functions: List[str], 
                               max_depth: int = 3) -> Dict[str, Dict]:
        """
        Find all functions impacted by changes to given functions.
        
        Uses BFS to traverse the call graph upward (reverse graph).
        
        Args:
            changed_functions: List of function names that changed
            max_depth: Maximum depth to traverse
            
        Returns:
            Dict of impacted_function -> impact_info
        """
        impacted = {}
        
        for func_name in changed_functions:
            if func_name not in self.functions:
                continue
            
            changed_node = self.functions[func_name]
            
            # BFS from changed function
            queue = deque([(changed_node, 0)])
            visited = {changed_node}
            
            while queue:
                current_node, depth = queue.popleft()
                
                if depth > max_depth:
                    continue
                
                # Find all callers of this function
                callers = self.reverse_graph.get(current_node, set())
                
                for caller in callers:
                    if caller not in visited:
                        visited.add(caller)
                        
                        # Calculate impact score
                        impact_score = self._calculate_impact_score(
                            changed_node, caller, depth
                        )
                        
                        impacted[f"{caller.class_name}.{caller.name}" if caller.class_name else caller.name] = {
                            'function': caller,
                            'depth': depth + 1,
                            'impact_score': impact_score,
                            'reason': f"Calls {current_node.name} (depth {depth + 1})",
                            'file': caller.file_path,
                            'line': caller.line_number,
                            'is_direct_caller': depth == 0
                        }
                        
                        queue.append((caller, depth + 1))
        
        return impacted
    
    def _calculate_impact_score(self, changed_func: FunctionNode, 
                                impacted_func: FunctionNode,
                                depth: int) -> float:
        """
        Calculate impact score for a function.
        
        Factors:
        - Depth in call graph (closer = higher impact)
        - Complexity of impacted function
        - Whether changed function is a helper
        - Number of callers of impacted function
        """
        # Base score decreases with depth
        score = 1.0 / (depth + 1)
        
        # Helper functions have higher impact
        if changed_func.is_helper:
            score *= 1.5
        
        # Complex functions are more risky to impact
        complexity_factor = min(impacted_func.complexity / 10, 2.0)
        score *= complexity_factor
        
        # Functions with many callers have higher impact
        caller_count = len(self.reverse_graph.get(impacted_func, set()))
        caller_factor = min(1.0 + (caller_count * 0.1), 2.0)
        score *= caller_factor
        
        return min(score, 1.0)
    
    def identify_helper_method_impacts(self, changed_files: List[str]) -> List[Dict]:
        """
        Specifically identify impacts of helper method changes.
        
        Args:
            changed_files: List of file paths that changed
            
        Returns:
            List of impact summaries
        """
        impacts = []
        
        # Find all helper functions in changed files
        for func_name, func_node in self.functions.items():
            if func_node.is_helper and any(f in func_node.file_path for f in changed_files):
                # Find all callers
                callers = self.reverse_graph.get(func_node, set())
                
                if callers:
                    impacts.append({
                        'helper_function': func_name,
                        'file': func_node.file_path,
                        'line': func_node.line_number,
                        'caller_count': len(callers),
                        'callers': [
                            {
                                'name': f"{c.class_name}.{c.name}" if c.class_name else c.name,
                                'file': c.file_path,
                                'line': c.line_number
                            }
                            for c in list(callers)[:10]  # Limit to first 10
                        ],
                        'impact_level': 'high' if len(callers) > 5 else 'medium'
                    })
        
        return impacts
    
    def get_critical_paths(self, changed_function: str) -> List[List[str]]:
        """
        Find critical execution paths affected by a change.
        
        Args:
            changed_function: Name of the changed function
            
        Returns:
            List of execution paths (list of function names)
        """
        if changed_function not in self.functions:
            return []
        
        changed_node = self.functions[changed_function]
        paths = []
        
        def dfs(node: FunctionNode, current_path: List[str], depth: int = 0):
            if depth > 5:  # Limit depth
                return
            
            current_path.append(node.name)
            
            callers = self.reverse_graph.get(node, set())
            if not callers:
                # End of path - this is a top-level function
                paths.append(current_path.copy())
            else:
                for caller in callers:
                    dfs(caller, current_path, depth + 1)
            
            current_path.pop()
        
        dfs(changed_node, [])
        return paths
    
    def generate_test_recommendations(self, impacted_functions: Dict[str, Dict]) -> List[Dict]:
        """
        Generate test recommendations based on impacted functions.
        
        Args:
            impacted_functions: Output from find_impacted_functions
            
        Returns:
            List of test recommendations
        """
        recommendations = []
        
        # Group by impact score
        high_impact = [f for f, info in impacted_functions.items() if info['impact_score'] > 0.7]
        medium_impact = [f for f, info in impacted_functions.items() if 0.4 < info['impact_score'] <= 0.7]
        
        # High impact - unit tests + integration tests
        for func_name in high_impact:
            info = impacted_functions[func_name]
            recommendations.append({
                'function': func_name,
                'test_types': ['unit', 'integration'],
                'priority': 'high',
                'reason': f"High impact score ({info['impact_score']:.2f})",
                'file': info['file'],
                'suggested_tests': [
                    f"test_{func_name.lower().replace('.', '_')}_with_changed_dependency",
                    f"test_{func_name.lower().replace('.', '_')}_integration"
                ]
            })
        
        # Medium impact - unit tests
        for func_name in medium_impact:
            info = impacted_functions[func_name]
            recommendations.append({
                'function': func_name,
                'test_types': ['unit'],
                'priority': 'medium',
                'reason': f"Medium impact score ({info['impact_score']:.2f})",
                'file': info['file'],
                'suggested_tests': [
                    f"test_{func_name.lower().replace('.', '_')}_basic"
                ]
            })
        
        return recommendations


class ImpactVisualizer:
    """
    Visualize call graph and impact analysis.
    
    Single Responsibility: Visualization
    """
    
    @staticmethod
    def format_impact_tree(impacted_functions: Dict[str, Dict]) -> str:
        """
        Format impacted functions as a tree structure.
        
        Args:
            impacted_functions: Output from find_impacted_functions
            
        Returns:
            Formatted tree string
        """
        # Sort by depth
        sorted_impacts = sorted(
            impacted_functions.items(),
            key=lambda x: (x[1]['depth'], x[0])
        )
        
        tree = ["Impact Tree:", "=" * 60]
        
        current_depth = -1
        for func_name, info in sorted_impacts:
            if info['depth'] != current_depth:
                current_depth = info['depth']
                tree.append(f"\nDepth {current_depth}:")
            
            indent = "  " * current_depth
            impact_symbol = "🔴" if info['impact_score'] > 0.7 else "🟡" if info['impact_score'] > 0.4 else "🟢"
            tree.append(f"{indent}{impact_symbol} {func_name} (score: {info['impact_score']:.2f})")
            tree.append(f"{indent}   └─ {info['file']}:{info['line']}")
        
        return "\n".join(tree)

