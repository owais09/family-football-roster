CREATE TABLE IF NOT EXISTS public.signups (signup_id SERIAL PRIMARY KEY,
        week TEXT NOT NULL,
        player_id INT NOT NULL,
        session_date DATE,
        FOREIGN KEY (player_id) REFERENCES players (player_id) ON DELETE CASCADE);