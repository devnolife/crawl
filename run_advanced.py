#!/usr/bin/env python3
"""
Advanced Runner Script
Full-featured menu system for Construction Cost Estimator
"""

import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    missing = []
    
    # Check Python packages
    packages = {
        'streamlit': 'Streamlit',
        'pandas': 'Pandas',
        'requests': 'Requests',
        'bs4': 'BeautifulSoup4',
        'openpyxl': 'OpenPyXL'
    }
    
    for package, name in packages.items():
        try:
            __import__(package)
            print(f"  ✓ {name}")
        except ImportError:
            print(f"  ✗ {name} (missing)")
            missing.append(name)
    
    # Check optional packages
    try:
        __import__('selenium')
        print(f"  ✓ Selenium (advanced crawling)")
        selenium_available = True
    except ImportError:
        print(f"  ⚠ Selenium (optional - for real web crawling)")
        selenium_available = False
    
    # Check Node.js
    import subprocess
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, timeout=5)
        if result.returncode == 0:
            print(f"  ✓ Node.js {result.stdout.decode().strip()}")
            nodejs_available = True
        else:
            nodejs_available = False
    except:
        print(f"  ⚠ Node.js (optional - for document generation)")
        nodejs_available = False
    
    # Check docx package
    if nodejs_available:
        try:
            result = subprocess.run(['npm', 'list', '-g', 'docx'], 
                                  capture_output=True, timeout=5)
            if 'docx@' in result.stdout.decode():
                print(f"  ✓ docx package")
                docx_available = True
            else:
                print(f"  ⚠ docx package (install with: npm install -g docx)")
                docx_available = False
        except:
            docx_available = False
    else:
        docx_available = False
    
    return {
        'missing': missing,
        'selenium': selenium_available,
        'nodejs': nodejs_available,
        'docx': docx_available
    }

def show_main_menu(deps):
    """Display main menu"""
    print("\n" + "="*70)
    print("🏗️  CONSTRUCTION COST ESTIMATOR - ADVANCED EDITION")
    print("="*70)
    print("\n📊 AVAILABLE FEATURES:\n")
    
    print("1. 🖥️  Run Streamlit App (Basic UI)")
    print("2. 🕷️  Multi-Source Web Crawler")
    print("3. 📄 Generate Documents (RAB, Price Request, Server Cost)")
    print("4. 💾 Update Database")
    print("5. 📊 Run Analytics & Reports")
    print("6. 🧪 Run Tests")
    print("7. 🎓 Run Demo (Basic)")
    print("8. 🚀 Run Advanced Demo")
    print("9. ⚙️  Install Missing Dependencies")
    print("10. 📚 View Documentation")
    print("0. ❌ Exit")
    
    # Show status
    print("\n" + "-"*70)
    print("📌 STATUS:")
    print(f"  Selenium: {'✓ Available' if deps['selenium'] else '✗ Not installed'}")
    print(f"  Node.js: {'✓ Available' if deps['nodejs'] else '✗ Not installed'}")
    print(f"  docx: {'✓ Available' if deps['docx'] else '✗ Not installed'}")
    print("-"*70)
    
    choice = input("\n👉 Select option (0-10): ").strip()
    return choice

def run_streamlit():
    """Run Streamlit app"""
    print("\n🖥️  Starting Streamlit app...")
    print("📱 App will open at: http://localhost:8501")
    print("⏹️  Press Ctrl+C to stop\n")
    
    import subprocess
    subprocess.run(['streamlit', 'run', 'app.py'])

