"""Dependency data models"""
from dataclasses import dataclass, field
from typing import List, Dict
from enum import Enum

class DependencyType(Enum):
    DIRECT = "direct"
    TRANSITIVE = "transitive"

@dataclass
class Dependency:
    """Represents a dependency between repositories"""
    source: str
    target: str
    dep_type: DependencyType
    components: List[str] = field(default_factory=list)
    strength: float = 1.0

@dataclass
class DependencyGraph:
    """Represents the complete dependency graph"""
    repositories: Dict[str, 'Repository']
    dependencies: List[Dependency]
    
    def get_dependencies(self, repo_name: str, include_transitive: bool = True) -> List[Dependency]:
        """Get all dependencies for a repository"""
        direct_deps = [d for d in self.dependencies if d.source == repo_name]
        if not include_transitive:
            return direct_deps
        
        all_deps = set()
        visited = set()
        queue = [repo_name]
        
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            
            for dep in self.dependencies:
                if dep.source == current:
                    all_deps.add(dep)
                    queue.append(dep.target)
        
        return list(all_deps)
    
    def get_dependents(self, repo_name: str) -> List[str]:
        """Get all repositories that depend on this one"""
        return [d.source for d in self.dependencies if d.target == repo_name]
    
    def topological_sort(self, repos: List[str]) -> List[str]:
        """Get deployment order using topological sort"""
        from collections import defaultdict, deque
        
        in_degree = defaultdict(int)
        graph = defaultdict(list)
        
        for dep in self.dependencies:
            if dep.source in repos and dep.target in repos:
                graph[dep.target].append(dep.source)
                in_degree[dep.source] += 1
        
        queue = deque([r for r in repos if in_degree[r] == 0])
        result = []
        
        while queue:
            node = queue.popleft()
            result.append(node)
            
            for neighbor in graph[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        return result

