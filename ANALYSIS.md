# Analisis Project SkillPulse AI & GitHub Portfolio ML

## Ringkasan Eksekutif

Project ini merupakan **platform all-in-one** untuk analisis skill developer yang terdiri dari dua sistem terintegrasi:

1. **SkillPulse AI** - Platform intelijen gaji developer berbasis Streamlit dengan AI/ML
2. **GitHub Portfolio ML** - Aplikasi analisis portfolio GitHub berbasis Next.js + FastAPI

---

## Arsitektur Project

```
┌─────────────────────────────────────────────────────────────────────┐
│                         SKILLPULSE AI                                │
│                    (Streamlit Web Interface)                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│  │ Job Search   │  │ AI Prediction│  │ Skill Matcher│               │
│  │ (Firecrawl)  │  │ (ML Models)  │  │ (Embeddings) │               │
│  └──────────────┘  └──────────────┘  └──────────────┘               │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                    NLP MODELS LAYER                           │   │
│  │  - SalaryExtractor (NER - bert-base-NER)                     │   │
│  │  - SkillMatcher (Sentence Transformers - MiniLM-L12-v2)      │   │
│  │  - SalaryPredictor (Embeddings - all-MiniLM-L6-v2)           │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                    CRAWLER LAYER                              │   │
│  │  - DeveloperSkillsCrawler (Web scraping + Learning)          │   │
│  │  - LearningDataStore (Penyimpanan data + Tren)               │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                     GITHUB PORTFOLIO ML                              │
│                   (Next.js 16 + FastAPI)                            │
├──────────────────────────────┬──────────────────────────────────────┤
│         FRONTEND             │              BACKEND                  │
│         (Next.js)            │              (FastAPI)                │
├──────────────────────────────┼──────────────────────────────────────┤
│  - App Router (Next.js 16)   │  - SkillAnalyzer Service             │
│  - NextAuth v5 (Auth)        │  - CVRecommender Service             │
│  - Prisma ORM (PostgreSQL)   │  - Sentence Transformers             │
│  - Tailwind CSS v4           │  - API Endpoints (/api/*)            │
│  - React 19.2                │  - CORS Middleware                   │
└──────────────────────────────┴──────────────────────────────────────┘
```

---

## Stack Teknologi

### Frontend (Next.js Application)
| Teknologi | Versi | Kegunaan |
|-----------|-------|----------|
| Next.js | 16.1.1 | Framework React dengan App Router |
| React | 19.2.3 | Library UI |
| TypeScript | 5.x | Type safety |
| Tailwind CSS | 4.x | Styling |
| NextAuth | 5.0.0-beta.30 | Authentication |
| Prisma | 7.2.0 | ORM untuk PostgreSQL |

### Backend ML (Python)
| Teknologi | Versi | Kegunaan |
|-----------|-------|----------|
| FastAPI | 0.104+ | API Framework |
| Transformers | 4.35+ | Hugging Face NLP |
| Sentence-Transformers | 2.2+ | Semantic similarity |
| PyTorch | 2.1+ | ML Framework |
| scikit-learn | 1.3+ | ML utilities |

### SkillPulse (Streamlit)
| Teknologi | Versi | Kegunaan |
|-----------|-------|----------|
| Streamlit | 1.28+ | Web interface |
| BeautifulSoup4 | 4.12+ | Web scraping |
| Selenium | 4.15+ | Browser automation (optional) |
| Firecrawl | 0.0.1+ | Advanced scraping (optional) |

---

## Fitur Utama

### 1. SkillPulse AI Features

#### 🔍 Job Search (Firecrawl Integration)
- Pencarian lowongan real-time dari Glints, Jobstreet, LinkedIn
- Scraping data gaji dengan Firecrawl API
- Filtering berdasarkan lokasi dan keyword

#### 🤖 AI Salary Prediction
- Prediksi gaji dari job description menggunakan NER
- Support input manual skills
- City multiplier untuk berbagai kota di Indonesia:
  - Jakarta: 1.35x
  - Bandung: 0.95x
  - Surabaya: 0.88x
  - Makassar: 0.75x (default)
  - Remote Global: 2.5x

