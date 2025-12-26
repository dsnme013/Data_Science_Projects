# ═══════════════════════════════════════════════════════════════════════════════
# RESUME INTELLIGENCE PLATFORM - CONFIGURATION
# All configurable parameters in one place - NO hardcoding in main code
# ═══════════════════════════════════════════════════════════════════════════════

import os
from dataclasses import dataclass, field
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

# ═══════════════════════════════════════════════════════════════════════════════
# ENVIRONMENT VARIABLES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class APIConfig:
    """API Keys and external service configuration"""
    openai_api_key: str = field(default_factory=lambda: os.getenv('OPENAI_API_KEY', ''))
    serper_api_key: str = field(default_factory=lambda: os.getenv('SERPER_API_KEY', ''))
    
    # LLM Settings
    llm_model: str = field(default_factory=lambda: os.getenv('LLM_MODEL', 'gpt-4o'))
    llm_temperature: float = field(default_factory=lambda: float(os.getenv('LLM_TEMPERATURE', '0.2')))
    llm_temperature_creative: float = field(default_factory=lambda: float(os.getenv('LLM_TEMPERATURE_CREATIVE', '0.3')))


@dataclass
class ServerConfig:
    """Server configuration"""
    host: str = field(default_factory=lambda: os.getenv('HOST', '0.0.0.0'))
    port: int = field(default_factory=lambda: int(os.getenv('PORT', '5000')))
    debug: bool = field(default_factory=lambda: os.getenv('DEBUG', 'true').lower() == 'true')
    
    # CORS
    cors_origins: List[str] = field(default_factory=lambda: os.getenv(
        'CORS_ORIGINS', 
        'http://localhost:5173,http://localhost:3000'
    ).split(','))


@dataclass
class FileConfig:
    """File handling configuration"""
    upload_folder: str = field(default_factory=lambda: os.getenv('UPLOAD_FOLDER', 'uploads'))
    output_folder: str = field(default_factory=lambda: os.getenv('OUTPUT_FOLDER', 'outputs'))
    max_content_length_mb: int = field(default_factory=lambda: int(os.getenv('MAX_CONTENT_LENGTH_MB', '16')))
    allowed_extensions: List[str] = field(default_factory=lambda: os.getenv(
        'ALLOWED_EXTENSIONS', 
        'pdf,docx'
    ).split(','))
    
    @property
    def max_content_length(self) -> int:
        return self.max_content_length_mb * 1024 * 1024


# ═══════════════════════════════════════════════════════════════════════════════
# PROCESSING LIMITS (Configurable)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ProcessingLimits:
    """Processing limits - all configurable"""
    # Bullet limits per layer
    layer1_bullet_limit: int = field(default_factory=lambda: int(os.getenv('LAYER1_BULLET_LIMIT', '10')))
    layer2_bullet_limit: int = field(default_factory=lambda: int(os.getenv('LAYER2_BULLET_LIMIT', '8')))
    
    # Preview limits
    resume_preview_chars: int = field(default_factory=lambda: int(os.getenv('RESUME_PREVIEW_CHARS', '500')))
    bullets_preview_count: int = field(default_factory=lambda: int(os.getenv('BULLETS_PREVIEW_COUNT', '10')))
    
    # Verification limits
    max_verification_questions: int = field(default_factory=lambda: int(os.getenv('MAX_VERIFICATION_QUESTIONS', '5')))
    
    # Job search limits
    max_jobs_per_role: int = field(default_factory=lambda: int(os.getenv('MAX_JOBS_PER_ROLE', '10')))
    max_total_jobs: int = field(default_factory=lambda: int(os.getenv('MAX_TOTAL_JOBS', '30')))
    
    # Role suggestion limits
    max_role_suggestions: int = field(default_factory=lambda: int(os.getenv('MAX_ROLE_SUGGESTIONS', '6')))


