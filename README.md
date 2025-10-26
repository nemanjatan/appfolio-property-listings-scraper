# Python Scraper Service

This is the Python backend service that scrapes AppFolio property listings and prepares them for WordPress.

## 📁 Files

- `appfolio_scraper.py` - Main scraper using Playwright
- `scheduler.py` - Automated scheduling system
- `import_to_wordpress.py` - WordPress integration utility
- `wordpress_json_export.py` - Converts data to WordPress format
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

Set environment variables:
- `WP_URL` - WordPress site URL
- `WP_USERNAME` - WordPress admin username
- `WP_PASSWORD` - WordPress admin password
- `SCRAPE_INTERVAL_HOURS` - Update frequency (default: 4)
- `MAX_PROPERTIES` - Maximum properties to scrape (default: 100)

## 📊 Output

The scraper creates two JSON files:
- `appfolio_properties.json` - Raw scraped data
- `wordpress_properties.json` - WordPress-compatible format

## 🌐 Railway Deployment

This service is designed to run on Railway.app:

1. Deploy from GitHub
2. **Important**: Railway will automatically detect the Dockerfile and use it
3. **DO NOT** set a Custom Build Command (leave it empty/default)
4. Set Custom Start Command to: `python scheduler.py` (or leave empty to use Dockerfile CMD)
5. Add environment variables
6. Deploy!

See `/RAILWAY_DEPLOYMENT.md` for detailed instructions.
