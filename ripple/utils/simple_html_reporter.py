"""
Simple HTML report generator with clean table format
"""
from typing import List, Dict
from models.impact_report import ImpactReport
from datetime import datetime

class SimpleHTMLReportGenerator:
    """Generate simple, clean HTML reports with table format"""
    
    def __init__(self, llm_model_name: str, repositories: List[Dict], deployment_config: Dict = None):
        self.llm_model_name = llm_model_name
        self.repositories = repositories
        self.deployment_config = deployment_config or {}
    
    def generate(self, reports: List[ImpactReport], output_path: str):
        """Generate simple HTML report"""
        
        # Summary statistics
        total_commits = len(reports)
        date_range = self._get_date_range(reports)
        
        # Build header
        header_html = self._generate_header()
        
        # Build summary
        summary_html = self._generate_summary(total_commits, date_range)
        
        # Build repository connections table
        connections_html = self._generate_connections_table()
        
        # Build main impact table
        table_html = self._generate_impact_table(reports)
        
        # Fill template
        html = self._get_html_template()
        html = html.replace("{{HEADER}}", header_html)
        html = html.replace("{{SUMMARY}}", summary_html)
        html = html.replace("{{CONNECTIONS}}", connections_html)
        html = html.replace("{{TABLE}}", table_html)
        html = html.replace("{{TIMESTAMP}}", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        # Save to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✅ Simple HTML report generated: {output_path}")
    
    def _generate_header(self) -> str:
        """Generate header with configuration details"""
        from config import ANALYSIS_CONFIG, NAI_LLM_ENDPOINT_URL
        
        return f"""
        <div class="header">
            <h1>Multi-Repository Impact Analysis Report</h1>
            <div class="config-details">
                <div class="config-item"><strong>LLM Model:</strong> {self.llm_model_name}</div>
                <div class="config-item"><strong>Endpoint:</strong> {NAI_LLM_ENDPOINT_URL}</div>
                <div class="config-item"><strong>Max Tokens:</strong> {ANALYSIS_CONFIG.get('max_tokens', 4096)}</div>
                <div class="config-item"><strong>Analysis Period:</strong> Last {ANALYSIS_CONFIG.get('days_to_analyze', 7)} days</div>
                <div class="config-item"><strong>Repositories:</strong> {len(self.repositories)}</div>
            </div>
        </div>
        """
    
    def _generate_summary(self, total_commits: int, date_range: str) -> str:
        """Generate analysis summary"""
        return f"""
        <div class="summary">
            <h2>Analysis Summary</h2>
            <div class="summary-grid">
                <div class="summary-item">
                    <div class="label">Total Commits Analyzed</div>
                    <div class="value">{total_commits}</div>
                </div>
                <div class="summary-item">
                    <div class="label">Analysis Duration</div>
                    <div class="value">{date_range}</div>
                </div>
                <div class="summary-item">
                    <div class="label">Repositories</div>
                    <div class="value">{len(self.repositories)}</div>
                </div>
            </div>
        </div>
        """
    
    def _generate_connections_table(self) -> str:
        """Generate repository connections table"""
        rows_html = ""
        for repo in self.repositories:
            repo_name = repo['name']
            config = self.deployment_config.get(repo_name, {})
            depends_on = ', '.join(config.get('depends_on', [])) or 'None'
            
            # Find dependents
            dependents = [r for r, c in self.deployment_config.items() if repo_name in c.get('depends_on', [])]
            dependents_str = ', '.join(dependents) or 'None'
            
            rows_html += f"""
            <tr>
                <td><strong>{repo_name}</strong></td>
                <td>{depends_on}</td>
                <td>{dependents_str}</td>
                <td>{config.get('deployment_order', 'N/A')}</td>
                <td>{config.get('deployment_method', 'N/A')}</td>
                <td>{'Yes' if repo.get('user_facing', False) else 'No'}</td>
            </tr>
            """
        
        return f"""
        <div class="connections-section">
            <h2>Repository Connections & Dependencies</h2>
            <table class="connections-table">
                <thead>
                    <tr>
                        <th>Repository</th>
                        <th>Depends On</th>
                        <th>Used By</th>
                        <th>Deploy Order</th>
                        <th>Deploy Method</th>
                        <th>User Facing</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
        </div>
        """
    
    def _generate_impact_table(self, reports: List[ImpactReport]) -> str:
        """Generate main impact analysis table"""
        
        rows_html = ""
        row_num = 0
        
        for report in reports:
            if not report.impact_scores:
                # No impact - single row
                row_num += 1
                rows_html += f"""
                <tr>
                    <td>{row_num}</td>
                    <td><strong>{report.source_repository}</strong></td>
                    <td><code>{report.source_commit[:8]}</code></td>
                    <td>{report.change_summary[:80]}...</td>
                    <td colspan="4" class="no-impact">No Cross-Repository Impact</td>
                    <td>{len(report.changed_files)}</td>
                </tr>
                """
            else:
                # Has impacts - one row per impacted repo
                for i, score in enumerate(report.impact_scores):
                    row_num += 1
                    
                    # Get user flows
                    flows = [f.flow_name for f in score.user_flows] if score.user_flows else []
                    flows_str = ', '.join(flows) if flows else 'None'
                    
                    # Components
                    components_str = ', '.join(score.affected_components[:3]) if score.affected_components else 'N/A'
                    
                    # Risk color
                    risk_class = f"risk-{score.risk_level}"
                    
                    # Only show source info on first row
                    if i == 0:
                        rows_html += f"""
                        <tr>
                            <td rowspan="{len(report.impact_scores)}">{row_num}</td>
                            <td rowspan="{len(report.impact_scores)}"><strong>{report.source_repository}</strong></td>
                            <td rowspan="{len(report.impact_scores)}"><code>{report.source_commit[:8]}</code></td>
                            <td rowspan="{len(report.impact_scores)}">{report.change_summary[:80]}...</td>
                            <td><strong>{score.repository}</strong></td>
                            <td>{components_str}</td>
                            <td>{flows_str}</td>
                            <td class="{risk_class}">{score.risk_level.upper()}</td>
                            <td rowspan="{len(report.impact_scores)}">{len(report.changed_files)}</td>
                        </tr>
                        """
                    else:
                        rows_html += f"""
                        <tr>
                            <td><strong>{score.repository}</strong></td>
                            <td>{components_str}</td>
                            <td>{flows_str}</td>
                            <td class="{risk_class}">{score.risk_level.upper()}</td>
                        </tr>
                        """
        
        return f"""
        <div class="table-section">
            <h2>Impact Analysis Details</h2>
            <table class="impact-table">
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Source Repository</th>
                        <th>Commit</th>
                        <th>Change Summary</th>
                        <th>Impacted Repository</th>
                        <th>Impacted Components</th>
                        <th>Impacted User Workflows</th>
                        <th>Risk Level</th>
                        <th>Files Changed</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
        </div>
        """
    
    def _get_date_range(self, reports: List[ImpactReport]) -> str:
        """Get date range of analyzed commits"""
        if not reports:
            return "N/A"
        
        dates = [r.timestamp for r in reports]
        min_date = min(dates)
        max_date = max(dates)
        
        if min_date.date() == max_date.date():
            return min_date.strftime("%Y-%m-%d")
        else:
            return f"{min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}"
    
    def _get_html_template(self) -> str:
        """Get simple HTML template"""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Multi-Repository Impact Analysis</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f7fa;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-radius: 8px;
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px 40px;
        }
        
        .header h1 {
            font-size: 2em;
            margin-bottom: 20px;
        }
        
        .config-details {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            background: rgba(255, 255, 255, 0.1);
            padding: 15px;
            border-radius: 6px;
        }
        
        .config-item {
            font-size: 0.95em;
        }
        
        .summary {
            padding: 30px 40px;
            background: #f8f9fa;
            border-bottom: 1px solid #e9ecef;
        }
        
        .summary h2 {
            font-size: 1.5em;
            margin-bottom: 20px;
            color: #495057;
        }
        
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }
        
        .summary-item {
            background: white;
            padding: 20px;
            border-radius: 6px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            text-align: center;
        }
        
        .summary-item .label {
            font-size: 0.9em;
            color: #6c757d;
            margin-bottom: 10px;
        }
        
        .summary-item .value {
            font-size: 2em;
            font-weight: 700;
            color: #667eea;
        }
        
        .connections-section,
        .table-section {
            padding: 30px 40px;
        }
        
        .connections-section h2,
        .table-section h2 {
            font-size: 1.5em;
            margin-bottom: 20px;
            color: #495057;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
            background: white;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        th {
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            font-size: 0.95em;
        }
        
        td {
            padding: 12px;
            border-bottom: 1px solid #e9ecef;
            font-size: 0.9em;
        }
        
        tr:hover {
            background: #f8f9fa;
        }
        
        .no-impact {
            text-align: center;
            color: #28a745;
            font-weight: 600;
        }
        
        .risk-low {
            background: #d4edda;
            color: #155724;
            font-weight: 600;
            text-align: center;
        }
        
        .risk-medium {
            background: #fff3cd;
            color: #856404;
            font-weight: 600;
            text-align: center;
        }
        
        .risk-high {
            background: #f8d7da;
            color: #721c24;
            font-weight: 600;
            text-align: center;
        }
        
        .risk-critical {
            background: #f5c6cb;
            color: #491217;
            font-weight: 700;
            text-align: center;
        }
        
        code {
            background: #f8f9fa;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }
        
        .footer {
            background: #f8f9fa;
            padding: 20px 40px;
            text-align: center;
            color: #6c757d;
            font-size: 0.9em;
            border-top: 1px solid #e9ecef;
        }
        
        @media print {
            body {
                background: white;
            }
            .container {
                box-shadow: none;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        {{HEADER}}
        {{SUMMARY}}
        {{CONNECTIONS}}
        {{TABLE}}
        <div class="footer">
            <p><strong>Generated:</strong> {{TIMESTAMP}} | <strong>Powered by:</strong> Nutanix AI Platform | <strong>Architecture:</strong> Agents = Tools + LLM</p>
        </div>
    </div>
</body>
</html>
        """

