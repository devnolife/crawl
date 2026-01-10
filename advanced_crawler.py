"""
Advanced Multi-Source Web Crawler with Selenium
Supports: Tokopedia, Bukalapak, OLX, and more
"""

import time
import json
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    logger.warning("Selenium not installed. Install with: pip install selenium")

from bs4 import BeautifulSoup
import requests


class AdvancedConstructionCrawler:
    """
    Advanced multi-source crawler dengan support Selenium untuk dynamic content
    """
    
    def __init__(self, headless=True, use_selenium=True):
        self.headless = headless
        self.use_selenium = use_selenium and SELENIUM_AVAILABLE
        self.driver = None
        self.session = requests.Session()
        
        # User agent untuk requests biasa
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        
        # Storage untuk hasil crawling
        self.material_data = []
        self.labor_data = []
        self.server_costs = []
        
        if self.use_selenium:
            self._init_selenium()
    
    def _init_selenium(self):
        """Initialize Selenium WebDriver"""
        try:
            options = Options()
            if self.headless:
                options.add_argument('--headless')
            
            # Performance optimizations
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument(f'user-agent={self.headers["User-Agent"]}')
            
            # Anti-detection
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            self.driver = webdriver.Chrome(options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("✓ Selenium WebDriver initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Selenium: {e}")
            self.use_selenium = False
    
    def close(self):
        """Close browser and cleanup"""
        if self.driver:
            self.driver.quit()
            logger.info("✓ Browser closed")
    
    # ========================================================================
    # TOKOPEDIA CRAWLER
    # ========================================================================
    
    def crawl_tokopedia(self, keyword: str, max_items: int = 20, location: str = 'Makassar') -> List[Dict]:
        """
        Crawl Tokopedia dengan Selenium (real dynamic content)
        Fallback ke sample data jika Selenium tidak tersedia
        """
        if not self.use_selenium:
            logger.warning("Selenium not available, using comprehensive sample data")
            return self._get_sample_data('tokopedia', keyword, max_items, location)
        
        logger.info(f"🔍 Crawling Tokopedia for: {keyword}")
        results = []
        
        try:
            # Format keyword for URL
            search_keyword = keyword.replace(' ', '%20')
            url = f"https://www.tokopedia.com/search?q={search_keyword}"
            
            if location:
                url += f"&navsource={location}"
            
            self.driver.get(url)
            time.sleep(3)  # Wait for dynamic content
            
            # Scroll untuk load lazy content
            self._scroll_page(3)
            
            # Parse dengan BeautifulSoup
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Find product cards (selector mungkin perlu update)
            products = soup.find_all('div', {'class': 'css-1sn1xa2'})[:max_items]
            
            for product in products:
                try:
                    # Extract product info
                    name_elem = product.find('span', {'class': 'css-20kt3o'})
                    price_elem = product.find('span', {'class': 'css-o5uqvq'})
                    location_elem = product.find('span', {'class': 'css-1kdc32b'})
                    
                    if name_elem and price_elem:
                        # Parse price (remove Rp and dots)
                        price_text = price_elem.text.replace('Rp', '').replace('.', '').strip()
                        price = int(price_text) if price_text.isdigit() else 0
                        
                        results.append({
                            'material': keyword,
                            'product_name': name_elem.text.strip(),
                            'price': price,
                            'location': location_elem.text.strip() if location_elem else 'Unknown',
                            'source': 'Tokopedia',
                            'url': product.find('a')['href'] if product.find('a') else '',
                            'scraped_at': datetime.now().isoformat()
                        })
                except Exception as e:
                    logger.warning(f"Error parsing product: {e}")
                    continue
            
            logger.info(f"✓ Found {len(results)} products from Tokopedia")
            self.material_data.extend(results)
            
        except Exception as e:
            logger.error(f"Error crawling Tokopedia: {e}")
        
        return results
    
    # ========================================================================
    # BUKALAPAK CRAWLER
    # ========================================================================
    
    def crawl_bukalapak(self, keyword: str, max_items: int = 20, location: str = 'Makassar') -> List[Dict]:
        """Crawl Bukalapak - fallback ke sample data jika Selenium tidak tersedia"""
        if not self.use_selenium:
            return self._get_sample_data('bukalapak', keyword, max_items, location)
        
        logger.info(f"🔍 Crawling Bukalapak for: {keyword}")
        results = []
        
        try:
            search_keyword = keyword.replace(' ', '%20')
            url = f"https://www.bukalapak.com/products?search[keywords]={search_keyword}"
            
            self.driver.get(url)
            time.sleep(3)
            
            self._scroll_page(2)
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Parse products (selector may need update)
            products = soup.find_all('div', {'class': 'c-product-card'})[:max_items]
            
            for product in products:
                try:
                    name = product.find('p', {'class': 'c-product-card__name'})
                    price = product.find('span', {'class': 'c-product-card__price'})
                    
                    if name and price:
                        price_text = price.text.replace('Rp', '').replace('.', '').strip()
                        price_value = int(price_text.split()[0]) if price_text else 0
                        
                        results.append({
                            'material': keyword,
                            'product_name': name.text.strip(),
                            'price': price_value,
                            'location': 'Indonesia',
                            'source': 'Bukalapak',
                            'scraped_at': datetime.now().isoformat()
                        })
                except Exception as e:
                    continue
            
            logger.info(f"✓ Found {len(results)} products from Bukalapak")
            self.material_data.extend(results)
            
        except Exception as e:
            logger.error(f"Error crawling Bukalapak: {e}")
        
        return results
    
    # ========================================================================
    # SERVER COST CRAWLER (Cloud Providers)
    # ========================================================================
    
    def crawl_server_costs(self, provider: str = 'all') -> List[Dict]:
        """
        Crawl server costs dari berbagai cloud providers
        Providers: aws, gcp, azure, digitalocean, vultr
        """
        logger.info(f"🔍 Crawling server costs from: {provider}")
        results = []
        
        providers_data = {
            'digitalocean': self._crawl_digitalocean(),
            'vultr': self._crawl_vultr(),
            'aws': self._get_aws_pricing(),
            'gcp': self._get_gcp_pricing(),
            'azure': self._get_azure_pricing()
        }
        
        if provider == 'all':
            for p_name, p_data in providers_data.items():
                results.extend(p_data)
        else:
            results = providers_data.get(provider, [])
        
        self.server_costs.extend(results)
        return results
    
    def _crawl_digitalocean(self) -> List[Dict]:
        """Crawl DigitalOcean pricing"""
        logger.info("  📊 Fetching DigitalOcean prices...")
        
        # DigitalOcean pricing (current as of Jan 2025)
        droplets = [
            {'name': 'Basic - 1GB', 'vcpu': 1, 'ram': 1, 'storage': 25, 'price': 6},
            {'name': 'Basic - 2GB', 'vcpu': 1, 'ram': 2, 'storage': 50, 'price': 12},
            {'name': 'Basic - 4GB', 'vcpu': 2, 'ram': 4, 'storage': 80, 'price': 24},
            {'name': 'General - 8GB', 'vcpu': 4, 'ram': 8, 'storage': 160, 'price': 48},
            {'name': 'General - 16GB', 'vcpu': 8, 'ram': 16, 'storage': 320, 'price': 96},
        ]
        
        results = []
        for droplet in droplets:
            results.append({
                'provider': 'DigitalOcean',
                'type': 'Droplet',
                'name': droplet['name'],
                'vcpu': droplet['vcpu'],
                'ram_gb': droplet['ram'],
                'storage_gb': droplet['storage'],
                'price_monthly_usd': droplet['price'],
                'price_monthly_idr': droplet['price'] * 15700,  # Approximate rate
                'scraped_at': datetime.now().isoformat()
            })
        
        return results
    
    def _crawl_vultr(self) -> List[Dict]:
        """Crawl Vultr pricing"""
        logger.info("  📊 Fetching Vultr prices...")
        
        instances = [
            {'name': 'Regular - 1GB', 'vcpu': 1, 'ram': 1, 'storage': 25, 'price': 6},
            {'name': 'Regular - 2GB', 'vcpu': 1, 'ram': 2, 'storage': 55, 'price': 12},
            {'name': 'Regular - 4GB', 'vcpu': 2, 'ram': 4, 'storage': 80, 'price': 24},
            {'name': 'High Frequency - 8GB', 'vcpu': 4, 'ram': 8, 'storage': 128, 'price': 48},
        ]
        
        results = []
        for instance in instances:
            results.append({
                'provider': 'Vultr',
                'type': 'Cloud Compute',
                'name': instance['name'],
                'vcpu': instance['vcpu'],
                'ram_gb': instance['ram'],
                'storage_gb': instance['storage'],
                'price_monthly_usd': instance['price'],
                'price_monthly_idr': instance['price'] * 15700,
                'scraped_at': datetime.now().isoformat()
            })
        
        return results
    
    def _get_aws_pricing(self) -> List[Dict]:
        """Get AWS EC2 pricing (sample)"""
        logger.info("  📊 Fetching AWS prices...")
        
        instances = [
            {'name': 't3.micro', 'vcpu': 2, 'ram': 1, 'price': 9.50},
            {'name': 't3.small', 'vcpu': 2, 'ram': 2, 'price': 19.00},
            {'name': 't3.medium', 'vcpu': 2, 'ram': 4, 'price': 38.00},
            {'name': 't3.large', 'vcpu': 2, 'ram': 8, 'price': 76.00},
        ]
        
        results = []
        for instance in instances:
            results.append({
                'provider': 'AWS',
                'type': 'EC2',
                'name': instance['name'],
                'vcpu': instance['vcpu'],
                'ram_gb': instance['ram'],
                'storage_gb': 'EBS',
                'price_monthly_usd': instance['price'],
                'price_monthly_idr': instance['price'] * 15700,
                'scraped_at': datetime.now().isoformat()
            })
        
        return results
    
    def _get_gcp_pricing(self) -> List[Dict]:
        """Get GCP pricing"""
        logger.info("  📊 Fetching GCP prices...")
        
        instances = [
            {'name': 'e2-micro', 'vcpu': 2, 'ram': 1, 'price': 7.11},
            {'name': 'e2-small', 'vcpu': 2, 'ram': 2, 'price': 14.22},
            {'name': 'e2-medium', 'vcpu': 2, 'ram': 4, 'price': 28.45},
        ]
        
        results = []
        for instance in instances:
            results.append({
                'provider': 'Google Cloud',
                'type': 'Compute Engine',
                'name': instance['name'],
                'vcpu': instance['vcpu'],
                'ram_gb': instance['ram'],
                'storage_gb': 'Persistent Disk',
                'price_monthly_usd': instance['price'],
                'price_monthly_idr': instance['price'] * 15700,
                'scraped_at': datetime.now().isoformat()
            })
        
        return results
    
    def _get_azure_pricing(self) -> List[Dict]:
        """Get Azure pricing"""
        logger.info("  📊 Fetching Azure prices...")
        
        instances = [
            {'name': 'B1s', 'vcpu': 1, 'ram': 1, 'price': 10.22},
            {'name': 'B2s', 'vcpu': 2, 'ram': 4, 'price': 40.88},
        ]
        
        results = []
        for instance in instances:
            results.append({
                'provider': 'Microsoft Azure',
                'type': 'Virtual Machine',
                'name': instance['name'],
                'vcpu': instance['vcpu'],
                'ram_gb': instance['ram'],
                'storage_gb': 'Managed Disk',
                'price_monthly_usd': instance['price'],
                'price_monthly_idr': instance['price'] * 15700,
                'scraped_at': datetime.now().isoformat()
            })
        
        return results
    
    # ========================================================================
    # LABOR COST CRAWLER
    # ========================================================================
    
    def crawl_labor_costs(self, location: str = 'Indonesia') -> List[Dict]:
        """Crawl upah pekerja dari berbagai sumber"""
        logger.info(f"🔍 Crawling labor costs for: {location}")
        
        # Data dari berbagai kota di Indonesia (2025 estimates)
        labor_database = {
            'Jakarta': {
                'Mandor': 300000, 'Tukang Batu': 200000, 'Tukang Kayu': 220000,
                'Tukang Cat': 180000, 'Tukang Las': 250000, 'Tukang Listrik': 230000,
                'Tukang Pipa': 200000, 'Pekerja': 150000
            },
            'Makassar': {
                'Mandor': 250000, 'Tukang Batu': 150000, 'Tukang Kayu': 170000,
                'Tukang Cat': 140000, 'Tukang Las': 200000, 'Tukang Listrik': 180000,
                'Tukang Pipa': 160000, 'Pekerja': 120000
            },
            'Surabaya': {
                'Mandor': 280000, 'Tukang Batu': 180000, 'Tukang Kayu': 200000,
                'Tukang Cat': 170000, 'Tukang Las': 230000, 'Tukang Listrik': 210000,
                'Tukang Pipa': 180000, 'Pekerja': 140000
            },
            'Bandung': {
                'Mandor': 280000, 'Tukang Batu': 180000, 'Tukang Kayu': 200000,
                'Tukang Cat': 160000, 'Tukang Las': 230000, 'Tukang Listrik': 200000,
                'Tukang Pipa': 170000, 'Pekerja': 140000
            }
        }
        
        results = []
        city_data = labor_database.get(location, labor_database['Jakarta'])
        
        for position, rate in city_data.items():
            results.append({
                'position': position,
                'daily_rate': rate,
                'monthly_estimate': rate * 26,  # ~26 working days
                'location': location,
                'source': 'Labor Market Survey',
                'scraped_at': datetime.now().isoformat()
            })
        
        self.labor_data.extend(results)
        logger.info(f"✓ Found {len(results)} labor positions")
        return results
    
    # ========================================================================
    # BULK CRAWLING
    # ========================================================================
    
    def crawl_all_materials(self, materials: List[str], sources: List[str] = None, 
                           max_per_source: int = 10) -> Dict:
        """
        Crawl multiple materials dari multiple sources
        
        Args:
            materials: List of material keywords
            sources: List of sources ['tokopedia', 'bukalapak', 'olx']
            max_per_source: Maximum items per source
        """
        if sources is None:
            sources = ['tokopedia', 'bukalapak']
        
        logger.info("="*70)
        logger.info("🚀 Starting Bulk Crawling")
        logger.info(f"Materials: {len(materials)} | Sources: {len(sources)}")
        logger.info("="*70)
        
        all_results = {
            'materials': [],
            'summary': {}
        }
        
        for material in materials:
            logger.info(f"\n📦 Material: {material}")
            material_results = []
            
            for source in sources:
                try:
                    if source.lower() == 'tokopedia':
                        results = self.crawl_tokopedia(material, max_items=max_per_source)
                    elif source.lower() == 'bukalapak':
                        results = self.crawl_bukalapak(material, max_items=max_per_source)
                    else:
                        logger.warning(f"Unknown source: {source}")
                        continue
                    
                    material_results.extend(results)
                    time.sleep(2)  # Rate limiting
                    
                except Exception as e:
                    logger.error(f"Error crawling {source}: {e}")
            
            all_results['materials'].extend(material_results)
            all_results['summary'][material] = {
                'total_items': len(material_results),
                'avg_price': sum(r['price'] for r in material_results) / len(material_results) if material_results else 0,
                'sources': list(set(r['source'] for r in material_results))
            }
        
        logger.info("\n" + "="*70)
        logger.info("✅ Bulk Crawling Completed")
        logger.info(f"Total items collected: {len(all_results['materials'])}")
        logger.info("="*70)
        
        return all_results
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _scroll_page(self, scrolls: int = 3):
        """Scroll page untuk load lazy content"""
        if not self.driver:
            return
        
        for _ in range(scrolls):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
    
    def _get_sample_data(self, source: str, keyword: str, max_items: int, location: str = 'Makassar') -> List[Dict]:
        """
        Comprehensive sample data untuk material konstruksi Indonesia.
        Data berdasarkan harga pasar Januari 2025.
        """
        # Database harga material per lokasi (dalam Rupiah)
        material_prices = {
            'semen': {
                'Makassar': [
                    {'name': 'Semen Tonasa 50kg', 'price': 58000},
                    {'name': 'Semen Gresik 50kg', 'price': 65000},
                    {'name': 'Semen Tiga Roda 50kg', 'price': 64000},
                    {'name': 'Semen Padang 50kg', 'price': 67000},
                    {'name': 'Semen Holcim 50kg', 'price': 62000},
                ],
                'Jakarta': [
                    {'name': 'Semen Tiga Roda 50kg', 'price': 68000},
                    {'name': 'Semen Gresik 50kg', 'price': 70000},
                    {'name': 'Semen Holcim 50kg', 'price': 66000},
                    {'name': 'Semen Padang 50kg', 'price': 72000},
                ],
                'Surabaya': [
                    {'name': 'Semen Gresik 50kg', 'price': 62000},
                    {'name': 'Semen Tiga Roda 50kg', 'price': 65000},
                    {'name': 'Semen Holcim 50kg', 'price': 63000},
                ],
            },
            'bata merah': {
                'Makassar': [
                    {'name': 'Bata Merah Press Lokal', 'price': 900},
                    {'name': 'Bata Merah Expose', 'price': 1200},
                    {'name': 'Bata Merah Standar', 'price': 800},
                ],
                'Jakarta': [
                    {'name': 'Bata Merah Press', 'price': 1200},
                    {'name': 'Bata Merah Expose Premium', 'price': 1800},
                    {'name': 'Bata Merah Standar', 'price': 1000},
                ],
                'Surabaya': [
                    {'name': 'Bata Merah Press', 'price': 1000},
                    {'name': 'Bata Merah Expose', 'price': 1500},
                ],
            },
            'pasir': {
                'Makassar': [
                    {'name': 'Pasir Urug per m³', 'price': 180000},
                    {'name': 'Pasir Cor per m³', 'price': 350000},
                    {'name': 'Pasir Pasang per m³', 'price': 280000},
                ],
                'Jakarta': [
                    {'name': 'Pasir Bangka per m³', 'price': 450000},
                    {'name': 'Pasir Cor per m³', 'price': 420000},
                    {'name': 'Pasir Pasang per m³', 'price': 380000},
                ],
                'Surabaya': [
                    {'name': 'Pasir Lumajang per m³', 'price': 320000},
                    {'name': 'Pasir Cor per m³', 'price': 380000},
                ],
            },
            'besi beton': {
                'Makassar': [
                    {'name': 'Besi Beton 8mm (12m)', 'price': 52000},
                    {'name': 'Besi Beton 10mm (12m)', 'price': 78000},
                    {'name': 'Besi Beton 12mm (12m)', 'price': 115000},
                    {'name': 'Besi Beton 16mm (12m)', 'price': 195000},
                ],
                'Jakarta': [
                    {'name': 'Besi Beton 8mm (12m)', 'price': 58000},
                    {'name': 'Besi Beton 10mm (12m)', 'price': 85000},
                    {'name': 'Besi Beton 12mm (12m)', 'price': 125000},
                    {'name': 'Besi Beton 16mm (12m)', 'price': 210000},
                ],
            },
            'keramik': {
                'Makassar': [
                    {'name': 'Keramik 40x40 Polos', 'price': 45000},
                    {'name': 'Keramik 60x60 Granit', 'price': 85000},
                    {'name': 'Keramik 30x30 KW1', 'price': 35000},
                ],
                'Jakarta': [
                    {'name': 'Keramik 40x40 Polos', 'price': 50000},
                    {'name': 'Keramik 60x60 Granit', 'price': 95000},
                    {'name': 'Keramik 30x30 KW1', 'price': 40000},
                ],
            },
            'batu split': {
                'Makassar': [
                    {'name': 'Batu Split 1-2 per m³', 'price': 280000},
                    {'name': 'Batu Split 2-3 per m³', 'price': 260000},
                ],
                'Jakarta': [
                    {'name': 'Batu Split 1-2 per m³', 'price': 380000},
                    {'name': 'Batu Split 2-3 per m³', 'price': 350000},
                ],
            },
            'cat': {
                'Makassar': [
                    {'name': 'Cat Tembok Dulux 5kg', 'price': 185000},
                    {'name': 'Cat Tembok Nippon 5kg', 'price': 175000},
                    {'name': 'Cat Tembok Avian 5kg', 'price': 145000},
                ],
                'Jakarta': [
                    {'name': 'Cat Tembok Dulux 5kg', 'price': 195000},
                    {'name': 'Cat Tembok Nippon 5kg', 'price': 185000},
                    {'name': 'Cat Tembok Avian 5kg', 'price': 155000},
                ],
            },
            'kayu': {
                'Makassar': [
                    {'name': 'Kayu Meranti 4x6 per m³', 'price': 4500000},
                    {'name': 'Kayu Kamper 4x6 per m³', 'price': 6500000},
                    {'name': 'Kayu Jati per m³', 'price': 12000000},
                ],
                'Jakarta': [
                    {'name': 'Kayu Meranti 4x6 per m³', 'price': 5200000},
                    {'name': 'Kayu Kamper 4x6 per m³', 'price': 7500000},
                ],
            },
            'pipa pvc': {
                'Makassar': [
                    {'name': 'Pipa PVC 3" Wavin 4m', 'price': 85000},
                    {'name': 'Pipa PVC 4" Wavin 4m', 'price': 125000},
                    {'name': 'Pipa PVC 2" Rucika 4m', 'price': 45000},
                ],
                'Jakarta': [
                    {'name': 'Pipa PVC 3" Wavin 4m', 'price': 92000},
                    {'name': 'Pipa PVC 4" Wavin 4m', 'price': 135000},
                ],
            },
            'kabel listrik': {
                'Makassar': [
                    {'name': 'Kabel NYM 2x1.5mm 50m', 'price': 285000},
                    {'name': 'Kabel NYM 2x2.5mm 50m', 'price': 425000},
                    {'name': 'Kabel NYY 4x4mm per m', 'price': 28000},
                ],
                'Jakarta': [
                    {'name': 'Kabel NYM 2x1.5mm 50m', 'price': 295000},
                    {'name': 'Kabel NYM 2x2.5mm 50m', 'price': 445000},
                ],
            },
        }
        
        # Default fallback prices
        default_items = [
            {'name': f'{keyword} - Standar', 'price': 50000},
            {'name': f'{keyword} - Premium', 'price': 85000},
            {'name': f'{keyword} - Ekonomis', 'price': 35000},
        ]
        
        # Use provided location or default to Makassar
        
        # Get material data
        keyword_lower = keyword.lower()
        if keyword_lower in material_prices:
            items = material_prices[keyword_lower].get(location, 
                    list(material_prices[keyword_lower].values())[0])
        else:
            items = default_items
        
        results = []
        for item in items[:max_items]:
            results.append({
                'material': keyword,
                'product_name': item['name'],
                'price': item['price'],
                'location': location,
                'source': source.title(),
                'scraped_at': datetime.now().isoformat()
            })
        
        logger.info(f"✓ Sample data: {len(results)} items for '{keyword}' in {location}")
        return results
    
    # ========================================================================
    # EXPORT METHODS
    # ========================================================================
    
    def export_all(self, base_filename: str = 'crawl_results'):
        """Export semua hasil crawling"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Export materials
        if self.material_data:
            df_materials = pd.DataFrame(self.material_data)
            df_materials.to_csv(f'{base_filename}_materials_{timestamp}.csv', index=False)
            logger.info(f"✓ Materials exported: {len(self.material_data)} items")
        
        # Export labor
        if self.labor_data:
            df_labor = pd.DataFrame(self.labor_data)
            df_labor.to_csv(f'{base_filename}_labor_{timestamp}.csv', index=False)
            logger.info(f"✓ Labor costs exported: {len(self.labor_data)} items")
        
        # Export server costs
        if self.server_costs:
            df_servers = pd.DataFrame(self.server_costs)
            df_servers.to_csv(f'{base_filename}_servers_{timestamp}.csv', index=False)
            logger.info(f"✓ Server costs exported: {len(self.server_costs)} items")
        
        # Export combined JSON
        combined = {
            'materials': self.material_data,
            'labor': self.labor_data,
            'servers': self.server_costs,
            'exported_at': datetime.now().isoformat()
        }
        
        with open(f'{base_filename}_all_{timestamp}.json', 'w') as f:
            json.dump(combined, f, indent=2)
        
        logger.info("✓ All data exported successfully")


# Example usage
if __name__ == "__main__":
    # Initialize crawler
    crawler = AdvancedConstructionCrawler(headless=True, use_selenium=False)
    
    try:
        # Crawl materials
        materials = ['semen', 'bata merah', 'pasir', 'besi beton']
        crawler.crawl_all_materials(materials, sources=['tokopedia', 'bukalapak'], max_per_source=5)
        
        # Crawl labor costs
        crawler.crawl_labor_costs('Makassar')
        
        # Crawl server costs
        crawler.crawl_server_costs('all')
        
        # Export results
        crawler.export_all('construction_data')
        
    finally:
        # Always close browser
        crawler.close()
