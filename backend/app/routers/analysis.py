"""
Analysis router - Skill analysis and CV recommendations
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional, Any

from app.services.skill_analyzer import SkillAnalyzer
from app.services.cv_recommender import CVRecommender

router = APIRouter()

# Initialize services
skill_analyzer = SkillAnalyzer()
cv_recommender = CVRecommender()


class GitHubDataInput(BaseModel):
    """Input model for GitHub data analysis"""
    username: str
    repos: List[Dict[str, Any]]
    languages: Dict[str, int]
    contributions: Optional[Dict[str, Any]] = None


class SkillAnalysisResponse(BaseModel):
    """Response model for skill analysis"""
    username: str
    top_skills: List[Dict[str, Any]]
    skill_categories: Dict[str, List[str]]
    experience_level: str
    specialization: str
    strength_score: float


class CVRecommendationResponse(BaseModel):
    """Response model for CV recommendations"""
    summary: str
    highlight_projects: List[Dict[str, Any]]
    skills_section: Dict[str, List[str]]
    improvement_suggestions: List[str]
    cv_score: float


@router.post("/analyze-skills", response_model=SkillAnalysisResponse)
async def analyze_skills(data: GitHubDataInput):
    """
    Analyze skills based on GitHub data
    """
    try:
        result = await skill_analyzer.analyze(data.model_dump())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cv-recommendations", response_model=CVRecommendationResponse)
async def get_cv_recommendations(data: GitHubDataInput):
    """
    Get CV/portfolio recommendations based on GitHub data
    """
    try:
        result = await cv_recommender.generate_recommendations(data.model_dump())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/full-analysis")
async def full_analysis(data: GitHubDataInput):
    """
    Get both skill analysis and CV recommendations
    """
    try:
        skills = await skill_analyzer.analyze(data.model_dump())
        cv = await cv_recommender.generate_recommendations(data.model_dump())
        
        return {
            "skill_analysis": skills,
            "cv_recommendations": cv
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
