"""
Enhanced HTML report generator with detailed tables for user flows and test steps
"""
from typing import List
from models.impact_report import ImpactReport
from datetime import datetime

class EnhancedHTMLReportGenerator:
    """Generate comprehensive HTML reports with detailed tables"""
    
    def __init__(self, llm_model_name: str):
        self.llm_model_name = llm_model_name
    
    def generate(self, reports: List[ImpactReport], output_path: str):
        """Generate HTML report from multiple analysis reports"""
        
        # Filter out reports with no user impact if requested
        user_impacting_reports = [r for r in reports if r.user_impacting or r.impact_scores]
        
        # Summary statistics
        total_commits = len(reports)
        user_impacting_commits = len([r for r in reports if r.user_impacting])
        total_flows = sum(r.total_user_flows_affected for r in reports)
        high_risk = sum(1 for r in reports for s in r.impact_scores if s.risk_level in ['high', 'critical'])
        
        # Build summary section
        summary_html = f"""
        <div class="summary-grid">
            <div class="summary-card">
                <div class="summary-number">{total_commits}</div>
                <div class="summary-label">Total Commits</div>
            </div>
            <div class="summary-card">
                <div class="summary-number">{user_impacting_commits}</div>
                <div class="summary-label">User Impacting</div>
            </div>
            <div class="summary-card">
                <div class="summary-number">{total_flows}</div>
                <div class="summary-label">Affected User Flows</div>
            </div>
            <div class="summary-card warning">
                <div class="summary-number">{high_risk}</div>
                <div class="summary-label">High/Critical Risk</div>
            </div>
        </div>
        """
        
        # Build detailed reports - only showing those with impacts
        reports_html = ""
        for i, report in enumerate(user_impacting_reports, 1):
            reports_html += self._generate_report_section(report, i)
        
        # Fill template
        html = self._get_html_template()
        html = html.replace("{{SUMMARY}}", summary_html)
        html = html.replace("{{REPORTS}}", reports_html)
        html = html.replace("{{TIMESTAMP}}", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        html = html.replace("{{LLM_MODEL}}", self.llm_model_name)
        html = html.replace("{{TOTAL_COMMITS}}", str(total_commits))
        html = html.replace("{{USER_IMPACTING}}", str(user_impacting_commits))
        
        # Save to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✅ Enhanced HTML report generated: {output_path}")
    
    def _generate_report_section(self, report: ImpactReport, index: int) -> str:
        """Generate HTML for a single report with detailed tables"""
        
        # Changed files summary
        changed_files_html = ""
        for file in report.changed_files[:10]:
            changed_files_html += f'<li><code>{file}</code></li>'
        if len(report.changed_files) > 10:
            changed_files_html += f'<li><em>... and {len(report.changed_files) - 10} more files</em></li>'
        
        # Impact details for each affected repository
        impact_details_html = ""
        for score in report.impact_scores:
            impact_details_html += self._generate_impact_details_table(score, report.source_repository)
        
        if not report.impact_scores:
            impact_details_html = '<div class="no-impact">✅ No cross-repository impact detected</div>'
        
        return f"""
        <div class="report-section">
            <div class="report-header">
                <h2>Analysis #{index}: {report.source_repository}</h2>
                <div class="report-meta">
                    <span>Commit: <code>{report.source_commit[:12]}</code></span>
                    <span>Time: {report.timestamp.strftime('%Y-%m-%d %H:%M')}</span>
                    <span class="{'user-impact-yes' if report.user_impacting else 'user-impact-no'}">
                        {'👤 USER IMPACTING' if report.user_impacting else '⚪ Internal Change'}
                    </span>
                </div>
            </div>
            
            <div class="change-summary">
                <strong>📝 Change Summary:</strong> {report.change_summary}
            </div>
            
            <div class="section">
                <h3>📂 Changed Files ({len(report.changed_files)})</h3>
                <ul class="file-list">{changed_files_html}</ul>
            </div>
            
            <div class="section">
                <h3>📊 Impact Analysis & User Flows</h3>
                {impact_details_html}
            </div>
            
            <div class="section">
                <h3>🚀 Deployment Information</h3>
                <div class="deployment-info">
                    <strong>Deployment Order:</strong> {' → '.join(report.deployment_order)}
                    <br><strong>Estimated Effort:</strong> {report.estimated_effort_hours} hours
                </div>
            </div>
            
            <div class="section">
                <h3>💡 Recommendations & Warnings</h3>
                {''.join(f'<div class="warning-item">⚠️ {w}</div>' for w in report.warnings)}
                {''.join(f'<div class="recommendation-item">📌 {r}</div>' for r in report.recommendations)}
            </div>
        </div>
        """
    
    def _generate_impact_details_table(self, score, source_repo: str) -> str:
        """Generate detailed impact table for a repository"""
        
        risk_class = f"risk-{score.risk_level}"
        
        html = f"""
        <div class="impact-detail-section {risk_class}">
            <h4>
                <span class="risk-badge-{score.risk_level}">{score.risk_level.upper()}</span>
                {score.repository}
                <span class="impact-score-badge">Impact: {score.score:.2f}</span>
            </h4>
            <p class="reasoning"><strong>Reasoning:</strong> {score.reasoning}</p>
        """
        
        # Deployment Impact Table
        if score.deployment_impact:
            html += """
            <div class="table-container">
                <h5>🚀 Deployment Impact</h5>
                <table class="impact-table">
                    <thead>
                        <tr>
                            <th>Property</th>
                            <th>Details</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            dep = score.deployment_impact
            html += f"""
                        <tr><td>Deployment Order</td><td>{dep.get('deployment_order', 'N/A')}</td></tr>
                        <tr><td>Depends On</td><td>{', '.join(dep.get('depends_on', [])) or 'None'}</td></tr>
                        <tr><td>Deployment Method</td><td>{dep.get('deployment_method', 'N/A')}</td></tr>
                        <tr><td>Services to Restart</td><td>{', '.join(dep.get('services_to_restart', [])) or 'None'}</td></tr>
                        <tr><td>Dependent Repos</td><td>{', '.join(dep.get('dependent_repos', [])) or 'None'}</td></tr>
            """
            html += """
                    </tbody>
                </table>
            </div>
            """
        
        # User Flow Impact Tables
        if score.user_flows:
            html += f'<div class="user-flows-section"><h5>👤 Affected User Workflows ({len(score.user_flows)})</h5>'
            
            for flow in score.user_flows:
                html += self._generate_user_flow_table(flow, source_repo)
            
            html += '</div>'
        
        html += "</div>"
        return html
    
    def _generate_user_flow_table(self, flow, source_repo: str) -> str:
        """Generate detailed table for a user flow"""
        
        severity_class = f"severity-{flow.severity}"
        
        html = f"""
        <div class="user-flow {severity_class}">
            <div class="flow-header">
                <h6>🔄 {flow.flow_name}</h6>
                <span class="severity-badge {severity_class}">{flow.severity.upper()}</span>
            </div>
            <p class="flow-description"><strong>Description:</strong> {flow.description}</p>
            <p class="flow-path"><strong>UI Path:</strong> <code>{flow.ui_path}</code></p>
            <p class="flow-apis"><strong>API Endpoints:</strong> {', '.join(f'<code>{api}</code>' for api in flow.api_endpoints)}</p>
            
            <div class="table-container">
                <h6>📋 Workflow Steps</h6>
                <table class="flow-table">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Action</th>
                            <th>Repository</th>
                            <th>Component</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        impacted_steps = {s['step'] for s in flow.impacted_steps}
        for step in flow.all_steps:
            is_impacted = step['step'] in impacted_steps
            status_class = "impacted" if is_impacted else "normal"
            status_text = "⚠️ IMPACTED" if is_impacted else "✓"
            
            html += f"""
                        <tr class="{status_class}">
                            <td>{step['step']}</td>
                            <td>{step['action']}</td>
                            <td>{step.get('repository', 'N/A')}</td>
                            <td>{step.get('component', 'N/A')}</td>
                            <td class="status-{status_class}">{status_text}</td>
                        </tr>
            """
        
        html += """
                    </tbody>
                </table>
            </div>
            
            <div class="table-container">
                <h6>🧪 Test Steps with Validation</h6>
                <table class="test-steps-table">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Phase</th>
                            <th>Action</th>
                            <th>Validation</th>
                            <th>Expected Result</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        for test_step in flow.test_steps:
            impacted = test_step.get('impacted', False)
            row_class = "test-impacted" if impacted else ""
            
            html += f"""
                        <tr class="{row_class}">
                            <td>{test_step['step_num']}</td>
                            <td><span class="phase-badge phase-{test_step['phase'].lower()}">{test_step['phase']}</span></td>
                            <td>{test_step['action']}</td>
                            <td>{test_step['validation']}</td>
                            <td>{test_step['expected_result']}</td>
                        </tr>
            """
        
        html += """
                    </tbody>
                </table>
            </div>
            
            <div class="table-container">
                <h6>⚠️ Potential Failure Scenarios</h6>
                <table class="failure-table">
                    <thead>
                        <tr>
                            <th>Step</th>
                            <th>Failure Type</th>
                            <th>Description</th>
                            <th>User Impact</th>
                            <th>Symptoms</th>
                            <th>Severity</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        for scenario in flow.failure_scenarios:
            sev_class = f"sev-{scenario['severity']}"
            
            html += f"""
                        <tr class="{sev_class}">
                            <td>{scenario['step']}</td>
                            <td><strong>{scenario['failure_type']}</strong></td>
                            <td>{scenario['description']}</td>
                            <td>{scenario['impact']}</td>
                            <td>{scenario['symptom']}</td>
                            <td><span class="severity-badge {sev_class}">{scenario['severity'].upper()}</span></td>
                        </tr>
            """
        
        html += """
                    </tbody>
                </table>
            </div>
        </div>
        """
        
        return html
    
    def _get_html_template(self) -> str:
        """Get enhanced HTML template with table styles"""
        return """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Multi-Repository Impact Analysis</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; color: #333; }
.container { max-width: 1400px; margin: 0 auto; background: white; border-radius: 16px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); overflow: hidden; }
.header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; text-align: center; }
.header h1 { font-size: 2.5em; margin-bottom: 10px; font-weight: 700; }
.header .subtitle { font-size: 1.2em; opacity: 0.9; margin-bottom: 10px; }
.header .meta { margin-top: 20px; font-size: 0.9em; opacity: 0.8; }
.summary-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; padding: 40px; background: #f8f9fa; }
.summary-card { background: white; padding: 30px; border-radius: 12px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: transform 0.2s; }
.summary-card:hover { transform: translateY(-5px); }
.summary-card.warning { background: #fff3cd; border-left: 4px solid #ff9800; }
.summary-number { font-size: 3em; font-weight: 700; color: #667eea; margin-bottom: 10px; }
.summary-card.warning .summary-number { color: #ff9800; }
.summary-label { font-size: 1em; color: #666; text-transform: uppercase; letter-spacing: 1px; }
.content { padding: 40px; }
.report-section { margin-bottom: 60px; border: 1px solid #e0e0e0; border-radius: 12px; overflow: hidden; }
.report-header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; }
.report-header h2 { font-size: 1.8em; margin-bottom: 10px; }
.report-meta { display: flex; gap: 20px; flex-wrap: wrap; font-size: 0.9em; opacity: 0.9; margin-top: 10px; }
.report-meta code { background: rgba(255,255,255,0.2); padding: 2px 8px; border-radius: 4px; }
.user-impact-yes { background: #ff5722; padding: 4px 12px; border-radius: 12px; font-weight: 700; }
.user-impact-no { background: rgba(255,255,255,0.2); padding: 4px 12px; border-radius: 12px; }
.change-summary { padding: 20px 30px; background: #e3f2fd; border-left: 4px solid #2196f3; margin: 20px 30px; border-radius: 4px; }
.section { padding: 30px; }
.section h3 { font-size: 1.5em; margin-bottom: 20px; color: #667eea; border-bottom: 2px solid #f0f0f0; padding-bottom: 10px; }
.file-list { list-style: none; padding: 10px; max-height: 150px; overflow-y: auto; background: #f5f5f5; border-radius: 4px; }
.file-list li { padding: 5px 10px; }
.file-list code { background: white; padding: 2px 6px; border-radius: 3px; }
.impact-detail-section { margin-bottom: 30px; padding: 20px; border-radius: 8px; background: #f8f9fa; }
.impact-detail-section h4 { margin-bottom: 15px; display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.risk-badge-low { background: #4caf50; color: white; padding: 4px 12px; border-radius: 4px; font-size: 0.85em; }
.risk-badge-medium { background: #ff9800; color: white; padding: 4px 12px; border-radius: 4px; font-size: 0.85em; }
.risk-badge-high { background: #f57c00; color: white; padding: 4px 12px; border-radius: 4px; font-size: 0.85em; }
.risk-badge-critical { background: #f44336; color: white; padding: 4px 12px; border-radius: 4px; font-size: 0.85em; }
.impact-score-badge { background: #2196f3; color: white; padding: 4px 12px; border-radius: 12px; font-size: 0.85em; }
.reasoning { color: #555; margin-bottom: 15px; padding: 10px; background: white; border-radius: 4px; }
.table-container { margin: 20px 0; }
.table-container h5, .table-container h6 { margin-bottom: 10px; color: #333; }
.impact-table, .flow-table, .test-steps-table, .failure-table { width: 100%; border-collapse: collapse; box-shadow: 0 2px 4px rgba(0,0,0,0.1); background: white; }
.impact-table th, .flow-table th, .test-steps-table th, .failure-table th { background: #667eea; color: white; padding: 12px; text-align: left; font-weight: 600; }
.impact-table td, .flow-table td, .test-steps-table td, .failure-table td { padding: 10px 12px; border-bottom: 1px solid #e0e0e0; }
.impact-table tr:hover, .flow-table tr:hover, .test-steps-table tr:hover, .failure-table tr:hover { background: #f5f5f5; }
.impacted { background: #fff3e0 !important; }
.test-impacted { background: #fff3e0 !important; }
.status-impacted { color: #f57c00; font-weight: 700; }
.status-normal { color: #4caf50; }
.phase-badge { padding: 4px 10px; border-radius: 12px; font-size: 0.85em; font-weight: 600; }
.phase-setup { background: #e3f2fd; color: #1976d2; }
.phase-execution { background: #f3e5f5; color: #7b1fa2; }
.phase-validation { background: #e8f5e9; color: #388e3c; }
.sev-low { background: #e8f5e9; }
.sev-medium { background: #fff3e0; }
.sev-high { background: #ffe0b2; }
.sev-critical { background: #ffebee; }
.user-flows-section { margin-top: 20px; }
.user-flow { margin: 20px 0; padding: 20px; border: 2px solid #e0e0e0; border-radius: 8px; background: white; }
.flow-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; flex-wrap: wrap; }
.flow-header h6 { font-size: 1.2em; color: #333; }
.severity-badge { padding: 4px 12px; border-radius: 12px; font-size: 0.85em; font-weight: 700; }
.severity-low { background: #4caf50; color: white; }
.severity-medium { background: #ff9800; color: white; }
.severity-high { background: #f44336; color: white; }
.flow-description, .flow-path, .flow-apis { margin: 8px 0; color: #555; }
.deployment-info { background: #f5f5f5; padding: 15px; border-radius: 6px; line-height: 1.8; }
.warning-item { background: #fff3cd; border-left: 4px solid #ff9800; padding: 12px; margin-bottom: 10px; border-radius: 4px; }
.recommendation-item { background: #e8f5e9; border-left: 4px solid #4caf50; padding: 12px; margin-bottom: 10px; border-radius: 4px; }
.no-impact { padding: 30px; text-align: center; background: #e8f5e9; border-radius: 8px; color: #2e7d32; font-size: 1.2em; margin: 20px 0; }
.footer { background: #f8f9fa; padding: 30px; text-align: center; color: #666; border-top: 2px solid #e0e0e0; }
code { background: #f5f5f5; padding: 2px 6px; border-radius: 3px; font-family: 'Courier New', monospace; font-size: 0.9em; }
</style>
</head>
<body>
<div class="container">
<div class="header">
<h1>🔍 Multi-Repository Impact Analysis</h1>
<div class="subtitle">Nutanix Prism Element Ecosystem - User Flow Impact Analysis</div>
<div class="meta">Generated: {{TIMESTAMP}} | LLM Model: <strong>{{LLM_MODEL}}</strong> | Commits: {{TOTAL_COMMITS}} | User Impacting: {{USER_IMPACTING}}</div>
</div>
{{SUMMARY}}
<div class="content">{{REPORTS}}</div>
<div class="footer">
<p><strong>Multi-Repository Dependency Impact Analysis System</strong></p>
<p>Powered by Nutanix AI (<strong>{{LLM_MODEL}}</strong>) | Agents = Tools + LLM</p>
<p style="margin-top: 10px; font-size: 0.9em;">Comprehensive user flow impact analysis with deployment configuration tracking</p>
</div>
</div>
</body>
</html>"""

