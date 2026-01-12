"""
Skill Analyzer Service
Analyzes GitHub data to extract and categorize developer skills
"""

from typing import Dict, List, Any
import re


class SkillAnalyzer:
    """
    Analyzes developer skills based on GitHub repository data
    """
    
    # Skill category mappings
    SKILL_CATEGORIES = {
        "frontend": [
            "javascript", "typescript", "react", "vue", "angular", "svelte",
            "html", "css", "sass", "scss", "tailwindcss", "next.js", "nuxt",
            "webpack", "vite", "redux", "mobx", "zustand"
        ],
        "backend": [
            "python", "java", "go", "rust", "c#", "ruby", "php", "node.js",
            "express", "fastapi", "django", "flask", "spring", "laravel",
            "asp.net", "gin", "echo", "fiber"
        ],
        "mobile": [
            "kotlin", "swift", "dart", "flutter", "react-native", "objective-c",
            "android", "ios", "xamarin", "ionic"
        ],
        "database": [
            "sql", "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
            "prisma", "sequelize", "mongoose", "typeorm", "sqlite"
        ],
        "devops": [
            "docker", "kubernetes", "aws", "gcp", "azure", "terraform",
            "ansible", "jenkins", "github-actions", "gitlab-ci", "nginx"
        ],
        "data_science": [
            "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch",
            "jupyter", "matplotlib", "seaborn", "r", "spark"
        ]
    }
    
    # Experience level thresholds
    EXPERIENCE_LEVELS = {
        "beginner": (0, 10),
        "intermediate": (10, 30),
        "advanced": (30, 70),
        "expert": (70, float("inf"))
    }
    
    def __init__(self):
        self.skill_weights = self._build_skill_weights()
    
    def _build_skill_weights(self) -> Dict[str, float]:
        """Build skill weights based on category importance"""
        weights = {}
        for category, skills in self.SKILL_CATEGORIES.items():
            for skill in skills:
                weights[skill.lower()] = 1.0
        return weights
    
    async def analyze(self, github_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze GitHub data and return skill analysis
        
        Args:
            github_data: Dictionary containing repos, languages, contributions
            
        Returns:
            Skill analysis result
        """
        username = github_data.get("username", "unknown")
        repos = github_data.get("repos", [])
        languages = github_data.get("languages", {})
        
        # Extract skills from various sources
        extracted_skills = self._extract_skills_from_repos(repos)
        language_skills = self._process_languages(languages)
        
        # Merge all skills
        all_skills = self._merge_skills(extracted_skills, language_skills)
        
        # Categorize skills
        categorized = self._categorize_skills(all_skills)
        
        # Calculate experience level
        experience_level = self._calculate_experience_level(repos, all_skills)
        
        # Determine specialization
        specialization = self._determine_specialization(categorized)
        
        # Calculate strength score
        strength_score = self._calculate_strength_score(all_skills, repos)
        
        # Get top skills
        top_skills = self._get_top_skills(all_skills, limit=10)
        
        return {
            "username": username,
            "top_skills": top_skills,
            "skill_categories": categorized,
            "experience_level": experience_level,
            "specialization": specialization,
            "strength_score": round(strength_score, 2)
        }
    
    def _extract_skills_from_repos(self, repos: List[Dict]) -> Dict[str, float]:
        """Extract skills from repository names, descriptions, and topics"""
        skills = {}
        
        for repo in repos:
            # Extract from repo name
            name = repo.get("name", "").lower()
            self._extract_from_text(name, skills)
            
            # Extract from description
            description = repo.get("description", "") or ""
            self._extract_from_text(description.lower(), skills)
            
            # Extract from topics
            topics = repo.get("topics", [])
            for topic in topics:
                topic_lower = topic.lower()
                if topic_lower in self.skill_weights:
                    skills[topic_lower] = skills.get(topic_lower, 0) + 2.0
            
            # Weight by stars and forks
            stars = repo.get("stargazers_count", 0)
            forks = repo.get("forks_count", 0)
            multiplier = 1 + (stars * 0.1) + (forks * 0.2)
            
            for skill in list(skills.keys()):
                skills[skill] *= min(multiplier, 3.0)  # Cap multiplier
        
        return skills
    
    def _extract_from_text(self, text: str, skills: Dict[str, float]):
        """Extract skill mentions from text"""
        # Check for each known skill
        for category, category_skills in self.SKILL_CATEGORIES.items():
            for skill in category_skills:
                # Handle skills with special characters
                skill_pattern = re.escape(skill.lower())
                if re.search(rf'\b{skill_pattern}\b', text):
                    skills[skill.lower()] = skills.get(skill.lower(), 0) + 1.0
    
    def _process_languages(self, languages: Dict[str, int]) -> Dict[str, float]:
        """Process language data into skill scores"""
        if not languages:
            return {}
        
        total_bytes = sum(languages.values())
        if total_bytes == 0:
            return {}
        
        skills = {}
        for lang, bytes_count in languages.items():
            lang_lower = lang.lower()
            # Normalize by percentage
            percentage = (bytes_count / total_bytes) * 100
            skills[lang_lower] = percentage
        
        return skills
    
    def _merge_skills(self, *skill_dicts) -> Dict[str, float]:
        """Merge multiple skill dictionaries"""
        merged = {}
        for skill_dict in skill_dicts:
            for skill, score in skill_dict.items():
                merged[skill] = merged.get(skill, 0) + score
        return merged
    
    def _categorize_skills(self, skills: Dict[str, float]) -> Dict[str, List[str]]:
        """Categorize skills by domain"""
        categorized = {cat: [] for cat in self.SKILL_CATEGORIES.keys()}
        
        for skill in skills.keys():
            for category, category_skills in self.SKILL_CATEGORIES.items():
                if skill in [s.lower() for s in category_skills]:
                    categorized[category].append(skill)
                    break
        
        # Remove empty categories
        return {k: v for k, v in categorized.items() if v}
    
    def _calculate_experience_level(
        self, repos: List[Dict], skills: Dict[str, float]
    ) -> str:
        """Calculate developer experience level"""
        # Factors: number of repos, skill diversity, repo age
        repo_count = len(repos)
        skill_count = len(skills)
        
        # Simple scoring based on repos and skills
        score = (repo_count * 2) + (skill_count * 3)
        
        for level, (min_score, max_score) in self.EXPERIENCE_LEVELS.items():
            if min_score <= score < max_score:
                return level
        
        return "intermediate"
    
    def _determine_specialization(
        self, categorized: Dict[str, List[str]]
    ) -> str:
        """Determine primary specialization"""
        if not categorized:
            return "general"
        
        # Count skills per category
        category_scores = {
            cat: len(skills) for cat, skills in categorized.items()
        }
        
        if not category_scores:
            return "general"
        
        top_category = max(category_scores, key=category_scores.get)
        return top_category
    
    def _calculate_strength_score(
        self, skills: Dict[str, float], repos: List[Dict]
    ) -> float:
        """Calculate overall developer strength score (0-100)"""
        if not skills and not repos:
            return 0.0
        
        # Base score from number of skills
        skill_score = min(len(skills) * 5, 40)
        
        # Score from repos
        repo_score = min(len(repos) * 2, 30)
        
        # Score from popular repos (stars)
        star_count = sum(r.get("stargazers_count", 0) for r in repos)
        star_score = min(star_count * 0.5, 20)
        
        # Score from skill diversity
        diversity_score = min(len(skills) * 2, 10)
        
        return min(skill_score + repo_score + star_score + diversity_score, 100)
    
    def _get_top_skills(
        self, skills: Dict[str, float], limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get top N skills by score"""
        sorted_skills = sorted(
            skills.items(), key=lambda x: x[1], reverse=True
        )[:limit]
        
        max_score = sorted_skills[0][1] if sorted_skills else 1
        
        return [
            {
                "name": skill,
                "score": round(score, 2),
                "percentage": round((score / max_score) * 100, 1)
            }
            for skill, score in sorted_skills
        ]
