#!/usr/bin/env python3
"""
AppFolio Property Scheduler
Automated scheduling system for property data updates
"""

import schedule
import time
import asyncio
import logging
import threading
from datetime import datetime
from appfolio_scraper import AppFolioScraper
from wordpress_json_export import export_to_wordpress_json
from api_server import app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('appfolio_scheduler.log'),
        logging.StreamHandler()
    ]
)

class PropertyScheduler:
    def __init__(self):
        self.scraper = AppFolioScraper()
        self.last_update = None
        
    async def update_properties(self):
        """Main update function that scrapes and imports properties"""
        try:
            logging.info("Starting scheduled property update...")
            
            # Scrape properties
            properties = await self.scraper.scrape_listings()
            
            if properties:
                # Save to JSON (original format)
                json_file = self.scraper.save_to_json(properties)
                
                # Export to WordPress-compatible format
                wp_json_file = export_to_wordpress_json(properties, "wordpress_properties.json")
                
                self.last_update = datetime.now()
                logging.info(f"Successfully updated {len(properties)} properties at {self.last_update}")
                logging.info(f"Properties JSON saved to: {json_file}")
                logging.info(f"WordPress JSON saved to: {wp_json_file}")
                logging.info("Properties are now available via API at /api/properties")
            else:
                logging.warning("No properties were scraped in this update")
                
        except Exception as e:
            logging.error(f"Error during property update: {e}")
    
    def run_update(self):
        """Synchronous wrapper for the async update function"""
        asyncio.run(self.update_properties())
    
    def start_scheduler(self):
        """Start the scheduling system"""
        logging.info("Starting AppFolio Property Scheduler...")
        
        # Schedule updates every 4 hours
        schedule.every(4).hours.do(self.run_update)
        
        # Schedule daily update at 6 AM
        schedule.every().day.at("06:00").do(self.run_update)
        
        # Run initial update
        logging.info("Running initial property update...")
        self.run_update()
        
        # Keep the scheduler running
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute


def start_api_server():
    """Start the Flask API server in a separate thread"""
    import os
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)


def main():
    import os
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    
    # Initialize scheduler
    scheduler = PropertyScheduler()
    
    # Start API server in a separate thread
    api_thread = threading.Thread(target=start_api_server, daemon=True)
    api_thread.start()
    logging.info("API server started in background thread")
    
    try:
        scheduler.start_scheduler()
    except KeyboardInterrupt:
        logging.info("Scheduler stopped by user")
    except Exception as e:
        logging.error(f"Scheduler error: {e}")


if __name__ == "__main__":
    main()
