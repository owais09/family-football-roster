"""
Enhanced WhatsApp integration for automated notifications
Supports signup updates, booking confirmations, and monthly invoices
"""

import pandas as pd
import streamlit as st
from datetime import datetime
from config import get_whatsapp_config

# Lazy import pywhatkit to avoid GUI/display issues at module load time
_pywhatkit = None

def _get_pywhatkit():
    """Lazy import pywhatkit only when needed"""
    global _pywhatkit
    if _pywhatkit is None:
        try:
            import pywhatkit as pwk
            _pywhatkit = pwk
        except Exception as e:
            st.warning(f"WhatsApp features disabled: {str(e)}")
            _pywhatkit = False  # Mark as unavailable
    return _pywhatkit if _pywhatkit is not False else None


class WhatsAppNotifier:
    """Handle WhatsApp notifications for the football app"""
    
    def __init__(self, db):
        """
        Initialize WhatsApp notifier
        
        Args:
            db: DatabaseHandler instance
        """
        self.db = db
        
        # Get group ID from secrets or environment
        whatsapp_config = get_whatsapp_config()
        self.group_id = whatsapp_config['group_id']
    
    def send_message(self, message):
        """
        Send a message to WhatsApp group
        
        Args:
            message (str): Message to send
            
        Returns:
            bool: True if successful
        """
        pwk = _get_pywhatkit()
        if pwk is None:
            st.warning("WhatsApp notifications are currently disabled")
            return False
            
        try:
            pwk.sendwhatmsg_to_group_instantly(self.group_id, message)
            return True
        except Exception as e:
            st.error(f"Failed to send WhatsApp message: {e}")
            return False
    
    def send_signup_update(self, name, action, week, current_count, threshold_half, threshold_full):
        """
        Send notification when player signs up or removes themselves
        
        Args:
            name (str): Player name
            action (str): "signed up" or "removed"
            week (str): Week identifier
            current_count (int): Current number of players
            threshold_half (int): Half pitch threshold (14)
            threshold_full (int): Two thirds threshold (18)
        """
        message = f"🔔 {name} just {action}!\n\n"
        
        # Add threshold status
        if current_count >= threshold_full:
            message += f"✅ 2 Third Pitches ready! ({threshold_full}+ players)\n"
            message += "🤖 Auto-booking 2 third pitches...\n\n"
        elif current_count >= threshold_half:
            message += f"✅ 1 Third Pitch ready! ({threshold_half}+ players)\n"
            if action == "signed up":
                message += f"💡 {threshold_full - current_count} more for 2 third pitches\n\n"
        else:
            needed = threshold_half - current_count
            message += f"⏳ {needed} more needed for 1 third pitch\n\n"
        
        # Get and display full player list
        signups = self.db.fetch_signups(week)
        if signups:
            message += f"📋 CURRENT LIST ({len(signups)} players):\n"
            message += "=" * 30 + "\n"
            for idx, signup in enumerate(signups, 1):
                player_name = signup[0]  # First column is name
                message += f"{idx}. {player_name}\n"
            message += "=" * 30 + "\n"
        
        message += f"\nWeek: {week}"
        
        return self.send_message(message)
    
    def send_booking_confirmation(self, booking_details):
        """
        Send booking confirmation notification
        
        Args:
            booking_details (dict): Booking information
        """
        pitch_type = booking_details.get('pitch_type')
        
        if pitch_type == 'two_thirds':
            message = "⚽⚽ 2 PITCHES BOOKED! ⚽⚽\n\n"
            message += f"📅 Date: {booking_details.get('date')}\n"
            message += f"⏰ Time: {booking_details.get('time')}\n"
            message += f"📏 Pitches: 2x Third Pitch (side by side)\n"
        else:
            message = "⚽ PITCH BOOKED! ⚽\n\n"
            message += f"📅 Date: {booking_details.get('date')}\n"
            message += f"⏰ Time: {booking_details.get('time')}\n"
            message += f"📏 Pitch: {self._format_pitch_type(pitch_type)}\n"
        
        message += f"👥 Players: {booking_details.get('player_count')}\n"
        message += f"💰 Cost per player: £{booking_details.get('cost_per_player', 0):.2f}\n"
        message += f"💳 Total: £{booking_details.get('total_cost', 0):.2f}\n\n"
        
        if booking_details.get('confirmation_number'):
            message += f"🎫 Booking ref: {booking_details['confirmation_number']}\n\n"
        
        message += "See you there! ⚽"
        
        return self.send_message(message)
    
    def send_monthly_invoice(self, month, year):
        """
        Send end-of-month invoice summary
        
        Args:
            month (int): Month number
            year (int): Year
        """
        # Get player costs for the month
        player_costs = self.db.get_monthly_player_costs(month, year)
        
        if not player_costs:
            st.info("No bookings found for this month")
            return False
        
        # Format invoice message
        month_name = datetime(year, month, 1).strftime('%B')
        message = f"📊 MONTHLY INVOICE - {month_name} {year}\n"
        message += "=" * 40 + "\n\n"
        
        total_collected = 0
        for player in player_costs:
            # player structure: (name, email, sessions_attended, total_cost, weeks_attended, guests[])
            name = player[0]
            sessions = player[2]
            cost = float(player[3])
            guests = player[5] if len(player) > 5 else []
            
            message += f"👤 {name}\n"
            message += f"   Sessions: {sessions}\n"
            message += f"   Total: £{cost:.2f}\n"
            
            # Show guests if any
            if guests:
                guests_list = [g for g in guests if g]  # Filter None
                if guests_list:
                    message += f"   Guests: {', '.join(guests_list)}\n"
            
            message += "\n"
            
            total_collected += cost
        
        message += "=" * 40 + "\n"
        message += f"💰 TOTAL: £{total_collected:.2f}\n"
        message += f"📈 Players: {len(player_costs)}\n"
        
        return self.send_message(message)
    
    def send_reminder(self, week, date, time, pitch_type):
        """
        Send reminder about upcoming game
        
        Args:
            week (str): Week identifier
            date (str): Game date
            time (str): Game time
            pitch_type (str): Type of pitch
        """
        message = "⏰ GAME REMINDER ⏰\n\n"
        message += f"📅 Tomorrow: {date}\n"
        message += f"⏰ Time: {time}\n"
        message += f"📏 Pitch: {self._format_pitch_type(pitch_type)}\n"
        message += f"📍 Merky FC HQ\n\n"
        message += "Don't forget! See you there! ⚽"
        
        return self.send_message(message)
    
    def send_weekly_list(self, week):
        """
        Send current weekly signup list
        
        Args:
            week (str): Week identifier
        """
        signups = self.db.fetch_signups(week)
        signups_df = pd.DataFrame(signups, columns=["name", "email"]).dropna()
        
        if signups_df.empty:
            message = f"📋 Week {week}\n\nNo signups yet. Be the first!"
        else:
            message = f"📋 Weekly Signup List - {week}\n"
            message += "=" * 40 + "\n\n"
            
            for idx, row in signups_df.iterrows():
                message += f"{idx + 1}. {row['name']}\n"
            
            message += f"\n👥 Total: {len(signups_df)} players"
        
        return self.send_message(message)
    
    def _format_pitch_type(self, pitch_type):
        """Format pitch type for display"""
        pitch_map = {
            'half_pitch': 'Half Pitch',
            'full_pitch': 'Full Pitch',
            'third_pitch': 'Third Pitch'
        }
        return pitch_map.get(pitch_type, pitch_type)


# Legacy function for backward compatibility
def format_signup_message(signups_df):
    """Legacy function - kept for compatibility"""
    if signups_df.empty:
        return "No signups yet."

    message = "🎉 Weekly Football Signup List 🎉\n\n"
    for idx, row in signups_df.iterrows():
        if idx == 1:
            message += f"{idx + 1}. {row['name']}\n"
        else:
            message += f"{row['name']}\n"
    return message


# Legacy function for backward compatibility
def send_whatsapp_message(message, group_id='CHAjDSd8Tm14QZ4rGrqQxc'):
    """Legacy function - kept for compatibility"""
    try:
        pwk.sendwhatmsg_to_group_instantly(group_id, message)
        print("Message scheduled successfully!")
        return True
    except Exception as e:
        print(f"Failed to send message: {e}")
        return False
