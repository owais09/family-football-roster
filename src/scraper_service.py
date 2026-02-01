"""
Background scraper service for periodically updating available pitch times
"""

import schedule
import time
from threading import Thread
from datetime import datetime
from booking_bot import MerkyFCBookingBot
import streamlit as st


class ScraperService:
    """Background service for scraping pitch availability"""
    
    def __init__(self, db, scrape_interval_minutes=5):
        """
        Initialize the scraper service
        
        Args:
            db: DatabaseHandler instance
            scrape_interval_minutes (int): How often to scrape
        """
        self.db = db
        self.scrape_interval = scrape_interval_minutes
        self.running = False
        self.thread = None
        self.last_scrape_time = None
        self.scrape_count = 0
        self.error_count = 0
    
    def update_availability_cache(self):
        """Scrape and cache available slots for all pitch types"""
        try:
            st.info(f"Starting availability scrape at {datetime.now().strftime('%H:%M:%S')}")
            
            with MerkyFCBookingBot(headless=True) as bot:
                # Scrape both pitch types
                for pitch_type in ['half_pitch', 'full_pitch']:
                    try:
                        slots = bot.scrape_available_times(pitch_type)
                        
                        if slots:
                            self.db.cache_available_slots(slots)
                            st.success(f"Cached {len(slots)} slots for {pitch_type}")
                        else:
                            st.warning(f"No slots found for {pitch_type}")
                            
                    except Exception as e:
                        st.error(f"Error scraping {pitch_type}: {str(e)}")
                        self.error_count += 1
            
            self.last_scrape_time = datetime.now()
            self.scrape_count += 1
            
        except Exception as e:
            st.error(f"Scraper error: {str(e)}")
            self.error_count += 1
    
    def start_background_scraper(self):
        """Start the background scraping service"""
        if self.running:
            st.warning("Scraper service already running")
            return
        
        self.running = True
        
        # Schedule scraping every N minutes
        schedule.every(self.scrape_interval).minutes.do(self.update_availability_cache)
        
        # Also run once immediately
        self.update_availability_cache()
        
        def run_scheduler():
            """Run the scheduler in a loop"""
            while self.running:
                schedule.run_pending()
                time.sleep(1)
        
        # Start scheduler in daemon thread
        self.thread = Thread(target=run_scheduler, daemon=True)
        self.thread.start()
        
        st.success(f"Background scraper started (every {self.scrape_interval} minutes)")
    
    def stop_background_scraper(self):
        """Stop the background scraping service"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        st.info("Background scraper stopped")
    
    def get_status(self):
        """Get scraper service status"""
        return {
            'running': self.running,
            'last_scrape': self.last_scrape_time,
            'scrape_count': self.scrape_count,
            'error_count': self.error_count,
            'interval_minutes': self.scrape_interval
        }
    
    def force_update(self):
        """Force an immediate update"""
        if self.running:
            # Cancel pending jobs and reschedule
            schedule.clear()
            schedule.every(self.scrape_interval).minutes.do(self.update_availability_cache)
        
        # Run update now
        self.update_availability_cache()


# Streamlit-specific initialization using cache_resource
@st.cache_resource
def get_scraper_service(_db):
    """
    Get or create the scraper service (singleton pattern)
    
    Args:
        _db: DatabaseHandler instance (underscore prefix to prevent hashing)
        
    Returns:
        ScraperService: The service instance
    """
    service = ScraperService(_db, scrape_interval_minutes=5)
    
    # Auto-start the service
    try:
        service.start_background_scraper()
    except Exception as e:
        st.warning(f"Could not start background scraper: {e}")
    
    return service


# Simple scraper for immediate use (without background thread)
def scrape_now(db, pitch_types=None):
    """
    Immediately scrape and cache available slots
    
    Args:
        db: DatabaseHandler instance
        pitch_types (list): List of pitch types to scrape, or None for all
        
    Returns:
        dict: Results for each pitch type
    """
    if pitch_types is None:
        pitch_types = ['half_pitch', 'full_pitch']
    
    results = {}
    
    try:
        with MerkyFCBookingBot(headless=True) as bot:
            for pitch_type in pitch_types:
                try:
                    slots = bot.scrape_available_times(pitch_type)
                    
                    if slots:
                        db.cache_available_slots(slots)
                        results[pitch_type] = {
                            'success': True,
                            'slot_count': len(slots),
                            'slots': slots
                        }
                    else:
                        results[pitch_type] = {
                            'success': False,
                            'error': 'No slots found'
                        }
                        
                except Exception as e:
                    results[pitch_type] = {
                        'success': False,
                        'error': str(e)
                    }
    except Exception as e:
        st.error(f"Failed to initialize scraper: {e}")
        return None
    
    return results
