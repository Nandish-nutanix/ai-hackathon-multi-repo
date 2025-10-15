"""
╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║   ██████╗ ██████╗ ██████╗ ██████╗ ██╗     ███████╗                    ║
║   ██╔══██╗██╔══██╗██╔══██╗██╔══██╗██║     ██╔════╝                    ║
║   ██████╔╝██║  ██║██████╔╝██████╔╝██║     █████╗                      ║
║   ██╔══██╗██║  ██║██╔═══╝ ██╔═══╝ ██║     ██╔══╝                      ║
║   ██║  ██║██████╔╝██║     ██║     ███████╗███████╗                    ║
║   ╚═╝  ╚═╝╚═════╝ ╚═╝     ╚═╝     ╚══════╝╚══════╝                    ║
║                                                                          ║
║   Repository Impact Prediction & Propagation LLM Engine                 ║
║   ═════════════════════════════════════════════════════                 ║
║                                                                          ║
║   🌊 An Agentic AI Solution for Cross-Repository Impact Analysis        ║
║   🤖 Powered by Autonomous AI Agents + Intelligent Tools                ║
║   🧠 Nutanix AI Platform (pg-llama-33)                                  ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝

RIPPLE: Where AI Agents Predict the Impact of Every Code Change
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Architecture: Agentic AI (Autonomous Agents = Tools + LLM)
"""
import os
import sys
import json
import argparse
import warnings
from datetime import datetime, timedelta
from typing import List, Dict

warnings.filterwarnings('ignore')

from config import (
    NAI_ENDPOINT_API_KEY,
    NAI_LLM_ENDPOINT_URL,
    NAI_LLM_ENDPOINT_NAME,
    GITHUB_TOKEN,
    NUTANIX_REPOSITORIES,
    TOOL_DEFINITIONS,
    ANALYSIS_CONFIG
)
from agents.impact_analysis_agent import ImpactAnalysisAgent
from models.impact_report import ImpactReport
from utils.simple_html_reporter import SimpleHTMLReportGenerator
from utils.dynamic_config_builder import DynamicConfigBuilder


