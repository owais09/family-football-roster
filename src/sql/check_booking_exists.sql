-- Check if a booking already exists for a specific week
SELECT 
    booking_id,
    week,
    session_date,
    booking_time,
    pitch_type,
    status
FROM 
    public.booking_references
WHERE 
    week = %s
    AND status != 'cancelled'
LIMIT 1;
