# Architecture Overview

## 🏗️ New API-First Architecture

This project now uses a **clean separation of concerns** where WordPress pulls data from the Python API instead of Python pushing to WordPress.

## 📊 How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                     Python Service                           │
│  (Deployed on Railway.app)                                   │
│                                                              │
│  ┌──────────────┐      ┌──────────────┐                   │
│  │   Scraper    │ ───> │   API Server │                   │
│  │   (Playwright)│      │   (Flask)    │                   │
│  └──────────────┘      └──────────────┘                   │
│         │                      │                            │
│         │                      │                            │
│         └────────┬─────────────┘                            │
│                  │                                           │
│                  ▼                                           │
│         Saves to JSON files                                 │
│         - appfolio_properties.json                          │
│         - wordpress_properties.json                         │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           │ REST API (HTTPS)
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  WordPress Site                             │
│  (Any hosting - Railway, Bluehost, etc.)                    │
│                                                              │
│  ┌──────────────────────────────────────┐                  │
│  │   AppFolio Properties Plugin         │                  │
│  │   - Calls API endpoint                │                  │
│  │   - Displays properties               │                  │
│  │   - Supports filters                   │                  │
│  └──────────────────────────────────────┘                  │
└─────────────────────────────────────────────────────────────┘
```

## ✅ Benefits of This Architecture

### 1. **Separation of Concerns**
- Python service only scrapes and serves data
- WordPress only displays data
- No WordPress credentials needed in Python service

### 2. **Scalability**
- Multiple WordPress sites can consume the same API
- API can be cached and rate-limited independently
- Easier to scale horizontally

### 3. **Reliability**
- If WordPress is down, scraper continues working
- If scraper is down, WordPress can still display cached data
- Each service can be updated independently

### 4. **Flexibility**
- WordPress decides when to fetch new data
- Can implement caching strategies in WordPress
- Easy to add other consumers (mobile app, another website, etc.)

### 5. **Security**
- No direct database access from Python
- WordPress credentials not stored in Python service
- API can be secured with authentication if needed

## 🔄 Data Flow

### Step 1: Scraping
- `scheduler.py` runs the scraper every 4 hours
- `appfolio_scraper.py` uses Playwright to scrape properties
- Data is saved to JSON files

### Step 2: API Server
- Flask API server runs continuously
- Serves data from JSON files via REST endpoints
- Supports filtering and search

### Step 3: WordPress Consumption
- WordPress plugin calls the API
- Displays properties using shortcode
- Can filter by price, bedrooms, bathrooms, search term

## 📡 API Endpoints

### `GET /api/properties`
Get all properties with optional filters.

**Query Parameters:**
- `min_price` - Minimum rent price
- `max_price` - Maximum rent price
- `bedrooms` - Number of bedrooms
- `bathrooms` - Number of bathrooms
- `search` - Search term (searches title, address, description)

**Example:**
```
GET /api/properties?min_price=1000&max_price=2000&bedrooms=2
```

**Response:**
```json
{
  "success": true,
  "count": 15,
  "total": 50,
  "data": [
    {
      "id": 1,
      "title": "Beautiful 2BR Apartment",
      "address": "123 Main St, Athens, GA",
      "price": "1500",
      "bedrooms": "2",
      "bathrooms": "1.5",
      "square_feet": "1200",
      "images": ["url1", "url2"],
      "featured_image": "url1",
      "original_url": "https://..."
    }
  ],
  "timestamp": "2025-01-26T10:00:00"
}
```

### `GET /api/properties/<id>`
Get a single property by ID.

### `GET /api/health`
Health check endpoint.

## 🔌 WordPress Integration

### Installation
1. Upload `wordpress-plugin-api.php` to `/wp-content/plugins/appfolio-properties/`
2. Upload `wordpress-plugin-assets/style.css` to the same directory
3. Activate the plugin in WordPress admin

### Configuration
1. Go to **Settings → AppFolio API**
2. Enter your Railway API URL: `https://your-app.up.railway.app`
3. Save settings

### Usage
Add the shortcode to any page or post:

```php
[appfolio_properties]
```

With filters:
```php
[appfolio_properties bedrooms="2" min_price="1000" max_price="2000"]
```

With search:
```php
[appfolio_properties search="athens"]
```

## 🚀 Deployment

### Python Service (Railway)
1. Deploy from GitHub
2. Railway detects Dockerfile automatically
3. Service starts scraper + API server
4. API available at `https://your-app.up.railway.app`

### WordPress Plugin
1. Install plugin on WordPress site
2. Configure API URL
3. Add shortcode to pages

## 🔧 Environment Variables

**Python Service:**
- `SCRAPE_INTERVAL_HOURS` - How often to scrape (default: 4)
- `MAX_PROPERTIES` - Max properties to scrape (default: 100)
- `PORT` - API server port (default: 8000)

**WordPress:**
- Configured via admin panel (stored in database)

## 📝 Migration Notes

### If you were using the old architecture:
1. Remove WordPress credentials from Python service
2. WordPress will no longer receive direct pushes
3. WordPress now pulls data from API on each page load
4. Add caching plugin to WordPress for better performance

### Recommended WordPress Caching:
- Install a caching plugin (WP Super Cache, W3 Total Cache)
- Cache API responses for 5-15 minutes
- Reduces API calls and improves page load speed