class MultiRepoImpactAnalyzer:
    """Main orchestrator for multi-repository impact analysis"""
    
    def __init__(self, repositories: List[Dict], user_flows: Dict = None, deployment_config: Dict = None):
        self.repositories = repositories
        
        # Build dynamic configurations if not provided
        config_builder = DynamicConfigBuilder(repositories)
        self.user_flows = user_flows if user_flows else config_builder.build_user_flows()
        self.deployment_config = deployment_config if deployment_config else config_builder.build_deployment_config()
        
        self.config = {
            'api_key': NAI_ENDPOINT_API_KEY,
            'endpoint_url': NAI_LLM_ENDPOINT_URL,
            'model_name': NAI_LLM_ENDPOINT_NAME,
            'github_token': GITHUB_TOKEN,
            'tool_definitions': TOOL_DEFINITIONS,
            'analysis_config': ANALYSIS_CONFIG,
            'user_flows': self.user_flows,
            'deployment_config': self.deployment_config
        }
        
        self.agent = ImpactAnalysisAgent(self.config)
        self.html_reporter = SimpleHTMLReportGenerator(
            NAI_LLM_ENDPOINT_NAME, 
            self.repositories,
            self.deployment_config
        )
    
    def initialize(self, local_repo_paths: Dict[str, str] = None):
        """
        Initialize the RIPPLE agentic AI system.
        
        Args:
            local_repo_paths: Optional dict of repo_name -> local_path for code scanning
        """
        print("=" * 70)
        print("🌊 RIPPLE - Repository Impact Prediction & Propagation LLM Engine")
        print("   Powered by Agentic AI (Autonomous Agents = Tools + LLM)")
        print("   Nutanix AI Platform")
        print("=" * 70)
        print()
        
        print(f"🤖 AI Agent Architecture: Autonomous & Intelligent")
        print(f"📊 LLM Model: {NAI_LLM_ENDPOINT_NAME}")
        print(f"🔗 Endpoint: {NAI_LLM_ENDPOINT_URL}")
        print(f"🎯 Max Tokens per Request: {ANALYSIS_CONFIG.get('max_tokens', 512)}")
        print(f"🔬 Code Scanning: {'Enabled' if ANALYSIS_CONFIG.get('enable_code_scanning') else 'Disabled'}")
        print(f"📞 Call Graph Analysis: {'Enabled' if ANALYSIS_CONFIG.get('enable_call_graph') else 'Disabled'}")
        print()
        
        print(f"📦 Repositories: {len(self.repositories)}")
        for repo in self.repositories:
            # Check access to each repository
            has_access = self.agent.github_tools.check_repository_access(repo['url'])
            access_icon = "✅" if has_access else "⚠️"
            print(f"   {access_icon} {repo['name']}: {repo['url']}")
        print()
        
        print(f"🔄 Dynamic Configuration:")
        print(f"   • User Flows: {len(self.user_flows)} flows detected")
        for flow_id in list(self.user_flows.keys())[:3]:
            print(f"      - {self.user_flows[flow_id]['name']}")
        print(f"   • Deployment Dependencies: {len(self.deployment_config)} repos configured")
        print()
        
        # Initialize dependency graph with code scanning
        self.agent.initialize_dependency_graph(self.repositories, repo_paths=local_repo_paths)
    
    def analyze_repository_commits(self, repository_name: str, 
                                   days: int = 15,
                                   local_path: str = None) -> List[ImpactReport]:
        """Analyze recent commits from a repository using GitHub API"""
        
        repo_config = next((r for r in self.repositories if r['name'] == repository_name), None)
        if not repo_config:
            raise ValueError(f"Repository {repository_name} not found")
        
        print(f"\n{'=' * 70}")
        print(f"📂 Analyzing: {repository_name}")
        print(f"⏰ Time range: Last {days} days")
        print(f"{'=' * 70}\n")
        
        try:
            from tools.github_tools import GitHubTools
            github_tools = GitHubTools(GITHUB_TOKEN)
            
            # Fetch commits from GitHub API (no cloning needed!)
            print(f"🌐 Fetching commits via GitHub API...")
            since_date = datetime.now() - timedelta(days=days)
            api_commits = github_tools.get_commits_from_api(
                repo_config['url'], 
                since=since_date,
                branch="master"
            )
            
            max_commits = ANALYSIS_CONFIG.get('max_commits_per_repo', 10)
            commits_to_analyze = api_commits[:max_commits]
            
            print(f"✅ Found {len(api_commits)} commits via API, analyzing top {len(commits_to_analyze)}\n")
            
            if not commits_to_analyze:
                print("⚠️  No commits found in the specified time range")
                return []
            
            # Only clone if code scanning or call graph is enabled
            need_local_clone = (ANALYSIS_CONFIG.get('enable_code_scanning', False) or 
                              ANALYSIS_CONFIG.get('enable_call_graph', False))
            
            if need_local_clone:
                if not local_path:
                    local_path = f"/tmp/{repository_name}"
                print(f"📥 Cloning repository for code analysis to: {local_path}")
                github_tools.clone_or_update_repo(repo_config['url'], local_path)
                print(f"✅ Repository ready for code analysis\n")
            else:
                print(f"ℹ️  Skipping clone (code scanning disabled)\n")
                local_path = None
            
            # Analyze each commit
            reports = []
            for i, api_commit in enumerate(commits_to_analyze, 1):
                commit_sha = api_commit['sha']
                commit_msg = api_commit['commit']['message']
                
                print(f"{'─' * 70}")
                print(f"📝 Commit {i}/{len(commits_to_analyze)}: {commit_sha[:8]}")
                print(f"   {commit_msg.strip().split(chr(10))[0][:60]}...")
                print(f"{'─' * 70}")
                
                try:
                    report = self.agent.analyze_change_impact(
                        repository_name,
                        commit_sha,
                        local_path  # Will be None if no clone needed
                    )
                    reports.append(report)
                    self.print_report_summary(report)
                    
                except Exception as e:
                    print(f"⚠️  Error: {e}\n")
                    continue
            
            return reports
            
        except Exception as e:
            print(f"❌ Error accessing repository: {e}")
            print(f"   Make sure GITHUB_TOKEN is set and you have access to: {repo_config['url']}")
            return []
    
    def print_report_summary(self, report: ImpactReport):
        """Print brief report summary"""
        if report.user_impacting:
            print(f"   👤 User Impact: YES ({report.total_user_flows_affected} flows affected)")
        else:
            print(f"   👤 User Impact: No")
        
        if report.impact_scores:
            print(f"   📊 Impact: {len(report.impact_scores)} repos affected")
            for score in report.impact_scores[:2]:
                flows_text = f", {len(score.user_flows)} flows" if score.user_flows else ""
                print(f"      • {score.repository}: {score.risk_level} risk ({score.score:.2f}{flows_text})")
        else:
            print(f"   ✅ No cross-repo impact")
        
        print(f"   🧪 Tests: {len(report.generated_tests)} generated")
        print(f"   ⏱  Effort: {report.estimated_effort_hours}h\n")
    
    def generate_html_report(self, reports: List[ImpactReport], output_path: str):
        """Generate HTML report"""
        self.html_reporter.generate(reports, output_path)
    
    def save_json_report(self, reports: List[ImpactReport], output_path: str):
        """Save reports to JSON"""
        reports_data = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'llm_model': NAI_LLM_ENDPOINT_NAME,
                'total_commits': len(reports)
            },
            'reports': []
        }
        
        for report in reports:
            reports_data['reports'].append({
                'analysis_id': report.analysis_id,
                'timestamp': report.timestamp.isoformat(),
                'source_repository': report.source_repository,
                'source_commit': report.source_commit,
                'change_summary': report.change_summary,
                'affected_repositories': report.affected_repositories,
                'impact_scores': [
                    {
                        'repository': s.repository,
                        'score': s.score,
                        'risk_level': s.risk_level,
                        'reasoning': s.reasoning
                    }
                    for s in report.impact_scores
                ],
                'test_count': len(report.generated_tests),
                'test_coverage': report.test_coverage_estimate,
                'deployment_order': report.deployment_order,
                'estimated_effort_hours': report.estimated_effort_hours
            })
        
        with open(output_path, 'w') as f:
            json.dump(reports_data, f, indent=2)
        
        print(f"💾 JSON report saved: {output_path}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='RIPPLE - Repository Impact Prediction & Propagation LLM Engine\nAn Agentic AI Solution for Cross-Repository Impact Analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze last 5 days of commits from multiple repos
  python ripple.py --repos lcm-framework ntnx-api-lcm --days 5
  
  # Analyze specific repository with custom time range
  python ripple.py --repos lcm-framework --days 7
  
  # Analyze with code scanning disabled (faster)
  python ripple.py --repos lcm-networking --days 3 --disable-code-scan
  
  # Generate custom named reports
  python ripple.py --repos prism-ui-lcm-ui --days 2 --output-html my_report.html
        """
    )
    
    parser.add_argument('--repos', nargs='+', required=True,
                       help='Repository names to analyze (e.g., lcm-framework ntnx-api-lcm)')
    parser.add_argument('--days', type=int, default=5,
                       help='Number of days to analyze (default: 5)')
    parser.add_argument('--output-html', default='lcm_impact_report.html',
                       help='Output HTML file (default: lcm_impact_report.html)')
    parser.add_argument('--output-json', default='lcm_impact_report.json',
                       help='Output JSON file (default: lcm_impact_report.json)')
    parser.add_argument('--disable-code-scan', action='store_true',
                       help='Disable code scanning for dependencies')
    parser.add_argument('--disable-call-graph', action='store_true',
                       help='Disable call graph analysis')
    
    args = parser.parse_args()
    
    # Filter repositories based on user input
    requested_repos = set(args.repos)
    filtered_repositories = [
        repo for repo in NUTANIX_REPOSITORIES 
        if repo['name'] in requested_repos
    ]
    
    # Validate all requested repos exist
    found_repos = {repo['name'] for repo in filtered_repositories}
    missing_repos = requested_repos - found_repos
    if missing_repos:
        print(f"❌ Error: Unknown repositories: {', '.join(missing_repos)}")
        print(f"   Available repositories: {', '.join([r['name'] for r in NUTANIX_REPOSITORIES])}")
        sys.exit(1)
    
    # Initialize analyzer with filtered repositories
    print(f"🔧 Building dynamic configuration for {len(filtered_repositories)} repositories...")
    analyzer = MultiRepoImpactAnalyzer(filtered_repositories)
    
    # Clone repositories first for code scanning
    local_paths = {}
    for repo in filtered_repositories:
        local_path = f"/tmp/{repo['name']}"
        local_paths[repo['name']] = local_path
    
    analyzer.initialize(local_repo_paths=local_paths)
    
    all_reports = []
    
    try:
        # Multi-repository analysis with configurable time range
        for repo_name in args.repos:
            reports = analyzer.analyze_repository_commits(repo_name, days=args.days)
            all_reports.extend(reports)
        
        # Generate reports
        if all_reports:
            print(f"\n{'=' * 70}")
            print(f"📝 Generating Reports")
            print(f"{'=' * 70}\n")
            
            # HTML Report
            analyzer.generate_html_report(all_reports, args.output_html)
            
            # JSON Report
            analyzer.save_json_report(all_reports, args.output_json)
            
            print(f"\n{'=' * 70}")
            print(f"✅ Analysis Complete!")
            print(f"{'=' * 70}")
            print(f"\n📊 Summary:")
            print(f"   • Analyzed commits: {len(all_reports)}")
            print(f"   • User impacting commits: {len([r for r in all_reports if r.user_impacting])}")
            print(f"   • Total user flows affected: {sum(r.total_user_flows_affected for r in all_reports)}")
            print(f"   • LLM Model: {NAI_LLM_ENDPOINT_NAME}")
            print(f"   • Token Limit: {ANALYSIS_CONFIG['max_tokens']}")
            print(f"   • Time Range: Last {args.days} days")
            print(f"   • Code Scanning: {'Enabled' if not args.disable_code_scan else 'Disabled'}")
            print(f"   • Call Graph: {'Enabled' if not args.disable_call_graph else 'Disabled'}")
            print(f"   • HTML report: {args.output_html}")
            print(f"   • JSON report: {args.output_json}")
            
            # Summary statistics
            total_affected = sum(len(r.affected_repositories) for r in all_reports)
            total_tests = sum(len(r.generated_tests) for r in all_reports)
            high_risk = sum(1 for r in all_reports for s in r.impact_scores 
                          if s.risk_level in ['high', 'critical'])
            
            print(f"\n📈 Impact Analysis:")
            print(f"   • Total affected repos: {total_affected}")
            print(f"   • Total tests generated: {total_tests}")
            print(f"   • High/Critical risks: {high_risk}")
            print()
        else:
            print("\n⚠️  No commits to analyze")
        
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

