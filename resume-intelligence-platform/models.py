# ═══════════════════════════════════════════════════════════════════════════════
# RESUME INTELLIGENCE PLATFORM - DATA MODELS
# Pydantic-style dataclasses for all data structures
# ═══════════════════════════════════════════════════════════════════════════════

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime
import json


# ═══════════════════════════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════════════════════════

class RoleConfidence(str, Enum):
    STRONG = "strong"       # >85% match
    BORDERLINE = "borderline"  # 60-85% match
    RISKY = "risky"         # <60% match


class BulletStatus(str, Enum):
    ENHANCED = "enhanced"
    KEPT = "kept"
    FLAGGED = "flagged"


class SkillPriority(str, Enum):
    REQUIRED = "required"
    PREFERRED = "preferred"
    NICE_TO_HAVE = "nice_to_have"


class SkillStrength(str, Enum):
    STRONG = "strong"
    MODERATE = "moderate"
    BASIC = "basic"


class WorkType(str, Enum):
    ONSITE = "onsite"
    REMOTE = "remote"
    HYBRID = "hybrid"


class ApplicationStatus(str, Enum):
    NOT_APPLIED = "not_applied"
    APPLIED = "applied"
    SHORTLISTED = "shortlisted"
    INTERVIEWED = "interviewed"
    HIRED = "hired"
    REJECTED = "rejected"


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 1: INPUT COLLECTION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ResumeInput:
    """Raw resume input data"""
    sessionId: str
    rawText: str
    source: str  # 'pdf', 'docx', 'linkedin'
    filename: Optional[str] = None
    uploadedAt: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class LinkedInProfile:
    """LinkedIn profile data (optional)"""
    url: str
    name: Optional[str] = None
    headline: Optional[str] = None
    experience: List[Dict[str, Any]] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)
    extractedAt: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ConflictItem:
    """Mismatch between resume and LinkedIn"""
    field: str  # e.g., 'job_title', 'dates', 'company'
    resumeValue: str
    linkedinValue: str
    severity: str  # 'high', 'medium', 'low'
    resolved: bool = False
    resolution: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 2-4: EXPERIENCE GRAPH & ROLE DIAGNOSIS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class SkillCategories:
    """Categorized skills from experience"""
    technical: List[str] = field(default_factory=list)  # Languages, frameworks
    aiml: List[str] = field(default_factory=list)       # AI/ML specific
    tools: List[str] = field(default_factory=list)      # DevOps, cloud, productivity
    soft: List[str] = field(default_factory=list)       # Leadership, communication


@dataclass
class SeniorityScores:
    """Seniority assessment on 5 dimensions (0-10)"""
    technicalDepth: int = 0   # How deep is technical expertise?
    leadership: int = 0       # Team leadership experience?
    scope: int = 0            # Size/impact of projects?
    autonomy: int = 0         # Independent decision making?
    impact: int = 0           # Business/product impact?
    
    def average(self) -> float:
        return (self.technicalDepth + self.leadership + self.scope + 
                self.autonomy + self.impact) / 5


@dataclass
class ExperienceGraph:
    """Locked truth source - immutable after creation"""
    id: str
    skills: SkillCategories
    seniorityScores: SeniorityScores
    experienceYears: int
    industries: List[str]
    achievements: List[str]
    companies: List[str] = field(default_factory=list)
    educations: List[str] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)
    createdAt: str = field(default_factory=lambda: datetime.now().isoformat())
    locked: bool = True  # Once created, no fabrication allowed
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class VerificationQuestion:
    """Micro-verification question"""
    id: str
    question: str
    context: str  # What it relates to
    answered: bool = False
    answer: Optional[str] = None


