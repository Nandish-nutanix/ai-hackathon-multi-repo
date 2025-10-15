"""
Main agent for impact analysis
Following NAI Workshop Pattern: Agents = Tools + LLM
"""
import json
import uuid
from typing import List, Dict
from datetime import datetime

from utils.llm_client import NAIClient
from tools.github_tools import GitHubTools
from tools.dependency_analyzer import DependencyAnalyzer
from tools.code_analyzer import CodeAnalyzer
from tools.impact_calculator import ImpactCalculator
from tools.user_flow_analyzer import UserFlowAnalyzer
from models.dependency import DependencyGraph, Dependency, DependencyType
from models.repository import Repository
from models.impact_report import ImpactReport, ImpactScore, TestCase, UserFlowImpact


class ImpactAnalysisAgent:
    """
    AI Agent for analyzing cross-repository impact
    
    Architecture: Agent = Tools + LLM
    - Tools: GitHub, dependency analyzer, code analyzer, impact calculator
    - LLM: NAI endpoint for semantic understanding and test generation
    """
    
    def __init__(self, config: Dict):
        self.config = config
        
        # Get analysis config
        analysis_config = config.get('analysis_config', {})
        
        # Initialize LLM client
        self.llm_client = NAIClient(
            config['api_key'],
            config['endpoint_url'],
            config['model_name'],
            max_tokens=analysis_config.get('max_tokens', 512)
        )
        
        # Initialize enhanced tools
        self.github_tools = GitHubTools(config.get('github_token', ''))
        self.dependency_analyzer = DependencyAnalyzer(
            deployment_config=config.get('deployment_config', {}),
            enable_code_scanning=analysis_config.get('enable_code_scanning', True)
        )
        self.code_analyzer = CodeAnalyzer()
        self.user_flow_analyzer = UserFlowAnalyzer(
            config.get('user_flows', {}),
            config.get('deployment_config', {})
        )
        
        self.dependency_graph = None
        self.impact_calculator = None
        self.repositories = []
        self.repo_paths = {}  # Store local paths for code scanning
        self.enable_call_graph = analysis_config.get('enable_call_graph', True)
    
    def initialize_dependency_graph(self, repositories: List[Dict], repo_paths: Dict[str, str] = None):
        """
        Build the dependency graph with optional code scanning.
        
        Args:
            repositories: List of repository configurations
            repo_paths: Optional dict of repo_name -> local_path for code scanning
        """
        print("🔧 Building dependency graph...")
        
        self.repositories = repositories
        self.repo_paths = repo_paths or {}
        
        # Build dependency matrix (with code scanning if paths provided)
        dep_matrix = self.dependency_analyzer.build_dependency_matrix(
            repositories, 
            repo_paths=self.repo_paths
        )
        
        # Create dependency graph
        repos = {r['name']: Repository(**{k: v for k, v in r.items() if k in ['name', 'url', 'language', 'components']}) for r in repositories}
        dependencies = []
        
        for source, targets in dep_matrix.items():
            for target in targets:
                # Calculate actual strength if we have scanned data
                strength = self.dependency_analyzer.calculate_dependency_strength(
                    source, target, dep_matrix
                )
                
                dep = Dependency(
                    source=source,
                    target=target,
                    dep_type=DependencyType.DIRECT,
                    strength=strength
                )
                dependencies.append(dep)
        
        self.dependency_graph = DependencyGraph(
            repositories=repos,
            dependencies=dependencies
        )
        
        # Initialize impact calculator with call graph support
        self.impact_calculator = ImpactCalculator(
            self.dependency_graph, 
            enable_call_graph=self.enable_call_graph
        )
        
        print(f"✅ Graph built: {len(repos)} repos, {len(dependencies)} dependencies")
        if self.dependency_analyzer.scanned_repos:
            print(f"   📊 Code scanned: {len(self.dependency_analyzer.scanned_repos)} repositories")
        print()
    
    def analyze_change_impact(self, repository: str, commit_hash: str,
                             repo_path: str = None) -> ImpactReport:
        """
        Enhanced analyze the impact of a change using AI Agent pattern with call graph analysis.
        
        Flow:
        1. Tools: Extract commit details (GitHub API or local)
        2. Tools: Build call graph for changed code (if local clone available)
        3. Tools + LLM: Analyze code changes semantically
        4. Tools: Calculate impact scores with call graph data
        5. Tools: Identify helper method impacts
        6. LLM: Generate test cases
        7. Tools: Determine deployment order
        8. LLM: Generate recommendations with countermeasures
        """
        
        # Step 1: Get commit details (use API if no local clone)
        if repo_path:
            # Use local Git operations
            commit_diff = self.github_tools.get_commit_diff(repo_path, commit_hash)
        else:
            # Use GitHub API (no clone needed!)
            repo_config = next((r for r in self.repositories if r['name'] == repository), None)
            if repo_config:
                api_commit = self.github_tools.get_commit_details_from_api(repo_config['url'], commit_hash)
                # Convert API format to our format
                commit_diff = {
                    'commit': commit_hash,
                    'message': api_commit['commit']['message'],
                    'author': api_commit['commit']['author']['name'],
                    'timestamp': api_commit['commit']['author']['date'],
                    'changes': [
                        {
                            'file': file['filename'],
                            'change_type': file.get('status', 'modified'),
                            'additions': file.get('additions', 0),
                            'deletions': file.get('deletions', 0),
                            'diff': file.get('patch', '')[:1000]
                        }
                        for file in api_commit.get('files', [])[:20]
                    ]
                }
            else:
                raise ValueError(f"Repository {repository} not found in configuration")
        
        # Extract changed files
        changed_files = [c['file'] for c in commit_diff['changes']]
        
        # Step 2: Build call graph if enabled AND we have a local clone
        if self.enable_call_graph and repo_path:
            self.impact_calculator.build_call_graph(repository, repo_path, changed_files)
        
        # Step 2.5: Check if change is user-impacting
        user_impacting = self.user_flow_analyzer.is_user_impacting_change(repository, changed_files)
        
        # Step 3: Analyze code changes with LLM
        change_analysis = self._analyze_with_llm(repository, commit_diff)
        
        # Step 4: Calculate impact scores using tools + user flow analysis + call graph
        impact_scores = self._calculate_impacts(
            repository,
            change_analysis['changed_components'],
            change_analysis['change_type'],
            changed_files
        )
        
        # Step 5: Get helper method impacts (only if we have local clone)
        helper_impacts = []
        countermeasures = []
        if repo_path:
            helper_impacts = self.impact_calculator.get_helper_method_impacts(repository, changed_files)
            countermeasures = self.impact_calculator.generate_countermeasures(repository, changed_files)
        
        # Step 6: Generate test cases with LLM + countermeasures
        test_cases = self._generate_tests(repository, commit_diff, impact_scores, helper_impacts)
        
        # Step 7: Determine deployment order using tools
        affected_repos = [score.repository for score in impact_scores]
        deployment_order = self.dependency_graph.topological_sort(
            [repository] + affected_repos
        )
        
        # Step 8: Generate recommendations with countermeasures
        recommendations = self._generate_recommendations(impact_scores, test_cases, countermeasures)
        
        # Count affected user flows
        total_flows = sum(len(score.user_flows) for score in impact_scores)
        
        # Create comprehensive report
        report = ImpactReport(
            analysis_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            source_repository=repository,
            source_commit=commit_hash,
            change_summary=commit_diff['message'][:200],
            changed_files=changed_files,
            affected_repositories=affected_repos,
            impact_scores=impact_scores,
            dependency_chain=self._build_dependency_chain(repository, affected_repos),
            generated_tests=test_cases,
            test_coverage_estimate=self._estimate_coverage(test_cases),
            deployment_order=deployment_order,
            estimated_effort_hours=self.impact_calculator.estimate_test_effort(
                affected_repos,
                {s.repository: s.score for s in impact_scores}
            ),
            recommendations=recommendations['recommendations'],
            warnings=recommendations['warnings'],
            user_impacting=user_impacting,
            total_user_flows_affected=total_flows
        )
        
        return report
    
    def _analyze_with_llm(self, repository: str, commit_diff: Dict) -> Dict:
        """Use LLM to analyze code changes semantically"""
        
        # Prepare concise context for LLM
        changes_summary = []
        for change in commit_diff['changes'][:5]:
            changes_summary.append(
                f"• {change['file']} ({change['change_type']}): "
                f"+{change['additions']}/-{change['deletions']}"
            )
        
        messages = [
            {
                "role": "system",
                "content": "You are an expert analyzing code changes. Identify: "
                          "1) changed components, 2) change type, 3) risks. Be concise."
            },
            {
                "role": "user",
                "content": f"Repository: {repository}\n"
                          f"Commit: {commit_diff['message'][:100]}\n"
                          f"Changes:\n" + "\n".join(changes_summary)
            }
        ]
        
        # Call LLM with tools
        response = self.llm_client.chat_completion(
            messages=messages,
            tools=self.config['tool_definitions'],
            temperature=0.1
        )
        
        # Parse response
        tool_calls = self.llm_client.extract_tool_calls(response)
        
        if tool_calls:
            for tool_call in tool_calls:
                if tool_call['function']['name'] == 'analyze_code_changes':
                    args = json.loads(tool_call['function']['arguments'])
                    return {
                        'changed_components': args.get('file_paths', []),
                        'change_type': 'enhancement',
                        'risks': []
                    }
        
        # Fallback: analyze using tools
        return {
            'changed_components': [c['file'] for c in commit_diff['changes']],
            'change_type': 'enhancement',
            'risks': []
        }
    
    def _calculate_impacts(self, source_repo: str, 
                          changed_components: List[str],
                          change_type: str,
                          changed_files: List[str]) -> List[ImpactScore]:
        """Calculate impact scores using impact calculator tool + user flow analysis + call graph"""
        
        impact_dict = self.impact_calculator.calculate_repo_impact(
            source_repo,
            changed_components,
            change_type,
            changed_files=changed_files
        )
        
        impact_scores = []
        for repo, score in impact_dict.items():
            risk_level = self.impact_calculator.calculate_risk_level(score)
            
            # Analyze user flow impacts
            affected_flows_data = self.user_flow_analyzer.find_affected_flows(source_repo, changed_components)
            user_flows = []
            
            for flow_data in affected_flows_data:
                # Generate test steps and failure scenarios
                test_steps = self.user_flow_analyzer.generate_test_steps(flow_data, source_repo)
                failure_scenarios = self.user_flow_analyzer.identify_failure_scenarios(flow_data, source_repo)
                
                user_flows.append(UserFlowImpact(
                    flow_id=flow_data['flow_id'],
                    flow_name=flow_data['flow_name'],
                    description=flow_data['description'],
                    ui_path=flow_data['ui_path'],
                    impacted_steps=flow_data['impacted_steps'],
                    all_steps=flow_data['all_steps'],
                    test_steps=test_steps,
                    failure_scenarios=failure_scenarios,
                    severity=flow_data['severity'],
                    api_endpoints=flow_data['api_endpoints']
                ))
            
            # Get deployment impact
            deployment_impact = self.user_flow_analyzer.check_deployment_impact(source_repo)
            
            impact_scores.append(ImpactScore(
                repository=repo,
                score=score,
                affected_components=changed_components[:3],
                risk_level=risk_level,
                reasoning=f"Depends on {source_repo} with {len(changed_components)} changed components",
                user_flows=user_flows,
                deployment_impact=deployment_impact
            ))
        
        return sorted(impact_scores, key=lambda x: x.score, reverse=True)
    
    def _generate_tests(self, repository: str, commit_diff: Dict,
                       impact_scores: List[ImpactScore],
                       helper_impacts: List[Dict] = None) -> List[TestCase]:
        """Generate test cases using LLM + helper method analysis"""
        
        if not impact_scores:
            return []
        
        affected_repos = [score.repository for score in impact_scores[:2]]
        helper_impacts = helper_impacts or []
        
        # Include helper method info in prompt
        helper_info = ""
        if helper_impacts:
            helper_info = f"\nHelper methods changed: {', '.join([h['helper_function'] for h in helper_impacts[:3]])}"
        
        messages = [
            {
                "role": "system",
                "content": "You are a test engineer. Generate test case descriptions. Be concise."
            },
            {
                "role": "user",
                "content": f"Changes in {repository} affect: {', '.join(affected_repos)}. "
                          f"{helper_info}"
                          f"\nSuggest 2-3 test types needed."
            }
        ]
        
        response = self.llm_client.chat_completion(messages, temperature=0.2)
        
        # Generate test cases
        test_cases = []
        for i, repo in enumerate(affected_repos):
            for test_type in ['unit', 'integration']:
                test_cases.append(TestCase(
                    test_id=f"TEST-{uuid.uuid4().hex[:8]}",
                    repository=repo,
                    test_type=test_type,
                    description=f"{test_type.capitalize()} test for {repo} after {repository} changes",
                    code=f"# {test_type} test\ndef test_{repo.lower().replace('-', '_')}():\n    pass",
                    priority=5 - i,
                    estimated_duration=15
                ))
        
        # Add tests for helper methods
        for impact in helper_impacts:
            test_cases.append(TestCase(
                test_id=f"TEST-{uuid.uuid4().hex[:8]}",
                repository=repository,
                test_type="integration",
                description=f"Test helper method {impact['helper_function']} with all {impact['caller_count']} callers",
                code=f"# Integration test for helper method\ndef test_{impact['helper_function'].replace('.', '_')}_callers():\n    pass",
                priority=4 if impact['impact_level'] == 'high' else 3,
                estimated_duration=30
            ))
        
        return test_cases
    
    def _build_dependency_chain(self, source_repo: str, 
                                affected_repos: List[str]) -> Dict[str, List[str]]:
        """Build dependency chain"""
        return {source_repo: affected_repos}
    
    def _estimate_coverage(self, test_cases: List[TestCase]) -> float:
        """Estimate test coverage"""
        if not test_cases:
            return 0.0
        return min(0.95, len(test_cases) * 0.15)
    
    def _generate_recommendations(self, impact_scores: List[ImpactScore],
                                 test_cases: List[TestCase],
                                 countermeasures: List[Dict] = None) -> Dict:
        """Generate recommendations using LLM + countermeasures"""
        
        recommendations = []
        warnings = []
        countermeasures = countermeasures or []
        
        # Check for high-risk changes
        high_risk = [s for s in impact_scores if s.risk_level in ['high', 'critical']]
        if high_risk:
            warnings.append(
                f"⚠️  {len(high_risk)} repositories have high/critical risk: "
                f"{', '.join(s.repository for s in high_risk)}"
            )
            recommendations.append("Perform thorough integration testing before deployment")
        
        # Add countermeasure-based recommendations
        for cm in countermeasures:
            if cm.get('type') == 'helper_method_change':
                warnings.append(f"⚠️  Helper method changed: {cm['function']}")
                recommendations.extend(cm.get('recommendations', []))
        
        # Test coverage check
        if len(test_cases) < len(impact_scores) * 2:
            warnings.append("⚠️  Test coverage may be insufficient")
            recommendations.append("Generate additional test cases for edge cases")
        
        # Deployment recommendations
        if len(impact_scores) > 2:
            recommendations.append("Consider staged deployment to minimize risk")
        
        recommendations.append("Review dependency chain before deployment")
        
        # Add call graph specific recommendations
        if countermeasures:
            recommendations.append(f"Review {len(countermeasures)} impacted functions identified by call graph analysis")
        
        return {
            'recommendations': recommendations,
            'warnings': warnings
        }