#### 🔍 Semantic Skill Matcher
- Pencarian skill serupa dengan Sentence Transformers
- Pre-computed embeddings untuk 17+ kategori skill
- Similarity scoring dengan cosine similarity

#### 📝 Salary Extractor (NER)
- Ekstraksi gaji dari teks dengan regex + NER
- Support format IDR dan USD
- Deteksi range gaji

#### 📚 Learning System
- Weighted average berdasarkan recency data
- Trend analysis (naik/turun/stabil)
- Penyimpanan data points dengan timestamp

### 2. GitHub Portfolio ML Features

#### 📊 Skill Analysis
- Ekstraksi skills dari repository metadata
- Kategorisasi: Frontend, Backend, Mobile, Database, DevOps, Data Science
- Experience level calculation (Beginner → Expert)
- Strength score (0-100)

#### 📝 CV Recommendations
- Generate summary berdasarkan portfolio
- Highlight projects rekomendasi
- Skills section yang optimal
- Improvement suggestions

#### 🔐 Authentication
- GitHub OAuth (dengan scope repo access)
- Google OAuth
- Database session strategy

---

## Database Schema (PostgreSQL)

```prisma
// User Management
model User {
  id            String    @id
  name          String?
  email         String?   @unique
  emailVerified DateTime?
  image         String?
  accounts      Account[]
  sessions      Session[]
  githubData    GithubData?
}

// GitHub Data Storage
model GithubData {
  id                String   @id
  userId            String   @unique
  username          String
  publicRepos       Int
  followers         Int
  repos             Json     // Repository data
  languages         Json     // Language statistics
  contributions     Json     // Contribution data
  skillAnalysis     Json?    // ML analysis result
  cvRecommendations Json?    // CV recommendations
}
```

---

## Data Sources & Coverage

### Salary Data Sources
| Platform | Jenis Data | Status |
|----------|------------|--------|
| Upwork | Freelancer rates (USD/hour) | ✅ Implemented |
| Freelancer | Freelancer rates | ✅ Implemented |
| Toptal | Premium rates | ✅ Implemented |
| Arc.dev | Remote rates | ✅ Implemented |
| Glints | Indonesia salaries | ✅ Implemented |
| Jobstreet | Indonesia salaries | ✅ Implemented |
| LinkedIn | Indonesia salaries | ✅ Implemented |
| Kalibrr | Indonesia salaries | ✅ Implemented |

### Supported Roles
- Frontend Developer
- Backend Developer
- Fullstack Developer
- Mobile Developer
- DevOps Engineer
- Data Scientist
- UI/UX Designer
- QA Engineer

### Supported Cities (Indonesia)
- Jakarta (multiplier: 1.35x)
- Bandung (multiplier: 0.95x)
- Surabaya (multiplier: 0.88-0.9x)
- Makassar (base rate)
- Remote Indonesia (1.25x)
- Remote Global (2.5x)

---

## AI/ML Models

### 1. Named Entity Recognition (NER)
```
Model: dslim/bert-base-NER
Size: ~400MB
Task: Ekstraksi salary mentions dari teks
```

### 2. Semantic Similarity
```
Model: paraphrase-multilingual-MiniLM-L12-v2
Size: ~470MB
Task: Skill matching & similarity search
Support: Multilingual (termasuk Indonesia)
```

### 3. Text Embeddings
```
Model: all-MiniLM-L6-v2
Size: ~90MB
Task: Salary prediction & categorization
```

---

## API Endpoints

### Backend ML API (FastAPI)

| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| GET | `/` | Root info |
| GET | `/health` | Health check |
| POST | `/api/analyze-skills` | Analisis skill dari GitHub data |
| POST | `/api/cv-recommendations` | Generate rekomendasi CV |
| POST | `/api/full-analysis` | Kombinasi skill + CV analysis |

### Frontend API Routes (Next.js)

