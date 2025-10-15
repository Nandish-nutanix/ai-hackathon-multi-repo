"""Tools for analyzing code changes"""
import re
from typing import List, Dict, Set

class CodeAnalyzer:
    """Analyze code changes for semantic understanding"""
    
    def analyze_change_impact(self, diff: str, file_path: str) -> Dict:
        """Analyze the impact of code changes"""
        lines_added = diff.count('\n+')
        lines_removed = diff.count('\n-')
        
        # Detect change types
        change_types = []
        if 'class ' in diff:
            change_types.append('class_modification')
        if 'def ' in diff:
            change_types.append('function_modification')
        if 'import ' in diff:
            change_types.append('dependency_change')
        
        magnitude = min(1.0, (lines_added + lines_removed) / 100.0)
        
        return {
            "file": file_path,
            "lines_added": lines_added,
            "lines_removed": lines_removed,
            "change_types": change_types,
            "magnitude": magnitude,
            "is_breaking": self._is_breaking_change(diff)
        }
    
    def _is_breaking_change(self, diff: str) -> bool:
        """Detect if a change is potentially breaking"""
        breaking_indicators = [
            r'-\s*def\s+\w+',
            r'-\s*class\s+\w+',
            r'raise\s+\w+Error',
        ]
        
        for pattern in breaking_indicators:
            if re.search(pattern, diff):
                return True
        return False

