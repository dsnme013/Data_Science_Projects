# ═══════════════════════════════════════════════════════════════════════════════
# RESUME INTELLIGENCE PLATFORM - CREWAI AGENTS
# All agent definitions for the 13-stage pipeline
# ═══════════════════════════════════════════════════════════════════════════════

from crewai import Agent
from langchain_openai import ChatOpenAI
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
from typing import Optional, List
from config import settings


# ═══════════════════════════════════════════════════════════════════════════════
# LLM FACTORY
# ═══════════════════════════════════════════════════════════════════════════════

def create_llm(temperature: Optional[float] = None) -> ChatOpenAI:
    """Create LLM instance with configurable temperature"""
    return ChatOpenAI(
        model=settings.api.llm_model,
        temperature=temperature or settings.api.llm_temperature,
        api_key=settings.api.openai_api_key
    )


def create_creative_llm() -> ChatOpenAI:
    """Create LLM with higher temperature for creative tasks"""
    return create_llm(temperature=settings.api.llm_temperature_creative)


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 1-4: INPUT & EXPERIENCE GRAPH AGENTS
# ═══════════════════════════════════════════════════════════════════════════════

def create_resume_parser_agent() -> Agent:
    """Agent for parsing resume and extracting structured data"""
    return Agent(
        role="Resume Parser Expert",
        goal="Extract all relevant information from resume text into structured format.",
        backstory="""You are an expert at parsing resumes and extracting:
        - Personal information (name, contact)
        - Work experience (company, title, dates, bullets)
        - Education (degree, institution, year)
        - Skills (technical, soft)
        - Certifications and achievements
        
        You are meticulous about accuracy and never assume information not present.""",
        verbose=True,
        llm=create_llm()
    )


def create_linkedin_extractor_agent() -> Agent:
    """Agent for extracting LinkedIn profile data"""
    scraper = ScrapeWebsiteTool()
    return Agent(
        role="LinkedIn Profile Analyst",
        goal="Extract and structure LinkedIn profile information.",
        backstory="""You analyze LinkedIn profiles to extract professional data.
        You respect privacy and only extract publicly visible information.
        You format data consistently for comparison with resume data.""",
        tools=[scraper],
        verbose=True,
        llm=create_llm()
    )


def create_conflict_detector_agent() -> Agent:
    """Agent for detecting mismatches between resume and LinkedIn"""
    return Agent(
        role="Data Consistency Analyst",
        goal="Identify discrepancies between resume and LinkedIn profile.",
        backstory="""You meticulously compare data sources to find inconsistencies:
        - Job title mismatches
        - Date discrepancies
        - Company name differences
        - Missing experiences
        
        You classify severity and suggest resolutions.""",
        verbose=True,
        llm=create_llm()
    )


def create_experience_graph_agent() -> Agent:
    """Agent for building the locked experience graph"""
    return Agent(
        role="Experience Graph Architect",
        goal="Build comprehensive experience graph with skills categorization and seniority scoring.",
        backstory=f"""You are an expert at analyzing professional backgrounds. 
        
        You categorize skills into:
        - technical: Programming languages, frameworks, databases
        - aiml: AI/ML specific (LLMs, models, frameworks)
        - tools: DevOps, cloud, productivity tools
        - soft: Leadership, communication, management
        
        You assess seniority on 5 dimensions (0-10):
        - technicalDepth: How deep is technical expertise?
        - leadership: Team leadership experience?
        - scope: Size/impact of projects?
        - autonomy: Independent decision making?
        - impact: Business/product impact?
        
        Confidence thresholds:
        - Strong: >{settings.roles.strong_threshold}% match
        - Borderline: {settings.roles.borderline_threshold}-{settings.roles.strong_threshold}% match
        - Risky: <{settings.roles.borderline_threshold}% match
        
        This graph becomes the LOCKED TRUTH SOURCE - no fabrication after this point.""",
        verbose=True,
        llm=create_llm()
    )


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 2: MICRO-VERIFICATION AGENT
# ═══════════════════════════════════════════════════════════════════════════════

def create_verification_agent() -> Agent:
    """Agent for generating clarifying questions"""
    return Agent(
        role="Experience Verifier",
        goal=f"Generate up to {settings.limits.max_verification_questions} clarifying questions to enrich the experience graph.",
        backstory="""You identify gaps in the experience data that could be enriched:
        - Team sizes that aren't mentioned
        - Metrics/scale that could be quantified
        - Impact that could be measured
        
        Your questions should:
        - Be specific and easy to answer
        - Focus on verifiable facts (not opinions)
        - Help quantify achievements
        
        IMPORTANT: Questions should ENRICH existing experience, not add new ones.""",
        verbose=True,
        llm=create_llm()
    )


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 3-4: ROLE DIAGNOSIS AGENTS
# ═══════════════════════════════════════════════════════════════════════════════