# ═══════════════════════════════════════════════════════════════════════════════
# ATS SCORING CONFIGURATION (Configurable)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ATSConfig:
    """ATS scoring parameters - all configurable"""
    # Base score
    base_score: int = field(default_factory=lambda: int(os.getenv('ATS_BASE_SCORE', '30')))
    
    # Bonus scores
    metrics_bonus: int = field(default_factory=lambda: int(os.getenv('ATS_METRICS_BONUS', '20')))
    action_verb_bonus: int = field(default_factory=lambda: int(os.getenv('ATS_ACTION_VERB_BONUS', '15')))
    tech_term_bonus_per_match: int = field(default_factory=lambda: int(os.getenv('ATS_TECH_TERM_BONUS', '5')))
    tech_term_bonus_max: int = field(default_factory=lambda: int(os.getenv('ATS_TECH_TERM_BONUS_MAX', '25')))
    length_bonus: int = field(default_factory=lambda: int(os.getenv('ATS_LENGTH_BONUS', '10')))
    
    # Optimal bullet length
    optimal_length_min: int = field(default_factory=lambda: int(os.getenv('OPTIMAL_BULLET_LENGTH_MIN', '100')))
    optimal_length_max: int = field(default_factory=lambda: int(os.getenv('OPTIMAL_BULLET_LENGTH_MAX', '200')))
    
    # Score bounds
    original_score_min: int = field(default_factory=lambda: int(os.getenv('ORIGINAL_SCORE_MIN', '25')))
    original_score_max: int = field(default_factory=lambda: int(os.getenv('ORIGINAL_SCORE_MAX', '65')))
    enhanced_score_min: int = field(default_factory=lambda: int(os.getenv('ENHANCED_SCORE_MIN', '70')))
    enhanced_score_max: int = field(default_factory=lambda: int(os.getenv('ENHANCED_SCORE_MAX', '98')))
    
    # Layer 2 improvement range
    layer2_improvement_min: int = field(default_factory=lambda: int(os.getenv('LAYER2_IMPROVEMENT_MIN', '5')))
    layer2_improvement_max: int = field(default_factory=lambda: int(os.getenv('LAYER2_IMPROVEMENT_MAX', '12')))
    
    # Score multipliers
    original_multiplier: float = field(default_factory=lambda: float(os.getenv('ORIGINAL_SCORE_MULTIPLIER', '0.9')))
    enhanced_multiplier: float = field(default_factory=lambda: float(os.getenv('ENHANCED_SCORE_MULTIPLIER', '0.95')))


# ═══════════════════════════════════════════════════════════════════════════════
# ROLE CONFIDENCE THRESHOLDS (Configurable)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class RoleConfidenceConfig:
    """Role suggestion confidence thresholds"""
    strong_threshold: int = field(default_factory=lambda: int(os.getenv('ROLE_STRONG_THRESHOLD', '85')))
    borderline_threshold: int = field(default_factory=lambda: int(os.getenv('ROLE_BORDERLINE_THRESHOLD', '60')))
    # Below borderline = risky


# ═══════════════════════════════════════════════════════════════════════════════
# KEYWORD LISTS (Loadable from files or env)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class KeywordConfig:
    """Keyword lists for scoring - can be loaded from files"""
    action_verbs: List[str] = field(default_factory=lambda: _load_list_config(
        'ACTION_VERBS',
        'built,designed,developed,led,created,implemented,architected,optimized,'
        'delivered,launched,managed,spearheaded,orchestrated,pioneered,transformed,'
        'streamlined,automated,engineered,established,executed'
    ))
    
    tech_terms: List[str] = field(default_factory=lambda: _load_list_config(
        'TECH_TERMS',
        'python,javascript,typescript,java,go,rust,aws,azure,gcp,docker,kubernetes,'
        'ml,ai,api,database,cloud,tensorflow,pytorch,langchain,llm,genai,fastapi,'
        'react,node,sql,nosql,redis,kafka,spark,airflow,mlops,ci/cd'
    ))
    
    bullet_prefixes: List[str] = field(default_factory=lambda: _load_list_config(
        'BULLET_PREFIXES',
        '•,-,*,–,►,▪,●'
    ))


