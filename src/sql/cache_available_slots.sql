-- Insert or update available slots in cache
INSERT INTO public.available_slots_cache (
    date,
    time,
    pitch_type,
    price,
    available,
    scraped_at
) VALUES (
    %s, %s, %s, %s, %s, CURRENT_TIMESTAMP
)
ON CONFLICT (date, time, pitch_type) 
DO UPDATE SET
    price = EXCLUDED.price,
    available = EXCLUDED.available,
    scraped_at = CURRENT_TIMESTAMP;
