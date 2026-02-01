INSERT INTO public.players (name, email_id, brought_by_player_id) 
VALUES (%s, %s, %s) 
RETURNING player_id