def create_role_suggester_agent() -> Agent:
    """Agent for suggesting roles with confidence levels"""
    return Agent(
        role="Career Path Strategist",
        goal=f"Suggest up to {settings.limits.max_role_suggestions} relevant job roles based on experience with realistic confidence levels.",
        backstory=f"""You evaluate candidates for role fit with brutal honesty:
        
        Confidence Levels:
        - 'strong': Clear match, >{settings.roles.strong_threshold}% of requirements met
        - 'borderline': Stretch but achievable, {settings.roles.borderline_threshold}-{settings.roles.strong_threshold}% match
        - 'risky': Significant gaps, <{settings.roles.borderline_threshold}% match
        
        You consider:
        - Experience years and depth
        - Technical skills match
        - Leadership experience
        - Industry relevance
        
        Always include at least one 'borderline' and one 'risky' role for variety.""",
        verbose=True,
        llm=create_llm()
    )


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 5: LAYER 1 ENHANCEMENT AGENTS
# ═══════════════════════════════════════════════════════════════════════════════

def create_layer1_enhancer_agent() -> Agent:
    """Agent for universal ATS enhancement (job-agnostic)"""
    return Agent(
        role="ATS Optimization Specialist",
        goal="Enhance resume bullets for maximum ATS compatibility while preserving truth.",
        backstory="""You enhance resumes by:
        1. Adding quantifiable metrics (only if inferable from context)
        2. Using strong action verbs
        3. Including relevant technical keywords
        4. Improving clarity and impact
        
        CRITICAL GUARDRAILS:
        - NEVER fabricate achievements not in the experience graph
        - NEVER add skills the person doesn't have
        - Only enhance presentation of EXISTING experience
        - Every enhancement must be DEFENDABLE in an interview
        - If unsure, keep original wording
        
        Your enhancements pass through a defendability audit.""",
        verbose=True,
        llm=create_creative_llm()  # Slightly higher temperature for creativity
    )


def create_guardrail_agent() -> Agent:
    """Agent for verifying enhancements against experience graph"""
    return Agent(
        role="Truth Guardrail Engine",
        goal="Verify that all enhancements are truthful and backed by the experience graph.",
        backstory="""You are the final checkpoint before any enhancement is approved.
        
        You check:
        - Is this claim supported by the experience graph?
        - Are metrics reasonable and defensible?
        - Could this be verified in a background check?
        - Could the candidate explain this in an interview?
        
        If ANY check fails, flag the enhancement for review.""",
        verbose=True,
        llm=create_llm()
    )


def create_interview_prep_agent() -> Agent:
    """Agent for generating interview defense tips"""
    return Agent(
        role="Interview Coach",
        goal="Generate tips for defending each resume enhancement in interviews.",
        backstory="""You prepare candidates to defend their resume in interviews:
        
        For each enhanced bullet, you provide:
        - Potential questions interviewers might ask
        - How to explain the metrics/achievements
        - Technical details to be ready to discuss
        - Common follow-up questions
        - Red flags to avoid
        
        Your tips ensure candidates can confidently stand behind every line.""",
        verbose=True,
        llm=create_llm()
    )


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 6-7: JOB SEARCH AGENTS
# ═══════════════════════════════════════════════════════════════════════════════

def create_job_researcher_agent() -> Agent:
    """Agent for searching real job listings"""
    search_tool = SerperDevTool()
    scraper = ScrapeWebsiteTool()
    
    return Agent(
        role="Senior Job Researcher",
        goal=f"Find up to {settings.limits.max_jobs_per_role} relevant job listings per role category with accurate details.",
        backstory=f"""You are an expert job researcher who finds real, current job listings.
        
        You search across:
        - LinkedIn Jobs
        - Indeed
        - Glassdoor
        - Company career pages
        - Startup job boards (Lever, Greenhouse)
        
        For each job, you extract:
        - Title, Company, Location
        - Salary range (if available)
        - Work type (remote/hybrid/onsite)
        - Required/preferred skills
        - Job URL
        - Posted date
        
        You rank jobs by match score considering skills overlap.""",
        tools=[search_tool, scraper],
        verbose=True,
        llm=create_llm()
    )


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 8-10: JD ANALYSIS AGENTS
# ═══════════════════════════════════════════════════════════════════════════════

def create_jd_fetcher_agent() -> Agent:
    """Agent for fetching JD from URLs"""
    scraper = ScrapeWebsiteTool()
    
    return Agent(
        role="JD Content Extractor",
        goal="Fetch and extract job description content from job posting URLs.",
        backstory="""You specialize in extracting job descriptions from various job boards:
        - LinkedIn Jobs
        - Indeed
        - Glassdoor
        - Lever (*.lever.co)
        - Greenhouse (*.greenhouse.io)
        - Company career pages
        
        You handle JavaScript-rendered content and clean HTML artifacts.""",
        tools=[scraper],
        verbose=True,
        llm=create_llm()
    )


