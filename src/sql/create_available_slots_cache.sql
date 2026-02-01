-- Cache table for available pitch booking slots scraped from Merky FC HQ
CREATE TABLE IF NOT EXISTS public.available_slots_cache (
    slot_id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    time TIME NOT NULL,
    pitch_type VARCHAR(20) NOT NULL,
    price DECIMAL(10,2),
    available BOOLEAN DEFAULT true,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date, time, pitch_type)
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_slots_date ON public.available_slots_cache(date);
CREATE INDEX IF NOT EXISTS idx_slots_available ON public.available_slots_cache(available);