def run_crawler():
    """Run web crawler"""
    print("\n🕷️  WEB CRAWLER")
    print("="*70)
    print("\n⚠️  Note: For real crawling, Selenium must be installed")
    print("Current mode will use sample data if Selenium is not available\n")
    
    print("Select crawler mode:")
    print("1. Quick crawl (5 items per source)")
    print("2. Standard crawl (20 items per source)")
    print("3. Deep crawl (50 items per source)")
    print("4. Server cost only")
    print("5. Custom")
    print("0. Back")
    
    choice = input("\n👉 Select: ").strip()
    
    if choice == '0':
        return
    
    from advanced_crawler import AdvancedConstructionCrawler
    
    crawler = AdvancedConstructionCrawler(headless=True, use_selenium=False)
    
    try:
        if choice in ['1', '2', '3']:
            items_per_source = {'1': 5, '2': 20, '3': 50}[choice]
            
            materials = ['semen', 'bata merah', 'pasir', 'besi beton', 'keramik']
            sources = ['tokopedia', 'bukalapak']
            
            print(f"\nCrawling {len(materials)} materials from {len(sources)} sources...")
            results = crawler.crawl_all_materials(materials, sources, items_per_source)
            
            print(f"\n✓ Collected {len(results['materials'])} items")
            
        elif choice == '4':
            print("\nCrawling server costs from cloud providers...")
            servers = crawler.crawl_server_costs('all')
            print(f"\n✓ Found {len(servers)} server options")
            
        elif choice == '5':
            materials_input = input("Materials (comma-separated): ")
            materials = [m.strip() for m in materials_input.split(',')]
            
            max_items = int(input("Max items per source: "))
            
            results = crawler.crawl_all_materials(materials, ['tokopedia', 'bukalapak'], max_items)
            print(f"\n✓ Collected {len(results['materials'])} items")
        
        # Always crawl labor and servers
        crawler.crawl_labor_costs('Makassar')
        
        # Export
        print("\nExporting data...")
        crawler.export_all('crawl_results')
        print("✓ Data exported")
        
    finally:
        crawler.close()
    
    input("\n✅ Press Enter to continue...")

def run_document_generator():
    """Run document generator"""
    print("\n📄 DOCUMENT GENERATOR")
    print("="*70)
    
    if not os.path.exists('documents'):
        os.makedirs('documents')
    
    print("\nSelect document type:")
    print("1. RAB (Rencana Anggaran Biaya)")
    print("2. Price Request Letter")
    print("3. Server Cost Analysis")
    print("4. All documents")
    print("0. Back")
    
    choice = input("\n👉 Select: ").strip()
    
    if choice == '0':
        return
    
    # Sample data
    from document_generator import DocumentGenerator
    from document_generators_extra import (
        generate_price_request_document,
        generate_server_cost_document
    )
    
    doc_gen = DocumentGenerator(output_dir="documents")
    
    if choice in ['1', '4']:
        print("\n📊 Generating RAB document...")
        
        project_data = {
            'name': 'Pembangunan Rumah Tinggal 2 Lantai',
            'location': 'Makassar',
            'building_area': 120,
            'prepared_by': 'Tim Estimator'
        }
        
        material_data = [
            {'name': 'Semen 50kg', 'quantity': 600, 'unit': 'sak', 'price': 65000, 'total_cost': 39000000},
            {'name': 'Bata Merah', 'quantity': 8400, 'unit': 'buah', 'price': 1200, 'total_cost': 10080000},
        ]
        
        labor_data = [
            {'position': 'Mandor', 'quantity': 90, 'unit': 'hari', 'daily_rate': 250000, 'total_cost': 22500000},
            {'position': 'Tukang Batu', 'quantity': 90, 'unit': 'hari', 'daily_rate': 150000, 'total_cost': 13500000},
        ]
        
        try:
            path = doc_gen.generate_rab_document(project_data, material_data, labor_data)
            if path:
                print(f"✓ RAB created: {path}")
        except Exception as e:
            print(f"✗ Error: {e}")
    
    if choice in ['2', '4']:
        print("\n📧 Generating Price Request...")
        
        suppliers = [{'name': 'PT Supplier', 'address': 'Address', 'contact': '0411-123456'}]
        materials = [
            {'name': 'Semen 50kg', 'specification': 'Type I', 'quantity': '500', 'unit': 'sak'}
        ]
        project_info = {'name': 'Project X', 'location': 'Makassar', 'timeline': '3 bulan', 'contact_person': 'Manager'}
        
        try:
            path = generate_price_request_document(suppliers, materials, project_info, "documents")
            if path:
                print(f"✓ Price request created: {path}")
        except Exception as e:
            print(f"✗ Error: {e}")
    
    if choice in ['3', '4']:
        print("\n💻 Generating Server Cost Analysis...")
        
        server_data = [
            {'provider': 'DigitalOcean', 'name': 'Basic 2GB', 'vcpu': 1, 'ram_gb': 2, 'price_monthly_usd': 12},
        ]
        
        project_req = {
            'project_name': 'Web Platform',
            'traffic': '10K/day',
            'storage': '500GB',
            'bandwidth': '2TB',
            'availability': '99.9%'
        }
        
        try:
            path = generate_server_cost_document(server_data, project_req, "documents")
            if path:
                print(f"✓ Server cost analysis created: {path}")
        except Exception as e:
            print(f"✗ Error: {e}")
    
    input("\n✅ Press Enter to continue...")

