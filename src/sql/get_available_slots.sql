-- Fetch available slots from cache
SELECT 
    slot_id,
    date,
    time,
    pitch_type,
    price,
    available,
    scraped_at
FROM 
    public.available_slots_cache
WHERE 
    available = true
    AND date >= CURRENT_DATE
    AND (pitch_type = %s OR %s IS NULL)
ORDER BY 
    date, time;
