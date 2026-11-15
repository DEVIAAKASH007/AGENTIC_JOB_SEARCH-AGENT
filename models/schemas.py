from typing import List
from pydantic import BaseModel


class CandidateProfile(BaseModel):
    skills: List[str] = []
    projects: List[str] = []
    education: List[str] = []
    experience: List[str] = []
    certifications: List[str] = []


class GitHubSkill(BaseModel):
    skill: str
    evidence: str
    repositories: List[str]
    confidence: str = ""
    score: int = 0
    evidence_breakdown: dict = {}


class GitHubProfile(BaseModel):
    skills: List[GitHubSkill] = []


class JobSkills(BaseModel):
    required_skills: List[str] = []
    preferred_skills: List[str] = []