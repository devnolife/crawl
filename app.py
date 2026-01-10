"""
🚀 SkillPulse AI - Web Interface
Real-time Developer Salary Intelligence Platform
Powered by Hugging Face Transformers
"""

import streamlit as st
import pandas as pd
from developer_crawler import DeveloperSkillsCrawler, NLP_AVAILABLE
from datetime import datetime

# Import NLP models if available
if NLP_AVAILABLE:
    from nlp_models import SalaryExtractor, SkillMatcher, SalaryPredictor

st.set_page_config(
    page_title="SkillPulse AI",
    page_icon="🚀",
    layout="wide"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
    }
    .aggregate-card {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 1.2rem;
        border-radius: 12px;
        color: white;
        margin: 0.5rem 0;
    }
    .ai-card {
        background: linear-gradient(135deg, #8E2DE2 0%, #4A00E0 100%);
        padding: 1.2rem;
        border-radius: 12px;
        color: white;
        margin: 0.5rem 0;
    }
    .live-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.3rem 0;
    }
    .skill-badge {
        display: inline-block;
        background: #667eea;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        margin: 0.2rem;
        font-size: 0.85rem;
    }
    .source-card {
        background: #f8f9fa;
        padding: 0.8rem;
        border-radius: 8px;
        border-left: 3px solid #667eea;
        margin: 0.3rem 0;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">🚀 SkillPulse AI</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; color:#666;">Real-time Developer Salary Intelligence • Powered by Hugging Face 🤗</p>', unsafe_allow_html=True)

@st.cache_resource
def get_crawler():
    return DeveloperSkillsCrawler(use_selenium=False)

@st.cache_resource
def get_nlp_models():
    if NLP_AVAILABLE:
        return {
            'extractor': SalaryExtractor(),
            'matcher': SkillMatcher(),
            'predictor': SalaryPredictor()
        }
    return None

crawler = get_crawler()
nlp_models = get_nlp_models()
skill_categories = crawler.get_skill_categories()

# Sidebar
st.sidebar.title("🤖 AI Status")
if NLP_AVAILABLE:
    st.sidebar.success("✅ NLP Models Loaded")
    st.sidebar.markdown("""
    **Models:**
    - 🔍 NER: `bert-base-NER`
    - 🎯 Similarity: `MiniLM-L12-v2`
    - 💰 Predictor: `all-MiniLM-L6-v2`
    """)
else:
    st.sidebar.warning("⚠️ NLP Models Not Available")
    st.sidebar.code("pip install transformers torch sentence-transformers")

st.sidebar.markdown("---")
stats = crawler.get_learning_stats()
st.sidebar.metric("📊 Learning Data", stats['total_salary_keys'])

# Main tabs
tabs = st.tabs(["🤖 AI Prediction", "🔍 Skill Matcher", "📝 Salary Extractor", 
                "🌐 Live Search", "💰 Rates", "🇮🇩 Salaries"])

# ========================================================================
# TAB 1: AI PREDICTION
# ========================================================================
with tabs[0]:
    st.subheader("🤖 AI Salary Prediction")
    st.markdown("Prediksi gaji berdasarkan deskripsi pekerjaan atau skill menggunakan AI")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📝 Input")
        
        input_method = st.radio("Metode Input", ["Job Description", "Manual Skills"])
        
        if input_method == "Job Description":
            job_desc = st.text_area(
                "Paste Job Description",
                height=150,
                placeholder="Contoh: Looking for React.js developer with 3+ years experience in building web applications..."
            )
            skills_input = None
        else:
            job_desc = None
            skills_input = st.multiselect(
                "Pilih Skills",
                ['react', 'vue', 'angular', 'nextjs', 'python', 'nodejs', 'php',
                 'golang', 'java', 'flutter', 'react_native', 'devops', 'aws',
                 'machine_learning', 'data_science'],
                default=['react', 'nodejs']
            )
        
        experience = st.selectbox("Experience Level", ['junior', 'mid', 'senior', 'lead'])
        city = st.selectbox("Kota", ['Makassar', 'Jakarta', 'Bandung', 'Surabaya', 'Remote (Indonesia)', 'Remote (Global)'])
        
        if st.button("🔮 Predict Salary", type="primary"):
            if NLP_AVAILABLE and nlp_models:
                with st.spinner("AI is analyzing..."):
                    predictor = nlp_models['predictor']
                    
                    prediction = predictor.predict_salary(
                        job_description=job_desc,
                        skills=skills_input,
                        experience=experience,
                        city=city
                    )
                    
                    with col2:
                        st.markdown("### 🎯 AI Prediction Result")
                        
                        st.markdown(f"""
                        <div class="ai-card">
                            <div style="font-size: 0.9rem; opacity: 0.9;">Predicted Salary</div>
                            <div style="font-size: 2rem; font-weight: 700;">
                                {prediction['predicted_formatted']}/bulan
                            </div>
                            <div style="font-size: 1rem; margin-top: 0.5rem;">
                                📊 Range: {prediction['range_formatted']}
                            </div>
                            <div style="margin-top: 1rem; font-size: 0.85rem; opacity: 0.9;">
                                🎯 Confidence: {prediction['confidence']:.0%}<br>
                                📂 Category: {prediction['category'].title()}<br>
                                📍 City Multiplier: {prediction['city_multiplier']:.2f}x
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.markdown("#### 🔧 Skills Detected")
                        skills = prediction.get('skills_detected', [])
                        if skills:
                            badges = ''.join([f'<span class="skill-badge">{s}</span>' for s in skills[:10]])
                            st.markdown(badges, unsafe_allow_html=True)
                        else:
                            st.info("No specific skills detected")
            else:
                with col2:
                    st.error("NLP Models not available. Install dependencies first.")
    
    with col2:
        if not NLP_AVAILABLE:
            st.warning("Install NLP dependencies untuk menggunakan fitur ini")
            st.code("pip install transformers torch sentence-transformers")

# ========================================================================
# TAB 2: SKILL MATCHER
# ========================================================================
with tabs[1]:
    st.subheader("🔍 Semantic Skill Matcher")
    st.markdown("Temukan skill serupa menggunakan AI semantic search")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        query = st.text_input("🔍 Cari Skill", placeholder="e.g., frontend web developer")
        top_k = st.slider("Jumlah hasil", 3, 10, 5)
        
        if st.button("🎯 Find Similar", type="primary", key="skill_match"):
            if NLP_AVAILABLE and nlp_models:
                with st.spinner("Searching..."):
                    matcher = nlp_models['matcher']
                    results = matcher.find_similar_skills(query, top_k)
                    
                    with col2:
                        st.markdown(f"### 🎯 Skills Similar to '{query}'")
                        
                        for r in results:
                            similarity_pct = int(r['similarity'] * 100)
                            bar_width = similarity_pct
                            
                            st.markdown(f"""
                            <div style="margin: 0.5rem 0;">
                                <div style="font-weight: 600;">{r['readable']}</div>
                                <div style="background: #e9ecef; border-radius: 5px; overflow: hidden;">
                                    <div style="width: {bar_width}%; background: linear-gradient(90deg, #667eea, #764ba2); 
                                                color: white; padding: 0.3rem 0.5rem; font-size: 0.85rem;">
                                        {similarity_pct}%
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
            else:
                with col2:
                    st.error("NLP models not available")
    
    with col2:
        if not query:
            st.info("👈 Masukkan skill yang ingin dicari")

# ========================================================================
# TAB 3: SALARY EXTRACTOR
# ========================================================================
with tabs[2]:
    st.subheader("📝 AI Salary Extractor")
    st.markdown("Ekstrak informasi gaji dari teks menggunakan NER (Named Entity Recognition)")
    
    sample_text = """
    Lowongan Frontend Developer di Makassar
    Gaji: Rp 15 juta - 25 juta per bulan
    
    Requirements:
    - React.js (3+ years)
    - TypeScript
    - Senior level bisa dapat sampai Rp 40 juta
    
    Untuk posisi remote, salary bisa mencapai $50-80/hour.
    """
    
    text_input = st.text_area("📝 Paste teks yang mengandung informasi gaji", 
                              value=sample_text, height=200)
    
    if st.button("🔍 Extract Salaries", type="primary", key="extract_btn"):
        if NLP_AVAILABLE and nlp_models:
            with st.spinner("Extracting with NER..."):
                extractor = nlp_models['extractor']
                salaries = extractor.extract_salary_from_text(text_input)
                
                if salaries:
                    st.markdown("### 💰 Extracted Salaries")
                    
                    for i, s in enumerate(salaries):
                        currency = s.get('currency', 'IDR')
                        value = s.get('value', 0)
                        
                        if currency == 'IDR':
                            formatted = f"Rp {value:,}"
                        else:
                            formatted = f"${value:,}"
                        
                        st.markdown(f"""
                        <div class="live-card">
                            <div style="font-size: 1.3rem; font-weight: 700;">{formatted}</div>
                            <div style="font-size: 0.85rem; opacity: 0.9;">
                                Source: {s.get('source', 'Unknown').title()}<br>
                                Raw: "{s.get('raw_text', '')}"
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No salary information found in the text")
        else:
            st.error("NLP models not available")

# ========================================================================
# TAB 4: LIVE SEARCH
# ========================================================================
with tabs[3]:
    st.subheader("🌐 Live Web Search")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        role = st.selectbox("👨‍💻 Role", 
                           ['frontend_developer', 'backend_developer', 'fullstack_developer',
                            'mobile_developer', 'devops_engineer', 'data_scientist'],
                           format_func=lambda x: x.replace('_', ' ').title())
        city = st.selectbox("📍 City", ['Makassar', 'Jakarta', 'Bandung', 'Surabaya'])
        
        if st.button("🚀 Live Search", type="primary"):
            with st.spinner("Searching the web..."):
                results = crawler.live_search_salaries(role, city)
                
                with col2:
                    st.markdown(f"### Results: {len(results)} found")
                    for r in results[:10]:
                        salary = r.get('salary', 0)
                        st.markdown(f"""
                        <div class="source-card">
                            <b>Rp {salary:,}</b> - {r.get('source', 'Unknown')}<br>
                            <small>{r.get('experience', 'Unknown')} | Confidence: {r.get('confidence', 0.5):.0%}</small>
                        </div>
                        """, unsafe_allow_html=True)

# ========================================================================
# TAB 5: RATES
# ========================================================================
with tabs[4]:
    st.subheader("💰 Freelancer Rates")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        cat = st.selectbox("Category", list(skill_categories.keys()))
        skill = st.selectbox("Skill", skill_categories[cat])
        
        if st.button("🔍 Get Rates", type="primary", key="rates_btn"):
            crawler.freelancer_rates = []
            results = crawler.crawl_freelancer_rates(skill)
            df = pd.DataFrame(results)
            
            with col2:
                for exp in ['Junior', 'Mid', 'Senior', 'Expert']:
                    exp_df = df[(df['experience'] == exp) & (df['is_aggregate'] == True)]
                    if not exp_df.empty:
                        agg = exp_df.iloc[0]
                        st.markdown(f"""
                        <div class="aggregate-card">
                            <b>{exp}</b>: ${int(agg['rate_avg_usd'])}/jam ≈ Rp {int(agg['rate_avg_idr']):,}
                        </div>
                        """, unsafe_allow_html=True)

# ========================================================================
# TAB 6: SALARIES
# ========================================================================
with tabs[5]:
    st.subheader("🇮🇩 Indonesia Developer Salaries")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        city = st.selectbox("City", ['Makassar', 'Jakarta', 'Bandung', 'Surabaya'], key="sal_c")
        role = st.selectbox("Role", ['frontend_developer', 'backend_developer', 'fullstack_developer',
                                     'mobile_developer', 'devops_engineer', 'data_scientist'],
                           format_func=lambda x: x.replace('_', ' ').title(), key="sal_r")
        
        if st.button("🔍 Get Salaries", type="primary", key="sal_btn"):
            crawler.salary_data = []
            results = crawler.crawl_indonesia_salaries(role, city)
            df = pd.DataFrame(results)
            
            with col2:
                for exp in ['Junior', 'Mid', 'Senior', 'Lead']:
                    exp_df = df[(df['experience'] == exp) & (df['is_aggregate'] == True)]
                    if not exp_df.empty:
                        agg = exp_df.iloc[0]
                        st.markdown(f"""
                        <div class="aggregate-card">
                            <b>{exp}</b>: {agg['salary_avg_formatted']}/bulan
                            <small style="opacity:0.9;">| Trend: {agg.get('trend', 'N/A')}</small>
                        </div>
                        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<p style="text-align:center; color:#888; font-size:0.85rem;">
    🚀 <b>SkillPulse AI</b> | Real-time Developer Salary Intelligence<br>
    Powered by Hugging Face 🤗 • Made with ❤️ in Makassar
</p>
""", unsafe_allow_html=True)
