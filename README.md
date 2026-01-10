<div align="center">

# 🚀 SkillPulse AI

### *Real-time Developer Salary Intelligence Platform*

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![HuggingFace](https://img.shields.io/badge/🤗_Transformers-yellow?style=for-the-badge)](https://huggingface.co)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

*Powered by AI to help developers understand their market value*

[**Live Demo**](#-quick-start) · [**Features**](#-features) · [**Documentation**](#-documentation) · [**Contributing**](#-contributing)

---

<img src="https://raw.githubusercontent.com/devnolife/crawl/main/docs/demo.gif" alt="SkillPulse Demo" width="600">

</div>

---

## 🎯 What is SkillPulse AI?

**SkillPulse AI** is an intelligent platform that provides real-time insights into developer salaries, freelancer rates, and skill valuations across Southeast Asia. Using cutting-edge NLP models from Hugging Face, it analyzes job postings, extracts salary data, and predicts compensation based on skills and experience.

### 💡 Why SkillPulse?

- 🎯 **Know Your Worth** — Get accurate salary estimates for your skill set
- 📊 **Data-Driven Decisions** — Make informed career choices with real market data
- 🤖 **AI-Powered** — Leverages BERT and Sentence Transformers for intelligent analysis
- 🌍 **Local Focus** — Specialized for Indonesian tech market (Jakarta, Makassar, Bandung, Surabaya)

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 🤖 AI Salary Prediction
Paste a job description and get instant salary predictions using semantic analysis.

### 🔍 Semantic Skill Matcher  
Find related skills using AI embeddings — "React" → Next.js, TypeScript, Redux

</td>
<td width="50%">

### 📝 NER Salary Extraction
Extract salary mentions from any text using Named Entity Recognition.

### 📚 Learning System
Platform learns from collected data to improve accuracy over time.

</td>
</tr>
</table>

### 🌐 Multi-Source Data Aggregation

```
┌─────────────────────────────────────────────────────────────┐
│                     DATA SOURCES                             │
├─────────────┬─────────────┬─────────────┬──────────────────┤
│   Upwork    │  Freelancer │   Toptal    │     Arc.dev     │
├─────────────┼─────────────┼─────────────┼──────────────────┤
│   Glints    │  Jobstreet  │  LinkedIn   │    Kalibrr      │
└─────────────┴─────────────┴─────────────┴──────────────────┘
                           ↓
              📊 Aggregated & Weighted Average
                           ↓
                   🎯 Final Estimate
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- pip or conda

### Installation

```bash
# Clone the repository
git clone https://github.com/devnolife/crawl.git
cd crawl

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

### Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit with your API keys (optional but recommended)
nano .env
```

### Run

```bash
streamlit run app.py
```

🎉 Open **http://localhost:8501** in your browser!

---

## 🤗 AI Models

SkillPulse uses state-of-the-art NLP models:

| Model | Purpose | Size |
|-------|---------|------|
| `dslim/bert-base-NER` | Named Entity Recognition | ~400MB |
| `paraphrase-multilingual-MiniLM-L12-v2` | Semantic Similarity | ~470MB |
| `all-MiniLM-L6-v2` | Text Embeddings | ~90MB |

> Models are automatically downloaded on first run and cached locally.

---

## 📁 Project Structure

```
skillpulse-ai/
│
├── 🎨 app.py                    # Streamlit web interface
├── 🔧 developer_crawler.py      # Core crawler & learning engine
├── 🧠 nlp_models.py             # HuggingFace NLP models
│
├── 📁 src/
│   ├── __init__.py
│   └── config.py                # Environment configuration
│
├── 📁 data/
│   ├── learning_data.json       # Learning history
│   └── exports/                 # CSV/JSON exports
│
├── 📁 models/
│   └── cache/                   # Model cache
│
├── 📄 .env.example              # Environment template
├── 📄 requirements.txt          # Dependencies
└── 📄 README.md                 # You are here!
```

---

## ⚙️ Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `FIRECRAWL_API_KEY` | API key for advanced scraping | - |
| `HUGGINGFACE_TOKEN` | HF token for private models | - |
| `DEFAULT_CITY` | Default city for salary lookup | `Makassar` |
| `USD_TO_IDR` | Exchange rate | `15800` |
| `USE_SELENIUM` | Enable browser automation | `false` |

---

## 📊 Sample Output

### Salary Prediction

```json
{
  "predicted_salary": 24000000,
  "range": "Rp 20,400,000 - Rp 27,600,000",
  "confidence": 0.85,
  "category": "fullstack",
  "skills_detected": ["react", "nodejs", "typescript"],
  "city_multiplier": 0.75
}
```

### Skill Matching

```
Query: "frontend web developer"

Results:
├── React        (92% match)
├── Vue          (88% match)
├── Angular      (85% match)
├── Next.js      (82% match)
└── TypeScript   (79% match)
```

---

## 📈 Roadmap

- [x] Multi-source salary aggregation
- [x] AI salary prediction
- [x] Semantic skill matching
- [x] NER salary extraction
- [x] Learning system
- [ ] Firecrawl integration
- [ ] Job search & matching
- [ ] Browser extension
- [ ] API endpoints
- [ ] Mobile app

---

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) first.

```bash
# Fork, clone, and create a branch
git checkout -b feature/amazing-feature

# Make your changes and commit
git commit -m 'Add amazing feature'

# Push and create a Pull Request
git push origin feature/amazing-feature
```

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

<div align="center">

**Devnolife**

[![GitHub](https://img.shields.io/badge/GitHub-@devnolife-181717?style=for-the-badge&logo=github)](https://github.com/devnolife)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0077B5?style=for-the-badge&logo=linkedin)](https://linkedin.com/in/devnolife)

</div>

---

<div align="center">

### ⭐ Star this repo if you find it useful!

Made with ❤️ in **Makassar, Indonesia** 🇮🇩

</div>
