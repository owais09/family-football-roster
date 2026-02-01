-- Query to fetch all bookings for a specific month
SELECT 
    booking_id,
    week,
    session_date,
    booking_time,
    pitch_type,
    booking_amount,
    cost_per_player,
    number_of_players,
    auto_booked,
    booking_confirmation,
    status
FROM 
    public.booking_references
WHERE 
    EXTRACT(MONTH FROM session_date) = %s
    AND EXTRACT(YEAR FROM session_date) = %s
ORDER BY 
    session_date, booking_time;
