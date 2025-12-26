# Resume Intelligence Platform
## Frontend ↔ Backend API Mapping

This document maps the Lovable frontend prompts to the Flask backend endpoints.

---

## 📊 API Endpoint Mapping

| Frontend Action | Lovable Prompt | Backend Endpoint | Status |
|-----------------|----------------|------------------|--------|
| Upload Resume | Prompt 2 | `POST /api/parse-resume` | ✅ Ready |
| Create Experience Graph | Prompt 4 | `POST /api/build-graph` | ✅ Ready |
| Micro-Verification | Prompt 4 | `POST /api/verify` | ✅ Ready |
| Suggest Roles | Prompt 5 | `POST /api/suggest-roles` | ✅ Ready |
| Confirm Roles | Prompt 5 | `POST /api/confirm-roles` | ✅ Ready |
| Layer 1 Enhancement | Prompt 6 | `POST /api/enhance/layer1` | ✅ Ready |
| Search Jobs | Prompt 8 | `POST /api/search-jobs` | ✅ Ready |
| Get Jobs | Prompt 9 | `GET /api/jobs` | ✅ Ready |
| Fetch JD | Prompt 10 | `POST /api/fetch-jd` | ✅ Ready |
| Analyze JD | Prompt 10 | `POST /api/analyze-jd` | ✅ Ready |
| Gap Analysis | Prompt 10 | `POST /api/gap-analysis` | ✅ Ready |
| Layer 2 Enhancement | Prompt 11 | `POST /api/enhance/layer2` | ✅ Ready |
| Export DOCX | Prompt 14 | `POST /api/export/docx` | ✅ Ready |
| Submit Feedback | N/A | `POST /api/feedback` | ✅ Ready |

---

## 🔌 Frontend API Client

