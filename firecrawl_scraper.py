"""
🔥 Firecrawl Integration for SkillPulse AI
Scrape job portals and convert to LLM-ready data
"""

import os
import re
import logging
from typing import List, Dict, Optional
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check if Firecrawl is available
FIRECRAWL_AVAILABLE = False
try:
    from firecrawl import FirecrawlApp
    FIRECRAWL_AVAILABLE = True
    logger.info("✓ Firecrawl SDK available")
except ImportError:
    logger.warning("Firecrawl not installed. Run: pip install firecrawl-py")

# Load API key from environment
from dotenv import load_dotenv
load_dotenv()

FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY", "")


class FirecrawlScraper:
    """
    Advanced web scraper using Firecrawl API
    Features:
    - Bypass anti-bot protection
    - Get clean markdown output
    - JavaScript rendering
    - Structured data extraction
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or FIRECRAWL_API_KEY
        self.app = None
        self._init_client()
    
    def _init_client(self):
        """Initialize Firecrawl client"""
        if not FIRECRAWL_AVAILABLE:
            logger.warning("Firecrawl SDK not available")
            return
        
        if not self.api_key or self.api_key.startswith("fc-YOUR"):
            logger.warning("Firecrawl API key not configured")
            return
        
        try:
            self.app = FirecrawlApp(api_key=self.api_key)
            logger.info("✓ Firecrawl client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Firecrawl: {e}")
    
    def is_available(self) -> bool:
        """Check if Firecrawl is ready to use"""
        return self.app is not None
    
    def scrape_url(self, url: str, formats: List[str] = None) -> Dict:
        """
        Scrape a single URL and get clean content
        
        Args:
            url: URL to scrape
            formats: Output formats ['markdown', 'html', 'links', 'screenshot']
        
        Returns:
            Dict with scraped content
        """
        if not self.is_available():
            return {'error': 'Firecrawl not available', 'url': url}
        
        formats = formats or ['markdown']
        
        try:
            logger.info(f"🔥 Scraping: {url}")
            result = self.app.scrape_url(url, params={'formats': formats})
            
            return {
                'url': url,
                'success': True,
                'markdown': result.get('markdown', ''),
                'html': result.get('html', ''),
                'metadata': result.get('metadata', {}),
                'scraped_at': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Scrape failed: {e}")
            return {'error': str(e), 'url': url, 'success': False}
    
    def scrape_glints_jobs(self, keyword: str, location: str = 'Makassar') -> List[Dict]:
        """
        Scrape job listings from Glints
        """
        if not self.is_available():
            logger.warning("Firecrawl not available, using fallback")
            return self._fallback_glints_data(keyword, location)
        
        # Build Glints search URL
        keyword_slug = keyword.lower().replace(' ', '-').replace('_', '-')
        url = f"https://glints.com/id/opportunities/jobs/explore?keyword={keyword_slug}&country=ID&locationName={location}"
        
        result = self.scrape_url(url)
        
        if not result.get('success'):
            return self._fallback_glints_data(keyword, location)
        
        # Parse jobs from markdown
        jobs = self._parse_jobs_from_markdown(result.get('markdown', ''), 'Glints')
        
        # Extract salaries using NLP
        for job in jobs:
            job['keyword'] = keyword
            job['location'] = location
            job['source'] = 'Glints (Firecrawl)'
        
        logger.info(f"✓ Found {len(jobs)} jobs from Glints")
        return jobs
    
    def scrape_jobstreet_jobs(self, keyword: str, location: str = 'Makassar') -> List[Dict]:
        """
        Scrape job listings from Jobstreet
        """
        if not self.is_available():
            return self._fallback_jobstreet_data(keyword, location)
        
        keyword_slug = keyword.lower().replace(' ', '-').replace('_', '-')
        url = f"https://www.jobstreet.co.id/id/{keyword_slug}-jobs/in-{location.lower()}"
        
        result = self.scrape_url(url)
        
        if not result.get('success'):
            return self._fallback_jobstreet_data(keyword, location)
        
        jobs = self._parse_jobs_from_markdown(result.get('markdown', ''), 'Jobstreet')
        
        for job in jobs:
            job['keyword'] = keyword
            job['location'] = location
            job['source'] = 'Jobstreet (Firecrawl)'
        
        logger.info(f"✓ Found {len(jobs)} jobs from Jobstreet")
        return jobs
    
    def scrape_linkedin_jobs(self, keyword: str, location: str = 'Indonesia') -> List[Dict]:
        """
        Scrape job listings from LinkedIn
        """
        if not self.is_available():
            return self._fallback_linkedin_data(keyword, location)
        
        keyword_encoded = keyword.replace(' ', '%20').replace('_', '%20')
        url = f"https://www.linkedin.com/jobs/search?keywords={keyword_encoded}&location={location}"
        
        result = self.scrape_url(url)
        
        if not result.get('success'):
            return self._fallback_linkedin_data(keyword, location)
        
        jobs = self._parse_jobs_from_markdown(result.get('markdown', ''), 'LinkedIn')
        
        for job in jobs:
            job['keyword'] = keyword
            job['location'] = location
            job['source'] = 'LinkedIn (Firecrawl)'
        
        logger.info(f"✓ Found {len(jobs)} jobs from LinkedIn")
        return jobs
    
    def search_all_portals(self, keyword: str, location: str = 'Makassar') -> List[Dict]:
        """
        Search all job portals at once
        """
        logger.info(f"🔍 Searching all portals for: {keyword} in {location}")
        
        all_jobs = []
        
        # Scrape from multiple sources
        all_jobs.extend(self.scrape_glints_jobs(keyword, location))
        all_jobs.extend(self.scrape_jobstreet_jobs(keyword, location))
        all_jobs.extend(self.scrape_linkedin_jobs(keyword, location))
        
        logger.info(f"✓ Total jobs found: {len(all_jobs)}")
        return all_jobs
    
    def _parse_jobs_from_markdown(self, markdown: str, source: str) -> List[Dict]:
        """
        Parse job listings from markdown content
        Extract: title, company, salary, requirements
        """
        jobs = []
        
        if not markdown:
            return jobs
        
        # Salary extraction patterns
        salary_patterns = [
            r'Rp\s*([\d.,]+)\s*-?\s*([\d.,]+)?\s*(juta|jt|ribu)?',
            r'([\d.,]+)\s*-\s*([\d.,]+)\s*(juta|jt)',
            r'IDR\s*([\d.,]+)',
        ]
        
        # Split by common job card separators
        sections = re.split(r'\n---+\n|\n\n\n+', markdown)
        
        for section in sections[:20]:  # Limit to 20 jobs
            if len(section) < 50:
                continue
            
            job = {
                'title': '',
                'company': '',
                'salary_min': None,
                'salary_max': None,
                'salary_text': '',
                'description': section[:500],
                'source': source,
                'scraped_at': datetime.now().isoformat()
            }
            
            # Try to extract salary
            for pattern in salary_patterns:
                match = re.search(pattern, section, re.IGNORECASE)
                if match:
                    try:
                        groups = match.groups()
                        value = groups[0].replace('.', '').replace(',', '')
                        salary = int(value)
                        
                        suffix = groups[-1] if groups[-1] else ''
                        if suffix.lower() in ['juta', 'jt']:
                            salary *= 1000000
                        elif suffix.lower() in ['ribu']:
                            salary *= 1000
                        
                        if 1000000 < salary < 500000000:
                            job['salary_min'] = salary
                            job['salary_text'] = match.group()
                            
                            if len(groups) > 1 and groups[1]:
                                max_val = groups[1].replace('.', '').replace(',', '')
                                max_salary = int(max_val)
                                if suffix.lower() in ['juta', 'jt']:
                                    max_salary *= 1000000
                                job['salary_max'] = max_salary
                            
                            break
                    except:
                        continue
            
            # Extract title (usually first line or header)
            lines = section.strip().split('\n')
            if lines:
                title_line = lines[0].strip('#').strip()
                if len(title_line) < 100:
                    job['title'] = title_line
            
            if job['salary_min'] or job['title']:
                jobs.append(job)
        
        return jobs
    
    def _fallback_glints_data(self, keyword: str, location: str) -> List[Dict]:
        """Fallback sample data when Firecrawl is not available"""
        base_salaries = {
            'frontend': {'junior': 5000000, 'mid': 10000000, 'senior': 20000000},
            'backend': {'junior': 6000000, 'mid': 12000000, 'senior': 24000000},
            'fullstack': {'junior': 6000000, 'mid': 12000000, 'senior': 25000000},
            'mobile': {'junior': 5500000, 'mid': 11000000, 'senior': 22000000},
            'devops': {'junior': 7000000, 'mid': 15000000, 'senior': 30000000},
            'data': {'junior': 8000000, 'mid': 17000000, 'senior': 35000000},
        }
        
        category = 'fullstack'
        for key in base_salaries.keys():
            if key in keyword.lower():
                category = key
                break
        
        salaries = base_salaries.get(category, base_salaries['fullstack'])
        
        return [
            {
                'title': f'{keyword.title()} - Junior',
                'company': 'Sample Company',
                'salary_min': salaries['junior'],
                'salary_max': int(salaries['junior'] * 1.3),
                'source': 'Glints (Sample)',
                'location': location,
                'keyword': keyword
            },
            {
                'title': f'{keyword.title()} - Mid Level',
                'company': 'Sample Company',
                'salary_min': salaries['mid'],
                'salary_max': int(salaries['mid'] * 1.3),
                'source': 'Glints (Sample)',
                'location': location,
                'keyword': keyword
            },
            {
                'title': f'{keyword.title()} - Senior',
                'company': 'Sample Company',
                'salary_min': salaries['senior'],
                'salary_max': int(salaries['senior'] * 1.3),
                'source': 'Glints (Sample)',
                'location': location,
                'keyword': keyword
            },
        ]
    
    def _fallback_jobstreet_data(self, keyword: str, location: str) -> List[Dict]:
        """Fallback for Jobstreet"""
        return self._fallback_glints_data(keyword, location)
    
    def _fallback_linkedin_data(self, keyword: str, location: str) -> List[Dict]:
        """Fallback for LinkedIn"""
        return self._fallback_glints_data(keyword, location)


# Helper function
def scrape_jobs(keyword: str, location: str = 'Makassar') -> List[Dict]:
    """Quick function to scrape jobs from all portals"""
    scraper = FirecrawlScraper()
    return scraper.search_all_portals(keyword, location)


# Test
if __name__ == "__main__":
    scraper = FirecrawlScraper()
    
    if scraper.is_available():
        print("\n=== Testing Firecrawl ===\n")
        
        # Test single URL
        result = scraper.scrape_url("https://glints.com/id")
        print(f"Scrape result: {result.get('success')}")
        print(f"Content length: {len(result.get('markdown', ''))}")
        
        # Test job search
        print("\n=== Searching Jobs ===\n")
        jobs = scraper.scrape_glints_jobs("react developer", "Makassar")
        for job in jobs[:3]:
            print(f"- {job.get('title', 'N/A')}: Rp {job.get('salary_min', 0):,}")
    else:
        print("Firecrawl not available. Using fallback data.")
        jobs = scraper._fallback_glints_data("react developer", "Makassar")
        for job in jobs:
            print(f"- {job['title']}: Rp {job['salary_min']:,}")