| Route | Deskripsi |
|-------|-----------|
| `/api/auth/[...nextauth]` | NextAuth handlers |
| `/api/github` | Sync GitHub data |
| `/api/analysis` | Trigger ML analysis |

---

## Kelebihan Project

### ✅ Technical Excellence
1. **Modern Stack**: Next.js 16 + React 19 + FastAPI + PyTorch
2. **Type Safety**: TypeScript di frontend, Pydantic di backend
3. **Scalable Architecture**: Microservices-ready dengan separation of concerns
4. **Learning System**: Data-driven dengan weighted averages

### ✅ Feature Rich
1. **Multi-source data**: 8+ sumber data gaji
2. **AI-powered**: 3 model ML berbeda untuk tasks berbeda
3. **Real-time scraping**: Live data dengan Firecrawl/Selenium
4. **Indonesian Focus**: Data khusus pasar Indonesia

### ✅ User Experience
1. **Beautiful UI**: Modern glassmorphism design
2. **Responsive**: Mobile-friendly
3. **Real-time**: Live data updates
4. **OAuth Integration**: Login mudah dengan GitHub/Google

---

## Area untuk Improvement

### 🔧 Technical Debt
1. **Error Handling**: Beberapa try-except terlalu generic
2. **Testing**: Belum ada test coverage yang comprehensive
3. **Logging**: Perlu centralized logging system
4. **Rate Limiting**: API belum ada rate limiting

### 🔧 Feature Gaps
1. **Firecrawl Integration**: Masih optional, perlu full integration
2. **Mobile App**: Roadmap item, belum diimplementasi
3. **Browser Extension**: Roadmap item
4. **Job Alerts**: Belum ada notification system

### 🔧 Performance
1. **Model Loading**: Lazy loading untuk ML models
2. **Caching**: Redis caching untuk frequent queries
3. **Database Indexing**: Optimasi query dengan proper indexes

---

## Cara Menjalankan

### SkillPulse (Streamlit)
```bash
# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env dengan API keys

# Run
streamlit run app.py
# Buka http://localhost:8501
```

### GitHub Portfolio Frontend
```bash
cd frontend

# Install dependencies
npm install

# Setup environment
cp .env.example .env.local
# Edit dengan GitHub/Google OAuth credentials

# Setup database
npx prisma generate
npx prisma db push

# Run development
npm run dev
# Buka http://localhost:3000
```

### Backend ML API
```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env

# Run
uvicorn app.main:app --reload
# API di http://localhost:8000
# Docs di http://localhost:8000/docs
```

---

## Environment Variables

### Root (.env)
```
FIRECRAWL_API_KEY=fc-xxx
HUGGINGFACE_TOKEN=hf_xxx
DEFAULT_CITY=Makassar
USD_TO_IDR=15800
USE_SELENIUM=false
```

### Frontend (.env.local)
```
AUTH_SECRET=xxx
GITHUB_CLIENT_ID=xxx
GITHUB_CLIENT_SECRET=xxx
GOOGLE_CLIENT_ID=xxx
GOOGLE_CLIENT_SECRET=xxx
DATABASE_URL=postgresql://...
```

### Backend (.env)
```
CORS_ORIGINS=http://localhost:3000
API_HOST=0.0.0.0
API_PORT=8000
```

---

## Kesimpulan

Project ini adalah **platform analisis skill developer yang komprehensif** dengan kombinasi:
- Web scraping untuk data gaji real-time
- Machine Learning untuk prediksi dan similarity
- GitHub integration untuk analisis portfolio
- Modern tech stack dengan excellent DX

Project ini cocok untuk:
1. **Developer** yang ingin tahu market value mereka
2. **HR/Recruiter** yang butuh benchmark gaji
3. **Job Seeker** yang mau optimize CV

**Rating Technical: 8/10** - Arsitektur solid, implementasi modern, dengan room for improvement di testing dan production-readiness.

---

*Analisis dibuat pada: January 19, 2026*
*Author: AI Analysis Bot*