```typescript
// src/lib/api.ts

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:5000';

export interface ParseResumeResponse {
  success: boolean;
  sessionId: string;
  rawText: string;
  bulletCount: number;
  bullets: string[];
  nextStep: string;
}

export interface ExperienceGraph {
  id: string;
  skills: {
    technical: string[];
    aiml: string[];
    tools: string[];
    soft: string[];
  };
  seniorityScores: {
    technicalDepth: number;
    leadership: number;
    scope: number;
    autonomy: number;
    impact: number;
  };
  experienceYears: number;
  industries: string[];
  achievements: string[];
}

export interface SuggestedRole {
  title: string;
  confidence: 'strong' | 'borderline' | 'risky';
  reason: string;
  matchScore: number;
  selected?: boolean;
}

export interface BulletEnhancement {
  id: string;
  original: string;
  enhanced: string;
  originalScore: number;
  enhancedScore: number;
  changes: string[];
  status: 'enhanced' | 'kept' | 'flagged';
  defendable: boolean;
  interviewTips: string[];
}

export interface Layer1Result {
  sessionId: string;
  originalATS: number;
  enhancedATS: number;
  bullets: BulletEnhancement[];
  summary: {
    totalBullets: number;
    enhanced: number;
    kept: number;
    flagged: number;
  };
}

export interface JobListing {
  id: string;
  title: string;
  company: string;
  location: string;
  salary?: string;
  workType: string;
  url: string;
  source: string;
  postedDate?: string;
  requiredSkills: string[];
  preferredSkills: string[];
  matchScore: number;
  skillMatch: {
    present: string[];
    missing: string[];
  };
}

export interface JDAnalysis {
  jobTitle: string;
  company: string;
  location?: string;
  salary?: string;
  requiredSkills: Array<{ skill: string; priority: string; years?: string }>;
  preferredSkills: Array<{ skill: string; priority: string }>;
  responsibilities: string[];
  keywords: string[];
  senioritySignals: string[];
}

export interface GapAnalysis {
  skillsPresent: Array<{ skill: string; evidence: string; strength: string }>;
  skillsHidden: Array<{ skill: string; evidence: string; action: string }>;
  skillsMissing: Array<{ skill: string; priority: string; reason: string }>;
  enhancementScope: Array<{ suggestion: string; impact: string }>;
  overallMatch: number;
}

export interface Layer2Result {
  sessionId: string;
  jobId: string;
  customizedResume: {
    bullets: Array<{
      id: string;
      layer1: string;
      layer2: string;
      relevanceScore: number;
      changes: string[];
      jdKeywordsMatched: string[];
      position: number;
    }>;
    reorderedSections: boolean;
  };
  scores: {
    originalATS: number;
    layer1ATS: number;
    layer2ATS: number;
    jdMatch: number;
    keywordCoverage: number;
    confidence: number;
  };
  improvements: {
    totalImprovement: string;
    fromLayer1: string;
  };
  jdKeywordsMatched: string[];
}

// API Functions
export const api = {
  // Stage 1: Parse Resume
  async parseResume(file: File): Promise<ParseResumeResponse> {
    const formData = new FormData();
    formData.append('resume', file);
    
    const response = await fetch(`${API_BASE}/api/parse-resume`, {
      method: 'POST',
      body: formData,
    });
    return response.json();
  },

  // Stage 2: Micro-Verification (Optional)
  async getVerificationQuestions(sessionId: string) {
    const response = await fetch(`${API_BASE}/api/verify`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sessionId }),
    });
    return response.json();
  },

  async submitVerificationAnswers(sessionId: string, answers: Array<{id: string, answer: string}>) {
    const response = await fetch(`${API_BASE}/api/verify/answers`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sessionId, answers }),
    });
    return response.json();
  },

  // Stage 3: Build Experience Graph
  async buildExperienceGraph(sessionId: string) {
    const response = await fetch(`${API_BASE}/api/build-graph`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sessionId }),
    });
    return response.json();
  },

  // Stage 4: Role Suggestions
  async suggestRoles(sessionId: string) {
    const response = await fetch(`${API_BASE}/api/suggest-roles`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sessionId }),
    });
    return response.json();
  },

  async confirmRoles(sessionId: string, selectedRoles: string[]) {
    const response = await fetch(`${API_BASE}/api/confirm-roles`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sessionId, selectedRoles }),
    });
    return response.json();
  },

  // Stage 5: Layer 1 Enhancement
  async enhanceLayer1(sessionId: string) {
    const response = await fetch(`${API_BASE}/api/enhance/layer1`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sessionId }),
    });
    return response.json();
  },

  // Stage 6: Job Search
  async searchJobs(sessionId: string, location?: string) {
    const response = await fetch(`${API_BASE}/api/search-jobs`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sessionId, location }),
    });
    return response.json();
  },

  // Stage 7: Get Jobs
  async getJobs(sessionId: string) {
    const response = await fetch(`${API_BASE}/api/jobs?sessionId=${sessionId}`);
    return response.json();
  },

  // Stage 8: Fetch JD
  async fetchJD(sessionId: string, jobId: string, jobUrl: string, manualJD?: string) {
    const response = await fetch(`${API_BASE}/api/fetch-jd`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sessionId, jobId, jobUrl, manualJD }),
    });
    return response.json();
  },

  // Stage 9: Analyze JD
  async analyzeJD(sessionId: string, jobId: string) {
    const response = await fetch(`${API_BASE}/api/analyze-jd`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sessionId, jobId }),
    });
    return response.json();
  },

  // Stage 10: Gap Analysis
  async gapAnalysis(sessionId: string, jobId: string) {
    const response = await fetch(`${API_BASE}/api/gap-analysis`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sessionId, jobId }),
    });
    return response.json();
  },

  // Stage 11: Layer 2 Enhancement
  async enhanceLayer2(sessionId: string, jobId: string) {
    const response = await fetch(`${API_BASE}/api/enhance/layer2`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sessionId, jobId }),
    });
    return response.json();
  },

  // Stage 12: Export DOCX
  async exportDocx(sessionId: string, version: 'layer1' | 'layer2', jobId?: string) {
    const response = await fetch(`${API_BASE}/api/export/docx`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sessionId, version, jobId }),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error);
    }
    
    // Download the file
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `resume_${version}_${sessionId}.docx`;
    a.click();
    window.URL.revokeObjectURL(url);
  },

  // Stage 13: Feedback
  async submitFeedback(sessionId: string, jobId: string, status: string, notes?: string) {
    const response = await fetch(`${API_BASE}/api/feedback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sessionId, jobId, status, notes }),
    });
    return response.json();
  },
};
```

---

## 🔄 Frontend Flow → Backend Calls

### Upload Page (Prompt 2)
```
User uploads resume
    ↓
