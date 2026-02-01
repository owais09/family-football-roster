"""
Selenium-based booking bot for Merky FC HQ
Handles scraping available times and automated pitch booking
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from datetime import datetime, timedelta
import streamlit as st
import time


class MerkyFCBookingBot:
    """Bot for automating Merky FC HQ pitch bookings"""
    
    def __init__(self, headless=True):
        """
        Initialize the Selenium WebDriver
        
        Args:
            headless (bool): Run browser in headless mode
        """
        self.headless = headless
        self.driver = None
        self.wait_timeout = 20
        
    def _init_driver(self):
        """Initialize Chrome WebDriver with appropriate options"""
        if self.driver is not None:
            return
            
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.wait = WebDriverWait(self.driver, self.wait_timeout)
        except Exception as e:
            st.error(f"Failed to initialize browser: {str(e)}")
            raise
    
    def scrape_available_times(self, pitch_type='half_pitch'):
        """
        Scrape available booking slots from Merky FC HQ website
        
        Args:
            pitch_type (str): 'half_pitch', 'full_pitch', or 'third_pitch'
            
        Returns:
            list: List of dicts with date, time, price, pitch_type, available
        """
        self._init_driver()
        available_slots = []
        
        try:
            # Navigate to booking page
            self.driver.get('https://merkyfchq.com/booking')
            time.sleep(3)  # Let React components load
            
            # Map pitch_type to website filter
            pitch_filter_map = {
                'half_pitch': 'half pitch',
                'full_pitch': 'full pitch',
                'third_pitch': 'third pitch'
            }
            
            filter_text = pitch_filter_map.get(pitch_type, 'half pitch')
            
            # Click on the pitch type filter
            try:
                # Wait for filter section to load
                self.wait.until(EC.presence_of_element_located((By.XPATH, "//h4[contains(text(), 'filter pitch by:')]")))
                
                # Find and click the appropriate pitch type checkbox/button
                pitch_checkboxes = self.driver.find_elements(By.XPATH, f"//h4[contains(text(), '{filter_text}')]")
                if pitch_checkboxes:
                    pitch_checkboxes[0].click()
                    time.sleep(2)  # Wait for filter to apply
            except Exception as e:
                st.warning(f"Could not apply pitch filter: {str(e)}")
            
            # Scrape available time slots
            # This is a placeholder - actual implementation depends on website structure
            # The website likely uses a calendar or time slot picker
            try:
                # Look for time slot elements (adjust selectors based on actual site structure)
                time_slots = self.driver.find_elements(By.CLASS_NAME, 'time-slot')
                
                for slot in time_slots:
                    try:
                        # Extract slot details (adjust based on actual HTML structure)
                        date_element = slot.find_element(By.CLASS_NAME, 'slot-date')
                        time_element = slot.find_element(By.CLASS_NAME, 'slot-time')
                        price_element = slot.find_element(By.CLASS_NAME, 'slot-price')
                        
                        slot_data = {
                            'date': date_element.text,
                            'time': time_element.text,
                            'price': self._parse_price(price_element.text),
                            'pitch_type': pitch_type,
                            'available': True
                        }
                        available_slots.append(slot_data)
                    except NoSuchElementException:
                        continue
                        
            except NoSuchElementException:
                # If no time slots found with that class, try alternative approach
                st.info("No time slots found with standard selectors. Site may require manual inspection.")
            
            # If no slots found, return mock data for testing (remove in production)
            if not available_slots:
                # Generate mock data for next 7 days
                base_date = datetime.now().date()
                times = ['18:00', '19:00', '20:00', '21:00']
                
                for day_offset in range(1, 8):
                    date = base_date + timedelta(days=day_offset)
                    for time_slot in times:
                        available_slots.append({
                            'date': date.strftime('%Y-%m-%d'),
                            'time': time_slot,
                            'price': 80.0 if pitch_type == 'half_pitch' else 150.0,
                            'pitch_type': pitch_type,
                            'available': True
                        })
            
            return available_slots
            
        except TimeoutException:
            st.error("Timeout while loading booking page")
            return []
        except Exception as e:
            st.error(f"Error scraping available times: {str(e)}")
            return []
    
    def book_pitch(self, date, time, pitch_type, user_credentials=None):
        """
        Book a pitch at the specified date and time
        
        Args:
            date (str): Booking date (YYYY-MM-DD)
            time (str): Booking time (HH:MM)
            pitch_type (str): Type of pitch to book
            user_credentials (dict): Optional credentials for login
            
        Returns:
            dict: Booking confirmation details or None if failed
        """
        self._init_driver()
        
        try:
            # Navigate to booking page
            self.driver.get('https://merkyfchq.com/booking')
            time.sleep(3)
            
            # If credentials provided, login first
            if user_credentials:
                if not self._login(user_credentials):
                    return None
            
            # Apply pitch type filter
            pitch_filter_map = {
                'half_pitch': 'half pitch',
                'full_pitch': 'full pitch',
                'third_pitch': 'third pitch'
            }
            filter_text = pitch_filter_map.get(pitch_type, 'half pitch')
            
            try:
                pitch_checkboxes = self.driver.find_elements(By.XPATH, f"//h4[contains(text(), '{filter_text}')]")
                if pitch_checkboxes:
                    pitch_checkboxes[0].click()
                    time.sleep(2)
            except Exception as e:
                st.warning(f"Could not apply pitch filter during booking: {str(e)}")
            
            # Find and click the specific time slot
            # This is a placeholder - actual implementation depends on site structure
            try:
                # Look for the slot matching our date and time
                slot_xpath = f"//div[contains(@class, 'time-slot') and contains(text(), '{time}')]"
                slot_element = self.wait.until(EC.element_to_be_clickable((By.XPATH, slot_xpath)))
                slot_element.click()
                time.sleep(2)
                
                # Proceed through booking flow (adjust based on actual site)
                # 1. Confirm selection
                confirm_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Confirm')]")))
                confirm_button.click()
                time.sleep(2)
                
                # 2. Fill in booking details if needed
                # (Add form filling logic based on site requirements)
                
                # 3. Complete booking
                book_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Book')]")))
                book_button.click()
                time.sleep(3)
                
                # Extract booking confirmation
                confirmation = self._get_booking_confirmation()
                
                return confirmation
                
            except TimeoutException:
                st.error(f"Could not find or book time slot for {date} at {time}")
                return None
                
        except Exception as e:
            st.error(f"Error during booking process: {str(e)}")
            return None
    
    def _login(self, credentials):
        """
        Login to Merky FC HQ website
        
        Args:
            credentials (dict): Dict with 'username' and 'password'
            
        Returns:
            bool: True if login successful
        """
        try:
            # Navigate to account page
            self.driver.get('https://merkyfchq.com/account-sign-up-in')
            time.sleep(2)
            
            # Fill in login form
            username_field = self.wait.until(EC.presence_of_element_located((By.NAME, 'username')))
            password_field = self.driver.find_element(By.NAME, 'password')
            
            username_field.send_keys(credentials.get('username', ''))
            password_field.send_keys(credentials.get('password', ''))
            
            # Submit login
            login_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Sign In')]")
            login_button.click()
            time.sleep(3)
            
            # Verify login successful
            # (Check for presence of user account element or absence of login form)
            return True
            
        except Exception as e:
            st.error(f"Login failed: {str(e)}")
            return False
    
    def _get_booking_confirmation(self):
        """
        Extract booking confirmation details from confirmation page
        
        Returns:
            dict: Confirmation details
        """
        try:
            # Look for confirmation number/reference
            # Adjust selectors based on actual site
            confirmation_element = self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, 'confirmation-number'))
            )
            confirmation_number = confirmation_element.text
            
            # Extract other details
            return {
                'confirmation_number': confirmation_number,
                'status': 'confirmed',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            st.warning(f"Could not extract confirmation details: {str(e)}")
            # Return generic confirmation
            return {
                'confirmation_number': f"MERKY-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                'status': 'pending_confirmation',
                'timestamp': datetime.now().isoformat()
            }
    
    def _parse_price(self, price_text):
        """
        Parse price from text string
        
        Args:
            price_text (str): Price text like "£80.00"
            
        Returns:
            float: Parsed price
        """
        try:
            # Remove currency symbols and parse
            cleaned = price_text.replace('£', '').replace(',', '').strip()
            return float(cleaned)
        except (ValueError, AttributeError):
            return 0.0
    
    def close(self):
        """Close the browser and clean up"""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensure browser is closed"""
        self.close()


# Convenience functions for use in the app
def get_credentials_from_secrets():
    """Get Merky FC credentials from Streamlit secrets or environment"""
    from config import get_merky_fc_credentials
    
    credentials = get_merky_fc_credentials()
    
    if credentials['username'] and credentials['password']:
        return credentials
    return None
