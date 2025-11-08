"""
GitHub API service - Fetch user profile and repository data
"""
import aiohttp
import logging
from collections import defaultdict
from typing import Dict, List, Tuple, Any

logger = logging.getLogger(__name__)


class GitHubFetcher:
    """Fetch and aggregate GitHub user data"""
    
    BASE_URL = "https://api.github.com"
    
    def __init__(self, access_token: str = None):
        """
        Initialize GitHub fetcher
        
        Args:
            access_token: Optional GitHub personal access token for higher rate limits
        """
        self.access_token = access_token
        self.headers = {}
        if access_token:
            self.headers["Authorization"] = f"token {access_token}"
    
    async def get_user_profile(self, username: str) -> Dict[str, Any]:
        """
        Fetch GitHub user profile
        
        Args:
            username: GitHub username
            
        Returns:
            User profile data
        """
        try:
            logger.info(f"Fetching GitHub profile for user: {username}")
            
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(f"{self.BASE_URL}/users/{username}") as response:
                    if response.status == 404:
                        raise ValueError(f"GitHub user '{username}' not found")
                    elif response.status == 403:
                        raise ValueError("GitHub API rate limit exceeded. Please try again later or provide an access token.")
                    elif response.status != 200:
                        raise ValueError(f"GitHub API error: {response.status}")
                    
                    user_data = await response.json()
                    logger.info(f"Successfully fetched profile for {username}")
                    return user_data
                    
        except aiohttp.ClientError as e:
            logger.error(f"Network error fetching GitHub profile: {str(e)}")
            raise ValueError(f"Failed to connect to GitHub API: {str(e)}")
    
    async def get_user_repos(self, username: str, max_repos: int = 100) -> List[Dict[str, Any]]:
        """
        Fetch user's public repositories
        
        Args:
            username: GitHub username
            max_repos: Maximum number of repos to fetch
            
        Returns:
            List of repository data
        """
        try:
            logger.info(f"Fetching repositories for user: {username}")
            
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(
                    f"{self.BASE_URL}/users/{username}/repos",
                    params={"per_page": max_repos, "sort": "updated"}
                ) as response:
                    if response.status != 200:
                        raise ValueError(f"Failed to fetch repositories: {response.status}")
                    
                    repos = await response.json()
                    logger.info(f"Fetched {len(repos)} repositories")
                    return repos
                    
        except aiohttp.ClientError as e:
            logger.error(f"Network error fetching repositories: {str(e)}")
            raise ValueError(f"Failed to fetch repositories: {str(e)}")
    
    async def get_repo_languages(self, username: str, repo_name: str) -> Dict[str, int]:
        """
        Fetch detailed language breakdown for a specific repository
        
        Args:
            username: GitHub username
            repo_name: Repository name
            
        Returns:
            Dictionary of language: bytes_of_code
        """
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(
                    f"{self.BASE_URL}/repos/{username}/{repo_name}/languages"
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    return {}
        except Exception as e:
            logger.warning(f"Could not fetch languages for {repo_name}: {str(e)}")
            return {}
    
    async def get_user_and_repos(self, username: str) -> Tuple[Dict, List[Dict]]:
        """
        Fetch both user profile and repositories
        
        Args:
            username: GitHub username
            
        Returns:
            Tuple of (user_data, repo_data)
        """
        user_data = await self.get_user_profile(username)
        repo_data = await self.get_user_repos(username)
        return user_data, repo_data
    
    def summarize_data(self, user_data: Dict, repo_data: List[Dict]) -> Dict[str, Any]:
        """
        Aggregate and summarize GitHub profile data
        
        Args:
            user_data: User profile data
            repo_data: List of repository data
            
        Returns:
            Structured summary of GitHub activity
        """
        logger.info("Summarizing GitHub data...")
        
        # Language statistics
        language_count = defaultdict(int)
        language_bytes = defaultdict(int)
        
        # Repository statistics
        total_stars = 0
        total_forks = 0
        topics_used = set()
        
        # Repository summaries
        repos_summary = []
        
        for repo in repo_data:
            # Skip forks unless they have significant activity
            if repo.get("fork") and repo["stargazers_count"] == 0:
                continue
            
            # Language statistics
            language = repo.get("language")
            if language:
                language_count[language] += 1
            
            # Stars and forks
            stars = repo["stargazers_count"]
            forks = repo["forks_count"]
            total_stars += stars
            total_forks += forks
            
            # Topics
            topics = repo.get("topics", [])
            topics_used.update(topics)
            
            # Repository summary
            repos_summary.append({
                "name": repo["name"],
                "description": repo["description"] or "No description",
                "language": language or "Not specified",
                "stars": stars,
                "forks": forks,
                "topics": topics,
                "url": repo["html_url"],
                "updated_at": repo["updated_at"],
                "size": repo["size"]
            })
        
        # Sort repos by stars
        repos_summary.sort(key=lambda x: x["stars"], reverse=True)
        
        # Calculate activity level
        account_age_days = (2025 - int(user_data.get("created_at", "2020")[:4])) * 365
        repos_per_year = len(repo_data) / max(account_age_days / 365, 1)
        
        summary = {
            "user": {
                "username": user_data.get("login"),
                "name": user_data.get("name") or user_data.get("login"),
                "bio": user_data.get("bio") or "No bio provided",
                "location": user_data.get("location"),
                "company": user_data.get("company"),
                "email": user_data.get("email"),
                "blog": user_data.get("blog"),
                "twitter": user_data.get("twitter_username"),
                "followers": user_data.get("followers", 0),
                "following": user_data.get("following", 0),
                "public_repos": user_data.get("public_repos", 0),
                "created_at": user_data.get("created_at"),
                "profile_url": user_data.get("html_url")
            },
            "stats": {
                "total_repositories": len(repo_data),
                "languages_used": dict(language_count),
                "total_stars_earned": total_stars,
                "total_forks": total_forks,
                "topics_explored": list(topics_used),
                "activity_metrics": {
                    "repos_per_year": round(repos_per_year, 2),
                    "avg_stars_per_repo": round(total_stars / len(repo_data), 2) if repo_data else 0
                }
            },
            "repositories": repos_summary[:20]  # Top 20 repos
        }
        
        logger.info(f"Summary complete: {len(repo_data)} repos, {len(language_count)} languages")
        return summary