@dataclass
class SuggestedRole:
    """Role suggestion with confidence level"""
    title: str
    confidence: str  # 'strong', 'borderline', 'risky'
    reason: str
    matchScore: int  # 0-100
    selected: bool = False


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 5: LAYER 1 ENHANCEMENT
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class BulletEnhancement:
    """Single bullet enhancement result"""
    id: str
    original: str
    enhanced: str
    originalScore: int
    enhancedScore: int
    changes: List[str]
    status: str  # 'enhanced', 'kept', 'flagged'
    defendable: bool
    interviewTips: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)


@dataclass
class Layer1Result:
    """Universal ATS enhancement result"""
    sessionId: str
    originalATS: int
    enhancedATS: int
    bullets: List[BulletEnhancement]
    summary: Dict[str, int]  # totalBullets, enhanced, kept, flagged
    processedAt: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            'sessionId': self.sessionId,
            'originalATS': self.originalATS,
            'enhancedATS': self.enhancedATS,
            'bullets': [asdict(b) for b in self.bullets],
            'summary': self.summary,
            'processedAt': self.processedAt
        }


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 6-7: JOB SEARCH
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class SkillMatch:
    """Skills matching between candidate and job"""
    present: List[str] = field(default_factory=list)
    hidden: List[str] = field(default_factory=list)   # In graph but not highlighted
    missing: List[str] = field(default_factory=list)


@dataclass
class JobListing:
    """Real job listing from job board"""
    id: str
    title: str
    company: str
    location: str
    salary: Optional[str] = None
    workType: str = "onsite"  # onsite, remote, hybrid
    url: str = ""
    source: str = ""  # linkedin, indeed, glassdoor
    postedDate: Optional[str] = None
    description: Optional[str] = None
    requiredSkills: List[str] = field(default_factory=list)
    preferredSkills: List[str] = field(default_factory=list)
    matchScore: int = 0
    skillMatch: Optional[SkillMatch] = None
    
    def to_dict(self) -> Dict:
        result = asdict(self)
        if self.skillMatch:
            result['skillMatch'] = asdict(self.skillMatch)
        return result


@dataclass
class JobSearchResult:
    """Result of job search"""
    roleCategory: str
    jobs: List[JobListing]
    totalFound: int
    searchUrls: Dict[str, str]  # Board name -> search URL
    searchedAt: str = field(default_factory=lambda: datetime.now().isoformat())


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 8-10: JD ANALYSIS & GAP MAPPING
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class JDSkill:
    """Skill extracted from JD"""
    skill: str
    priority: str  # 'required', 'preferred', 'nice_to_have'
    years: Optional[str] = None


@dataclass
class JDAnalysis:
    """Parsed job description"""
    jobId: str
    jobTitle: str
    company: str
    location: Optional[str] = None
    salary: Optional[str] = None
    requiredSkills: List[JDSkill] = field(default_factory=list)
    preferredSkills: List[JDSkill] = field(default_factory=list)
    responsibilities: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    senioritySignals: List[str] = field(default_factory=list)
    rawText: Optional[str] = None
    analyzedAt: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            'jobId': self.jobId,
            'jobTitle': self.jobTitle,
            'company': self.company,
            'location': self.location,
            'salary': self.salary,
            'requiredSkills': [asdict(s) for s in self.requiredSkills],
            'preferredSkills': [asdict(s) for s in self.preferredSkills],
            'responsibilities': self.responsibilities,
            'keywords': self.keywords,
            'senioritySignals': self.senioritySignals,
            'analyzedAt': self.analyzedAt
        }


@dataclass
class GapSkillPresent:
    """Skill present in candidate profile"""
    skill: str
    evidence: str
    strength: str  # 'strong', 'moderate', 'basic'


@dataclass
class GapSkillHidden:
    """Skill in graph but not highlighted"""
    skill: str
    evidence: str
    action: str  # What to do to highlight it


@dataclass
class GapSkillMissing:
    """Skill missing from candidate profile"""
    skill: str
    priority: str  # 'high', 'medium', 'low'
    reason: str


@dataclass
class EnhancementSuggestion:
    """Suggestion for enhancement"""
    suggestion: str
    impact: str  # e.g., "+15% ATS"
    priority: int = 1