api.parseResume(file)
    ↓
Store sessionId in state
    ↓
Navigate to /roles
```

### Role Selection (Prompt 5)
```
Page loads
    ↓
api.buildExperienceGraph(sessionId)
    ↓
api.suggestRoles(sessionId)
    ↓
Display roles with confidence badges
    ↓
User selects roles
    ↓
api.confirmRoles(sessionId, selectedRoles)
    ↓
Navigate to /processing
```

### Processing Page (Prompt 6)
```
Page loads
    ↓
api.enhanceLayer1(sessionId)  // Takes 20-60 seconds
    ↓
Poll for progress (or use websockets)
    ↓
api.searchJobs(sessionId)     // Run in parallel
    ↓
Navigate to /results
```

### Results Dashboard (Prompts 7, 9, 13, 14)
```
Page loads with Layer1 results
    ↓
Tabs:
├── Resume: Show before/after from layer1Result.bullets
├── Diff: Show changes and interview tips
├── Jobs: api.getJobs(sessionId)
├── Skills: From experienceGraph
└── Export: api.exportDocx(sessionId, 'layer1')
```

### Job Customization (Prompts 10-12)
```
User clicks "Customize for This Job"
    ↓
api.fetchJD(sessionId, jobId, jobUrl)
    ↓
api.analyzeJD(sessionId, jobId)
    ↓
api.gapAnalysis(sessionId, jobId)
    ↓
api.enhanceLayer2(sessionId, jobId)
    ↓
Display customized resume with scores
    ↓
api.exportDocx(sessionId, 'layer2', jobId)
```

---

## 📱 React State Structure

```typescript
// src/store/resumeStore.ts (using Zustand)

import { create } from 'zustand';

interface ResumeState {
  // Session
  sessionId: string | null;
  
  // Stage 1: Upload
  uploadedFile: File | null;
  parsedData: ParseResumeResponse | null;
  
  // Stage 3: Experience Graph
  experienceGraph: ExperienceGraph | null;
  
  // Stage 4: Roles
  suggestedRoles: SuggestedRole[];
  selectedRoles: string[];
  
  // Stage 5: Layer 1
  layer1Result: Layer1Result | null;
  
  // Stage 6-7: Jobs
  jobs: JobListing[];
  selectedJob: JobListing | null;
  
  // Stage 9-10: JD Analysis
  jdAnalysis: JDAnalysis | null;
  gapAnalysis: GapAnalysis | null;
  
  // Stage 11: Layer 2
  layer2Result: Layer2Result | null;
  
  // UI State
  currentStage: number;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  setSessionId: (id: string) => void;
  setUploadedFile: (file: File) => void;
  setParsedData: (data: ParseResumeResponse) => void;
  setExperienceGraph: (graph: ExperienceGraph) => void;
  setSuggestedRoles: (roles: SuggestedRole[]) => void;
  setSelectedRoles: (roles: string[]) => void;
  setLayer1Result: (result: Layer1Result) => void;
  setJobs: (jobs: JobListing[]) => void;
  setSelectedJob: (job: JobListing) => void;
  setJdAnalysis: (analysis: JDAnalysis) => void;
  setGapAnalysis: (analysis: GapAnalysis) => void;
  setLayer2Result: (result: Layer2Result) => void;
  setCurrentStage: (stage: number) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  reset: () => void;
}

