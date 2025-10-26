#!/usr/bin/env python3
"""
AppFolio Property Scraper for City Block Properties
Scrapes property listings from cityblockprop.appfolio.com and formats them for WordPress integration
"""

import asyncio
import json
import os
import re
import time
from datetime import datetime
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright


class AppFolioScraper:
    def __init__(self, base_url: str = "https://cityblockprop.appfolio.com"):
        self.base_url = base_url
        self.listings_url = f"{base_url}/listings"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
    async def scrape_listings(self) -> List[Dict]:
        """Main method to scrape all property listings"""
        print("Starting AppFolio property scraping...")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                # Navigate to listings page
                print(f"Navigating to {self.listings_url}")
                await page.goto(self.listings_url, wait_until='networkidle')
                
                # Wait for listings to load
                await page.wait_for_selector('.property-card, .listing-item, .property-item', timeout=10000)
                
                # Get all property links - focus on detail pages only
                property_links = await page.evaluate("""
                    () => {
                        const links = [];
                        // Look for property detail links specifically
                        const selectors = [
                            'a[href*="/listings/detail/"]',
                            '.property-card a[href*="/listings/detail/"]',
                            '.listing-item a[href*="/listings/detail/"]',
                            '.property-item a[href*="/listings/detail/"]',
                            '[data-listing-id] a[href*="/listings/detail/"]'
                        ];
                        
                        selectors.forEach(selector => {
                            document.querySelectorAll(selector).forEach(link => {
                                if (link.href && link.href.includes('/listings/detail/')) {
                                    links.push(link.href);
                                }
                            });
                        });
                        
                        // If no detail links found, try broader search but filter out application links
                        if (links.length === 0) {
                            document.querySelectorAll('a[href*="/listings/"]').forEach(link => {
                                if (link.href && 
                                    link.href.includes('/listings/') && 
                                    !link.href.includes('/apply/') &&
                                    !link.href.includes('/rental_applications/') &&
                                    !link.href.includes('/start?') &&
                                    link.href.includes('/detail/')) {
                                    links.push(link.href);
                                }
                            });
                        }
                        
                        return [...new Set(links)]; // Remove duplicates
                    }
                """)
                
                print(f"Found {len(property_links)} property links")
                
                # Scrape each property
                properties = []
                for i, link in enumerate(property_links[:10]):  # Limit to 10 for demo
                    print(f"Scraping property {i+1}/{min(10, len(property_links))}: {link}")
                    try:
                        property_data = await self.scrape_property_detail(page, link)
                        if property_data:
                            properties.append(property_data)
                        await asyncio.sleep(1)  # Be respectful to the server
                    except Exception as e:
                        print(f"Error scraping property {link}: {e}")
                        continue
                
                await browser.close()
                return properties
                
            except Exception as e:
                print(f"Error during scraping: {e}")
                await browser.close()
                return []
    
    async def scrape_property_detail(self, page, property_url: str) -> Optional[Dict]:
        """Scrape detailed information for a single property"""
        try:
            print(f"  Loading page: {property_url}")
            await page.goto(property_url, wait_until='networkidle')
            
            # Wait a bit for dynamic content to load
            await page.wait_for_timeout(2000)
            
            # Extract property data using multiple strategies
            property_data = await page.evaluate("""
                () => {
                    const data = {
                        url: window.location.href,
                        scraped_at: new Date().toISOString()
                    };
                    
                    // Try to extract title
                    const titleSelectors = [
                        'h1.property-title',
                        'h1.listing-title',
                        '.property-header h1',
                        '.listing-header h1',
                        'h1',
                        '.property-name',
                        '[data-testid="property-title"]',
                        '.property-title',
                        '.listing-title'
                    ];
                    
                    for (const selector of titleSelectors) {
                        const element = document.querySelector(selector);
                        if (element && element.textContent && element.textContent.trim()) {
                            data.title = element.textContent.trim();
                            break;
                        }
                    }
                    
                    // If no title found, try to extract from page title or meta
                    if (!data.title) {
                        const pageTitle = document.title;
                        if (pageTitle && !pageTitle.includes('AppFolio')) {
                            data.title = pageTitle;
                        }
                    }
                    
                    // Try to extract price
                    const priceSelectors = [
                        '.price',
                        '.rent-price',
                        '.monthly-rent',
                        '.property-price',
                        '[class*="price"]',
                        '[class*="rent"]',
                        '[data-testid*="price"]',
                        '.rent-amount',
                        '.listing-price'
                    ];
                    
                    for (const selector of priceSelectors) {
                        const element = document.querySelector(selector);
                        if (element && element.textContent && element.textContent.trim()) {
                            const priceText = element.textContent.trim();
                            const priceMatch = priceText.match(/\\$?([\\d,]+)/);
                            if (priceMatch) {
                                data.price = priceMatch[1].replace(',', '');
                                data.price_display = priceText;
                                break;
                            }
                        }
                    }
                    
                    // Also search in the entire page text for price patterns
                    if (!data.price || data.price.length < 3) {
                        const bodyText = document.body.textContent;
                        const pricePatterns = [
                            /\\$([\\d,]+)\\s*\\/\\s*month/i,
                            /\\$([\\d,]+)\\s*per\\s*month/i,
                            /rent:\\s*\\$([\\d,]+)/i,
                            /\\$([\\d,]+)\\s*monthly/i,
                            /\\$([\\d,]+)\\s*mo/i
                        ];
                        
                        for (const pattern of pricePatterns) {
                            const match = bodyText.match(pattern);
                            if (match) {
                                data.price = match[1].replace(',', '');
                                data.price_display = '$' + match[1] + '/month';
                                break;
                            }
                        }
                    }
                    
                    // If still no good price, try to extract from price_display
                    if ((!data.price || data.price.length < 3) && data.price_display) {
                        const priceMatch = data.price_display.match(/\\$([\\d,]+)/);
                        if (priceMatch) {
                            data.price = priceMatch[1].replace(',', '');
                        }
                    }
                    
                    // Try to extract address
                    const addressSelectors = [
                        '.address',
                        '.property-address',
                        '.listing-address',
                        '[class*="address"]',
                        '[data-testid*="address"]',
                        '.property-location',
                        '.listing-location'
                    ];
                    
                    for (const selector of addressSelectors) {
                        const element = document.querySelector(selector);
                        if (element && element.textContent && element.textContent.trim()) {
                            data.address = element.textContent.trim();
                            break;
                        }
                    }
                    
                    // If no address found, try to extract from page content
                    if (!data.address) {
                        const bodyText = document.body.textContent;
                        // Look for address patterns
                        const addressPatterns = [
                            /([\\d]+\\s+[\\w\\s]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd|Way|Place|Pl|Court|Ct|Circle|Cir|Athens, GA))/i,
                            /([\\d]+\\s+[\\w\\s]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd|Way|Place|Pl|Court|Ct|Circle|Cir))/i
                        ];
                        
                        for (const pattern of addressPatterns) {
                            const match = bodyText.match(pattern);
                            if (match) {
                                data.address = match[1].trim();
                                break;
                            }
                        }
                    }
                    
                    // Try to extract description
                    const descSelectors = [
                        '.description',
                        '.property-description',
                        '.listing-description',
                        '[class*="description"]',
                        '.property-details p'
                    ];
                    
                    for (const selector of descSelectors) {
                        const element = document.querySelector(selector);
                        if (element && element.textContent.trim()) {
                            data.description = element.textContent.trim();
                            break;
                        }
                    }
                    
                    // Try to extract images
                    const images = [];
                    const imgSelectors = [
                        '.property-images img',
                        '.listing-images img',
                        '.gallery img',
                        '[class*="image"] img',
                        '.property-photos img',
                        '.carousel img',
                        '.slider img',
                        '[data-testid*="image"] img',
                        '.photo-gallery img'
                    ];
                    
                    for (const selector of imgSelectors) {
                        document.querySelectorAll(selector).forEach(img => {
                            if (img && img.src && !img.src.includes('data:') && !img.src.includes('placeholder')) {
                                // Convert relative URLs to absolute
                                const imgUrl = img.src.startsWith('http') ? img.src : new URL(img.src, window.location.href).href;
                                images.push(imgUrl);
                            }
                        });
                    }
                    
                    // Also try to extract from background images
                    document.querySelectorAll('[style*="background-image"]').forEach(element => {
                        const style = element.style.backgroundImage;
                        if (style && style.includes('url(')) {
                            const match = style.match(/url\\(["']?([^"']+)["']?\\)/);
                            if (match && match[1]) {
                                const imgUrl = match[1].startsWith('http') ? match[1] : new URL(match[1], window.location.href).href;
                                if (!imgUrl.includes('placeholder')) {
                                    images.push(imgUrl);
                                }
                            }
                        }
                    });
                    
                    data.images = [...new Set(images)]; // Remove duplicates
                    
                    // Try to extract property details
                    const details = {};
                    const detailSelectors = [
                        '.property-details li',
                        '.listing-details li',
                        '.amenities li',
                        '[class*="detail"] li'
                    ];
                    
                    for (const selector of detailSelectors) {
                        document.querySelectorAll(selector).forEach(li => {
                            if (li && li.textContent) {
                                const text = li.textContent.trim();
                                if (text && text.includes(':')) {
                                    const parts = text.split(':', 1);
                                    if (parts.length >= 2) {
                                        const key = parts[0] ? parts[0].trim().toLowerCase() : '';
                                        const value = parts[1] ? parts[1].trim() : '';
                                        if (key && value) {
                                            details[key] = value;
                                        }
                                    }
                                }
                            }
                        });
                    }
                    
                    data.details = details;
                    
                    // Try to extract bedrooms, bathrooms, square footage
                    const text = document.body.textContent;
                    
                    // Look for bedroom count in common patterns
                    const bedroomPatterns = [
                        /(\\d+)\\s*(?:bed|bedroom|br)\\s*\\/\\s*(?:\\d+(?:\\.\\d+)?)\\s*(?:bath|bathroom|ba)/i,
                        /(\\d+)\\s*(?:bed|bedroom|br)/i
                    ];
                    
                    for (const pattern of bedroomPatterns) {
                        const match = text.match(pattern);
                        if (match) {
                            data.bedrooms = match[1];
                            break;
                        }
                    }
                    
                    // Look for bathroom count in common patterns
                    const bathroomPatterns = [
                        /(\\d+(?:\\.\\d+)?)\\s*(?:bath|bathroom|ba)\\s*\\/\\s*(?:\\d+)\\s*(?:bed|bedroom|br)/i,
                        /(\\d+(?:\\.\\d+)?)\\s*(?:bath|bathroom|ba)/i
                    ];
                    
                    for (const pattern of bathroomPatterns) {
                        const match = text.match(pattern);
                        if (match) {
                            data.bathrooms = match[1];
                            break;
                        }
                    }
                    
                    // Look for square footage
                    const sqftPatterns = [
                        /(\\d+(?:,\\d+)?)\\s*(?:sq\\.?\\s*ft|square\\s*feet)/i,
                        /(\\d+(?:,\\d+)?)\\s*sqft/i
                    ];
                    
                    for (const pattern of sqftPatterns) {
                        const match = text.match(pattern);
                        if (match) {
                            data.square_feet = match[1].replace(',', '');
                            break;
                        }
                    }
                    
                    return data;
                }
            """)
            
            # Clean and validate the data
            if not property_data.get('title'):
                property_data['title'] = f"Property at {property_data.get('address', 'Unknown Location')}"
            
            if not property_data.get('address'):
                # Try to extract from title or URL
                title = property_data.get('title', '')
                if 'at' in title.lower():
                    property_data['address'] = title.split('at', 1)[1].strip()
                else:
                    property_data['address'] = "Athens, GA"
            
            # Debug output
            print(f"    Extracted: {property_data.get('title', 'No title')[:50]}...")
            print(f"    Price: {property_data.get('price', 'No price')}")
            print(f"    Address: {property_data.get('address', 'No address')[:50]}...")
            print(f"    Images: {len(property_data.get('images', []))}")
            
            return property_data
            
        except Exception as e:
            print(f"Error scraping property detail {property_url}: {e}")
            return None
    
    def save_to_json(self, properties: List[Dict], filename: str = "appfolio_properties.json"):
        """Save scraped properties to JSON file"""
        filepath = os.path.join(os.path.dirname(__file__), filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(properties, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(properties)} properties to {filepath}")
        return filepath


async def main():
    """Main function to run the scraper"""
    scraper = AppFolioScraper()
    properties = await scraper.scrape_listings()
    
    if properties:
        print(f"Successfully scraped {len(properties)} properties")
        scraper.save_to_json(properties)
        
        # Print sample data
        print("\nSample property data:")
        for i, prop in enumerate(properties[:2]):
            print(f"\nProperty {i+1}:")
            for key, value in prop.items():
                if key != 'images':  # Don't print all images
                    print(f"  {key}: {value}")
            if prop.get('images'):
                print(f"  images: {len(prop['images'])} found")
    else:
        print("No properties were scraped")


if __name__ == "__main__":
    asyncio.run(main())
