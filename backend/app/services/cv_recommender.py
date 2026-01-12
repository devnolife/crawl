"""
CV Recommender Service
Generates CV/portfolio recommendations based on GitHub analysis
"""

from typing import Dict, List, Any


class CVRecommender:
    """
    Generates CV and portfolio recommendations based on GitHub data
    """
    
    # Project quality indicators
    PROJECT_INDICATORS = {
        "readme": 5,
        "license": 3,
        "tests": 4,
        "ci_cd": 5,
        "documentation": 4
    }
    
    def __init__(self):
        pass
    
    async def generate_recommendations(
        self, github_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate CV recommendations from GitHub data
        
        Args:
            github_data: Dictionary containing repos, languages, contributions
            
        Returns:
            CV recommendation result
        """
        username = github_data.get("username", "unknown")
        repos = github_data.get("repos", [])
        languages = github_data.get("languages", {})
        contributions = github_data.get("contributions", {})
        
        # Generate professional summary
        summary = self._generate_summary(username, repos, languages)
        
        # Select highlight projects
        highlight_projects = self._select_highlight_projects(repos)
        
        # Organize skills for CV
        skills_section = self._organize_skills_section(repos, languages)
        
        # Generate improvement suggestions
        suggestions = self._generate_suggestions(repos, languages)
        
        # Calculate CV score
        cv_score = self._calculate_cv_score(repos, languages)
        
        return {
            "summary": summary,
            "highlight_projects": highlight_projects,
            "skills_section": skills_section,
            "improvement_suggestions": suggestions,
            "cv_score": round(cv_score, 2)
        }
    
    def _generate_summary(
        self, 
        username: str, 
        repos: List[Dict], 
        languages: Dict[str, int]
    ) -> str:
        """Generate a professional summary for CV"""
        repo_count = len(repos)
        
        # Determine primary languages
        if languages:
            sorted_langs = sorted(
                languages.items(), key=lambda x: x[1], reverse=True
            )
            primary_langs = [lang for lang, _ in sorted_langs[:3]]
        else:
            primary_langs = ["various technologies"]
        
        # Calculate total stars
        total_stars = sum(r.get("stargazers_count", 0) for r in repos)
        
        # Determine experience level based on repos
        if repo_count >= 50:
            exp_text = "experienced"
        elif repo_count >= 20:
            exp_text = "proficient"
        elif repo_count >= 10:
            exp_text = "skilled"
        else:
            exp_text = "passionate"
        
        summary = (
            f"An {exp_text} software developer with {repo_count} public repositories "
            f"on GitHub. Proficient in {', '.join(primary_langs)}. "
        )
        
        if total_stars > 100:
            summary += f"Open source contributor with {total_stars} stars across projects. "
        elif total_stars > 10:
            summary += f"Active open source contributor with community recognition. "
        
        summary += "Passionate about building quality software and continuous learning."
        
        return summary
    
    def _select_highlight_projects(
        self, repos: List[Dict], limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Select best projects to highlight on CV"""
        if not repos:
            return []
        
        # Score each repo
        scored_repos = []
        for repo in repos:
            score = self._calculate_project_score(repo)
            scored_repos.append((score, repo))
        
        # Sort by score and get top N
        scored_repos.sort(key=lambda x: x[0], reverse=True)
        top_repos = [r for _, r in scored_repos[:limit]]
        
        # Format for display
        return [
            {
                "name": repo.get("name", "Unknown"),
                "description": repo.get("description", "") or "No description",
                "language": repo.get("language", "N/A"),
                "stars": repo.get("stargazers_count", 0),
                "forks": repo.get("forks_count", 0),
                "url": repo.get("html_url", ""),
                "topics": repo.get("topics", [])[:5]
            }
            for repo in top_repos
        ]
    
    def _calculate_project_score(self, repo: Dict) -> float:
        """Calculate quality score for a project"""
        score = 0.0
        
        # Stars weight
        stars = repo.get("stargazers_count", 0)
        score += min(stars * 2, 50)
        
        # Forks weight
        forks = repo.get("forks_count", 0)
        score += min(forks * 3, 30)
        
        # Has description
        if repo.get("description"):
            score += 10
        
        # Has topics (indicates well-documented)
        topics = repo.get("topics", [])
        score += min(len(topics) * 2, 10)
        
        # Recent activity (not archived)
        if not repo.get("archived", False):
            score += 5
        
        # Is not a fork (original work)
        if not repo.get("fork", False):
            score += 15
        
        return score
    
    def _organize_skills_section(
        self, repos: List[Dict], languages: Dict[str, int]
    ) -> Dict[str, List[str]]:
        """Organize skills into CV sections"""
        sections = {
            "programming_languages": [],
            "frameworks": [],
            "tools": [],
            "databases": []
        }
        
        # Extract from languages
        if languages:
            sorted_langs = sorted(
                languages.items(), key=lambda x: x[1], reverse=True
            )
            sections["programming_languages"] = [
                lang for lang, _ in sorted_langs[:8]
            ]
        
        # Extract from repo topics and names
        frameworks = set()
        tools = set()
        databases = set()
        
        framework_keywords = [
            "react", "vue", "angular", "django", "flask", "fastapi",
            "express", "next", "nuxt", "spring", "laravel"
        ]
        tool_keywords = [
            "docker", "kubernetes", "git", "github-actions", "jenkins",
            "terraform", "ansible", "aws", "gcp", "azure"
        ]
        db_keywords = [
            "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
            "sqlite", "prisma", "sequelize"
        ]
        
        for repo in repos:
            topics = [t.lower() for t in repo.get("topics", [])]
            name = repo.get("name", "").lower()
            desc = (repo.get("description", "") or "").lower()
            
            combined = " ".join(topics + [name, desc])
            
            for fw in framework_keywords:
                if fw in combined:
                    frameworks.add(fw.title())
            
            for tool in tool_keywords:
                if tool in combined:
                    tools.add(tool.title())
            
            for db in db_keywords:
                if db in combined:
                    databases.add(db.title())
        
        sections["frameworks"] = list(frameworks)[:6]
        sections["tools"] = list(tools)[:6]
        sections["databases"] = list(databases)[:4]
        
        # Remove empty sections
        return {k: v for k, v in sections.items() if v}
    
    def _generate_suggestions(
        self, repos: List[Dict], languages: Dict[str, int]
    ) -> List[str]:
        """Generate suggestions for improving CV/portfolio"""
        suggestions = []
        
        # Check for common issues
        repo_count = len(repos)
        
        if repo_count < 5:
            suggestions.append(
                "Consider creating more public repositories to showcase your work"
            )
        
        # Check for README presence (estimate from description)
        repos_without_desc = sum(
            1 for r in repos if not r.get("description")
        )
        if repos_without_desc > repo_count * 0.5:
            suggestions.append(
                "Add descriptions to your repositories to improve discoverability"
            )
        
        # Check for topics
        repos_without_topics = sum(
            1 for r in repos if not r.get("topics")
        )
        if repos_without_topics > repo_count * 0.5:
            suggestions.append(
                "Add topics/tags to your repositories for better categorization"
            )
        
        # Check for language diversity
        if languages and len(languages) < 3:
            suggestions.append(
                "Consider exploring additional programming languages or frameworks"
            )
        
        # Check for popular repos
        total_stars = sum(r.get("stargazers_count", 0) for r in repos)
        if total_stars < 10:
            suggestions.append(
                "Engage with the open source community to gain more visibility"
            )
        
        # General suggestions
        if len(suggestions) < 3:
            general = [
                "Pin your best repositories on your GitHub profile",
                "Create a portfolio website linking to your GitHub projects",
                "Write blog posts or documentation about your projects",
                "Contribute to popular open source projects in your field"
            ]
            needed = 3 - len(suggestions)
            suggestions.extend(general[:needed])
        
        return suggestions[:5]
    
    def _calculate_cv_score(
        self, repos: List[Dict], languages: Dict[str, int]
    ) -> float:
        """Calculate overall CV strength score (0-100)"""
        score = 0.0
        
        # Repository quantity (max 20 points)
        repo_count = len(repos)
        score += min(repo_count * 2, 20)
        
        # Language diversity (max 15 points)
        lang_count = len(languages) if languages else 0
        score += min(lang_count * 3, 15)
        
        # Stars/popularity (max 25 points)
        total_stars = sum(r.get("stargazers_count", 0) for r in repos)
        score += min(total_stars * 0.5, 25)
        
        # Project quality indicators (max 25 points)
        quality_score = 0
        for repo in repos[:10]:  # Check top 10 repos
            if repo.get("description"):
                quality_score += 1
            if repo.get("topics"):
                quality_score += 1
            if not repo.get("fork", False):
                quality_score += 0.5
        score += min(quality_score * 2, 25)
        
        # Activity/engagement (max 15 points)
        total_forks = sum(r.get("forks_count", 0) for r in repos)
        score += min(total_forks * 0.3, 15)
        
        return min(score, 100)
