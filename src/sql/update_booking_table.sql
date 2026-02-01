-- Add new columns to booking_references table for enhanced booking management
ALTER TABLE public.booking_references 
ADD COLUMN IF NOT EXISTS pitch_type VARCHAR(20),
ADD COLUMN IF NOT EXISTS booking_confirmation VARCHAR(100),
ADD COLUMN IF NOT EXISTS cost_per_player DECIMAL(10,2),
ADD COLUMN IF NOT EXISTS auto_booked BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS merky_booking_id VARCHAR(100),
ADD COLUMN IF NOT EXISTS booking_time TIME,
ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'confirmed';
