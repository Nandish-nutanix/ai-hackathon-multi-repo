"""
Tools for analyzing user flow impacts
"""
from typing import List, Dict, Set

class UserFlowAnalyzer:
    """Analyze impacts on user-triggered workflows"""
    
    def __init__(self, user_flows: Dict, deployment_config: Dict):
        self.user_flows = user_flows
        self.deployment_config = deployment_config
    
    def find_affected_flows(self, repository: str, changed_components: List[str]) -> List[Dict]:
        """Find all user flows affected by changes in a repository"""
        affected_flows = []
        
        for flow_id, flow in self.user_flows.items():
            if repository not in flow['affected_by_repos']:
                continue
            
            # Check if any step involves the changed components
            impacted_steps = []
            for step in flow['steps']:
                if step['repository'] == repository:
                    # Check if component is affected
                    if any(comp in step.get('component', '') for comp in changed_components):
                        impacted_steps.append(step)
                    # Or if no specific component match, include if repo matches
                    elif not changed_components:
                        impacted_steps.append(step)
            
            if impacted_steps or not changed_components:
                affected_flows.append({
                    'flow_id': flow_id,
                    'flow_name': flow['name'],
                    'description': flow['description'],
                    'impacted_steps': impacted_steps if impacted_steps else flow['steps'],
                    'all_steps': flow['steps'],
                    'api_endpoints': flow['api_endpoints'],
                    'ui_path': flow['ui_path'],
                    'severity': self._calculate_flow_severity(flow, impacted_steps)
                })
        
        return affected_flows
    
    def _calculate_flow_severity(self, flow: Dict, impacted_steps: List[Dict]) -> str:
        """Calculate severity of impact on user flow"""
        if not impacted_steps:
            return "low"
        
        total_steps = len(flow['steps'])
        impacted_count = len(impacted_steps)
        
        # If more than 50% steps impacted, it's high severity
        if impacted_count / total_steps > 0.5:
            return "high"
        elif impacted_count / total_steps > 0.25:
            return "medium"
        else:
            return "low"
    
    def generate_test_steps(self, affected_flow: Dict, repository: str) -> List[Dict]:
        """Generate detailed test steps for affected flow"""
        test_steps = []
        
        # Pre-requisites
        test_steps.append({
            'phase': 'Setup',
            'step_num': 0,
            'action': 'Setup test environment',
            'details': f'Ensure {repository} is deployed with latest changes',
            'validation': 'Verify all services are running',
            'expected_result': 'System is healthy and ready'
        })
        
        # Test each step in the user flow
        for i, step in enumerate(affected_flow['all_steps'], 1):
            is_impacted = any(s['step'] == step['step'] for s in affected_flow['impacted_steps'])
            
            test_steps.append({
                'phase': 'Execution',
                'step_num': i,
                'action': step['action'],
                'details': f"Test step: {step['action']}",
                'validation': f"Verify {step['component']} responds correctly" if 'component' in step else "Verify operation completes",
                'expected_result': 'Step completes without errors',
                'impacted': is_impacted,
                'component': step.get('component', 'N/A'),
                'repository': step.get('repository', 'N/A')
            })
        
        # Post-validation
        test_steps.append({
            'phase': 'Validation',
            'step_num': len(affected_flow['all_steps']) + 1,
            'action': 'Verify end-to-end flow completion',
            'details': f'Confirm {affected_flow["flow_name"]} completed successfully',
            'validation': 'Check logs, UI state, and data consistency',
            'expected_result': 'Flow completed with expected outcome'
        })
        
        return test_steps
    
    def identify_failure_scenarios(self, affected_flow: Dict, repository: str) -> List[Dict]:
        """Identify potential failure scenarios"""
        scenarios = []
        
        for step in affected_flow['impacted_steps']:
            scenarios.append({
                'step': step['step'],
                'action': step['action'],
                'failure_type': 'API Failure',
                'description': f"API call fails in {step.get('component', 'component')}",
                'impact': f"User cannot proceed with {affected_flow['flow_name']}",
                'symptom': 'Error message displayed in UI or API timeout',
                'severity': 'high' if step['step'] < 3 else 'medium'
            })
            
            scenarios.append({
                'step': step['step'],
                'action': step['action'],
                'failure_type': 'Data Inconsistency',
                'description': f"Incorrect data returned from {repository}",
                'impact': f"User sees stale or incorrect information",
                'symptom': 'UI displays wrong values or outdated status',
                'severity': 'medium'
            })
        
        # Add critical flow failure
        scenarios.append({
            'step': 'All',
            'action': 'Complete workflow',
            'failure_type': 'Workflow Failure',
            'description': f"Changes in {repository} break the entire {affected_flow['flow_name']}",
            'impact': 'Critical feature unavailable to users',
            'symptom': f"Users cannot access {affected_flow['ui_path']}",
            'severity': 'critical'
        })
        
        return scenarios
    
    def check_deployment_impact(self, repository: str) -> Dict:
        """Check deployment configuration impact"""
        if repository not in self.deployment_config:
            return {}
        
        config = self.deployment_config[repository]
        
        return {
            'deployment_order': config['deployment_order'],
            'depends_on': config['depends_on'],
            'deployment_method': config['deployment_method'],
            'services_to_restart': config['restart_required'],
            'config_files': config['config_files'],
            'dependent_repos': [
                repo for repo, conf in self.deployment_config.items()
                if repository in conf['depends_on']
            ]
        }
    
    def is_user_impacting_change(self, repository: str, changed_files: List[str]) -> bool:
        """Determine if change impacts user-facing functionality"""
        # Check if repository is user-facing
        for repo_config in [r for r in [] if r.get('name') == repository]:
            if repo_config.get('user_facing', False):
                return True
        
        # Check if any changed file is in API or UI paths
        user_impacting_patterns = [
            '/api/', '/ui/', '/rest/', '/v1/', '/v2/', 
            'endpoint', 'handler', 'controller', 'view'
        ]
        
        for file in changed_files:
            if any(pattern in file.lower() for pattern in user_impacting_patterns):
                return True
        
        return False

