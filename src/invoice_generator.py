"""
Invoice generator for end-of-month billing
"""

import pandas as pd
from datetime import datetime
from whatsapp import WhatsAppNotifier
import streamlit as st


class InvoiceGenerator:
    """Generate and send monthly invoices"""
    
    def __init__(self, db):
        """
        Initialize the invoice generator
        
        Args:
            db: DatabaseHandler instance
        """
        self.db = db
        self.whatsapp = WhatsAppNotifier(db)
    
    def generate_monthly_report(self, month, year, format='summary'):
        """
        Generate monthly invoice report
        
        Args:
            month (int): Month number (1-12)
            year (int): Year
            format (str): 'summary' or 'detailed'
            
        Returns:
            dict: Report data
        """
        # Get player costs
        player_costs = self.db.get_monthly_player_costs(month, year)
        
        if not player_costs:
            return None
        
        # Get booking details
        bookings = self.db.get_bookings_for_month(month, year)
        
        # Build report
        report = {
            'month': month,
            'year': year,
            'month_name': datetime(year, month, 1).strftime('%B'),
            'player_data': [],
            'booking_data': [],
            'summary': {}
        }
        
        # Process player data
        total_revenue = 0
        for player in player_costs:
            player_info = {
                'name': player[0],
                'email': player[1],
                'sessions_attended': player[2],
                'total_cost': float(player[3]),
                'weeks_attended': player[4] if len(player) > 4 else [],
                'guests': player[5] if len(player) > 5 else []  # Guest names
            }
            report['player_data'].append(player_info)
            total_revenue += player_info['total_cost']
        
        # Process booking data
        total_spent = 0
        for booking in bookings:
            booking_info = {
                'booking_id': booking[0],
                'week': booking[1],
                'date': booking[2],
                'time': booking[3],
                'pitch_type': booking[4],
                'amount': float(booking[5]),
                'cost_per_player': float(booking[6]) if booking[6] else 0,
                'num_players': booking[7],
                'auto_booked': booking[8],
                'confirmation': booking[9],
                'status': booking[10]
            }
            report['booking_data'].append(booking_info)
            total_spent += booking_info['amount']
        
        # Calculate summary
        report['summary'] = {
            'total_players': len(player_costs),
            'total_sessions': len(bookings),
            'total_revenue': round(total_revenue, 2),
            'total_spent': round(total_spent, 2),
            'profit': round(total_revenue - total_spent, 2),
            'avg_per_player': round(total_revenue / len(player_costs), 2) if player_costs else 0,
            'avg_per_session': round(total_spent / len(bookings), 2) if bookings else 0
        }
        
        return report
    
    def format_report_text(self, report, format='summary'):
        """
        Format report as text for display or messaging
        
        Args:
            report (dict): Report data from generate_monthly_report
            format (str): 'summary' or 'detailed'
            
        Returns:
            str: Formatted report text
        """
        if not report:
            return "No data available for the selected month."
        
        text = f"📊 MONTHLY INVOICE - {report['month_name']} {report['year']}\n"
        text += "=" * 50 + "\n\n"
        
        if format == 'detailed':
            # Detailed player breakdown
            text += "👥 PLAYER COSTS:\n"
            text += "-" * 50 + "\n"
            
            for player in sorted(report['player_data'], key=lambda x: x['name']):
                text += f"\n{player['name']}\n"
                text += f"  Sessions: {player['sessions_attended']}\n"
                text += f"  Total: £{player['total_cost']:.2f}\n"
                
                # Show guests if any
                if player.get('guests') and player['guests']:
                    guests_list = [g for g in player['guests'] if g]  # Filter None
                    if guests_list:
                        text += f"  Guests: {', '.join(guests_list)}\n"
                
                if player['weeks_attended']:
                    weeks = ', '.join(player['weeks_attended'])
                    text += f"  Weeks: {weeks}\n"
            
            text += "\n" + "=" * 50 + "\n\n"
            
            # Detailed booking breakdown
            text += "⚽ BOOKINGS:\n"
            text += "-" * 50 + "\n"
            
            for booking in report['booking_data']:
                text += f"\n{booking['date']} at {booking['time']}\n"
                text += f"  Week: {booking['week']}\n"
                text += f"  Pitch: {self._format_pitch_type(booking['pitch_type'])}\n"
                text += f"  Players: {booking['num_players']}\n"
                text += f"  Cost: £{booking['amount']:.2f}\n"
                text += f"  Per player: £{booking['cost_per_player']:.2f}\n"
            
            text += "\n" + "=" * 50 + "\n\n"
        
        else:
            # Summary only
            text += "👥 PLAYER SUMMARY:\n"
            text += "-" * 50 + "\n"
            
            for player in sorted(report['player_data'], key=lambda x: x['name']):
                guest_info = ""
                if player.get('guests') and player['guests']:
                    guests_list = [g for g in player['guests'] if g]
                    if guests_list:
                        guest_info = f" + {len(guests_list)} guest(s)"
                text += f"{player['name']}{guest_info}: £{player['total_cost']:.2f} ({player['sessions_attended']} sessions)\n"
            
            text += "\n" + "=" * 50 + "\n\n"
        
        # Always show summary statistics
        summary = report['summary']
        text += "📈 SUMMARY:\n"
        text += "-" * 50 + "\n"
        text += f"Total Players: {summary['total_players']}\n"
        text += f"Total Sessions: {summary['total_sessions']}\n"
        text += f"Revenue Collected: £{summary['total_revenue']:.2f}\n"
        text += f"Total Spent: £{summary['total_spent']:.2f}\n"
        text += f"Profit/Loss: £{summary['profit']:.2f}\n"
        text += f"Avg per Player: £{summary['avg_per_player']:.2f}\n"
        text += f"Avg per Session: £{summary['avg_per_session']:.2f}\n"
        
        return text
    
    def generate_csv_export(self, report):
        """
        Generate CSV export of invoice data
        
        Args:
            report (dict): Report data
            
        Returns:
            str: CSV formatted string
        """
        if not report:
            return None
        
        # Create player DataFrame
        player_df = pd.DataFrame(report['player_data'])
        
        # Create booking DataFrame
        booking_df = pd.DataFrame(report['booking_data'])
        
        # Combine into CSV string
        csv_output = f"# MONTHLY INVOICE - {report['month_name']} {report['year']}\n\n"
        csv_output += "## PLAYER COSTS\n"
        csv_output += player_df.to_csv(index=False)
        csv_output += "\n## BOOKINGS\n"
        csv_output += booking_df.to_csv(index=False)
        csv_output += f"\n## SUMMARY\n"
        
        summary_df = pd.DataFrame([report['summary']])
        csv_output += summary_df.to_csv(index=False)
        
        return csv_output
    
    def send_invoice_via_whatsapp(self, month, year, format='summary'):
        """
        Generate and send invoice via WhatsApp
        
        Args:
            month (int): Month number
            year (int): Year
            format (str): 'summary' or 'detailed'
            
        Returns:
            bool: True if successful
        """
        # Generate report
        report = self.generate_monthly_report(month, year, format)
        
        if not report:
            st.error("No data available for the selected month")
            return False
        
        # Format as text
        message = self.format_report_text(report, format)
        
        # Send via WhatsApp
        success = self.whatsapp.send_message(message)
        
        if success:
            st.success(f"Invoice sent via WhatsApp for {report['month_name']} {year}")
        else:
            st.error("Failed to send invoice via WhatsApp")
        
        return success
    
    def display_invoice_in_app(self, month, year):
        """
        Display invoice in Streamlit app
        
        Args:
            month (int): Month number
            year (int): Year
        """
        report = self.generate_monthly_report(month, year)
        
        if not report:
            st.warning("No data available for the selected month")
            return
        
        st.header(f"📊 Invoice - {report['month_name']} {report['year']}")
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Players", report['summary']['total_players'])
        with col2:
            st.metric("Sessions", report['summary']['total_sessions'])
        with col3:
            st.metric("Revenue", f"£{report['summary']['total_revenue']:.2f}")
        with col4:
            st.metric("Profit", f"£{report['summary']['profit']:.2f}")
        
        # Player costs table
        st.subheader("👥 Player Costs")
        player_df = pd.DataFrame(report['player_data'])
        if not player_df.empty:
            display_df = player_df[['name', 'sessions_attended', 'total_cost']].copy()
            display_df.columns = ['Player', 'Sessions', 'Total Cost (£)']
            st.dataframe(display_df, use_container_width=True)
        
        # Booking details table
        st.subheader("⚽ Bookings")
        booking_df = pd.DataFrame(report['booking_data'])
        if not booking_df.empty:
            display_df = booking_df[['date', 'time', 'pitch_type', 'num_players', 'amount']].copy()
            display_df.columns = ['Date', 'Time', 'Pitch Type', 'Players', 'Cost (£)']
            display_df['Pitch Type'] = display_df['Pitch Type'].apply(self._format_pitch_type)
            st.dataframe(display_df, use_container_width=True)
    
    def _format_pitch_type(self, pitch_type):
        """Format pitch type for display"""
        pitch_map = {
            'half_pitch': 'Half Pitch',
            'full_pitch': 'Full Pitch',
            'third_pitch': 'Third Pitch'
        }
        return pitch_map.get(pitch_type, pitch_type)


# Convenience function for quick invoice generation
def generate_and_send_invoice(db, month=None, year=None):
    """
    Generate and send invoice for current or specified month
    
    Args:
        db: DatabaseHandler instance
        month (int): Month number (defaults to last month)
        year (int): Year (defaults to current year)
        
    Returns:
        bool: True if successful
    """
    if month is None or year is None:
        # Default to last month
        today = datetime.now()
        if today.month == 1:
            month = 12
            year = today.year - 1
        else:
            month = today.month - 1
            year = today.year
    
    generator = InvoiceGenerator(db)
    return generator.send_invoice_via_whatsapp(month, year)