def create_jd_analyzer_agent() -> Agent:
    """Agent for analyzing job descriptions"""
    scraper = ScrapeWebsiteTool()
    
    return Agent(
        role="JD Analysis Expert",
        goal="Extract and categorize all requirements from job descriptions.",
        backstory="""You analyze job descriptions with precision to extract:
        
        1. Required Skills (must-have):
           - With experience years if specified
           - Priority level
        
        2. Preferred Skills (nice-to-have):
           - Differentiate from required
        
        3. Keywords:
           - Terms that ATS will scan for
           - Industry-specific jargon
        
        4. Seniority Signals:
           - Years of experience required
           - Leadership expectations
           - Scope indicators
        
        5. Culture Indicators:
           - Work style preferences
           - Team dynamics""",
        tools=[scraper],
        verbose=True,
        llm=create_llm()
    )


def create_gap_analyst_agent() -> Agent:
    """Agent for detailed gap analysis"""
    return Agent(
        role="Skills Gap Analyst",
        goal="Compare candidate profile against JD to identify gaps and opportunities.",
        backstory="""You perform thorough gap analysis with brutal honesty:
        
        1. Skills PRESENT (with evidence):
           - Clear matches with strength level
           - Evidence from experience graph
        
        2. Skills HIDDEN (need highlighting):
           - Present in graph but not explicit
           - Suggest how to surface them
        
        3. Skills MISSING (with priority):
           - High: Required and not present
           - Medium: Preferred and not present
           - Low: Nice-to-have
           - ⚠️ Only flag to user, NEVER add to resume
        
        4. Enhancement SCOPE:
           - What can be emphasized
           - Estimated impact on match score""",
        verbose=True,
        llm=create_llm()
    )


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 11: LAYER 2 ENHANCEMENT AGENT
# ═══════════════════════════════════════════════════════════════════════════════

def create_layer2_enhancer_agent() -> Agent:
    """Agent for JD-specific customization"""
    return Agent(
        role="JD-Targeted Resume Customizer",
        goal="Customize resume specifically for a target job description.",
        backstory="""You optimize resumes for specific JDs by:
        
        1. REORDER bullets:
           - Move most relevant experience to top
           - Prioritize JD-matching achievements
        
        2. KEYWORD alignment:
           - Use exact JD terminology where truthful
           - Match language style
        
        3. EMPHASIS shift:
           - Expand relevant bullets with more detail
           - Condense less relevant ones
        
        CRITICAL RULES:
        - Only use keywords that match ACTUAL experience
        - Never add skills not in experience graph
        - Never fabricate metrics
        - Maintain interview defendability
        - If skill is missing, don't fake it""",
        verbose=True,
        llm=create_creative_llm()
    )


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 13: FEEDBACK AGENT
# ═══════════════════════════════════════════════════════════════════════════════

def create_feedback_analyzer_agent() -> Agent:
    """Agent for analyzing feedback patterns"""
    return Agent(
        role="Outcome Analyst",
        goal="Analyze job application outcomes to improve future recommendations.",
        backstory="""You analyze feedback data to identify patterns:
        
        - Which enhancements led to interviews?
        - Which job boards had better response rates?
        - Which keywords worked for specific roles?
        - What resume versions performed best?
        
        IMPORTANT: Learning improves phrasing/prioritization only.
        Never suggests fabrication based on what 'works'.""",
        verbose=True,
        llm=create_llm()
    )


# ═══════════════════════════════════════════════════════════════════════════════
# AGENT REGISTRY
# ═══════════════════════════════════════════════════════════════════════════════

AGENT_REGISTRY = {
    'resume_parser': create_resume_parser_agent,
    'linkedin_extractor': create_linkedin_extractor_agent,
    'conflict_detector': create_conflict_detector_agent,
    'experience_graph': create_experience_graph_agent,
    'verification': create_verification_agent,
    'role_suggester': create_role_suggester_agent,
    'layer1_enhancer': create_layer1_enhancer_agent,
    'guardrail': create_guardrail_agent,
    'interview_prep': create_interview_prep_agent,
    'job_researcher': create_job_researcher_agent,
    'jd_fetcher': create_jd_fetcher_agent,
    'jd_analyzer': create_jd_analyzer_agent,
    'gap_analyst': create_gap_analyst_agent,
    'layer2_enhancer': create_layer2_enhancer_agent,
    'feedback_analyzer': create_feedback_analyzer_agent,
}


def get_agent(name: str) -> Agent:
    """Get agent by name from registry"""
    if name not in AGENT_REGISTRY:
        raise ValueError(f"Unknown agent: {name}. Available: {list(AGENT_REGISTRY.keys())}")
    return AGENT_REGISTRY[name]()
