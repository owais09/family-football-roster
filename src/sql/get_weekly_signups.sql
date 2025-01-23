SELECT name FROM public.signups as pbs join public.players as pp on pbs.player_id = pp.player_id  WHERE week = %s