def _load_list_config(env_key: str, default: str) -> List[str]:
    """Load a list from environment variable or use default"""
    value = os.getenv(env_key, default)
    return [item.strip().lower() for item in value.split(',') if item.strip()]


# ═══════════════════════════════════════════════════════════════════════════════
# JOB SEARCH CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class JobSearchConfig:
    """Job search parameters"""
    default_location: str = field(default_factory=lambda: os.getenv('DEFAULT_LOCATION', 'United States'))
    search_recency_days: int = field(default_factory=lambda: int(os.getenv('JOB_SEARCH_RECENCY_DAYS', '7')))
    
    # Job boards to search
    enabled_job_boards: List[str] = field(default_factory=lambda: _load_list_config(
        'ENABLED_JOB_BOARDS',
        'linkedin,indeed,glassdoor,lever,greenhouse'
    ))
    
    # Search URL templates (use {query} and {location} placeholders)
    job_board_urls: Dict[str, str] = field(default_factory=lambda: {
        'linkedin': os.getenv('LINKEDIN_SEARCH_URL', 
            'https://linkedin.com/jobs/search?keywords={query}&location={location}'),
        'indeed': os.getenv('INDEED_SEARCH_URL',
            'https://indeed.com/jobs?q={query}&l={location}'),
        'glassdoor': os.getenv('GLASSDOOR_SEARCH_URL',
            'https://glassdoor.com/Job/{location}-{query}-jobs.htm'),
    })
    
    # Use mock data for POC
    use_mock_data: bool = field(default_factory=lambda: os.getenv('USE_MOCK_JOB_DATA', 'true').lower() == 'true')


# ═══════════════════════════════════════════════════════════════════════════════
# DOCUMENT GENERATION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class DocxConfig:
    """DOCX generation settings"""
    title_font_size: int = field(default_factory=lambda: int(os.getenv('DOCX_TITLE_FONT_SIZE', '14')))
    body_font_size: int = field(default_factory=lambda: int(os.getenv('DOCX_BODY_FONT_SIZE', '11')))
    subtitle_font_size: int = field(default_factory=lambda: int(os.getenv('DOCX_SUBTITLE_FONT_SIZE', '10')))
    highlight_enhanced: bool = field(default_factory=lambda: os.getenv('DOCX_HIGHLIGHT_ENHANCED', 'true').lower() == 'true')


# ═══════════════════════════════════════════════════════════════════════════════
# MASTER CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Settings:
    """Master configuration object"""
    api: APIConfig = field(default_factory=APIConfig)
    server: ServerConfig = field(default_factory=ServerConfig)
    files: FileConfig = field(default_factory=FileConfig)
    limits: ProcessingLimits = field(default_factory=ProcessingLimits)
    ats: ATSConfig = field(default_factory=ATSConfig)
    roles: RoleConfidenceConfig = field(default_factory=RoleConfidenceConfig)
    keywords: KeywordConfig = field(default_factory=KeywordConfig)
    job_search: JobSearchConfig = field(default_factory=JobSearchConfig)
    docx: DocxConfig = field(default_factory=DocxConfig)
    
    def validate(self) -> bool:
        """Validate required configuration"""
        if not self.api.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required")
        return True
    
    def print_config(self):
        """Print configuration summary"""
        print("=" * 60)
        print("🚀 RESUME INTELLIGENCE PLATFORM - CONFIGURATION")
        print("=" * 60)
        print(f"🤖 Model: {self.api.llm_model}")
        print(f"🌡️  Temperature: {self.api.llm_temperature}")
        print(f"🌐 Server: {self.server.host}:{self.server.port}")
        print(f"📁 Upload Folder: {self.files.upload_folder}")
        print(f"📊 Layer 1 Limit: {self.limits.layer1_bullet_limit} bullets")
        print(f"📊 Layer 2 Limit: {self.limits.layer2_bullet_limit} bullets")
        print(f"💼 Max Jobs: {self.limits.max_total_jobs}")
        print(f"🎯 Mock Data: {self.job_search.use_mock_data}")
        print("=" * 60)


# Singleton instance
settings = Settings()