@dataclass
class GapAnalysis:
    """Gap analysis between profile and JD"""
    sessionId: str
    jobId: str
    skillsPresent: List[GapSkillPresent]
    skillsHidden: List[GapSkillHidden]
    skillsMissing: List[GapSkillMissing]
    enhancementScope: List[EnhancementSuggestion]
    overallMatch: int  # 0-100
    analyzedAt: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            'sessionId': self.sessionId,
            'jobId': self.jobId,
            'skillsPresent': [asdict(s) for s in self.skillsPresent],
            'skillsHidden': [asdict(s) for s in self.skillsHidden],
            'skillsMissing': [asdict(s) for s in self.skillsMissing],
            'enhancementScope': [asdict(s) for s in self.enhancementScope],
            'overallMatch': self.overallMatch,
            'analyzedAt': self.analyzedAt
        }


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 11: LAYER 2 ENHANCEMENT
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Layer2Bullet:
    """Layer 2 customized bullet"""
    id: str
    layer1: str
    layer2: str
    relevanceScore: int
    changes: List[str]
    jdKeywordsMatched: List[str]
    position: int  # Order in resume


@dataclass
class Layer2Scores:
    """Scoring for Layer 2 result"""
    originalATS: int
    layer1ATS: int
    layer2ATS: int
    jdMatch: int
    keywordCoverage: int
    confidence: int  # 1-5 stars


@dataclass
class Layer2Result:
    """JD-tailored enhancement result"""
    sessionId: str
    jobId: str
    customizedResume: Dict[str, Any]  # bullets, reorderedSections
    scores: Layer2Scores
    improvements: Dict[str, str]
    jdKeywordsMatched: List[str]
    processedAt: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            'sessionId': self.sessionId,
            'jobId': self.jobId,
            'customizedResume': self.customizedResume,
            'scores': asdict(self.scores),
            'improvements': self.improvements,
            'jdKeywordsMatched': self.jdKeywordsMatched,
            'processedAt': self.processedAt
        }


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 12-13: RESULTS & FEEDBACK
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class BenchmarkResult:
    """Benchmark dashboard data"""
    sessionId: str
    atsScores: Dict[str, int]  # original, layer1, layer2
    jdMatch: Optional[int] = None
    keywordCoverage: Optional[int] = None
    confidence: int = 0
    interviewReady: bool = True
    allBulletsDefendable: bool = True


@dataclass
class FeedbackEntry:
    """User feedback on job application outcome"""
    sessionId: str
    jobId: str
    status: str  # ApplicationStatus
    responseDate: Optional[str] = None
    notes: Optional[str] = None
    createdAt: str = field(default_factory=lambda: datetime.now().isoformat())


# ═══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class SessionState:
    """Complete session state for a user"""
    sessionId: str
    currentStage: int = 1
    resumeInput: Optional[ResumeInput] = None
    linkedinProfile: Optional[LinkedInProfile] = None
    conflicts: List[ConflictItem] = field(default_factory=list)
    experienceGraph: Optional[ExperienceGraph] = None
    verificationQuestions: List[VerificationQuestion] = field(default_factory=list)
    suggestedRoles: List[SuggestedRole] = field(default_factory=list)
    confirmedRoles: List[str] = field(default_factory=list)
    layer1Result: Optional[Layer1Result] = None
    jobSearchResults: List[JobSearchResult] = field(default_factory=list)
    selectedJob: Optional[JobListing] = None
    jdAnalysis: Optional[JDAnalysis] = None
    gapAnalysis: Optional[GapAnalysis] = None
    layer2Result: Optional[Layer2Result] = None
    feedback: List[FeedbackEntry] = field(default_factory=list)
    createdAt: str = field(default_factory=lambda: datetime.now().isoformat())
    lastUpdated: str = field(default_factory=lambda: datetime.now().isoformat())
