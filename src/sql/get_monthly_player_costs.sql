-- Query to calculate player costs for monthly invoicing
SELECT 
    p.name,
    p.email_id,
    COUNT(DISTINCT s.week) as sessions_attended,
    SUM(b.cost_per_player) as total_cost,
    ARRAY_AGG(DISTINCT s.week ORDER BY s.week) as weeks_attended
FROM 
    public.player_dimensions p
JOIN 
    public.weekly_signups s ON p.player_id = s.player_id
JOIN 
    public.booking_references b ON s.week = b.week
WHERE 
    EXTRACT(MONTH FROM b.session_date) = %s
    AND EXTRACT(YEAR FROM b.session_date) = %s
    AND b.status = 'confirmed'
GROUP BY 
    p.player_id, p.name, p.email_id
ORDER BY 
    p.name;
