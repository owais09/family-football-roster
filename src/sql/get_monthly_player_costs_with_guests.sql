-- Query to calculate player costs for monthly invoicing
-- INCLUDES guests - guests are expensed to the player who brought them

WITH player_sessions AS (
    -- Get all sessions for regular players
    SELECT 
        p.player_id,
        p.name,
        p.email_id,
        p.brought_by_player_id,
        s.week,
        b.cost_per_player,
        b.session_date
    FROM 
        public.players p
    JOIN 
        public.signups s ON p.player_id = s.player_id
    JOIN 
        public.bookings b ON s.week = b.week
    WHERE 
        EXTRACT(MONTH FROM b.session_date) = %s
        AND EXTRACT(YEAR FROM b.session_date) = %s
        AND b.status = 'confirmed'
),
host_costs AS (
    -- Calculate costs for each host including their guests
    SELECT 
        COALESCE(ps.brought_by_player_id, ps.player_id) as billing_player_id,
        COUNT(DISTINCT ps.week) as sessions_attended,
        SUM(ps.cost_per_player) as total_cost,
        ARRAY_AGG(DISTINCT ps.week ORDER BY ps.week) as weeks_attended,
        -- Collect guest names
        ARRAY_AGG(
            CASE 
                WHEN ps.brought_by_player_id IS NOT NULL THEN ps.name 
                ELSE NULL 
            END
        ) FILTER (WHERE ps.brought_by_player_id IS NOT NULL) as guest_names
    FROM 
        player_sessions ps
    GROUP BY 
        COALESCE(ps.brought_by_player_id, ps.player_id)
)
SELECT 
    p.name,
    p.email_id,
    hc.sessions_attended,
    hc.total_cost,
    hc.weeks_attended,
    COALESCE(hc.guest_names, ARRAY[]::text[]) as guests
FROM 
    host_costs hc
JOIN 
    public.players p ON p.player_id = hc.billing_player_id
ORDER BY 
    p.name;
