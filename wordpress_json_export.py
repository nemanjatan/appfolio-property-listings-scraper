#!/usr/bin/env python3
"""
WordPress JSON Export
Converts scraped AppFolio properties to WordPress-compatible JSON format
"""

import json
import os
from typing import List, Dict


def export_to_wordpress_json(properties: List[Dict], output_file: str = "wordpress_properties.json"):
    """
    Convert scraped properties to WordPress-compatible JSON format
    
    Args:
        properties: List of scraped property dictionaries
        output_file: Output JSON file path
    
    Returns:
        str: Path to the created JSON file
    """
    wp_properties = []
    
    for i, prop in enumerate(properties, start=1):
        # Clean title - remove extra whitespace and MAP text
        title = prop.get('title', '')
        if 'MAP' in title:
            title = title.split('MAP')[0].strip()
        
        # Extract and clean address
        address = prop.get('address', '')
        if not address or address == 'Athens, GA':
            # Try to extract from title
            if ',' in title:
                address = title.split(',')[0].strip()
        
        # Get images
        images = prop.get('images', [])
        featured_image = images[0] if images else ''
        
        # Build WordPress property object
        wp_property = {
            'id': i,
            'title': title,
            'content': prop.get('description', ''),
            'excerpt': prop.get('description', '')[:200] + '...' if len(prop.get('description', '')) > 200 else prop.get('description', ''),
            'price': prop.get('price', ''),
            'price_display': prop.get('price_display', f"${prop.get('price', '0')}/month"),
            'address': address,
            'bedrooms': prop.get('bedrooms', ''),
            'bathrooms': prop.get('bathrooms', ''),
            'square_feet': prop.get('square_feet', ''),
            'original_url': prop.get('url', ''),
            'images': images,
            'featured_image': featured_image,
            'scraped_at': prop.get('scraped_at', ''),
            'details': prop.get('details', {})
        }
        
        wp_properties.append(wp_property)
    
    # Save to JSON file
    filepath = os.path.join(os.path.dirname(__file__), output_file)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(wp_properties, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Exported {len(wp_properties)} properties to {filepath}")
    return filepath


def convert_existing_json(input_file: str = "appfolio_properties.json", output_file: str = "wordpress_properties.json"):
    """
    Convert existing AppFolio JSON to WordPress format
    
    Args:
        input_file: Input JSON file path
        output_file: Output JSON file path
    """
    if not os.path.exists(input_file):
        print(f"❌ File not found: {input_file}")
        return
    
    with open(input_file, 'r', encoding='utf-8') as f:
        properties = json.load(f)
    
    export_to_wordpress_json(properties, output_file)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Convert from specified file
        convert_existing_json(sys.argv[1])
    else:
        # Convert from default file
        convert_existing_json()
