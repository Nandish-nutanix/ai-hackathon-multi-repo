"""Impact analysis report models"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime

@dataclass
class UserFlowImpact:
    """Impact on a specific user workflow"""
    flow_id: str
    flow_name: str
    description: str
    ui_path: str
    impacted_steps: List[Dict]
    all_steps: List[Dict]
    test_steps: List[Dict]
    failure_scenarios: List[Dict]
    severity: str
    api_endpoints: List[str]

@dataclass
class ImpactScore:
    """Impact score for a repository"""
    repository: str
    score: float
    affected_components: List[str]
    risk_level: str
    reasoning: str
    user_flows: List[UserFlowImpact] = field(default_factory=list)
    deployment_impact: Optional[Dict] = None

@dataclass
class TestCase:
    """Generated test case"""
    test_id: str
    repository: str
    test_type: str
    description: str
    code: str
    priority: int
    estimated_duration: int

@dataclass
class ImpactReport:
    """Complete impact analysis report"""
    analysis_id: str
    timestamp: datetime
    source_repository: str
    source_commit: str
    change_summary: str
    changed_files: List[str]
    affected_repositories: List[str]
    impact_scores: List[ImpactScore]
    dependency_chain: Dict[str, List[str]]
    generated_tests: List[TestCase]
    test_coverage_estimate: float
    deployment_order: List[str]
    estimated_effort_hours: float
    recommendations: List[str]
    warnings: List[str]
    user_impacting: bool = False
    total_user_flows_affected: int = 0
    
    def get_high_risk_repos(self) -> List[str]:
        """Get repositories with high or critical risk"""
        return [
            score.repository for score in self.impact_scores
            if score.risk_level in ['high', 'critical']
        ]
    
    def get_prioritized_tests(self) -> List[TestCase]:
        """Get tests sorted by priority"""
        return sorted(self.generated_tests, key=lambda t: t.priority, reverse=True)
    
    def get_all_affected_flows(self) -> List[UserFlowImpact]:
        """Get all affected user flows across all impacted repos"""
        flows = []
        for score in self.impact_scores:
            flows.extend(score.user_flows)
        return flows
    
    def get_critical_failure_scenarios(self) -> List[Dict]:
        """Get all critical failure scenarios"""
        scenarios = []
        for flow in self.get_all_affected_flows():
            scenarios.extend([s for s in flow.failure_scenarios if s['severity'] == 'critical'])
        return scenarios

