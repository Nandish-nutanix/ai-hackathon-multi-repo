"""HTML report generator for impact analysis"""
from typing import List
from models.impact_report import ImpactReport
from datetime import datetime

class HTMLReportGenerator:
    """Generate beautiful HTML reports"""
    
    def __init__(self, llm_model_name: str):
        self.llm_model_name = llm_model_name
    
    def generate(self, reports: List[ImpactReport], output_path: str):
        """Generate HTML report from multiple analysis reports"""
        
        # Summary statistics
        total_commits = len(reports)
        total_affected_repos = len(set(
            repo for r in reports for repo in r.affected_repositories
        ))
        total_tests = sum(len(r.generated_tests) for r in reports)
        high_risk_count = sum(
            1 for r in reports 
            for s in r.impact_scores 
            if s.risk_level in ['high', 'critical']
        )
        
        # Build summary section
        summary_html = f"""
        <div class="summary-grid">
            <div class="summary-card">
                <div class="summary-number">{total_commits}</div>
                <div class="summary-label">Commits Analyzed</div>
            </div>
            <div class="summary-card">
                <div class="summary-number">{total_affected_repos}</div>
                <div class="summary-label">Affected Repositories</div>
            </div>
            <div class="summary-card">
                <div class="summary-number">{total_tests}</div>
                <div class="summary-label">Tests Generated</div>
            </div>
            <div class="summary-card warning">
                <div class="summary-number">{high_risk_count}</div>
                <div class="summary-label">High Risk Changes</div>
            </div>
        </div>
        """
        
        # Build detailed reports
        reports_html = ""
        for i, report in enumerate(reports, 1):
            reports_html += self._generate_report_section(report, i)
        
        # Fill template
        html = self._get_html_template()
        html = html.replace("{{SUMMARY}}", summary_html)
        html = html.replace("{{REPORTS}}", reports_html)
        html = html.replace("{{TIMESTAMP}}", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        html = html.replace("{{LLM_MODEL}}", self.llm_model_name)
        html = html.replace("{{TOTAL_COMMITS}}", str(total_commits))
        
        # Save to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✅ HTML report generated: {output_path}")
    
    def _generate_report_section(self, report: ImpactReport, index: int) -> str:
        """Generate HTML for a single report"""
        
        risk_emoji = {'low': '✅', 'medium': '⚠️', 'high': '🔶', 'critical': '🔴'}
        
        # Impact scores HTML
        impact_html = ""
        if report.impact_scores:
            for score in report.impact_scores:
                impact_html += f"""
                <div class="impact-item risk-{score.risk_level}">
                    <div class="impact-header">
                        <span class="risk-badge">{risk_emoji[score.risk_level]} {score.risk_level.upper()}</span>
                        <span class="repo-name">{score.repository}</span>
                        <span class="impact-score">Impact: {score.score:.2f}</span>
                    </div>
                    <div class="impact-detail">{score.reasoning}</div>
                </div>
                """
        else:
            impact_html = '<div class="no-impact">✅ No other repositories affected</div>'
        
        # Test cases HTML
        tests_html = ""
        for test in report.get_prioritized_tests()[:5]:
            stars = '⭐' * test.priority
            tests_html += f"""
            <div class="test-case">
                <div class="test-header">
                    <span class="test-id">{test.test_id}</span>
                    <span class="test-type">{test.test_type}</span>
                    <span class="test-priority">{stars}</span>
                </div>
                <div class="test-description">{test.description}</div>
            </div>
            """
        
        # Deployment order HTML
        deployment_html = "".join(f'<div class="deployment-step">{i}. {repo}</div>' 
                                  for i, repo in enumerate(report.deployment_order, 1))
        
        # Warnings HTML
        warnings_html = "".join(f'<div class="warning-item">⚠️ {w}</div>' for w in report.warnings)
        
        # Recommendations HTML
        recommendations_html = "".join(f'<div class="recommendation-item">📌 {r}</div>' 
                                      for r in report.recommendations)
        
        return f"""
        <div class="report-section">
            <div class="report-header">
                <h2>Report #{index}: {report.source_repository}</h2>
                <div class="report-meta">
                    <span>Commit: <code>{report.source_commit[:8]}</code></span>
                    <span>Time: {report.timestamp.strftime('%Y-%m-%d %H:%M')}</span>
                </div>
            </div>
            
            <div class="change-summary">
                <strong>Change:</strong> {report.change_summary[:150]}...
            </div>
            
            <div class="section">
                <h3>📊 Impact Analysis</h3>
                {impact_html}
            </div>
            
            <div class="section">
                <h3>🧪 Tests ({len(report.generated_tests)} total, {report.test_coverage_estimate*100:.1f}% coverage)</h3>
                {tests_html}
            </div>
            
            <div class="section">
                <h3>🚀 Deployment ({report.estimated_effort_hours}h effort)</h3>
                <div class="deployment-order">{deployment_html}</div>
            </div>
            
            <div class="section">
                <h3>💡 Recommendations</h3>
                {warnings_html}
                {recommendations_html}
            </div>
        </div>
        """
    
    def _get_html_template(self) -> str:
        """Get HTML template with CSS"""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Multi-Repository Impact Analysis Report</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; color: #333; }
        .container { max-width: 1200px; margin: 0 auto; background: white; border-radius: 16px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); overflow: hidden; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; text-align: center; }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; font-weight: 700; }
        .header .subtitle { font-size: 1.2em; opacity: 0.9; }
        .header .meta { margin-top: 20px; font-size: 0.9em; opacity: 0.8; }
        .summary-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; padding: 40px; background: #f8f9fa; }
        .summary-card { background: white; padding: 30px; border-radius: 12px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: transform 0.2s; }
        .summary-card:hover { transform: translateY(-5px); box-shadow: 0 8px 12px rgba(0,0,0,0.15); }
        .summary-card.warning { background: #fff3cd; border-left: 4px solid #ff9800; }
        .summary-number { font-size: 3em; font-weight: 700; color: #667eea; margin-bottom: 10px; }
        .summary-card.warning .summary-number { color: #ff9800; }
        .summary-label { font-size: 1em; color: #666; text-transform: uppercase; letter-spacing: 1px; }
        .content { padding: 40px; }
        .report-section { margin-bottom: 40px; border: 1px solid #e0e0e0; border-radius: 12px; overflow: hidden; }
        .report-header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; }
        .report-header h2 { font-size: 1.8em; margin-bottom: 10px; }
        .report-meta { display: flex; gap: 20px; flex-wrap: wrap; font-size: 0.9em; opacity: 0.9; }
        .report-meta code { background: rgba(255,255,255,0.2); padding: 2px 8px; border-radius: 4px; }
        .change-summary { padding: 20px 30px; background: #e3f2fd; border-left: 4px solid #2196f3; margin: 20px 30px; border-radius: 4px; }
        .section { padding: 30px; }
        .section h3 { font-size: 1.5em; margin-bottom: 20px; color: #667eea; border-bottom: 2px solid #f0f0f0; padding-bottom: 10px; }
        .impact-item { margin-bottom: 15px; padding: 15px; border-radius: 8px; border-left: 4px solid #ddd; }
        .impact-item.risk-low { background: #e8f5e9; border-left-color: #4caf50; }
        .impact-item.risk-medium { background: #fff3e0; border-left-color: #ff9800; }
        .impact-item.risk-high { background: #ffe0b2; border-left-color: #f57c00; }
        .impact-item.risk-critical { background: #ffebee; border-left-color: #f44336; }
        .impact-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; flex-wrap: wrap; gap: 10px; }
        .risk-badge { font-weight: 700; font-size: 0.9em; }
        .repo-name { font-size: 1.2em; font-weight: 600; }
        .impact-score { background: rgba(0,0,0,0.1); padding: 4px 12px; border-radius: 20px; font-size: 0.9em; }
        .impact-detail { margin-top: 10px; color: #555; }
        .no-impact { padding: 20px; text-align: center; background: #e8f5e9; border-radius: 8px; color: #2e7d32; font-size: 1.1em; }
        .test-case { background: #f5f5f5; padding: 15px; border-radius: 8px; margin-bottom: 15px; border-left: 3px solid #667eea; }
        .test-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; flex-wrap: wrap; gap: 10px; }
        .test-id { font-family: 'Courier New', monospace; background: #667eea; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.85em; }
        .test-type { background: #e0e0e0; padding: 2px 10px; border-radius: 12px; font-size: 0.85em; text-transform: uppercase; }
        .test-priority { font-size: 0.9em; }
        .test-description { color: #333; }
        .deployment-order { background: #f5f5f5; padding: 20px; border-radius: 8px; }
        .deployment-step { padding: 10px; margin-bottom: 5px; background: white; border-radius: 4px; font-weight: 500; }
        .warning-item { background: #fff3cd; border-left: 4px solid #ff9800; padding: 12px; margin-bottom: 10px; border-radius: 4px; }
        .recommendation-item { background: #e8f5e9; border-left: 4px solid #4caf50; padding: 12px; margin-bottom: 10px; border-radius: 4px; }
        .footer { background: #f8f9fa; padding: 30px; text-align: center; color: #666; border-top: 2px solid #e0e0e0; }
        code { background: #f5f5f5; padding: 2px 6px; border-radius: 3px; font-family: 'Courier New', monospace; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 Multi-Repository Impact Analysis</h1>
            <div class="subtitle">Nutanix AI Agent Workshop</div>
            <div class="meta">Generated: {{TIMESTAMP}} | LLM Model: <strong>{{LLM_MODEL}}</strong> | Analyzed: {{TOTAL_COMMITS}} commits</div>
        </div>
        {{SUMMARY}}
        <div class="content">{{REPORTS}}</div>
        <div class="footer">
            <p><strong>Multi-Repository Dependency Impact Analysis System</strong></p>
            <p>Powered by Nutanix AI (<strong>{{LLM_MODEL}}</strong>) | Generated automatically using AI agents</p>
            <p style="margin-top: 10px; font-size: 0.9em;">This report analyzes code changes and their impact across the Nutanix ecosystem.<br><strong>Agents = Tools + LLM</strong></p>
        </div>
    </div>
</body>
</html>"""

