"""
Dynamic configuration builder for user flows and dependencies
Builds configuration based on repository metadata
"""
from typing import List, Dict, Any


class DynamicConfigBuilder:
    """Dynamically builds user flows and deployment config from repository metadata"""
    
    def __init__(self, repositories: List[Dict]):
        self.repositories = repositories
        self.repo_map = {repo['name']: repo for repo in repositories}
    
    def build_deployment_config(self) -> Dict[str, Any]:
        """
        Dynamically build deployment configuration based on repository metadata.
        
        Architecture inference:
        - API layer (deployment_layer: 'api') -> deployed first (order 1)
        - Core layer (deployment_layer: 'core') -> deployed second (order 2)
        - Module/Testing layer -> deployed last (order 3+)
        
        Dependencies:
        - Core depends on API (if API exists)
        - Modules depend on Core
        - Testing depends on what it tests
        """
        deployment_config = {}
        
        # Group repos by deployment layer
        api_repos = [r for r in self.repositories if r.get('deployment_layer') == 'api']
        core_repos = [r for r in self.repositories if r.get('deployment_layer') == 'core']
        testing_repos = [r for r in self.repositories if r.get('deployment_layer') == 'testing']
        other_repos = [r for r in self.repositories 
                      if r.get('deployment_layer') not in ['api', 'core', 'testing']]
        
        # API layer repos (no dependencies)
        for repo in api_repos:
            deployment_config[repo['name']] = {
                'depends_on': [],
                'deployment_order': 1,
                'deployment_method': self._infer_deployment_method(repo),
                'services': self._infer_services(repo),
                'config_files': self._infer_config_files(repo),
                'restart_required': self._infer_restart_services(repo)
            }
        
        # Core repos (depend on API layer)
        api_repo_names = [r['name'] for r in api_repos]
        for repo in core_repos:
            deployment_config[repo['name']] = {
                'depends_on': api_repo_names,
                'deployment_order': 2,
                'deployment_method': self._infer_deployment_method(repo),
                'services': self._infer_services(repo),
                'config_files': self._infer_config_files(repo),
                'restart_required': self._infer_restart_services(repo)
            }
        
        # Module/Other repos (depend on core)
        core_repo_names = [r['name'] for r in core_repos]
        for repo in other_repos:
            deployment_config[repo['name']] = {
                'depends_on': core_repo_names if core_repo_names else api_repo_names,
                'deployment_order': 3,
                'deployment_method': self._infer_deployment_method(repo),
                'services': self._infer_services(repo),
                'config_files': self._infer_config_files(repo),
                'restart_required': self._infer_restart_services(repo)
            }
        
        # Testing repos (depend on what they test, usually core or modules)
        for repo in testing_repos:
            deployment_config[repo['name']] = {
                'depends_on': core_repo_names if core_repo_names else [],
                'deployment_order': 4,
                'deployment_method': self._infer_deployment_method(repo),
                'services': [],
                'config_files': [],
                'restart_required': []
            }
        
        return deployment_config
    
    def build_user_flows(self) -> Dict[str, Any]:
        """
        Dynamically build user flows based on repository operations and endpoints.
        
        Strategy:
        - Find user-facing repositories (user_facing: True)
        - Look at their operations to identify workflows
        - Build flow steps based on deployment layers (API -> Core -> Modules)
        - Map UI endpoints to flows
        """
        user_flows = {}
        
        # Get user-facing repos
        user_facing_repos = [r for r in self.repositories if r.get('user_facing', False)]
        
        if not user_facing_repos:
            # No user flows if no user-facing repos
            return {}
        
        # Find API and Core repos for flow construction
        api_repos = [r for r in self.repositories if r.get('deployment_layer') == 'api']
        core_repos = [r for r in self.repositories if r.get('deployment_layer') == 'core']
        
        # Build flows based on common operations
        operation_groups = self._group_operations_by_type()
        
        for operation_type, repos_with_op in operation_groups.items():
            flow_id = f"{operation_type}_flow"
            flow_name = self._humanize_operation_name(operation_type)
            
            # Build flow steps
            steps = self._build_flow_steps(operation_type, repos_with_op, api_repos, core_repos)
            
            # Collect affected repos and endpoints
            affected_repos = list(set([r['name'] for r in repos_with_op]))
            api_endpoints = self._collect_api_endpoints(repos_with_op)
            ui_path = self._infer_ui_path(operation_type, repos_with_op)
            
            user_flows[flow_id] = {
                'name': flow_name,
                'description': f"User performs {operation_type.replace('_', ' ')} operation",
                'steps': steps,
                'affected_by_repos': affected_repos,
                'api_endpoints': api_endpoints,
                'ui_path': ui_path
            }
        
        # If no specific operations found, create generic flows
        if not user_flows:
            user_flows = self._create_generic_flows(user_facing_repos, api_repos, core_repos)
        
        return user_flows
    
    def _group_operations_by_type(self) -> Dict[str, List[Dict]]:
        """Group repositories by operation types"""
        operation_groups = {}
        
        for repo in self.repositories:
            operations = repo.get('operations', [])
            for op in operations:
                # Extract operation category (e.g., "inventory_scan" -> "inventory")
                op_category = op.split('_')[0] if '_' in op else op
                
                if op_category not in operation_groups:
                    operation_groups[op_category] = []
                
                operation_groups[op_category].append(repo)
        
        return operation_groups
    
    def _build_flow_steps(self, operation_type: str, 
                         repos_with_op: List[Dict],
                         api_repos: List[Dict],
                         core_repos: List[Dict]) -> List[Dict]:
        """Build flow steps for an operation"""
        steps = []
        step_num = 1
        
        # Step 1: User initiates via API (if API layer exists)
        if api_repos:
            api_repo = api_repos[0]
            steps.append({
                'step': step_num,
                'action': f"User initiates {operation_type.replace('_', ' ')} via UI",
                'repository': api_repo['name'],
                'component': 'api_gateway'
            })
            step_num += 1
            
            # Step 2: API authentication
            if 'authentication' in api_repo.get('components', []):
                steps.append({
                    'step': step_num,
                    'action': "API authenticates and routes request",
                    'repository': api_repo['name'],
                    'component': 'authentication'
                })
                step_num += 1
        
        # Step 3+: Core processing
        for core_repo in core_repos:
            if core_repo in repos_with_op:
                for component in core_repo.get('components', []):
                    if operation_type in component or any(op.startswith(operation_type) for op in core_repo.get('operations', [])):
                        steps.append({
                            'step': step_num,
                            'action': f"System processes {operation_type.replace('_', ' ')} in {component}",
                            'repository': core_repo['name'],
                            'component': component
                        })
                        step_num += 1
        
        # Step final: API returns result
        if api_repos:
            api_repo = api_repos[0]
            steps.append({
                'step': step_num,
                'action': f"API returns {operation_type.replace('_', ' ')} result to user",
                'repository': api_repo['name'],
                'component': 'rest_handlers'
            })
        
        return steps
    
    def _collect_api_endpoints(self, repos: List[Dict]) -> List[str]:
        """Collect all API endpoints from repositories"""
        endpoints = []
        for repo in repos:
            endpoints.extend(repo.get('ui_endpoints', []))
        return list(set(endpoints))
    
    def _infer_ui_path(self, operation_type: str, repos: List[Dict]) -> str:
        """Infer UI path based on operation type"""
        # Common patterns
        if 'inventory' in operation_type:
            return "Prism UI -> Settings -> Upgrade Software -> Inventory"
        elif 'upgrade' in operation_type:
            return "Prism UI -> Settings -> Upgrade Software -> Upgrade"
        elif 'status' in operation_type:
            return "Prism UI -> Settings -> Upgrade Software -> Status"
        else:
            return f"Prism UI -> {operation_type.replace('_', ' ').title()}"
    
    def _create_generic_flows(self, user_facing_repos: List[Dict],
                            api_repos: List[Dict],
                            core_repos: List[Dict]) -> Dict[str, Any]:
        """Create generic flows when no specific operations are defined"""
        flows = {}
        
        # Generic data retrieval flow
        flows['generic_data_flow'] = {
            'name': 'Generic Data Retrieval',
            'description': 'User retrieves data from the system',
            'steps': [
                {'step': 1, 'action': 'User requests data via API', 
                 'repository': api_repos[0]['name'] if api_repos else user_facing_repos[0]['name'],
                 'component': 'api_gateway'},
                {'step': 2, 'action': 'System processes request',
                 'repository': core_repos[0]['name'] if core_repos else user_facing_repos[0]['name'],
                 'component': 'core'},
                {'step': 3, 'action': 'System returns data to user',
                 'repository': api_repos[0]['name'] if api_repos else user_facing_repos[0]['name'],
                 'component': 'rest_handlers'}
            ],
            'affected_by_repos': [r['name'] for r in (api_repos + core_repos + user_facing_repos)],
            'api_endpoints': self._collect_api_endpoints(user_facing_repos + api_repos),
            'ui_path': 'Prism UI -> Dashboard'
        }
        
        return flows
    
    def _humanize_operation_name(self, operation_type: str) -> str:
        """Convert operation_type to human-readable name"""
        return operation_type.replace('_', ' ').title() + ' Workflow'
    
    def _infer_deployment_method(self, repo: Dict) -> str:
        """Infer deployment method from repository metadata"""
        language = repo.get('language', '').lower()
        
        if language == 'python':
            return 'rpm'  # Common for Nutanix Python services
        elif language in ['javascript', 'typescript']:
            return 'npm'
        elif language == 'go':
            return 'binary'
        else:
            return 'tar'
    
    def _infer_services(self, repo: Dict) -> List[str]:
        """Infer system services from repository metadata"""
        services = []
        
        # API layer repos typically need nginx/api-gateway
        if repo.get('deployment_layer') == 'api':
            services.extend(['nginx', 'api-gateway'])
        
        # Core repos typically need genesis/ergon (Nutanix specific)
        if repo.get('deployment_layer') == 'core':
            services.extend(['genesis', 'ergon'])
        
        return services
    
    def _infer_config_files(self, repo: Dict) -> List[str]:
        """Infer config files from repository metadata"""
        repo_name = repo['name']
        
        # Nutanix convention: /home/nutanix/config/<service>.yml
        if repo.get('deployment_layer') in ['api', 'core']:
            return [f"/home/nutanix/config/{repo_name}.yml"]
        
        return []
    
    def _infer_restart_services(self, repo: Dict) -> List[str]:
        """Infer which services need restart after deployment"""
        services = self._infer_services(repo)
        
        # Typically the first service needs restart
        if services:
            return [services[0]]
        
        return []

