#!/usr/bin/env python3
"""
AppFolio Property Scheduler
Automated scheduling system for property data updates
"""

import schedule
import time
import asyncio
import logging
from datetime import datetime
from appfolio_scraper import AppFolioScraper
from import_to_wordpress import WordPressImporter
from wordpress_json_export import export_to_wordpress_json

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
    def __init__(self, wp_url: str, wp_username: str, wp_password: str):
        self.scraper = AppFolioScraper()
        self.importer = WordPressImporter(wp_url, wp_username, wp_password)
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
                
                # Import to WordPress (if WordPress URL is configured)
                try:
                    self.importer.import_properties(json_file)
                except Exception as e:
                    logging.warning(f"WordPress import failed (may be intentional): {e}")
                
                self.last_update = datetime.now()
                logging.info(f"Successfully updated {len(properties)} properties at {self.last_update}")
                logging.info(f"WordPress JSON saved to: {wp_json_file}")
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


def main():
    import os
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    
    # Configuration - Get from environment variables
    wp_url = os.getenv('WP_URL', 'https://farmersathens.com')
    wp_username = os.getenv('WP_USERNAME', 'admin')
    wp_password = os.getenv('WP_PASSWORD', 'password')
    
    logging.info(f"Configuration loaded - WP_URL: {wp_url}")
    
    # Initialize and start scheduler
    scheduler = PropertyScheduler(wp_url, wp_username, wp_password)
    
    try:
        scheduler.start_scheduler()
    except KeyboardInterrupt:
        logging.info("Scheduler stopped by user")
    except Exception as e:
        logging.error(f"Scheduler error: {e}")


if __name__ == "__main__":
    main()
