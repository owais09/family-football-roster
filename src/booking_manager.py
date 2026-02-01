"""
Booking Manager - Monitors signups and triggers automatic bookings
"""

from datetime import datetime, time, timedelta
from booking_bot import MerkyFCBookingBot, get_credentials_from_secrets
from config import get_booking_config
import streamlit as st


class BookingManager:
    """Manages the automatic booking process based on player signups"""
    
    def __init__(self, db, auto_book_enabled=None):
        """
        Initialize the booking manager
        
        Args:
            db: DatabaseHandler instance
            auto_book_enabled (bool): Enable/disable automatic booking
        """
        self.db = db
        
        # Load configuration from secrets or environment
        booking_config = get_booking_config()
        
        self.auto_book_enabled = auto_book_enabled if auto_book_enabled is not None else booking_config['auto_book_enabled']
        self.thresholds = {
            'half_pitch': booking_config['half_pitch_threshold'],
            'full_pitch': booking_config['full_pitch_threshold']
        }
        self.preferred_time = booking_config['preferred_time']
    
    def check_and_book(self, week):
        """
        Check signup count and trigger booking if threshold reached
        
        NEW LOGIC: 18+ players = 2 third pitches (not 1 full pitch)
        
        Args:
            week (str): Week identifier (e.g., "2026-W05")
            
        Returns:
            dict: Booking confirmation details or None
        """
        if not self.auto_book_enabled:
            return None
        
        # Get current signup count
        signups = self.db.fetch_signups(week)
        count = len(signups)
        
        # Determine booking strategy based on count
        booking_strategy = None
        if count >= self.thresholds['full_pitch']:
            # 18+ players: Book 2 third pitches
            booking_strategy = 'two_thirds'
        elif count >= self.thresholds['half_pitch']:
            # 14+ players: Book 1 third pitch
            booking_strategy = 'one_third'
        else:
            # Not enough players
            return None
        
        # Check if already booked for this week
        if self.is_already_booked(week):
            return {'status': 'already_booked', 'week': week}
        
        # Execute booking strategy
        if booking_strategy == 'two_thirds':
            return self._book_two_third_pitches(week, count)
        elif booking_strategy == 'one_third':
            return self._book_single_pitch('third_pitch', week, count)
        
        return None
    
    def _book_single_pitch(self, pitch_type, week, count):
        """
        Book a single pitch
        
        Args:
            pitch_type (str): Type of pitch to book
            week (str): Week identifier
            count (int): Number of players
            
        Returns:
            dict: Booking confirmation or None
        """
        # Get available slots
        available_slots = self._get_available_slots(pitch_type)
        
        if not available_slots:
            st.warning(f"No available slots found for {pitch_type}")
            return None
        
        # Select best slot
        best_slot = self.select_best_slot(available_slots)
        
        if not best_slot:
            st.warning("Could not select a suitable time slot")
            return None
        
        # Book the pitch
        confirmation = self.book_pitch_slot(best_slot, week, count)
        
        return confirmation
    
    def _book_two_third_pitches(self, week, count):
        """
        Book 2 third pitches for 18+ players
        
        Args:
            week (str): Week identifier
            count (int): Number of players
            
        Returns:
            dict: Combined booking confirmation or None
        """
        # Get available third pitch slots
        available_slots = self._get_available_slots('third_pitch')
        
        if not available_slots or len(available_slots) < 2:
            st.warning("Not enough third pitch slots available. Need at least 2 slots at the same time.")
            return None
        
        # Find 2 slots at the same date/time
        slots_by_datetime = {}
        for slot in available_slots:
            key = f"{slot['date']}_{slot['time']}"
            if key not in slots_by_datetime:
                slots_by_datetime[key] = []
            slots_by_datetime[key].append(slot)
        
        # Filter to only datetime slots with at least 2 pitches available
        valid_datetimes = {k: v for k, v in slots_by_datetime.items() if len(v) >= 2}
        
        if not valid_datetimes:
            st.warning("Could not find 2 third pitches available at the same time.")
            return None
        
        # Select best datetime
        best_datetime_key = list(valid_datetimes.keys())[0]  # TODO: Smart selection
        two_slots = valid_datetimes[best_datetime_key][:2]
        
        # Book both pitches
        confirmations = []
        booking_ids = []
        total_cost = 0
        
        for i, slot in enumerate(two_slots):
            try:
                result = self.book_pitch_slot(slot, week, count)
                if result:
                    confirmations.append(result)
                    booking_ids.append(result.get('booking_id'))
                    total_cost += result.get('total_cost', 0)
                else:
                    st.error(f"Failed to book third pitch {i+1}")
                    # TODO: Cancel first booking if second fails
                    return None
            except Exception as e:
                st.error(f"Error booking third pitch {i+1}: {str(e)}")
                return None
        
        # Return combined confirmation
        return {
            'status': 'two_thirds_booked',
            'booking_ids': booking_ids,
            'confirmations': confirmations,
            'slot': {
                'date': two_slots[0]['date'],
                'time': two_slots[0]['time'],
                'pitch_type': 'two_thirds',
            },
            'cost_per_player': round(total_cost / count, 2),
            'total_cost': total_cost,
            'player_count': count
        }
    
    def is_already_booked(self, week):
        """
        Check if a booking already exists for the week
        
        Args:
            week (str): Week identifier
            
        Returns:
            bool: True if booking exists
        """
        return self.db.check_booking_exists(week)
    
    def _get_available_slots(self, pitch_type):
        """
        Get available slots from cache or scrape if cache is stale
        
        Args:
            pitch_type (str): Type of pitch
            
        Returns:
            list: Available slots
        """
        # Try to get from cache first
        cached_slots = self.db.get_available_slots(pitch_type)
        
        # Check if cache is fresh (less than 30 minutes old)
        if cached_slots:
            # Assuming slot structure: (slot_id, date, time, pitch_type, price, available, scraped_at)
            latest_scrape = cached_slots[0][6] if len(cached_slots) > 0 else None
            if latest_scrape:
                age = datetime.now() - latest_scrape
                if age.total_seconds() < 1800:  # 30 minutes
                    # Convert to dict format
                    return [
                        {
                            'date': slot[1].strftime('%Y-%m-%d') if hasattr(slot[1], 'strftime') else str(slot[1]),
                            'time': slot[2].strftime('%H:%M') if hasattr(slot[2], 'strftime') else str(slot[2]),
                            'pitch_type': slot[3],
                            'price': float(slot[4]),
                            'available': slot[5]
                        }
                        for slot in cached_slots
                    ]
        
        # Cache is stale or empty, scrape new data
        return self._scrape_and_cache_slots(pitch_type)
    
    def _scrape_and_cache_slots(self, pitch_type):
        """
        Scrape available slots and cache them
        
        Args:
            pitch_type (str): Type of pitch
            
        Returns:
            list: Available slots
        """
        try:
            with MerkyFCBookingBot(headless=True) as bot:
                slots = bot.scrape_available_times(pitch_type)
                
                # Cache the slots
                if slots:
                    self.db.cache_available_slots(slots)
                
                return slots
        except Exception as e:
            st.error(f"Error scraping slots: {str(e)}")
            return []
    
    def select_best_slot(self, available_slots):
        """
        Select the best time slot based on preferences
        
        Args:
            available_slots (list): List of available slots
            
        Returns:
            dict: Best slot or None
        """
        if not available_slots:
            return None
        
        # Get next week's date range
        today = datetime.now().date()
        week_start = today + timedelta(days=(7 - today.weekday()))  # Next Monday
        week_end = week_start + timedelta(days=6)
        
        # Filter slots for next week
        next_week_slots = []
        for slot in available_slots:
            try:
                slot_date = datetime.strptime(slot['date'], '%Y-%m-%d').date()
                if week_start <= slot_date <= week_end:
                    next_week_slots.append(slot)
            except (ValueError, KeyError):
                continue
        
        if not next_week_slots:
            # If no slots next week, just take first available
            return available_slots[0]
        
        # Prefer slots close to preferred time
        preferred_hour = int(self.preferred_time.split(':')[0])
        
        def time_score(slot):
            """Score based on proximity to preferred time"""
            try:
                slot_hour = int(slot['time'].split(':')[0])
                return abs(slot_hour - preferred_hour)
            except (ValueError, KeyError):
                return 999
        
        # Sort by time score and return best
        next_week_slots.sort(key=time_score)
        return next_week_slots[0]
    
    def book_pitch_slot(self, slot, week, player_count):
        """
        Book the selected pitch slot
        
        Args:
            slot (dict): Selected time slot
            week (str): Week identifier
            player_count (int): Number of players
            
        Returns:
            dict: Booking confirmation
        """
        try:
            # Get credentials
            credentials = get_credentials_from_secrets()
            
            # Book via Selenium bot
            with MerkyFCBookingBot(headless=True) as bot:
                confirmation = bot.book_pitch(
                    slot['date'],
                    slot['time'],
                    slot['pitch_type'],
                    credentials
                )
                
                if not confirmation:
                    return None
                
                # Calculate cost per player
                total_cost = slot['price']
                cost_per_player = round(total_cost / player_count, 2)
                
                # Store booking in database
                booking_id = self.db.insert_booking_with_details(
                    week=week,
                    session_date=slot['date'],
                    booking_time=slot['time'],
                    pitch_type=slot['pitch_type'],
                    booking_amount=total_cost,
                    cost_per_player=cost_per_player,
                    number_of_players=player_count,
                    auto_booked=True,
                    booking_confirmation=confirmation.get('confirmation_number'),
                    merky_booking_id=confirmation.get('confirmation_number')
                )
                
                return {
                    'booking_id': booking_id,
                    'confirmation': confirmation,
                    'slot': slot,
                    'cost_per_player': cost_per_player,
                    'total_cost': total_cost,
                    'player_count': player_count
                }
                
        except Exception as e:
            st.error(f"Error booking pitch: {str(e)}")
            return None
    
    def manual_book(self, date, time, pitch_type, week, player_count=14):
        """
        Manually trigger a booking (for admin use)
        
        Args:
            date (str): Booking date
            time (str): Booking time
            pitch_type (str): Type of pitch
            week (str): Week identifier
            player_count (int): Expected number of players
            
        Returns:
            dict: Booking confirmation
        """
        slot = {
            'date': date,
            'time': time,
            'pitch_type': pitch_type,
            'price': 80.0 if pitch_type == 'half_pitch' else 150.0,
            'available': True
        }
        
        return self.book_pitch_slot(slot, week, player_count)
    
    def get_booking_status(self, week):
        """
        Get the current booking status for a week
        
        Args:
            week (str): Week identifier
            
        Returns:
            dict: Status information
        """
        signups = self.db.fetch_signups(week)
        count = len(signups)
        is_booked = self.is_already_booked(week)
        
        # Determine status
        if is_booked:
            status = 'booked'
        elif count >= self.thresholds['full_pitch']:
            status = 'ready_full'
        elif count >= self.thresholds['half_pitch']:
            status = 'ready_half'
        else:
            status = 'waiting'
        
        # Calculate needed players
        half_needed = max(0, self.thresholds['half_pitch'] - count)
        full_needed = max(0, self.thresholds['full_pitch'] - count)
        
        return {
            'week': week,
            'status': status,
            'current_count': count,
            'is_booked': is_booked,
            'players_needed_half': half_needed,
            'players_needed_full': full_needed,
            'threshold_half': self.thresholds['half_pitch'],
            'threshold_full': self.thresholds['full_pitch']
        }
