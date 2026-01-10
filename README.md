# 🤖 Developer Skills & Rates AI

Sistem estimasi harga skill developer dengan AI (Hugging Face 🤗).

## ⭐ Features

| Feature | Description |
|---------|-------------|
| 🤖 **AI Prediction** | Prediksi gaji dari job description |
| 🔍 **Skill Matcher** | Semantic similarity search |
| 📝 **NER Extraction** | Ekstrak gaji dari teks |
| 🌐 **Live Search** | Web scraping real-time |
| 📚 **Learning** | Belajar dari data historis |

## 🚀 Quick Start

```bash
# Install dependencies
pip install streamlit pandas requests beautifulsoup4
pip install transformers torch sentence-transformers

# Run app
streamlit run app.py
```

Buka: **http://localhost:8501**

## 🤗 Hugging Face Models

| Model | Purpose |
|-------|---------|
| `dslim/bert-base-NER` | Named Entity Recognition |
| `paraphrase-multilingual-MiniLM-L12-v2` | Skill Similarity |
| `all-MiniLM-L6-v2` | Salary Prediction |

## 📁 Files

```
app.py                 # Streamlit UI
developer_crawler.py   # Main crawler + learning
nlp_models.py          # Hugging Face models
learning_data.json     # Auto-generated learning data
```

## 📊 Data Sources

**Freelancer Rates**: Upwork, Freelancer.com, Toptal, Arc.dev  
**Gaji Indonesia**: Glints, Jobstreet, LinkedIn, Kalibrr

---

**Version**: 3.0 (AI Edition)  
**Author**: Devnolife
