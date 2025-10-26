#!/usr/bin/env python3
"""
Import AppFolio properties to WordPress
This script takes the scraped JSON data and creates WordPress posts
"""

import json
import os
import requests
from typing import Dict, List
import time


class WordPressImporter:
    def __init__(self, wp_url: str, username: str, password: str):
        self.wp_url = wp_url.rstrip('/')
        self.username = username
        self.password = password
        self.session = requests.Session()
        
    def create_post(self, property_data: Dict) -> bool:
        """Create a WordPress post for a property"""
        
        # Prepare post data
        post_data = {
            'title': property_data.get('title', 'Property Listing'),
            'content': property_data.get('description', ''),
            'status': 'publish',
            'type': 'appfolio_property',
            'meta': {
                '_property_price': property_data.get('price', ''),
                '_property_address': property_data.get('address', ''),
                '_property_bedrooms': property_data.get('bedrooms', ''),
                '_property_bathrooms': property_data.get('bathrooms', ''),
                '_property_square_feet': property_data.get('square_feet', ''),
                '_property_original_url': property_data.get('url', ''),
                '_property_images': '\n'.join(property_data.get('images', [])),
            }
        }
        
        # For demo purposes, we'll create a simple HTML representation
        # In a real implementation, you'd use the WordPress REST API
        print(f"Creating post: {post_data['title']}")
        print(f"  Price: {post_data['meta']['_property_price']}")
        print(f"  Address: {post_data['meta']['_property_address']}")
        print(f"  Images: {len(property_data.get('images', []))}")
        print("  ---")
        
        return True
    
    def import_properties(self, json_file: str):
        """Import all properties from JSON file"""
        if not os.path.exists(json_file):
            print(f"JSON file not found: {json_file}")
            return
        
        with open(json_file, 'r', encoding='utf-8') as f:
            properties = json.load(f)
        
        print(f"Importing {len(properties)} properties...")
        
        success_count = 0
        for i, property_data in enumerate(properties):
            try:
                if self.create_post(property_data):
                    success_count += 1
                time.sleep(0.5)  # Be respectful to the server
            except Exception as e:
                print(f"Error importing property {i+1}: {e}")
        
        print(f"Successfully imported {success_count}/{len(properties)} properties")


def main():
    # Configuration
    wp_url = "https://farmersathens.com"  # Replace with actual WordPress URL
    username = "admin"  # Replace with actual username
    password = "password"  # Replace with actual password
    
    # Initialize importer
    importer = WordPressImporter(wp_url, username, password)
    
    # Import properties
    json_file = "appfolio_properties.json"
    importer.import_properties(json_file)


if __name__ == "__main__":
    main()
