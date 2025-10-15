"""
Enhanced tools for interacting with GitHub repositories.

Integrates GitHubAPIClient for real API operations with local Git operations.
Follows Single Responsibility Principle.
"""
import requests
from typing import List, Dict, Optional
from datetime import datetime
from github import Github
import git
import os

from .github_api_client import GitHubAPIClient, RepositoryParser


class GitHubTools:
    """
    Enhanced GitHub operations tool.
    
    Combines API-based operations with local Git operations.
    Single Responsibility: GitHub repository management
    """
    
    def __init__(self, github_token: str):
        self.github = Github(github_token) if github_token else None
        self.api_client = GitHubAPIClient(github_token) if github_token else None
        self.session = requests.Session()
        self.parser = RepositoryParser()
    
    def get_commits_from_api(self, repo_url: str, since: datetime, 
                            until: Optional[datetime] = None,
                            branch: str = "master") -> List[Dict]:
        """
        Get commits using GitHub API (no local clone needed).
        
        Args:
            repo_url: GitHub repository URL
            since: Start date
            until: End date
            branch: Branch name
            
        Returns:
            List of commits with metadata
        """
        if not self.api_client:
            raise ValueError("GitHub token required for API access")
        
        owner, repo = self.parser.parse_github_url(repo_url)
        
        # Try master first, fallback to main
        try:
            commits = self.api_client.get_recent_commits(owner, repo, since, until, branch)
        except Exception as e:
            if branch == "master":
                print(f"   ℹ️  Trying 'main' branch instead of 'master'...")
                commits = self.api_client.get_recent_commits(owner, repo, since, until, "main")
            else:
                raise e
        
        return commits
    
    def get_commit_details_from_api(self, repo_url: str, sha: str) -> Dict:
        """
        Get detailed commit information from API.
        
        Args:
            repo_url: GitHub repository URL
            sha: Commit SHA
            
        Returns:
            Detailed commit data
        """
        if not self.api_client:
            raise ValueError("GitHub token required for API access")
        
        owner, repo = self.parser.parse_github_url(repo_url)
        return self.api_client.get_commit_details(owner, repo, sha)
    
    def clone_or_update_repo(self, repo_url: str, local_path: str) -> git.Repo:
        """
        Clone repository or update if already exists.
        
        Args:
            repo_url: GitHub repository URL
            local_path: Local directory path
            
        Returns:
            Git repository object
        """
        if os.path.exists(local_path):
            try:
                repo = git.Repo(local_path)
                origin = repo.remotes.origin
                origin.fetch()
                
                # Try to pull from current branch
                try:
                    origin.pull()
                except Exception as e:
                    print(f"   ℹ️  Could not pull latest changes: {e}")
                
                return repo
            except Exception as e:
                print(f"   ⚠️  Warning: Could not update repo: {e}")
                return git.Repo(local_path)
        else:
            print(f"   📥 Cloning repository...")
            return git.Repo.clone_from(repo_url, local_path)
    
    def get_commit_diff(self, repo_path: str, commit_hash: str) -> Dict:
        """
        Get detailed diff for a commit from local repository.
        
        Args:
            repo_path: Local repository path
            commit_hash: Commit SHA
            
        Returns:
            Commit diff data
        """
        repo = git.Repo(repo_path)
        commit = repo.commit(commit_hash)
        
        changes = []
        parent = commit.parents[0] if commit.parents else None
        
        if parent:
            diffs = commit.diff(parent, create_patch=True)
        else:
            diffs = commit.diff(None, create_patch=True)
        
        for diff in diffs:
            file_path = diff.a_path or diff.b_path
            changes.append({
                "file": file_path,
                "change_type": diff.change_type,
                "additions": str(diff.diff).count('\n+') if diff.diff else 0,
                "deletions": str(diff.diff).count('\n-') if diff.diff else 0,
                "diff": str(diff.diff)[:1000] if diff.diff else ""  # Increased limit
            })
        
        return {
            "commit": commit_hash,
            "message": commit.message.strip(),
            "author": str(commit.author.name),
            "timestamp": commit.committed_datetime,
            "changes": changes[:20]  # Increased limit
        }
    
    def check_repository_access(self, repo_url: str) -> bool:
        """
        Check if repository is accessible with current credentials.
        
        Args:
            repo_url: GitHub repository URL
            
        Returns:
            True if accessible, False otherwise
        """
        if not self.api_client:
            return False
        
        try:
            owner, repo = self.parser.parse_github_url(repo_url)
            self.api_client.get_repository_info(owner, repo)
            return True
        except Exception:
            return False

