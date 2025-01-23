CREATE TABLE IF NOT EXISTS public.booking_references (booking_id SERIAL PRIMARY KEY,
                week TEXT NOT NULL,
                booking_amount FLOAT,
                session_date DATE,
                number_of_players INT NOT NULL);