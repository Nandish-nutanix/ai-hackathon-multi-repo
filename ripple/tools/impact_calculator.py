"""
Enhanced impact calculator with call graph analysis.

Follows SOLID Principles.
"""
from typing import List, Dict, Optional
from .call_graph_analyzer import CallGraphAnalyzer


class ImpactCalculator:
    """
    Calculate impact scores for code changes using call graph analysis.
    
    Single Responsibility: Impact scoring
    """
    
    def __init__(self, dependency_graph, enable_call_graph: bool = True):
        """
        Initialize impact calculator.
        
        Args:
            dependency_graph: Repository dependency graph
            enable_call_graph: Whether to use call graph analysis
        """
        self.dependency_graph = dependency_graph
        self.enable_call_graph = enable_call_graph
        self.call_graph_analyzers: Dict[str, CallGraphAnalyzer] = {}
    
    def build_call_graph(self, repo_name: str, repo_path: str, 
                        changed_files: List[str]) -> Optional[CallGraphAnalyzer]:
        """
        Build call graph for a repository.
        
        Args:
            repo_name: Repository name
            repo_path: Local repository path
            changed_files: List of changed file paths
            
        Returns:
            CallGraphAnalyzer instance
        """
        if not self.enable_call_graph:
            return None
        
        analyzer = CallGraphAnalyzer()
        analyzer.build_call_graph(repo_path, changed_files)
        self.call_graph_analyzers[repo_name] = analyzer
        return analyzer
    
    def calculate_repo_impact(self, source_repo: str, 
                             changed_components: List[str],
                             change_type: str,
                             changed_files: Optional[List[str]] = None) -> Dict[str, float]:
        """
        Calculate impact score for each affected repository.
        
        Enhanced with call graph analysis when available.
        
        Args:
            source_repo: Source repository name
            changed_components: List of changed component/file paths
            change_type: Type of change
            changed_files: Optional list of changed files for call graph
            
        Returns:
            Dict of repo_name -> impact_score
        """
        dependents = self.dependency_graph.get_dependents(source_repo)
        
        change_weights = {
            "breaking": 1.0,
            "enhancement": 0.6,
            "bugfix": 0.4,
            "refactor": 0.3
        }
        
        base_weight = change_weights.get(change_type, 0.5)
        impact_scores = {}
        
        # Get call graph analysis if available
        call_graph_impact = {}
        if source_repo in self.call_graph_analyzers and changed_files:
            analyzer = self.call_graph_analyzers[source_repo]
            
            # Find impacted functions from changed files
            changed_functions = []
            for func_name, func_node in analyzer.functions.items():
                if any(cf in func_node.file_path for cf in changed_files):
                    changed_functions.append(func_name)
            
            if changed_functions:
                impacted = analyzer.find_impacted_functions(changed_functions, max_depth=3)
                
                # Calculate average impact score from call graph
                if impacted:
                    avg_impact = sum(info['impact_score'] for info in impacted.values()) / len(impacted)
                    call_graph_impact['average_score'] = avg_impact
                    call_graph_impact['impacted_function_count'] = len(impacted)
        
        # Calculate impacts for dependents
        for dependent in dependents:
            deps = [d for d in self.dependency_graph.dependencies 
                   if d.source == dependent and d.target == source_repo]
            
            if not deps:
                continue
            
            dep = deps[0]
            overlap = len(set(changed_components) & set(dep.components))
            component_factor = overlap / max(len(changed_components), 1) if changed_components else 0.5
            
            # Base score
            score = base_weight * dep.strength * (0.5 + 0.5 * component_factor)
            
            # Enhance with call graph data
            if call_graph_impact:
                cg_score = call_graph_impact.get('average_score', 0)
                func_count = call_graph_impact.get('impacted_function_count', 0)
                
                # Boost score if call graph shows high impact
                if func_count > 5:
                    score = min(1.0, score * 1.2)
                if cg_score > 0.7:
                    score = min(1.0, score * 1.15)
            
            impact_scores[dependent] = min(1.0, score)
        
        return impact_scores
    
    def calculate_risk_level(self, impact_score: float, 
                           is_breaking: bool = False,
                           helper_method_changed: bool = False) -> str:
        """
        Convert impact score to risk level.
        
        Enhanced to consider helper method changes.
        
        Args:
            impact_score: Calculated impact score
            is_breaking: Whether this is a breaking change
            helper_method_changed: Whether a helper method was changed
            
        Returns:
            Risk level string
        """
        # Helper method changes are inherently risky
        if helper_method_changed and impact_score > 0.5:
            return "high"
        
        if is_breaking or impact_score >= 0.8:
            return "critical"
        elif impact_score >= 0.6:
            return "high"
        elif impact_score >= 0.4:
            return "medium"
        else:
            return "low"
    
    def get_helper_method_impacts(self, repo_name: str, 
                                  changed_files: List[str]) -> List[Dict]:
        """
        Get specific impacts of helper method changes.
        
        Args:
            repo_name: Repository name
            changed_files: List of changed files
            
        Returns:
            List of helper method impact information
        """
        if repo_name not in self.call_graph_analyzers:
            return []
        
        analyzer = self.call_graph_analyzers[repo_name]
        return analyzer.identify_helper_method_impacts(changed_files)
    
    def estimate_test_effort(self, affected_repos: List[str],
                           impact_scores: Dict[str, float],
                           call_graph_data: Optional[Dict] = None) -> float:
        """
        Estimate testing effort in hours.
        
        Enhanced with call graph data.
        
        Args:
            affected_repos: List of affected repositories
            impact_scores: Impact scores for each repo
            call_graph_data: Optional call graph analysis data
            
        Returns:
            Estimated hours
        """
        base_hours_per_repo = 4.0
        total_hours = 0.0
        
        for repo in affected_repos:
            score = impact_scores.get(repo, 0.5)
            repo_hours = base_hours_per_repo * (1 + score)
            
            # Add time for impacted functions if we have call graph data
            if call_graph_data and repo in call_graph_data:
                impacted_func_count = call_graph_data[repo].get('impacted_function_count', 0)
                # Add 30 minutes per impacted function (max 8 hours)
                additional_hours = min(impacted_func_count * 0.5, 8.0)
                repo_hours += additional_hours
            
            total_hours += repo_hours
        
        return round(total_hours, 2)
    
    def generate_countermeasures(self, repo_name: str, 
                                changed_files: List[str]) -> List[Dict]:
        """
        Generate countermeasures and test recommendations.
        
        Args:
            repo_name: Repository name
            changed_files: List of changed files
            
        Returns:
            List of countermeasure recommendations
        """
        countermeasures = []
        
        # Get helper method impacts
        helper_impacts = self.get_helper_method_impacts(repo_name, changed_files)
        
        for impact in helper_impacts:
            countermeasures.append({
                'type': 'helper_method_change',
                'function': impact['helper_function'],
                'risk': impact['impact_level'],
                'recommendations': [
                    f"Test all {impact['caller_count']} caller functions",
                    f"Run integration tests for affected flows",
                    f"Review changes in {impact['file']}"
                ],
                'test_cases': [
                    {
                        'name': f"test_{impact['helper_function'].replace('.', '_')}_with_all_callers",
                        'priority': 'high',
                        'type': 'integration'
                    }
                ]
            })
        
        # Get call graph recommendations if available
        if repo_name in self.call_graph_analyzers:
            analyzer = self.call_graph_analyzers[repo_name]
            
            # Find changed functions
            changed_functions = []
            for func_name, func_node in analyzer.functions.items():
                if any(cf in func_node.file_path for cf in changed_files):
                    changed_functions.append(func_name)
            
            if changed_functions:
                impacted = analyzer.find_impacted_functions(changed_functions)
                test_recs = analyzer.generate_test_recommendations(impacted)
                
                for rec in test_recs:
                    countermeasures.append({
                        'type': 'function_impact',
                        'function': rec['function'],
                        'risk': rec['priority'],
                        'recommendations': [
                            f"Run {', '.join(rec['test_types'])} tests",
                            rec['reason']
                        ],
                        'test_cases': [
                            {
                                'name': test_name,
                                'priority': rec['priority'],
                                'type': rec['test_types'][0] if rec['test_types'] else 'unit'
                            }
                            for test_name in rec['suggested_tests']
                        ]
                    })
        
        return countermeasures

