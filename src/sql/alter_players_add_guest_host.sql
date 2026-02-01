-- Add column to track who brought a guest
-- This allows guests to be expensed to the host player

ALTER TABLE public.players 
ADD COLUMN IF NOT EXISTS brought_by_player_id INT DEFAULT NULL;

-- Add foreign key constraint (optional, for referential integrity)
ALTER TABLE public.players
ADD CONSTRAINT fk_guest_host 
FOREIGN KEY (brought_by_player_id) 
REFERENCES public.players(player_id) 
ON DELETE SET NULL;

-- Add index for performance
CREATE INDEX IF NOT EXISTS idx_players_brought_by 
ON public.players(brought_by_player_id);
