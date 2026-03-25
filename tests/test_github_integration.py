"""
Unit tests for GitHub integration.
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
from src.integrations.github_integration import GitHubIntegration


class TestGitHubIntegration(unittest.TestCase):
    """Test GitHub integration functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_token = "test_token_123"
    
    @patch('src.integrations.github_integration.Github')
    def test_initialization(self, mock_github):
        """Test GitHub integration initialization."""
        mock_user = Mock()
        mock_github.return_value.get_user.return_value = mock_user
        
        integration = GitHubIntegration(token=self.mock_token)
        
        self.assertIsNotNone(integration.github)
        self.assertIsNotNone(integration.user)
        mock_github.assert_called_once_with(self.mock_token)
    
    @patch('src.integrations.github_integration.Github')
    def test_set_repository(self, mock_github):
        """Test setting repository."""
        mock_repo = Mock()
        mock_github.return_value.get_repo.return_value = mock_repo
        mock_github.return_value.get_user.return_value = Mock()
        
        integration = GitHubIntegration(token=self.mock_token)
        repo = integration.set_repository("owner/repo")
        
        self.assertEqual(repo, mock_repo)
        self.assertEqual(integration.repo_name, "owner/repo")
        mock_github.return_value.get_repo.assert_called_with("owner/repo")
    
    @patch('src.integrations.github_integration.Github')
    def test_create_repository(self, mock_github):
        """Test repository creation."""
        mock_user = Mock()
        mock_repo = Mock()
        mock_repo.full_name = "owner/new-repo"
        mock_user.create_repo.return_value = mock_repo
        mock_github.return_value.get_user.return_value = mock_user
        
        integration = GitHubIntegration(token=self.mock_token)
        repo = integration.create_repository(
            name="new-repo",
            description="Test repo",
            private=True
        )
        
        self.assertEqual(repo, mock_repo)
        mock_user.create_repo.assert_called_once_with(
            name="new-repo",
            description="Test repo",
            private=True,
            auto_init=True
        )
    
    @patch('src.integrations.github_integration.Github')
    def test_push_file_create(self, mock_github):
        """Test creating a new file."""
        mock_repo = Mock()
        mock_github.return_value.get_user.return_value = Mock()
        
        # Simulate file not existing
        from github import GithubException
        mock_repo.get_contents.side_effect = GithubException(404, "Not found")
        
        mock_commit = Mock()
        mock_commit.sha = "abc123"
        mock_repo.create_file.return_value = {'commit': mock_commit}
        
        integration = GitHubIntegration(token=self.mock_token)
        integration.repo = mock_repo
        
        result = integration.push_file(
            file_path="test.txt",
            content="Hello World",
            commit_message="Test commit",
            agent_name="TestAgent"
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['commit_sha'], "abc123")
        self.assertEqual(result['agent'], "TestAgent")
        mock_repo.create_file.assert_called_once()
    
    @patch('src.integrations.github_integration.Github')
    def test_push_file_update(self, mock_github):
        """Test updating an existing file."""
        mock_repo = Mock()
        mock_github.return_value.get_user.return_value = Mock()
        
        # Simulate file existing
        mock_existing = Mock()
        mock_existing.sha = "old_sha"
        mock_repo.get_contents.return_value = mock_existing
        
        mock_commit = Mock()
        mock_commit.sha = "new_sha"
        mock_repo.update_file.return_value = {'commit': mock_commit}
        
        integration = GitHubIntegration(token=self.mock_token)
        integration.repo = mock_repo
        
        result = integration.push_file(
            file_path="test.txt",
            content="Updated content",
            commit_message="Update file",
            agent_name="TestAgent"
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['commit_sha'], "new_sha")
        mock_repo.update_file.assert_called_once()
    
    @patch('src.integrations.github_integration.Github')
    def test_push_multiple_files(self, mock_github):
        """Test pushing multiple files."""
        mock_repo = Mock()
        mock_github.return_value.get_user.return_value = Mock()
        
        from github import GithubException
        mock_repo.get_contents.side_effect = GithubException(404, "Not found")
        
        mock_commit = Mock()
        mock_commit.sha = "abc123"
        mock_repo.create_file.return_value = {'commit': mock_commit}
        
        integration = GitHubIntegration(token=self.mock_token)
        integration.repo = mock_repo
        
        files = {
            "file1.txt": "Content 1",
            "file2.txt": "Content 2"
        }
        
        result = integration.push_multiple_files(
            files=files,
            commit_message="Add files",
            agent_name="TestAgent"
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(len(result['files']), 2)
        self.assertEqual(mock_repo.create_file.call_count, 2)
    
    @patch('src.integrations.github_integration.Github')
    def test_create_branch(self, mock_github):
        """Test branch creation."""
        mock_repo = Mock()
        mock_branch = Mock()
        mock_commit = Mock()
        mock_commit.sha = "commit_sha"
        mock_branch.commit = mock_commit
        mock_repo.get_branch.return_value = mock_branch
        mock_github.return_value.get_user.return_value = Mock()
        
        integration = GitHubIntegration(token=self.mock_token)
        integration.repo = mock_repo
        
        result = integration.create_branch("feature-branch", "main")
        
        self.assertTrue(result)
        mock_repo.create_git_ref.assert_called_once_with(
            ref="refs/heads/feature-branch",
            sha="commit_sha"
        )
    
    @patch('src.integrations.github_integration.Github')
    def test_create_pull_request(self, mock_github):
        """Test PR creation."""
        mock_repo = Mock()
        mock_pr = Mock()
        mock_pr.number = 42
        mock_pr.html_url = "https://github.com/owner/repo/pull/42"
        mock_repo.create_pull.return_value = mock_pr
        mock_github.return_value.get_user.return_value = Mock()
        
        integration = GitHubIntegration(token=self.mock_token)
        integration.repo = mock_repo
        
        result = integration.create_pull_request(
            title="Test PR",
            body="PR description",
            head_branch="feature",
            agent_name="TestAgent"
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['pr_number'], 42)
        self.assertEqual(result['agent'], "TestAgent")
        mock_repo.create_pull.assert_called_once()
    
    @patch('src.integrations.github_integration.Github')
    @patch('time.sleep')
    def test_push_file_retry_on_conflict(self, mock_sleep, mock_github):
        """Test retry logic on conflict."""
        mock_repo = Mock()
        mock_github.return_value.get_user.return_value = Mock()
        
        from github import GithubException
        
        # First attempt: conflict
        # Second attempt: success
        mock_existing = Mock()
        mock_existing.sha = "old_sha"
        mock_repo.get_contents.return_value = mock_existing
        
        mock_commit = Mock()
        mock_commit.sha = "new_sha"
        
        # First call raises conflict, second succeeds
        mock_repo.update_file.side_effect = [
            GithubException(409, "Conflict"),
            {'commit': mock_commit}
        ]
        
        integration = GitHubIntegration(token=self.mock_token)
        integration.repo = mock_repo
        
        result = integration.push_file(
            file_path="test.txt",
            content="Content",
            commit_message="Commit",
            max_retries=3,
            retry_delay=0.1
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(mock_repo.update_file.call_count, 2)
        mock_sleep.assert_called()


if __name__ == '__main__':
    unittest.main()
