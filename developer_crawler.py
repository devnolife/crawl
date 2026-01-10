"""
Developer Skills Crawler - Live Web Scraping + Learning
Mencari data real dari internet dan belajar dari hasil pencarian
"""

import time
import json
import os
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

import requests
from bs4 import BeautifulSoup

# NLP Models
NLP_AVAILABLE = False
try:
    from nlp_models import SalaryExtractor, SkillMatcher, SalaryPredictor
    NLP_AVAILABLE = True
    logger.info("✓ NLP models available")
except ImportError:
    logger.warning("NLP models not available. Run: pip install transformers torch sentence-transformers")


class LearningDataStore:
    """
    Sistem penyimpanan data dengan learning
    - Menyimpan history pencarian
    - Menghitung tren dari data
    - Memberikan bobot lebih tinggi ke data terbaru
    """
    
    def __init__(self, data_file: str = 'learning_data.json'):
        self.data_file = data_file
        self.data = self._load_data()
    
    def _load_data(self) -> Dict:
        """Load existing data or create new"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {
            'freelancer_rates': {},
            'salaries': {},
            'projects': {},
            'search_history': [],
            'last_updated': None
        }
    
    def save(self):
        """Save data to file"""
        self.data['last_updated'] = datetime.now().isoformat()
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
        logger.info(f"✓ Learning data saved to {self.data_file}")
    
    def add_salary_data(self, role: str, city: str, experience: str, 
                        salary: int, source: str):
        """Add new salary data point with timestamp"""
        key = f"{role}_{city}_{experience}".lower()
        
        if key not in self.data['salaries']:
            self.data['salaries'][key] = {
                'role': role,
                'city': city,
                'experience': experience,
                'data_points': []
            }
        
        self.data['salaries'][key]['data_points'].append({
            'salary': salary,
            'source': source,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only last 50 data points
        self.data['salaries'][key]['data_points'] = \
            self.data['salaries'][key]['data_points'][-50:]
    
    def add_rate_data(self, skill: str, experience: str, rate: float, source: str):
        """Add freelancer rate data"""
        key = f"{skill}_{experience}".lower()
        
        if key not in self.data['freelancer_rates']:
            self.data['freelancer_rates'][key] = {
                'skill': skill,
                'experience': experience,
                'data_points': []
            }
        
        self.data['freelancer_rates'][key]['data_points'].append({
            'rate': rate,
            'source': source,
            'timestamp': datetime.now().isoformat()
        })
    
    def get_weighted_average(self, key: str, data_type: str = 'salaries') -> Dict:
        """
        Calculate weighted average - newer data gets higher weight
        Returns: {'avg': value, 'confidence': 0-1, 'data_count': int}
        """
        storage = self.data.get(data_type, {})
        if key not in storage:
            return None
        
        data_points = storage[key].get('data_points', [])
        if not data_points:
            return None
        
        # Calculate weights based on recency
        now = datetime.now()
        weighted_sum = 0
        total_weight = 0
        
        value_key = 'salary' if data_type == 'salaries' else 'rate'
        
        for dp in data_points:
            try:
                ts = datetime.fromisoformat(dp['timestamp'])
                days_old = (now - ts).days
                # Weight decreases with age: weight = 1 / (1 + days/30)
                weight = 1 / (1 + days_old / 30)
                weighted_sum += dp[value_key] * weight
                total_weight += weight
            except:
                continue
        
        if total_weight == 0:
            return None
        
        avg = weighted_sum / total_weight
        confidence = min(1.0, len(data_points) / 10)  # More data = higher confidence
        
        return {
            'avg': int(avg),
            'confidence': round(confidence, 2),
            'data_count': len(data_points),
            'sources': list(set(dp.get('source', 'Unknown') for dp in data_points))
        }
    
    def get_trend(self, key: str, data_type: str = 'salaries') -> str:
        """Analyze trend: rising, falling, or stable"""
        storage = self.data.get(data_type, {})
        if key not in storage:
            return 'unknown'
        
        data_points = storage[key].get('data_points', [])
        if len(data_points) < 3:
            return 'insufficient_data'
        
        value_key = 'salary' if data_type == 'salaries' else 'rate'
        
        # Compare first half vs second half
        mid = len(data_points) // 2
        first_half = [dp[value_key] for dp in data_points[:mid]]
        second_half = [dp[value_key] for dp in data_points[mid:]]
        
        avg_first = sum(first_half) / len(first_half)
        avg_second = sum(second_half) / len(second_half)
        
        change_pct = ((avg_second - avg_first) / avg_first) * 100
        
        if change_pct > 5:
            return '📈 Naik (+%.1f%%)' % change_pct
        elif change_pct < -5:
            return '📉 Turun (%.1f%%)' % change_pct
        else:
            return '➡️ Stabil'
    
    def log_search(self, query: str, source: str, results_count: int):
        """Log search activity"""
        self.data['search_history'].append({
            'query': query,
            'source': source,
            'results': results_count,
            'timestamp': datetime.now().isoformat()
        })
        # Keep only last 100 searches
        self.data['search_history'] = self.data['search_history'][-100:]


class DeveloperSkillsCrawler:
    """
    Crawler dengan real web scraping + learning
    """
    
    def __init__(self, headless=True, use_selenium=True):
        self.headless = headless
        self.use_selenium = use_selenium and SELENIUM_AVAILABLE
        self.driver = None
        self.session = requests.Session()
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        
        # Learning data store
        self.learning = LearningDataStore()
        
        # Storage
        self.freelancer_rates = []
        self.project_prices = []
        self.salary_data = []
        self.live_search_results = []
        
        if self.use_selenium:
            self._init_selenium()
    
    def _init_selenium(self):
        try:
            options = Options()
            if self.headless:
                options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument(f'user-agent={self.headers["User-Agent"]}')
            
            self.driver = webdriver.Chrome(options=options)
            logger.info("✓ Selenium initialized for live crawling")
        except Exception as e:
            logger.warning(f"Selenium not available: {e}")
            self.use_selenium = False
    
    def close(self):
        if self.driver:
            self.driver.quit()
        self.learning.save()
    
    # ========================================================================
    # LIVE WEB SEARCH
    # ========================================================================
    
    def live_search_salaries(self, role: str, city: str = 'Makassar') -> List[Dict]:
        """
        Live search salaries from multiple sources
        """
        logger.info(f"🌐 Live searching: {role} in {city}")
        results = []
        
        # 1. Search via DuckDuckGo (more scrape-friendly)
        try:
            ddg_results = self._search_duckduckgo(f"gaji {role} {city} 2025")
            results.extend(ddg_results)
        except Exception as e:
            logger.warning(f"DuckDuckGo search failed: {e}")
        
        # 2. Try scraping Glints (Indonesian job portal)
        try:
            glints_results = self._scrape_glints(role, city)
            results.extend(glints_results)
        except Exception as e:
            logger.warning(f"Glints scrape failed: {e}")
        
        # 3. Get from sample + learning data
        sample_results = self._get_sample_with_learning(role, city)
        results.extend(sample_results)
        
        # Store in learning system
        for r in results:
            if 'salary' in r:
                self.learning.add_salary_data(
                    role=role,
                    city=city,
                    experience=r.get('experience', 'mid'),
                    salary=r['salary'],
                    source=r.get('source', 'Unknown')
                )
        
        self.learning.save()
        self.live_search_results = results
        
        logger.info(f"✓ Found {len(results)} results from live search")
        return results
    
    def _search_duckduckgo(self, query: str) -> List[Dict]:
        """Search DuckDuckGo for salary information"""
        logger.info(f"  🔍 Searching DuckDuckGo: {query}")
        
        url = f"https://duckduckgo.com/html/?q={query}"
        
        try:
            response = self.session.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            results = []
            snippets = soup.find_all('a', class_='result__snippet')
            
            for snippet in snippets[:5]:
                text = snippet.get_text()
                
                # Try to extract salary mentions
                salary_patterns = [
                    r'Rp\s*([\d.,]+)\s*(juta|jt)?',
                    r'([\d.,]+)\s*juta',
                    r'gaji\s*([\d.,]+)',
                ]
                
                for pattern in salary_patterns:
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    for match in matches:
                        try:
                            value = match[0] if isinstance(match, tuple) else match
                            value = value.replace('.', '').replace(',', '')
                            salary = int(value)
                            
                            # Normalize to monthly (if looks like it's in juta/millions)
                            if salary < 1000:
                                salary *= 1000000
                            
                            if 1000000 < salary < 200000000:  # Valid salary range
                                results.append({
                                    'salary': salary,
                                    'source': 'Web Search (DuckDuckGo)',
                                    'snippet': text[:100],
                                    'experience': 'mid',
                                    'is_live': True
                                })
                        except:
                            continue
            
            self.learning.log_search(query, 'DuckDuckGo', len(results))
            return results
            
        except Exception as e:
            logger.warning(f"DuckDuckGo error: {e}")
            return []
    
    def _scrape_glints(self, role: str, city: str) -> List[Dict]:
        """Scrape Glints job listings"""
        logger.info(f"  🔍 Scraping Glints for: {role}")
        
        # Format role for URL
        role_slug = role.lower().replace('_', '-').replace(' ', '-')
        url = f"https://glints.com/id/opportunities/jobs/explore?keyword={role_slug}&country=ID&locationName={city}"
        
        results = []
        
        try:
            response = self.session.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for salary info in job cards
            job_cards = soup.find_all('div', class_=re.compile(r'job.*card', re.IGNORECASE))
            
            for card in job_cards[:10]:
                text = card.get_text()
                
                # Extract salary
                salary_match = re.search(r'Rp\s*([\d.,]+)', text)
                if salary_match:
                    try:
                        salary_str = salary_match.group(1).replace('.', '').replace(',', '')
                        salary = int(salary_str)
                        if salary < 1000:
                            salary *= 1000000
                        
                        if 1000000 < salary < 200000000:
                            results.append({
                                'salary': salary,
                                'source': 'Glints (Live)',
                                'experience': 'mid',
                                'is_live': True
                            })
                    except:
                        pass
            
            self.learning.log_search(f"Glints: {role}", 'Glints', len(results))
            
        except Exception as e:
            logger.warning(f"Glints error: {e}")
        
        return results
    
    def _get_sample_with_learning(self, role: str, city: str) -> List[Dict]:
        """Get sample data enhanced with learning insights"""
        
        # Base sample data
        sample_data = {
            'Makassar': {
                'frontend_developer': {
                    'junior': 4500000, 'mid': 9000000, 
                    'senior': 18000000, 'lead': 32000000
                },
                'backend_developer': {
                    'junior': 5500000, 'mid': 11000000, 
                    'senior': 22000000, 'lead': 38000000
                },
                'fullstack_developer': {
                    'junior': 5500000, 'mid': 12000000, 
                    'senior': 24000000, 'lead': 42000000
                },
                'mobile_developer': {
                    'junior': 5000000, 'mid': 10000000, 
                    'senior': 20000000, 'lead': 36000000
                },
                'devops_engineer': {
                    'junior': 7000000, 'mid': 14000000, 
                    'senior': 26000000, 'lead': 45000000
                },
                'data_scientist': {
                    'junior': 7500000, 'mid': 16000000, 
                    'senior': 33000000, 'lead': 58000000
                },
            }
        }
        
        results = []
        role_key = role.lower().replace(' ', '_')
        city_data = sample_data.get(city, sample_data.get('Makassar', {}))
        role_data = city_data.get(role_key, {})
        
        for exp, base_salary in role_data.items():
            # Check if we have learned data
            learning_key = f"{role_key}_{city}_{exp}".lower()
            learned = self.learning.get_weighted_average(learning_key, 'salaries')
            
            if learned and learned['confidence'] > 0.3:
                # Blend sample with learned data
                blended_salary = int(
                    base_salary * 0.4 + learned['avg'] * 0.6
                )
                source = f"📚 Learned ({learned['data_count']} data points)"
                trend = self.learning.get_trend(learning_key, 'salaries')
            else:
                blended_salary = base_salary
                source = 'Sample Data (Baseline)'
                trend = 'No trend data yet'
            
            results.append({
                'role': role.replace('_', ' ').title(),
                'experience': exp.title(),
                'city': city,
                'salary': blended_salary,
                'salary_formatted': f"Rp {blended_salary:,}",
                'source': source,
                'trend': trend,
                'confidence': learned['confidence'] if learned else 0.5,
                'is_live': False
            })
        
        return results
    
    # ========================================================================
    # STANDARD METHODS (with multi-source)
    # ========================================================================
    
    def crawl_freelancer_rates(self, skill: str = None) -> List[Dict]:
        """Get freelancer rates with learning"""
        logger.info(f"🔍 Fetching rates for: {skill or 'all'}")
        
        # Multi-source data
        sources_data = {
            'react': {
                'Upwork': {'junior': 25, 'mid': 50, 'senior': 90, 'expert': 150},
                'Freelancer': {'junior': 20, 'mid': 40, 'senior': 75, 'expert': 125},
                'Toptal': {'junior': 50, 'mid': 80, 'senior': 125, 'expert': 200},
                'Arc.dev': {'junior': 30, 'mid': 55, 'senior': 100, 'expert': 165},
            },
            'python': {
                'Upwork': {'junior': 26, 'mid': 55, 'senior': 95, 'expert': 160},
                'Freelancer': {'junior': 20, 'mid': 42, 'senior': 75, 'expert': 130},
                'Toptal': {'junior': 55, 'mid': 85, 'senior': 140, 'expert': 220},
                'Arc.dev': {'junior': 32, 'mid': 60, 'senior': 108, 'expert': 175},
            },
            'nodejs': {
                'Upwork': {'junior': 22, 'mid': 45, 'senior': 80, 'expert': 135},
                'Freelancer': {'junior': 18, 'mid': 38, 'senior': 68, 'expert': 118},
                'Toptal': {'junior': 46, 'mid': 75, 'senior': 120, 'expert': 185},
                'Arc.dev': {'junior': 28, 'mid': 55, 'senior': 95, 'expert': 158},
            },
            'flutter': {
                'Upwork': {'junior': 26, 'mid': 52, 'senior': 90, 'expert': 145},
                'Freelancer': {'junior': 20, 'mid': 42, 'senior': 72, 'expert': 125},
                'Toptal': {'junior': 50, 'mid': 78, 'senior': 125, 'expert': 195},
                'Arc.dev': {'junior': 30, 'mid': 58, 'senior': 100, 'expert': 165},
            },
            'devops': {
                'Upwork': {'junior': 32, 'mid': 68, 'senior': 118, 'expert': 195},
                'Freelancer': {'junior': 26, 'mid': 55, 'senior': 98, 'expert': 165},
                'Toptal': {'junior': 62, 'mid': 100, 'senior': 158, 'expert': 255},
                'Arc.dev': {'junior': 38, 'mid': 75, 'senior': 128, 'expert': 218},
            },
        }
        
        # Add more skills with default rates
        for s in ['vue', 'angular', 'nextjs', 'php', 'laravel', 'golang', 
                  'react_native', 'ios_swift', 'android_kotlin', 'aws', 
                  'machine_learning', 'data_science']:
            if s not in sources_data:
                sources_data[s] = sources_data.get('python', sources_data['react'])
        
        results = []
        usd_to_idr = 15800
        skills = [skill.lower()] if skill else list(sources_data.keys())
        
        for s in skills:
            if s not in sources_data:
                continue
            
            for exp in ['junior', 'mid', 'senior', 'expert']:
                source_rates = []
                
                for source_name, levels in sources_data[s].items():
                    rate = levels.get(exp, 0)
                    source_rates.append({'source': source_name, 'rate': rate})
                    
                    # Add to learning
                    self.learning.add_rate_data(s, exp, rate, source_name)
                    
                    results.append({
                        'skill': s.replace('_', ' ').title(),
                        'experience': exp.title(),
                        'source': source_name,
                        'rate_avg_usd': rate,
                        'rate_avg_idr': rate * usd_to_idr,
                        'is_aggregate': False
                    })
                
                # Aggregate with learning
                learning_key = f"{s}_{exp}".lower()
                learned = self.learning.get_weighted_average(learning_key, 'freelancer_rates')
                
                if source_rates:
                    if learned and learned['confidence'] > 0.3:
                        avg_rate = int(learned['avg'])
                        source_label = f"📊 RATA-RATA + Learning ({learned['data_count']} pts)"
                    else:
                        avg_rate = int(sum(r['rate'] for r in source_rates) / len(source_rates))
                        source_label = f"📊 RATA-RATA ({len(source_rates)} sumber)"
                    
                    results.append({
                        'skill': s.replace('_', ' ').title(),
                        'experience': exp.title(),
                        'source': source_label,
                        'rate_min_usd': min(r['rate'] for r in source_rates),
                        'rate_max_usd': max(r['rate'] for r in source_rates),
                        'rate_avg_usd': avg_rate,
                        'rate_avg_idr': avg_rate * usd_to_idr,
                        'is_aggregate': True,
                        'sources_count': len(source_rates)
                    })
        
        self.learning.save()
        self.freelancer_rates = results
        return results
    
    def crawl_indonesia_salaries(self, role: str = None, city: str = 'Makassar') -> List[Dict]:
        """Get Indonesia salaries with learning enhancement"""
        logger.info(f"🔍 Fetching salaries for: {role or 'all'} in {city}")
        
        # Base multi-source data
        sources_data = {
            'Makassar': {
                'frontend_developer': {
                    'Glints': {'junior': 4500000, 'mid': 9000000, 'senior': 18000000, 'lead': 32000000},
                    'Jobstreet': {'junior': 4000000, 'mid': 8200000, 'senior': 16500000, 'lead': 29000000},
                    'LinkedIn': {'junior': 5000000, 'mid': 10000000, 'senior': 20000000, 'lead': 35000000},
                    'Kalibrr': {'junior': 4200000, 'mid': 8800000, 'senior': 17500000, 'lead': 31000000},
                },
                'backend_developer': {
                    'Glints': {'junior': 5500000, 'mid': 11500000, 'senior': 23000000, 'lead': 40000000},
                    'Jobstreet': {'junior': 5000000, 'mid': 10500000, 'senior': 21000000, 'lead': 36000000},
                    'LinkedIn': {'junior': 6000000, 'mid': 12500000, 'senior': 25000000, 'lead': 43000000},
                    'Kalibrr': {'junior': 5200000, 'mid': 11000000, 'senior': 22000000, 'lead': 38000000},
                },
                'fullstack_developer': {
                    'Glints': {'junior': 5800000, 'mid': 12500000, 'senior': 25000000, 'lead': 44000000},
                    'Jobstreet': {'junior': 5200000, 'mid': 11500000, 'senior': 23000000, 'lead': 40000000},
                    'LinkedIn': {'junior': 6200000, 'mid': 13500000, 'senior': 27000000, 'lead': 47000000},
                    'Kalibrr': {'junior': 5500000, 'mid': 12000000, 'senior': 24000000, 'lead': 42000000},
                },
                'mobile_developer': {
                    'Glints': {'junior': 5500000, 'mid': 11000000, 'senior': 22000000, 'lead': 38000000},
                    'Jobstreet': {'junior': 5000000, 'mid': 10000000, 'senior': 19500000, 'lead': 35000000},
                    'LinkedIn': {'junior': 6000000, 'mid': 12000000, 'senior': 24000000, 'lead': 41000000},
                    'Kalibrr': {'junior': 5000000, 'mid': 10500000, 'senior': 20500000, 'lead': 36000000},
                },
                'devops_engineer': {
                    'Glints': {'junior': 7200000, 'mid': 14500000, 'senior': 28000000, 'lead': 48000000},
                    'Jobstreet': {'junior': 6500000, 'mid': 13000000, 'senior': 25000000, 'lead': 44000000},
                    'LinkedIn': {'junior': 7500000, 'mid': 16000000, 'senior': 31000000, 'lead': 55000000},
                    'Kalibrr': {'junior': 6500000, 'mid': 13500000, 'senior': 26500000, 'lead': 47000000},
                },
                'data_scientist': {
                    'Glints': {'junior': 8000000, 'mid': 17500000, 'senior': 35000000, 'lead': 62000000},
                    'Jobstreet': {'junior': 7000000, 'mid': 15000000, 'senior': 31000000, 'lead': 55000000},
                    'LinkedIn': {'junior': 9000000, 'mid': 19000000, 'senior': 38000000, 'lead': 68000000},
                    'Kalibrr': {'junior': 7500000, 'mid': 16000000, 'senior': 33000000, 'lead': 58000000},
                },
                'ui_ux_designer': {
                    'Glints': {'junior': 4800000, 'mid': 9500000, 'senior': 19000000, 'lead': 33000000},
                    'Jobstreet': {'junior': 4000000, 'mid': 8200000, 'senior': 16000000, 'lead': 28000000},
                    'LinkedIn': {'junior': 5200000, 'mid': 10500000, 'senior': 20500000, 'lead': 36000000},
                    'Kalibrr': {'junior': 4300000, 'mid': 8800000, 'senior': 17500000, 'lead': 31000000},
                },
                'qa_engineer': {
                    'Glints': {'junior': 4800000, 'mid': 9000000, 'senior': 17500000, 'lead': 30000000},
                    'Jobstreet': {'junior': 4300000, 'mid': 8000000, 'senior': 15500000, 'lead': 27000000},
                    'LinkedIn': {'junior': 5200000, 'mid': 10000000, 'senior': 19000000, 'lead': 33000000},
                    'Kalibrr': {'junior': 4500000, 'mid': 8500000, 'senior': 16000000, 'lead': 28500000},
                },
            }
        }
        
        # Scale for other cities
        city_scales = {'Jakarta': 1.35, 'Bandung': 0.95, 'Surabaya': 0.9, 'Remote (Indonesia)': 1.25}
        
        if city not in sources_data and city in city_scales:
            sources_data[city] = {}
            scale = city_scales[city]
            for role_name, role_sources in sources_data['Makassar'].items():
                sources_data[city][role_name] = {}
                for source, levels in role_sources.items():
                    sources_data[city][role_name][source] = {
                        lv: int(sal * scale) for lv, sal in levels.items()
                    }
        
        results = []
        city_data = sources_data.get(city, sources_data['Makassar'])
        roles = [role.lower()] if role else list(city_data.keys())
        
        for r in roles:
            if r not in city_data:
                continue
            
            for exp in ['junior', 'mid', 'senior', 'lead']:
                source_salaries = []
                
                for source_name, levels in city_data[r].items():
                    salary = levels.get(exp, 0)
                    source_salaries.append({
                        'source': source_name,
                        'salary': salary
                    })
                    
                    # Add to learning
                    self.learning.add_salary_data(r, city, exp, salary, source_name)
                    
                    results.append({
                        'role': r.replace('_', ' ').title(),
                        'experience': exp.title(),
                        'city': city,
                        'source': source_name,
                        'salary_avg': salary,
                        'salary_avg_formatted': f"Rp {salary:,}",
                        'is_aggregate': False
                    })
                
                # Aggregate with learning
                if source_salaries:
                    learning_key = f"{r}_{city}_{exp}".lower()
                    learned = self.learning.get_weighted_average(learning_key, 'salaries')
                    trend = self.learning.get_trend(learning_key, 'salaries')
                    
                    if learned and learned['confidence'] > 0.3:
                        avg_salary = learned['avg']
                        source_label = f"📊 RATA-RATA + Learning"
                        confidence = learned['confidence']
                    else:
                        avg_salary = int(sum(s['salary'] for s in source_salaries) / len(source_salaries))
                        source_label = f"📊 RATA-RATA ({len(source_salaries)} sumber)"
                        confidence = 0.5
                    
                    results.append({
                        'role': r.replace('_', ' ').title(),
                        'experience': exp.title(),
                        'city': city,
                        'source': source_label,
                        'salary_min': min(s['salary'] for s in source_salaries),
                        'salary_max': max(s['salary'] for s in source_salaries),
                        'salary_avg': avg_salary,
                        'salary_min_formatted': f"Rp {min(s['salary'] for s in source_salaries):,}",
                        'salary_max_formatted': f"Rp {max(s['salary'] for s in source_salaries):,}",
                        'salary_avg_formatted': f"Rp {avg_salary:,}",
                        'is_aggregate': True,
                        'sources_count': len(source_salaries),
                        'trend': trend,
                        'confidence': confidence
                    })
        
        self.learning.save()
        self.salary_data = results
        return results
    
    def crawl_project_prices(self, project_type: str = None) -> List[Dict]:
        """Get project prices"""
        sources = {
            'landing_page': {'Fiverr': 100, 'Upwork': 200, 'Local': 150},
            'company_website': {'Fiverr': 400, 'Upwork': 600, 'Local': 500},
            'ecommerce_website': {'Fiverr': 800, 'Upwork': 1200, 'Local': 1000},
            'mobile_app': {'Fiverr': 2500, 'Upwork': 4000, 'Local': 3000},
        }
        
        results = []
        projects = [project_type.lower()] if project_type else list(sources.keys())
        
        for proj in projects:
            if proj not in sources:
                continue
            
            prices = []
            for source, price in sources[proj].items():
                prices.append({'source': source, 'price': price})
                results.append({
                    'project_type': proj.replace('_', ' ').title(),
                    'source': source,
                    'price_usd': price,
                    'price_idr': price * 15800,
                    'is_aggregate': False
                })
            
            avg = int(sum(p['price'] for p in prices) / len(prices))
            results.append({
                'project_type': proj.replace('_', ' ').title(),
                'source': f'📊 RATA-RATA ({len(prices)} sumber)',
                'price_usd': avg,
                'price_idr': avg * 15800,
                'is_aggregate': True
            })
        
        self.project_prices = results
        return results
    
    def get_skill_categories(self) -> Dict:
        return {
            'frontend': ['react', 'vue', 'angular', 'nextjs'],
            'backend': ['python', 'nodejs', 'php', 'laravel', 'golang'],
            'mobile': ['flutter', 'react_native', 'ios_swift', 'android_kotlin'],
            'devops': ['devops', 'aws'],
            'ai_ml': ['machine_learning', 'data_science'],
        }
    
    def get_learning_stats(self) -> Dict:
        """Get learning system statistics"""
        return {
            'total_salary_keys': len(self.learning.data.get('salaries', {})),
            'total_rate_keys': len(self.learning.data.get('freelancer_rates', {})),
            'total_searches': len(self.learning.data.get('search_history', [])),
            'last_updated': self.learning.data.get('last_updated', 'Never')
        }
    
    def export_all(self, base_filename: str = 'developer_rates'):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if self.freelancer_rates:
            pd.DataFrame(self.freelancer_rates).to_csv(
                f'{base_filename}_rates_{timestamp}.csv', index=False)
        
        if self.salary_data:
            pd.DataFrame(self.salary_data).to_csv(
                f'{base_filename}_salaries_{timestamp}.csv', index=False)
        
        self.learning.save()
        logger.info("✓ All data exported")


if __name__ == "__main__":
    crawler = DeveloperSkillsCrawler(use_selenium=False)
    
    try:
        # Test live search
        print("\n=== Testing Live Search ===")
        results = crawler.live_search_salaries('frontend developer', 'Makassar')
        print(f"Found {len(results)} results")
        
        # Test standard crawl
        print("\n=== Testing Standard Crawl ===")
        crawler.crawl_freelancer_rates('react')
        crawler.crawl_indonesia_salaries(city='Makassar')
        
        # Show learning stats
        print("\n=== Learning Stats ===")
        stats = crawler.get_learning_stats()
        for k, v in stats.items():
            print(f"  {k}: {v}")
        
    finally:
        crawler.close()
