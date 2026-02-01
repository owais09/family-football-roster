-- Insert a new booking with full details
INSERT INTO public.booking_references (
    week,
    session_date,
    booking_time,
    pitch_type,
    booking_amount,
    cost_per_player,
    number_of_players,
    auto_booked,
    booking_confirmation,
    merky_booking_id,
    status
) VALUES (
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
) RETURNING booking_id;
