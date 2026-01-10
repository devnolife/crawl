"""
NLP Models for Developer Skills Crawler
Menggunakan Hugging Face models untuk:
1. NER - Ekstrak gaji dari teks
2. Sentence Similarity - Skill matching
3. Salary Prediction - Prediksi gaji dari deskripsi
"""

import re
import logging
from typing import List, Dict, Tuple, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flag untuk check apakah models tersedia
MODELS_AVAILABLE = False
NER_MODEL = None
SIMILARITY_MODEL = None
TOKENIZER = None

try:
    from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification
    from sentence_transformers import SentenceTransformer, util
    import torch
    MODELS_AVAILABLE = True
    logger.info("✓ Transformers dan SentenceTransformers tersedia")
except ImportError as e:
    logger.warning(f"ML libraries not available: {e}")
    logger.warning("Install dengan: pip install transformers torch sentence-transformers")


class SalaryExtractor:
    """
    Ekstrak informasi gaji dari teks menggunakan NER + regex
    """
    
    def __init__(self):
        self.ner_pipeline = None
        self._init_ner()
        
        # Regex patterns untuk gaji Indonesia
        self.salary_patterns = [
            # Rp format
            r'[Rr]p\.?\s*([\d.,]+)\s*(juta|jt|ribu|rb|million|k)?',
            r'([\d.,]+)\s*(juta|jt)\s*(?:per\s*bulan|/\s*bulan|/bln)?',
            r'gaji\s*:?\s*([\d.,]+)\s*(juta|jt)?',
            r'salary\s*:?\s*\$?([\d.,]+)k?',
            # Range format
            r'([\d.,]+)\s*-\s*([\d.,]+)\s*(juta|jt|million)?',
            # USD format
            r'\$\s*([\d.,]+)(?:k|K)?(?:\s*/\s*(?:hour|hr|jam))?',
        ]
    
    def _init_ner(self):
        """Initialize NER model"""
        if not MODELS_AVAILABLE:
            return
        
        try:
            # Use a lightweight NER model
            self.ner_pipeline = pipeline(
                "ner",
                model="dslim/bert-base-NER",
                aggregation_strategy="simple"
            )
            logger.info("✓ NER model loaded: dslim/bert-base-NER")
        except Exception as e:
            logger.warning(f"Could not load NER model: {e}")
    
    def extract_salary_from_text(self, text: str) -> List[Dict]:
        """
        Ekstrak semua mention gaji dari teks
        Returns: List of {value, currency, period, raw_text}
        """
        results = []
        
        # 1. Regex-based extraction
        regex_results = self._extract_with_regex(text)
        results.extend(regex_results)
        
        # 2. NER-based extraction (for MONEY entities)
        if self.ner_pipeline:
            ner_results = self._extract_with_ner(text)
            results.extend(ner_results)
        
        # Remove duplicates
        seen = set()
        unique_results = []
        for r in results:
            key = (r.get('value', 0), r.get('currency', ''))
            if key not in seen:
                seen.add(key)
                unique_results.append(r)
        
        return unique_results
    
    def _extract_with_regex(self, text: str) -> List[Dict]:
        """Extract using regex patterns"""
        results = []
        
        for pattern in self.salary_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    groups = match.groups()
                    value_str = groups[0].replace('.', '').replace(',', '')
                    value = float(value_str)
                    
                    # Determine multiplier
                    suffix = groups[1].lower() if len(groups) > 1 and groups[1] else ''
                    if suffix in ['juta', 'jt', 'million']:
                        value *= 1000000
                    elif suffix in ['ribu', 'rb', 'k']:
                        value *= 1000
                    
                    # Determine currency
                    currency = 'IDR' if 'rp' in match.group().lower() else 'USD'
                    
                    results.append({
                        'value': int(value),
                        'currency': currency,
                        'period': 'monthly',
                        'raw_text': match.group(),
                        'source': 'regex'
                    })
                except:
                    continue
        
        return results
    
    def _extract_with_ner(self, text: str) -> List[Dict]:
        """Extract using NER model"""
        results = []
        
        try:
            entities = self.ner_pipeline(text)
            
            for entity in entities:
                if entity.get('entity_group') in ['MONEY', 'CARDINAL']:
                    word = entity.get('word', '')
                    # Try to parse as number
                    try:
                        value = float(re.sub(r'[^\d.]', '', word))
                        results.append({
                            'value': int(value),
                            'currency': 'USD',  # NER usually finds USD
                            'period': 'unknown',
                            'raw_text': word,
                            'source': 'ner',
                            'confidence': entity.get('score', 0)
                        })
                    except:
                        pass
        except Exception as e:
            logger.warning(f"NER extraction failed: {e}")
        
        return results


