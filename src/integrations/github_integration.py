"""
GitHub Integration Module
Auto-push agent outputs to GitHub with proper attribution and conflict handling.
"""
import os
import time
import logging
from typing import Optional, Dict, Any
from pathlib import Path
from github import Github, GithubException
from github.Repository import Repository
from github.ContentFile import ContentFile

logger = logging.getLogger(__name__)


class GitHubIntegration:
    """Handle GitHub operations with retry logic and conflict resolution."""
    
    def __init__(self, token: Optional[str] = None, repo_name: Optional[str] = None):
        """
        Initialize GitHub integration.
        
        Args:
            token: GitHub personal access token (defaults to GITHUB_TOKEN env var)
            repo_name: Repository name in format 'owner/repo'
        """
        self.token = token or os.getenv('GITHUB_TOKEN')
        if not self.token:
            raise ValueError("GitHub token not provided. Set GITHUB_TOKEN environment variable.")
        
        self.github = Github(self.token)
        self.user = self.github.get_user()
        self.repo_name = repo_name
        self.repo: Optional[Repository] = None
        
        if repo_name:
            self.set_repository(repo_name)
    
    def set_repository(self, repo_name: str) -> Repository:
        """
        Set the active repository.
        
        Args:
            repo_name: Repository name in format 'owner/repo'
            
        Returns:
            Repository object
        """
        try:
            self.repo = self.github.get_repo(repo_name)
            self.repo_name = repo_name
            logger.info(f"Connected to repository: {repo_name}")
            return self.repo
        except GithubException as e:
            logger.error(f"Failed to access repository {repo_name}: {e}")
            raise
    
    def create_repository(self, name: str, description: str = "", private: bool = False) -> Repository:
        """
        Create a new GitHub repository.
        
        Args:
            name: Repository name
            description: Repository description
            private: Whether repository should be private
            
        Returns:
            Created Repository object
        """
        try:
            repo = self.user.create_repo(
                name=name,
                description=description,
                private=private,
                auto_init=True
            )
            self.repo = repo
            self.repo_name = repo.full_name
            logger.info(f"Created repository: {repo.full_name}")
            return repo
        except GithubException as e:
            logger.error(f"Failed to create repository {name}: {e}")
            raise
    
    def push_file(
        self,
        file_path: str,
        content: str,
        commit_message: str,
        branch: str = "main",
        agent_name: Optional[str] = None,
        max_retries: int = 3,
        retry_delay: int = 2
    ) -> Dict[str, Any]:
        """
        Push a file to GitHub with agent attribution and retry logic.
        
        Args:
            file_path: Path in repository where file should be created/updated
            content: File content
            commit_message: Commit message
            branch: Target branch (default: main)
            agent_name: Name of the agent making the commit
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
            
        Returns:
            Dictionary with commit details
        """
        if not self.repo:
            raise ValueError("No repository set. Call set_repository() first.")
        
        # Add agent attribution to commit message
        if agent_name:
            commit_message = f"[{agent_name}] {commit_message}"
        
        for attempt in range(max_retries):
            try:
                # Try to get existing file
                try:
                    existing_file = self.repo.get_contents(file_path, ref=branch)
                    # Update existing file
                    result = self.repo.update_file(
                        path=file_path,
                        message=commit_message,
                        content=content,
                        sha=existing_file.sha,
                        branch=branch
                    )
                    logger.info(f"Updated file: {file_path} on branch {branch}")
                except GithubException as e:
                    if e.status == 404:
                        # File doesn't exist, create it
                        result = self.repo.create_file(
                            path=file_path,
                            message=commit_message,
                            content=content,
                            branch=branch
                        )
                        logger.info(f"Created file: {file_path} on branch {branch}")
                    else:
                        raise
                
                return {
                    'success': True,
                    'commit_sha': result['commit'].sha,
                    'file_path': file_path,
                    'branch': branch,
                    'agent': agent_name
                }
                
            except GithubException as e:
                if e.status == 409:  # Conflict
                    logger.warning(f"Conflict detected on attempt {attempt + 1}, retrying...")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
                        continue
                logger.error(f"Failed to push file {file_path}: {e}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error pushing file {file_path}: {e}")
                raise
        
        raise Exception(f"Failed to push file after {max_retries} attempts")
    
    def push_multiple_files(
        self,
        files: Dict[str, str],
        commit_message: str,
        branch: str = "main",
        agent_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Push multiple files in separate commits (for simplicity and attribution).
        
        Args:
            files: Dictionary mapping file paths to content
            commit_message: Base commit message
            branch: Target branch
            agent_name: Name of the agent making the commits
            
        Returns:
            Dictionary with results for each file
        """
        results = {
            'success': True,
            'files': {},
            'errors': []
        }
        
        for file_path, content in files.items():
            try:
                file_commit_msg = f"{commit_message} - {file_path}"
                result = self.push_file(
                    file_path=file_path,
                    content=content,
                    commit_message=file_commit_msg,
                    branch=branch,
                    agent_name=agent_name
                )
                results['files'][file_path] = result
            except Exception as e:
                results['success'] = False
                results['errors'].append({
                    'file': file_path,
                    'error': str(e)
                })
                logger.error(f"Failed to push {file_path}: {e}")
        
        return results
    
    def create_branch(self, branch_name: str, from_branch: str = "main") -> bool:
        """
        Create a new branch.
        
        Args:
            branch_name: Name of the new branch
            from_branch: Source branch to branch from
            
        Returns:
            True if successful
        """
        if not self.repo:
            raise ValueError("No repository set. Call set_repository() first.")
        
        try:
            source_branch = self.repo.get_branch(from_branch)
            self.repo.create_git_ref(
                ref=f"refs/heads/{branch_name}",
                sha=source_branch.commit.sha
            )
            logger.info(f"Created branch: {branch_name} from {from_branch}")
            return True
        except GithubException as e:
            logger.error(f"Failed to create branch {branch_name}: {e}")
            raise
    
    def create_pull_request(
        self,
        title: str,
        body: str,
        head_branch: str,
        base_branch: str = "main",
        agent_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a pull request.
        
        Args:
            title: PR title
            body: PR description
            head_branch: Source branch
            base_branch: Target branch
            agent_name: Name of the agent creating the PR
            
        Returns:
            Dictionary with PR details
        """
        if not self.repo:
            raise ValueError("No repository set. Call set_repository() first.")
        
        if agent_name:
            title = f"[{agent_name}] {title}"
        
        try:
            pr = self.repo.create_pull(
                title=title,
                body=body,
                head=head_branch,
                base=base_branch
            )
            logger.info(f"Created pull request: {pr.html_url}")
            return {
                'success': True,
                'pr_number': pr.number,
                'pr_url': pr.html_url,
                'agent': agent_name
            }
        except GithubException as e:
            logger.error(f"Failed to create pull request: {e}")
            raise
    
    def get_repository_info(self) -> Dict[str, Any]:
        """Get current repository information."""
        if not self.repo:
            raise ValueError("No repository set. Call set_repository() first.")
        
        return {
            'name': self.repo.name,
            'full_name': self.repo.full_name,
            'description': self.repo.description,
            'url': self.repo.html_url,
            'default_branch': self.repo.default_branch,
            'private': self.repo.private
        }