export const useResumeStore = create<ResumeState>((set) => ({
  sessionId: null,
  uploadedFile: null,
  parsedData: null,
  experienceGraph: null,
  suggestedRoles: [],
  selectedRoles: [],
  layer1Result: null,
  jobs: [],
  selectedJob: null,
  jdAnalysis: null,
  gapAnalysis: null,
  layer2Result: null,
  currentStage: 1,
  isLoading: false,
  error: null,
  
  setSessionId: (id) => set({ sessionId: id }),
  setUploadedFile: (file) => set({ uploadedFile: file }),
  setParsedData: (data) => set({ parsedData: data }),
  setExperienceGraph: (graph) => set({ experienceGraph: graph }),
  setSuggestedRoles: (roles) => set({ suggestedRoles: roles }),
  setSelectedRoles: (roles) => set({ selectedRoles: roles }),
  setLayer1Result: (result) => set({ layer1Result: result }),
  setJobs: (jobs) => set({ jobs: jobs }),
  setSelectedJob: (job) => set({ selectedJob: job }),
  setJdAnalysis: (analysis) => set({ jdAnalysis: analysis }),
  setGapAnalysis: (analysis) => set({ gapAnalysis: analysis }),
  setLayer2Result: (result) => set({ layer2Result: result }),
  setCurrentStage: (stage) => set({ currentStage: stage }),
  setLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error: error }),
  reset: () => set({
    sessionId: null,
    uploadedFile: null,
    parsedData: null,
    experienceGraph: null,
    suggestedRoles: [],
    selectedRoles: [],
    layer1Result: null,
    jobs: [],
    selectedJob: null,
    jdAnalysis: null,
    gapAnalysis: null,
    layer2Result: null,
    currentStage: 1,
    isLoading: false,
    error: null,
  }),
}));
```

---

## 🧪 Testing Endpoints

```bash
# Health check
curl http://localhost:5000/health

# Parse resume
curl -X POST http://localhost:5000/api/parse-resume \
  -F "resume=@test_resume.pdf"

# Build graph (replace SESSION_ID)
curl -X POST http://localhost:5000/api/build-graph \
  -H "Content-Type: application/json" \
  -d '{"sessionId": "SESSION_ID"}'

# Suggest roles
curl -X POST http://localhost:5000/api/suggest-roles \
  -H "Content-Type: application/json" \
  -d '{"sessionId": "SESSION_ID"}'

# Layer 1 enhancement
curl -X POST http://localhost:5000/api/enhance/layer1 \
  -H "Content-Type: application/json" \
  -d '{"sessionId": "SESSION_ID"}'

# Search jobs
curl -X POST http://localhost:5000/api/search-jobs \
  -H "Content-Type: application/json" \
  -d '{"sessionId": "SESSION_ID", "location": "San Francisco, CA"}'
```

---

## ⚠️ CORS Configuration

The backend is configured to accept requests from:
- `http://localhost:5173` (Vite default)
- `http://localhost:3000` (Create React App / Next.js)

To add more origins, update `.env`:
```
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,http://your-domain.com
```

---

## 🚀 Quick Start

### Backend
```bash
cd /workspace/resume-intelligence-platform
cp .env.example .env
# Add your OPENAI_API_KEY to .env
pip install -r requirements.txt
python app.py
```

### Frontend (after Lovable prompts)
```bash
# Create React app or use Lovable
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
# Add API client from above
npm run dev
```

---

## 📋 Validation Checklist

After each Lovable prompt, verify:

- [ ] API calls return expected data
- [ ] Loading states show correctly
- [ ] Errors are caught and displayed
- [ ] Navigation works between stages
- [ ] State persists correctly
- [ ] Mobile responsive
