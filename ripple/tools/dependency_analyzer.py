"""
Enhanced tools for analyzing dependencies between repositories.

Integrates code scanning for real dependency discovery.
Follows SOLID Principles.
"""
import os
import re
from typing import List, Dict, Set, Optional
from collections import defaultdict

from .code_dependency_scanner import CodeDependencyScanner, DependencyGraphBuilder


class DependencyAnalyzer:
    """
    Analyze dependencies between repositories using code scanning.
    
    Single Responsibility: Dependency analysis
    Open/Closed: Can be extended with new analysis strategies
    """
    
    def __init__(self, deployment_config: Optional[Dict] = None, 
                 enable_code_scanning: bool = True):
        """
        Initialize dependency analyzer.
        
        Args:
            deployment_config: Optional deployment configuration
            enable_code_scanning: Whether to scan actual code for dependencies
        """
        self.dependency_patterns = {
            "python": [r"^import\s+(\w+)", r"^from\s+(\w+)"],
        }
        self.deployment_config = deployment_config or {}
        self.enable_code_scanning = enable_code_scanning
        self.code_scanner = CodeDependencyScanner() if enable_code_scanning else None
        self.scanned_repos: Dict[str, Dict] = {}
    
    def scan_repository_code(self, repo_path: str, repo_name: str) -> Dict:
        """
        Scan repository code to discover actual dependencies.
        
        Args:
            repo_path: Local repository path
            repo_name: Repository name
            
        Returns:
            Scan results
        """
        if not self.code_scanner:
            return {}
        
        scan_result = self.code_scanner.scan_repository(repo_path, repo_name)
        self.scanned_repos[repo_name] = scan_result
        return scan_result
    
    def build_dependency_matrix(self, repositories: List[Dict], 
                               repo_paths: Optional[Dict[str, str]] = None) -> Dict[str, List[str]]:
        """
        Build cross-repository dependency matrix.
        
        Strategy:
        1. If code scanning is enabled and repo paths provided, scan actual code
        2. Otherwise use deployment_config if available
        3. Fallback to inferring from repository metadata
        
        Args:
            repositories: List of repository configurations
            repo_paths: Optional dict of repo_name -> local_path for code scanning
            
        Returns:
            Dependency matrix: repo_name -> list of repos it depends on
        """
        matrix = {repo["name"]: [] for repo in repositories}
        
        # Strategy 1: Code scanning (most accurate)
        if self.enable_code_scanning and repo_paths:
            code_deps = self._build_from_code_scanning(repositories, repo_paths)
            if code_deps:
                matrix.update(code_deps)
                return matrix
        
        # Strategy 2: Deployment config
        if self.deployment_config:
            for repo_name, config in self.deployment_config.items():
                if repo_name in matrix:
                    matrix[repo_name] = config.get('depends_on', [])
            return matrix
        
        # Strategy 3: Infer from metadata
        return self._infer_from_metadata(repositories)
    
    def _build_from_code_scanning(self, repositories: List[Dict],
                                  repo_paths: Dict[str, str]) -> Dict[str, List[str]]:
        """Build dependency matrix by scanning actual code"""
        # Scan all repositories
        for repo in repositories:
            repo_name = repo['name']
            if repo_name in repo_paths:
                repo_path = repo_paths[repo_name]
                if os.path.exists(repo_path):
                    print(f"   🔍 Scanning {repo_name} for dependencies...")
                    self.scan_repository_code(repo_path, repo_name)
        
        # Build cross-repo dependencies
        if self.scanned_repos and self.code_scanner:
            return self.code_scanner.find_cross_repo_dependencies(self.scanned_repos)
        
        return {}
    
    def _infer_from_metadata(self, repositories: List[Dict]) -> Dict[str, List[str]]:
        """Infer dependencies from repository metadata"""
        matrix = {repo["name"]: [] for repo in repositories}
        
        # Group repos by deployment layer
        api_repos = {r['name'] for r in repositories if r.get('deployment_layer') == 'api'}
        core_repos = {r['name'] for r in repositories if r.get('deployment_layer') == 'core'}
        ui_repos = {r['name'] for r in repositories if r.get('deployment_layer') == 'ui'}
        
        for repo in repositories:
            repo_name = repo['name']
            layer = repo.get('deployment_layer')
            
            # UI depends on API and Core
            if layer == 'ui':
                matrix[repo_name] = list(api_repos | core_repos)
            # Core depends on API
            elif layer == 'core' and api_repos:
                matrix[repo_name] = list(api_repos)
            # Modules depend on core (or API if no core)
            elif layer not in ['api', 'core', 'ui']:
                if core_repos:
                    matrix[repo_name] = list(core_repos)
                elif api_repos:
                    matrix[repo_name] = list(api_repos)
        
        return matrix
    
    def get_dynamic_dependencies(self, repo_name: str) -> Set[str]:
        """
        Get dynamically discovered dependencies for a repository.
        
        Args:
            repo_name: Repository name
            
        Returns:
            Set of repository names this repo depends on
        """
        if repo_name in self.scanned_repos and self.code_scanner:
            scan_result = self.scanned_repos[repo_name]
            all_scanned = self.scanned_repos
            deps = self.code_scanner.find_cross_repo_dependencies({
                repo_name: scan_result,
                **{k: v for k, v in all_scanned.items() if k != repo_name}
            })
            return deps.get(repo_name, set())
        return set()
    
    def update_dependency_graph(self, new_dependency: tuple[str, str]):
        """
        Dynamically update the dependency graph when new dependency is discovered.
        
        Args:
            new_dependency: Tuple of (source_repo, target_repo)
        """
        if not hasattr(self, '_dynamic_graph'):
            self._dynamic_graph = DependencyGraphBuilder()
        
        source, target = new_dependency
        self._dynamic_graph.add_dependency(source, target)
    
    def calculate_dependency_strength(self, source_repo: str, target_repo: str,
                                     dependencies: Dict) -> float:
        """
        Calculate dependency strength between two repositories.
        
        Considers:
        - Direct vs indirect dependency
        - Number of imports
        - Frequency of usage
        
        Args:
            source_repo: Source repository name
            target_repo: Target repository name
            dependencies: Dependency matrix
            
        Returns:
            Strength score (0.0 to 1.0)
        """
        if target_repo not in dependencies.get(source_repo, []):
            return 0.0
        
        # Base strength for direct dependency
        strength = 0.8
        
        # Increase strength based on actual code analysis
        if source_repo in self.scanned_repos and self.scanned_repos[source_repo]:
            scan_result = self.scanned_repos[source_repo]
            imports = scan_result.get('imports', {})
            
            # Count how many files import from target repo
            target_base = target_repo.replace('-', '_')
            import_count = sum(
                1 for file_imports in imports.values()
                for imp in file_imports
                if target_base in imp
            )
            
            # Normalize and add to strength (max 0.2 bonus)
            if import_count > 0:
                strength = min(1.0, strength + (import_count * 0.05))
        
        return strength

