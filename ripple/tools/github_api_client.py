"""
Enhanced GitHub API Client
Follows Single Responsibility Principle: Only handles GitHub API interactions
"""
import requests
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import time


class GitHubAPIClient:
    """
    GitHub REST API client for repository operations.
    
    Single Responsibility: GitHub API communication
    Open/Closed: Extendable for new endpoints without modifying existing code
    """
    
    BASE_URL = "https://api.github.com"
    
    def __init__(self, token: str):
        """
        Initialize GitHub API client.
        
        Args:
            token: GitHub personal access token
        """
        self.token = token
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        })
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Any:
        """
        Make an API request with error handling and rate limiting.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional request parameters
            
        Returns:
            Response JSON data
        """
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            
            # Handle rate limiting
            if response.status_code == 403 and 'X-RateLimit-Remaining' in response.headers:
                if response.headers['X-RateLimit-Remaining'] == '0':
                    reset_time = int(response.headers['X-RateLimit-Reset'])
                    wait_time = reset_time - int(time.time()) + 1
                    print(f"⏳ Rate limit reached. Waiting {wait_time}s...")
                    time.sleep(wait_time)
                    return self._make_request(method, endpoint, **kwargs)
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise ValueError(f"Repository not found or no access: {endpoint}")
            elif e.response.status_code == 401:
                raise ValueError("Invalid GitHub token or insufficient permissions")
            else:
                raise Exception(f"GitHub API error: {e}")
    
    def get_repository_info(self, owner: str, repo: str) -> Dict:
        """
        Get repository information.
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            Repository metadata
        """
        return self._make_request("GET", f"/repos/{owner}/{repo}")
    
    def get_recent_commits(self, owner: str, repo: str, 
                          since: datetime, 
                          until: Optional[datetime] = None,
                          branch: str = "master") -> List[Dict]:
        """
        Get commits from a repository within a time range.
        
        Args:
            owner: Repository owner
            repo: Repository name
            since: Start date
            until: End date (default: now)
            branch: Branch name (default: master)
            
        Returns:
            List of commit objects
        """
        params = {
            "sha": branch,
            "since": since.isoformat(),
            "per_page": 100
        }
        
        if until:
            params["until"] = until.isoformat()
        
        commits = []
        page = 1
        
        while True:
            params["page"] = page
            try:
                page_commits = self._make_request(
                    "GET", 
                    f"/repos/{owner}/{repo}/commits",
                    params=params
                )
                
                if not page_commits:
                    break
                
                commits.extend(page_commits)
                
                # GitHub limits to 100 per page, stop if we get less
                if len(page_commits) < 100:
                    break
                
                page += 1
                
            except Exception as e:
                print(f"⚠️  Warning: Could not fetch page {page}: {e}")
                break
        
        return commits
    
    def get_commit_details(self, owner: str, repo: str, sha: str) -> Dict:
        """
        Get detailed information about a specific commit.
        
        Args:
            owner: Repository owner
            repo: Repository name
            sha: Commit SHA
            
        Returns:
            Detailed commit information including files changed
        """
        return self._make_request("GET", f"/repos/{owner}/{repo}/commits/{sha}")
    
    def get_file_content(self, owner: str, repo: str, path: str, 
                        ref: Optional[str] = None) -> Dict:
        """
        Get content of a file from the repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            path: File path
            ref: Git reference (branch, tag, or commit SHA)
            
        Returns:
            File content and metadata
        """
        params = {"ref": ref} if ref else {}
        return self._make_request(
            "GET", 
            f"/repos/{owner}/{repo}/contents/{path}",
            params=params
        )
    
    def search_code(self, query: str, owner: str, repo: str) -> List[Dict]:
        """
        Search for code in a repository.
        
        Args:
            query: Search query
            owner: Repository owner
            repo: Repository name
            
        Returns:
            List of code search results
        """
        params = {
            "q": f"{query} repo:{owner}/{repo}",
            "per_page": 100
        }
        
        result = self._make_request("GET", "/search/code", params=params)
        return result.get("items", [])
    
    def get_repository_languages(self, owner: str, repo: str) -> Dict[str, int]:
        """
        Get languages used in the repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            Dictionary of language names to bytes of code
        """
        return self._make_request("GET", f"/repos/{owner}/{repo}/languages")
    
    def get_branches(self, owner: str, repo: str) -> List[Dict]:
        """
        Get all branches in the repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            List of branch objects
        """
        return self._make_request("GET", f"/repos/{owner}/{repo}/branches")
    
    def compare_commits(self, owner: str, repo: str, 
                       base: str, head: str) -> Dict:
        """
        Compare two commits to get differences.
        
        Args:
            owner: Repository owner
            repo: Repository name
            base: Base commit SHA
            head: Head commit SHA
            
        Returns:
            Comparison data including file changes
        """
        return self._make_request(
            "GET", 
            f"/repos/{owner}/{repo}/compare/{base}...{head}"
        )


class RepositoryParser:
    """
    Parse repository URLs and extract owner/repo information.
    
    Single Responsibility: URL parsing
    """
    
    @staticmethod
    def parse_github_url(url: str) -> tuple[str, str]:
        """
        Parse GitHub URL to extract owner and repository name.
        
        Args:
            url: GitHub repository URL
            
        Returns:
            Tuple of (owner, repo)
            
        Example:
            >>> parse_github_url("https://github.com/nutanix-core/lcm-framework")
            ('nutanix-core', 'lcm-framework')
        """
        # Remove trailing slashes and .git
        url = url.rstrip('/').replace('.git', '')
        
        # Handle various URL formats
        if url.startswith('https://github.com/'):
            parts = url.replace('https://github.com/', '').split('/')
        elif url.startswith('git@github.com:'):
            parts = url.replace('git@github.com:', '').split('/')
        else:
            raise ValueError(f"Invalid GitHub URL: {url}")
        
        if len(parts) < 2:
            raise ValueError(f"Invalid GitHub URL format: {url}")
        
        return parts[0], parts[1]


class CommitFilter:
    """
    Filter and process commits based on criteria.
    
    Single Responsibility: Commit filtering logic
    """
    
    @staticmethod
    def filter_by_files(commits: List[Dict], file_extensions: List[str]) -> List[Dict]:
        """
        Filter commits that touch files with specific extensions.
        
        Args:
            commits: List of commit objects
            file_extensions: List of file extensions (e.g., ['.py', '.js'])
            
        Returns:
            Filtered list of commits
        """
        filtered = []
        for commit in commits:
            if 'files' in commit:
                for file in commit['files']:
                    if any(file['filename'].endswith(ext) for ext in file_extensions):
                        filtered.append(commit)
                        break
        return filtered
    
    @staticmethod
    def exclude_merge_commits(commits: List[Dict]) -> List[Dict]:
        """
        Exclude merge commits from the list.
        
        Args:
            commits: List of commit objects
            
        Returns:
            List of non-merge commits
        """
        return [c for c in commits if len(c.get('parents', [])) <= 1]
    
    @staticmethod
    def get_commits_by_author(commits: List[Dict], author: str) -> List[Dict]:
        """
        Filter commits by author.
        
        Args:
            commits: List of commit objects
            author: Author name or email
            
        Returns:
            Commits by the specified author
        """
        return [
            c for c in commits 
            if c.get('commit', {}).get('author', {}).get('name') == author or
               c.get('commit', {}).get('author', {}).get('email') == author
        ]

