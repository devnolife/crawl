"""Quick test for advanced crawler"""
from advanced_crawler import AdvancedConstructionCrawler

print("="*60)
print("🧪 Testing Advanced Crawler with Sample Data")
print("="*60)

crawler = AdvancedConstructionCrawler(use_selenium=False)

try:
    # Test crawl materials
    results = crawler.crawl_all_materials(
        materials=['semen', 'bata merah', 'besi beton'],
        sources=['tokopedia'],
        max_per_source=3
    )
    
    print("\n📦 HASIL CRAWLING:")
    print("-"*60)
    for m in results['materials']:
        print(f"  {m['product_name']}: Rp{m['price']:,} ({m['location']})")
    
    print(f"\n✅ Total: {len(results['materials'])} items")
    
    # Test labor costs
    labor = crawler.crawl_labor_costs('Makassar')
    print(f"\n👷 Labor costs for Makassar: {len(labor)} positions")
    for l in labor[:3]:
        print(f"  {l['position']}: Rp{l['daily_rate']:,}/hari")
    
    # Test server costs
    servers = crawler.crawl_server_costs('digitalocean')
    print(f"\n☁️ Server costs: {len(servers)} options")
    for s in servers[:2]:
        print(f"  {s['name']}: ${s['price_monthly_usd']}/month")
    
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60)
    
finally:
    crawler.close()
