#!/usr/bin/env python3
"""
Test script for AppFolio scraper
This script tests the scraper with a limited number of properties
"""

import asyncio
import json
from appfolio_scraper import AppFolioScraper

async def test_scraper():
    """Test the scraper with a small sample"""
    print("Testing AppFolio scraper...")
    print("=" * 50)
    
    scraper = AppFolioScraper()
    
    try:
        # Test with a small sample
        properties = await scraper.scrape_listings()
        
        if properties:
            print(f"✅ Successfully scraped {len(properties)} properties")
            print("\nSample property data:")
            print("-" * 30)
            
            for i, prop in enumerate(properties[:2]):  # Show first 2 properties
                print(f"\nProperty {i+1}:")
                print(f"  Title: {prop.get('title', 'N/A')}")
                print(f"  Price: {prop.get('price', 'N/A')}")
                print(f"  Address: {prop.get('address', 'N/A')}")
                print(f"  Bedrooms: {prop.get('bedrooms', 'N/A')}")
                print(f"  Bathrooms: {prop.get('bathrooms', 'N/A')}")
                print(f"  Square Feet: {prop.get('square_feet', 'N/A')}")
                print(f"  Images: {len(prop.get('images', []))} found")
                print(f"  URL: {prop.get('url', 'N/A')}")
            
            # Save test data
            scraper.save_to_json(properties, "test_properties.json")
            print(f"\n✅ Test data saved to test_properties.json")
            
        else:
            print("❌ No properties were scraped")
            print("This might be due to:")
            print("- Network connectivity issues")
            print("- Changes in the AppFolio site structure")
            print("- Rate limiting or blocking")
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        print("\nTroubleshooting steps:")
        print("1. Check your internet connection")
        print("2. Verify the AppFolio site is accessible")
        print("3. Install Playwright browsers: playwright install")
        print("4. Check for any error messages above")

if __name__ == "__main__":
    asyncio.run(test_scraper())
