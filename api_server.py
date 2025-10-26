#!/usr/bin/env python3
"""
AppFolio Property API Server
Serves scraped property data via REST API for WordPress consumption
"""

import os
import json
import logging
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)
CORS(app)  # Enable CORS for WordPress access

# Default paths for property data
WP_PROPERTIES_FILE = "wordpress_properties.json"
APPFOLIO_PROPERTIES_FILE = "appfolio_properties.json"


def load_properties():
    """Load properties from JSON file"""
    # Try WordPress format first
    if os.path.exists(WP_PROPERTIES_FILE):
        with open(WP_PROPERTIES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    # Fallback to raw AppFolio format
    if os.path.exists(APPFOLIO_PROPERTIES_FILE):
        with open(APPFOLIO_PROPERTIES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    return []


@app.route('/api/properties', methods=['GET'])
def get_properties():
    """Get all properties"""
    try:
        properties = load_properties()
        
        # Support filtering via query parameters
        filters = {}
        
        # Price range filter
        min_price = request.args.get('min_price', type=int)
        max_price = request.args.get('max_price', type=int)
        
        # Bedrooms filter
        bedrooms = request.args.get('bedrooms', type=int)
        
        # Bathrooms filter
        bathrooms = request.args.get('bathrooms', type=float)
        
        # Search filter
        search = request.args.get('search', type=str)
        
        # Apply filters
        filtered_properties = properties
        if min_price is not None:
            filtered_properties = [p for p in filtered_properties if int(p.get('price', 0)) >= min_price]
        if max_price is not None:
            filtered_properties = [p for p in filtered_properties if int(p.get('price', 0)) <= max_price]
        if bedrooms is not None:
            filtered_properties = [p for p in filtered_properties if p.get('bedrooms') == str(bedrooms)]
        if bathrooms is not None:
            filtered_properties = [p for p in filtered_properties if float(p.get('bathrooms', 0)) >= bathrooms]
        if search:
            search_lower = search.lower()
            filtered_properties = [
                p for p in filtered_properties
                if search_lower in p.get('title', '').lower() or
                   search_lower in p.get('address', '').lower() or
                   search_lower in p.get('description', '').lower()
            ]
        
        return jsonify({
            'success': True,
            'count': len(filtered_properties),
            'total': len(properties),
            'data': filtered_properties,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logging.error(f"Error loading properties: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/properties/<int:property_id>', methods=['GET'])
def get_property(property_id):
    """Get a single property by ID"""
    try:
        properties = load_properties()
        
        # Find property by ID
        property_data = next((p for p in properties if p.get('id') == property_id), None)
        
        if property_data:
            return jsonify({
                'success': True,
                'data': property_data
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Property not found'
            }), 404
    
    except Exception as e:
        logging.error(f"Error loading property: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    properties = load_properties()
    return jsonify({
        'status': 'healthy',
        'properties_count': len(properties),
        'timestamp': datetime.now().isoformat()
    })


@app.route('/', methods=['GET'])
def index():
    """API documentation"""
    return jsonify({
        'name': 'AppFolio Property API',
        'version': '1.0.0',
        'endpoints': {
            'GET /api/properties': 'Get all properties (supports filters: min_price, max_price, bedrooms, bathrooms, search)',
            'GET /api/properties/<id>': 'Get a single property by ID',
            'GET /api/health': 'Health check endpoint'
        },
        'example_usage': {
            'all_properties': '/api/properties',
            'filtered_properties': '/api/properties?min_price=1000&max_price=2000&bedrooms=2',
            'search': '/api/properties?search=athens'
        }
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    logging.info(f"Starting AppFolio Property API Server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)

