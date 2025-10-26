# AppFolio Property API Service

This is a Python backend service that scrapes AppFolio property listings and serves them via a REST API for WordPress consumption.

## 📁 Files

- `appfolio_scraper.py` - Main scraper using Playwright
- `scheduler.py` - Automated scheduling system that runs scraper + API server
- `api_server.py` - Flask REST API server for serving property data
- `wordpress_json_export.py` - Converts data to WordPress format
- `wordpress-plugin-api.php` - WordPress plugin to consume the API
- `test_scraper.py` - Testing utility
- `requirements.txt` - Python dependencies

## 🚀 Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install

# Test the scraper
python test_scraper.py

# Run the scraper
python appfolio_scraper.py

# Run with scheduler
python scheduler.py
```

## 🔧 Configuration

Set environment variables (optional):
- `SCRAPE_INTERVAL_HOURS` - Update frequency (default: 4)
- `MAX_PROPERTIES` - Maximum properties to scrape (default: 100)
- `PORT` - API server port (default: 8000)

## 📊 Output

The scraper creates two JSON files:
- `appfolio_properties.json` - Raw scraped data
- `wordpress_properties.json` - WordPress-compatible format

## 🌐 API Endpoints

Once running, the service exposes these endpoints:

- `GET /api/properties` - Get all properties (supports filters: `min_price`, `max_price`, `bedrooms`, `bathrooms`, `search`)
- `GET /api/properties/<id>` - Get a single property by ID
- `GET /api/health` - Health check endpoint

**Example API calls:**
- All properties: `https://your-api.up.railway.app/api/properties`
- Filtered: `https://your-api.up.railway.app/api/properties?min_price=1000&max_price=2000&bedrooms=2`
- Search: `https://your-api.up.railway.app/api/properties?search=athens`

## 🌐 Railway Deployment

This service is designed to run on Railway.app:

1. Deploy from GitHub
2. **Important**: Railway will automatically detect the Dockerfile and use it
3. **DO NOT** set a Custom Build Command (leave it empty/default)
4. Set Custom Start Command to: `python scheduler.py` (or leave empty to use Dockerfile CMD)
5. Deploy!

See `/RAILWAY_DEPLOYMENT.md` for detailed instructions.

## 🔌 WordPress Integration

1. Install the WordPress plugin (`wordpress-plugin-api.php`) in your WordPress site
2. Go to **Settings → AppFolio API** in WordPress admin
3. Enter your Railway API URL (e.g., `https://your-app.up.railway.app`)
4. Add the shortcode `[appfolio_properties]` to any page or post
5. Optionally add filters: `[appfolio_properties bedrooms="2" min_price="1000"]`