def run_database_update():
    """Update database"""
    print("\n💾 DATABASE UPDATE")
    print("="*70)
    
    from database import PriceDatabase
    from advanced_crawler import AdvancedConstructionCrawler
    
    db = PriceDatabase()
    crawler = AdvancedConstructionCrawler(use_selenium=False)
    
    try:
        print("\n1. Crawling fresh data...")
        materials = ['semen', 'bata merah', 'pasir']
        results = crawler.crawl_all_materials(materials, ['tokopedia'], 5)
        labor = crawler.crawl_labor_costs('Makassar')
        
        print("\n2. Saving to database...")
        for item in crawler.material_data:
            db.insert_material_price({
                'material_name': item['material'],
                'product_name': item['product_name'],
                'price': item['price'],
                'location': item['location'],
                'province': 'Auto',
                'source': item['source']
            })
        
        for labor_item in labor:
            db.insert_labor_cost({
                'position': labor_item['position'],
                'daily_rate': labor_item['daily_rate'],
                'location': labor_item['location'],
                'province': 'Sulsel',
                'source': labor_item['source']
            })
        
        print("\n3. Updating price history...")
        db.update_price_history()
        
        print("\n4. Exporting to Excel...")
        db.export_to_excel("price_database.xlsx")
        
        print("\n✓ Database updated successfully!")
        
    finally:
        crawler.close()
    
    input("\n✅ Press Enter to continue...")

def install_dependencies():
    """Install missing dependencies"""
    print("\n⚙️  DEPENDENCY INSTALLER")
    print("="*70)
    
    print("\n1. Install Python packages")
    print("2. Install Selenium")
    print("3. Install Node.js (manual)")
    print("4. Install docx package")
    print("0. Back")
    
    choice = input("\n👉 Select: ").strip()
    
    import subprocess
    
    if choice == '1':
        print("\nInstalling Python packages...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        
    elif choice == '2':
        print("\nInstalling Selenium...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'selenium', 'webdriver-manager'])
        
    elif choice == '3':
        print("\nNode.js must be installed manually:")
        print("Visit: https://nodejs.org/")
        print("Download and install LTS version")
        
    elif choice == '4':
        print("\nInstalling docx package...")
        subprocess.run(['npm', 'install', '-g', 'docx'])
    
    input("\n✅ Press Enter to continue...")

def main():
    """Main function"""
    # Check dependencies
    deps = check_dependencies()
    
    while True:
        choice = show_main_menu(deps)
        
        if choice == '0':
            print("\n👋 Thank you for using Construction Cost Estimator!")
            break
            
        elif choice == '1':
            run_streamlit()
            
        elif choice == '2':
            run_crawler()
            
        elif choice == '3':
            run_document_generator()
            
        elif choice == '4':
            run_database_update()
            
        elif choice == '5':
            print("\n📊 Analytics feature coming soon!")
            input("\nPress Enter to continue...")
            
        elif choice == '6':
            print("\n🧪 Running tests...")
            import subprocess
            subprocess.run([sys.executable, 'test.py'])
            input("\nPress Enter to continue...")
            
        elif choice == '7':
            print("\n🎓 Running basic demo...")
            import subprocess
            subprocess.run([sys.executable, 'demo.py'])
            input("\nPress Enter to continue...")
            
        elif choice == '8':
            print("\n🚀 Running advanced demo...")
            import subprocess
            subprocess.run([sys.executable, 'demo_advanced.py'])
            input("\nPress Enter to continue...")
            
        elif choice == '9':
            install_dependencies()
            deps = check_dependencies()  # Recheck
            
        elif choice == '10':
            print("\n📚 DOCUMENTATION")
            print("="*70)
            print("\nAvailable documentation:")
            print("  - README.md - Project overview")
            print("  - README_ADVANCED.md - Advanced features")
            print("  - INSTALLATION.md - Installation guide")
            print("  - QUICKSTART.md - Quick reference")
            print("  - PROJECT_STRUCTURE.md - Architecture")
            print("  - INDEX.md - Navigation guide")
            input("\nPress Enter to continue...")
            
        else:
            print("\n❌ Invalid option!")
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Program interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