class SkillMatcher:
    """
    Semantic skill matching menggunakan Sentence Transformers
    """
    
    def __init__(self):
        self.model = None
        self.skill_embeddings = {}
        self._init_model()
        self._precompute_skill_embeddings()
    
    def _init_model(self):
        """Initialize sentence transformer model"""
        if not MODELS_AVAILABLE:
            return
        
        try:
            # Use multilingual model for Indonesian support
            self.model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
            logger.info("✓ Sentence Transformer loaded: paraphrase-multilingual-MiniLM-L12-v2")
        except Exception as e:
            logger.warning(f"Could not load Sentence Transformer: {e}")
    
    def _precompute_skill_embeddings(self):
        """Pre-compute embeddings for common skills"""
        if not self.model:
            return
        
        skills = {
            # Frontend
            'react': ['React.js', 'ReactJS', 'React Native', 'Frontend React'],
            'vue': ['Vue.js', 'VueJS', 'Nuxt.js', 'Frontend Vue'],
            'angular': ['Angular', 'AngularJS', 'Angular 2+'],
            'nextjs': ['Next.js', 'NextJS', 'React SSR'],
            
            # Backend
            'python': ['Python', 'Python Developer', 'Django', 'Flask', 'FastAPI'],
            'nodejs': ['Node.js', 'NodeJS', 'Express.js', 'Backend JavaScript'],
            'php': ['PHP', 'PHP Developer', 'Laravel', 'CodeIgniter'],
            'golang': ['Go', 'Golang', 'Go Developer'],
            'java': ['Java', 'Java Developer', 'Spring Boot', 'Spring Framework'],
            
            # Mobile
            'flutter': ['Flutter', 'Dart', 'Cross-platform Mobile'],
            'react_native': ['React Native', 'Mobile React', 'Cross-platform'],
            'ios_swift': ['iOS', 'Swift', 'SwiftUI', 'iOS Developer'],
            'android_kotlin': ['Android', 'Kotlin', 'Android Developer'],
            
            # DevOps
            'devops': ['DevOps', 'DevOps Engineer', 'CI/CD', 'Infrastructure'],
            'aws': ['AWS', 'Amazon Web Services', 'Cloud AWS'],
            'docker': ['Docker', 'Kubernetes', 'Container', 'K8s'],
            
            # Data
            'data_science': ['Data Science', 'Data Scientist', 'Machine Learning'],
            'machine_learning': ['Machine Learning', 'ML Engineer', 'Deep Learning', 'AI'],
        }
        
        try:
            for skill_key, variations in skills.items():
                # Combine all variations into one text
                combined = ' '.join(variations)
                self.skill_embeddings[skill_key] = self.model.encode(combined, convert_to_tensor=True)
            
            logger.info(f"✓ Pre-computed embeddings for {len(skills)} skills")
        except Exception as e:
            logger.warning(f"Failed to compute skill embeddings: {e}")
    
    def find_similar_skills(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Find skills similar to query
        Returns: List of {skill, similarity_score}
        """
        if not self.model or not self.skill_embeddings:
            return self._fallback_similarity(query)
        
        try:
            query_embedding = self.model.encode(query, convert_to_tensor=True)
            
            results = []
            for skill, embedding in self.skill_embeddings.items():
                similarity = util.cos_sim(query_embedding, embedding).item()
                results.append({
                    'skill': skill,
                    'similarity': round(similarity, 3),
                    'readable': skill.replace('_', ' ').title()
                })
            
            # Sort by similarity
            results.sort(key=lambda x: x['similarity'], reverse=True)
            return results[:top_k]
        
        except Exception as e:
            logger.warning(f"Similarity search failed: {e}")
            return self._fallback_similarity(query)
    
    def _fallback_similarity(self, query: str) -> List[Dict]:
        """Fallback using simple string matching"""
        query_lower = query.lower()
        skills = ['react', 'vue', 'angular', 'python', 'nodejs', 'flutter', 
                  'devops', 'data_science', 'machine_learning']
        
        results = []
        for skill in skills:
            if skill in query_lower or query_lower in skill:
                results.append({
                    'skill': skill,
                    'similarity': 0.8,
                    'readable': skill.replace('_', ' ').title()
                })
        
        return results[:5]
    
    def match_job_to_skills(self, job_description: str) -> List[Dict]:
        """
        Extract skills from job description
        """
        if not self.model:
            return self._extract_skills_regex(job_description)
        
        # Split into sentences/phrases
        sentences = re.split(r'[.,:;\n]', job_description)
        
        all_matches = []
        for sentence in sentences:
            if len(sentence.strip()) > 10:
                matches = self.find_similar_skills(sentence, top_k=2)
                for m in matches:
                    if m['similarity'] > 0.5:
                        all_matches.append(m)
        
        # Deduplicate and sort
        seen = set()
        unique = []
        for m in sorted(all_matches, key=lambda x: x['similarity'], reverse=True):
            if m['skill'] not in seen:
                seen.add(m['skill'])
                unique.append(m)
        
        return unique[:10]
    
    def _extract_skills_regex(self, text: str) -> List[Dict]:
        """Fallback skill extraction with regex"""
        skill_patterns = {
            'react': r'\breact(?:\.?js|native)?\b',
            'vue': r'\bvue(?:\.?js)?\b',
            'angular': r'\bangular\b',
            'python': r'\bpython\b',
            'nodejs': r'\bnode(?:\.?js)?\b',
            'flutter': r'\bflutter\b',
            'golang': r'\b(?:go|golang)\b',
            'java': r'\bjava\b(?!script)',
            'php': r'\bphp\b',
            'devops': r'\bdevops\b',
            'aws': r'\baws\b',
            'docker': r'\bdocker\b',
            'kubernetes': r'\bkubernetes|k8s\b',
        }
        
        results = []
        text_lower = text.lower()
        
        for skill, pattern in skill_patterns.items():
            if re.search(pattern, text_lower, re.IGNORECASE):
                results.append({
                    'skill': skill,
                    'similarity': 1.0,
                    'readable': skill.replace('_', ' ').title()
                })
        
        return results


class SalaryPredictor:
    """
    Prediksi gaji berdasarkan skill, experience, dan lokasi
    Menggunakan simple ML model dengan embeddings
    """
    
    def __init__(self):
        self.model = None
        self.skill_matcher = None
        self._init_model()
        
        # Base salary data untuk training (IDR/month)
        self.salary_baselines = {
            'frontend': {'junior': 5000000, 'mid': 10000000, 'senior': 20000000, 'lead': 35000000},
            'backend': {'junior': 6000000, 'mid': 12000000, 'senior': 24000000, 'lead': 42000000},
            'fullstack': {'junior': 6500000, 'mid': 13000000, 'senior': 26000000, 'lead': 45000000},
            'mobile': {'junior': 5500000, 'mid': 11000000, 'senior': 22000000, 'lead': 38000000},
            'devops': {'junior': 7500000, 'mid': 15000000, 'senior': 30000000, 'lead': 52000000},
            'data': {'junior': 8000000, 'mid': 17000000, 'senior': 35000000, 'lead': 60000000},
        }
        
        # City multipliers
        self.city_multipliers = {
            'Jakarta': 1.35,
            'Bandung': 0.95,
            'Surabaya': 0.88,
            'Makassar': 0.75,
            'Yogyakarta': 0.70,
            'Remote (Indonesia)': 1.20,
            'Remote (Global)': 2.5,
        }
    
    def _init_model(self):
        """Initialize embedding model for prediction"""
        if not MODELS_AVAILABLE:
            return
        
        try:
            self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
            self.skill_matcher = SkillMatcher()
            logger.info("✓ Salary Predictor initialized")
        except Exception as e:
            logger.warning(f"Salary Predictor init failed: {e}")
    
    def predict_salary(self, 
                       job_description: str = None,
                       skills: List[str] = None,
                       experience: str = 'mid',
                       city: str = 'Makassar') -> Dict:
        """
        Predict salary based on job description or skills
        """
        # Determine skill category
        if skills:
            category = self._determine_category(skills)
        elif job_description and self.skill_matcher:
            matched_skills = self.skill_matcher.match_job_to_skills(job_description)
            skills = [m['skill'] for m in matched_skills]
            category = self._determine_category(skills)
        else:
            category = 'fullstack'  # Default
        
        # Get base salary
        base = self.salary_baselines.get(category, self.salary_baselines['fullstack'])
        base_salary = base.get(experience.lower(), base['mid'])
        
        # Apply city multiplier
        multiplier = self.city_multipliers.get(city, 1.0)
        predicted = int(base_salary * multiplier)
        
        # Calculate range (±15%)
        min_salary = int(predicted * 0.85)
        max_salary = int(predicted * 1.15)
        
        # Calculate confidence based on matched skills
        confidence = min(0.9, 0.5 + len(skills or []) * 0.1)
        
        return {
            'predicted_salary': predicted,
            'min_salary': min_salary,
            'max_salary': max_salary,
            'predicted_formatted': f"Rp {predicted:,}",
            'range_formatted': f"Rp {min_salary:,} - Rp {max_salary:,}",
            'category': category,
            'skills_detected': skills or [],
            'experience': experience,
            'city': city,
            'city_multiplier': multiplier,
            'confidence': round(confidence, 2),
            'model': 'SentenceTransformer + Baseline'
        }
    
    def _determine_category(self, skills: List[str]) -> str:
        """Determine job category from skills"""
        skill_set = set(s.lower() for s in skills)
        
        frontend_skills = {'react', 'vue', 'angular', 'nextjs', 'html', 'css'}
        backend_skills = {'python', 'nodejs', 'php', 'golang', 'java', 'laravel'}
        mobile_skills = {'flutter', 'react_native', 'ios_swift', 'android_kotlin', 'swift', 'kotlin'}
        devops_skills = {'devops', 'aws', 'docker', 'kubernetes', 'terraform', 'ci/cd'}
        data_skills = {'data_science', 'machine_learning', 'tensorflow', 'pytorch', 'pandas'}
        
        # Count matches
        scores = {
            'frontend': len(skill_set & frontend_skills),
            'backend': len(skill_set & backend_skills),
            'mobile': len(skill_set & mobile_skills),
            'devops': len(skill_set & devops_skills),
            'data': len(skill_set & data_skills),
        }
        
        # Check for fullstack
        if scores['frontend'] > 0 and scores['backend'] > 0:
            return 'fullstack'
        
        # Return highest scoring category
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        
        return 'fullstack'


# Convenience functions
def extract_salaries(text: str) -> List[Dict]:
    """Quick function to extract salaries from text"""
    extractor = SalaryExtractor()
    return extractor.extract_salary_from_text(text)


def find_similar_skills(query: str) -> List[Dict]:
    """Quick function to find similar skills"""
    matcher = SkillMatcher()
    return matcher.find_similar_skills(query)


def predict_salary(job_description: str = None, skills: List[str] = None,
                   experience: str = 'mid', city: str = 'Makassar') -> Dict:
    """Quick function to predict salary"""
    predictor = SalaryPredictor()
    return predictor.predict_salary(job_description, skills, experience, city)


# Test
if __name__ == "__main__":
    print("\n=== Testing NLP Models ===\n")
    
    # Test salary extraction
    print("1. Salary Extraction:")
    test_text = "Gaji untuk posisi ini Rp 15 juta per bulan. Senior developer bisa dapat sampai Rp 30-50 juta."
    salaries = extract_salaries(test_text)
    for s in salaries:
        print(f"   - {s}")
    
    # Test skill matching
    print("\n2. Skill Matching:")
    similar = find_similar_skills("React frontend developer dengan TypeScript")
    for s in similar:
        print(f"   - {s['readable']}: {s['similarity']:.2f}")
    
    # Test salary prediction
    print("\n3. Salary Prediction:")
    prediction = predict_salary(
        skills=['react', 'nodejs', 'mongodb'],
        experience='senior',
        city='Makassar'
    )
    print(f"   Category: {prediction['category']}")
    print(f"   Predicted: {prediction['predicted_formatted']}")
    print(f"   Range: {prediction['range_formatted']}")
    print(f"   Confidence: {prediction['confidence']:.0%}")
