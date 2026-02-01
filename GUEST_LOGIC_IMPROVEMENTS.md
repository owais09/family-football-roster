# Guest Logic Improvements & WhatsApp Full List

## Summary

Two major improvements have been implemented:

1. **WhatsApp now shows the full player list** when someone signs up or removes themselves
2. **Guest logic fixed** - Guests are now properly linked to their host and costs are combined in invoices

---

## 1. WhatsApp Full Player List ✅

### What Changed:
The `send_signup_update()` method in `whatsapp.py` now fetches and displays all current signups.

### Before:
```
🔔 John just signed up!
Current count: 12 players
Week: 2026-W06
⏳ 2 more needed for 1 third pitch
```

### After:
```
🔔 John just signed up!
⏳ 2 more needed for 1 third pitch

📋 CURRENT LIST (12 players):
==============================
1. Ahmed
2. Owais
3. Sarah
4. John
5. Mike
6. ... (all 12 players)
==============================

Week: 2026-W06
```

---

## 2. Guest Logic - Proper Expense Tracking ✅

### The Problem:
Before, guests were created as **separate players** with their own invoice line items. This meant:
- Guests got individual invoices ❌
- No way to track who brought them ❌
- Hard to reconcile expenses ❌

### The Solution:
Guests are now **linked to the player who brought them**, and their costs are **added to the host's total**.

### Database Changes:

#### New Column in `players` table:
```sql
brought_by_player_id INT  -- NULL for regular players, references host player_id for guests
```

This maintains **full ACID compliance** with:
- **Atomicity**: All guest operations are transactional
- **Consistency**: Foreign key constraints ensure valid relationships
- **Isolation**: Proper transaction handling
- **Durability**: All changes are committed to database

#### Migration File:
`src/sql/alter_players_add_guest_host.sql` - Automatically runs on app startup

---

## 3. How Guest Signup Works Now

### UI Changes (app.py):
When selecting "Guest" as player type:
1. User enters **guest name**
2. Dropdown asks: **"Who is bringing this guest?"**
3. Host player is selected from existing players
4. Guest is created with `brought_by_player_id` linking to host

### Example:
```
Guest Name: Mike's Friend
Who is bringing this guest?: mike@example.com (Mike)

→ Creates guest linked to Mike's player_id
→ All costs for this guest will be added to Mike's invoice
```

---

## 4. Invoice Changes

### New SQL Query:
`src/sql/get_monthly_player_costs_with_guests.sql`

This query:
- Groups guests with their host player
- Sums all costs (host + guests)
- Returns guest names as an array

### Invoice Output Examples:

#### Summary Format:
```
📊 MONTHLY INVOICE - January 2026
==================================================

👥 PLAYER SUMMARY:
--------------------------------------------------
Ahmed: £20.00 (3 sessions)
Mike + 2 guest(s): £30.00 (3 sessions)
Owais: £13.33 (2 sessions)
```

#### Detailed Format:
```
👥 PLAYER COSTS:
--------------------------------------------------

Mike
  Sessions: 3
  Total: £30.00
  Guests: Mike's Friend, Sarah's Brother
  Weeks: 2026-W05, 2026-W06, 2026-W07
```

### WhatsApp Invoice:
```
📊 MONTHLY INVOICE - January 2026
========================================

👤 Mike
   Sessions: 3
   Total: £30.00
   Guests: Mike's Friend, Sarah's Brother

👤 Ahmed
   Sessions: 3
   Total: £20.00

========================================
💰 TOTAL: £50.00
📈 Players: 2
```

---

## 5. Files Modified

### Core Logic:
1. **`src/app.py`**
   - Added guest host selection UI
   - Passes `host_player_id` to signup function
   - Added migration to schema initialization

2. **`src/signups.py`**
   - Updated `add_player_signup()` to accept `host_player_id`
   - Updated `handle_new_player_signup()` to link guests to hosts
   - Added validation to ensure host is selected for guests

3. **`src/database.py`**
   - Updated `add_player_signup()` to accept `brought_by_player_id` parameter
   - Updated `get_monthly_player_costs()` to use new query with guests
   - Added fallback for backward compatibility

### SQL Files:
4. **`src/sql/alter_players_add_guest_host.sql`** (NEW)
   - Adds `brought_by_player_id` column
   - Creates foreign key constraint
   - Adds index for performance

5. **`src/sql/insert_new_player_entry.sql`**
   - Updated to include `brought_by_player_id` parameter

6. **`src/sql/get_monthly_player_costs_with_guests.sql`** (NEW)
   - New query that groups guests with hosts
   - Returns guest names array
   - Sums costs properly

### WhatsApp & Invoicing:
7. **`src/whatsapp.py`**
   - Updated `send_signup_update()` to show full player list
   - Updated `send_monthly_invoice()` to show guests under hosts

8. **`src/invoice_generator.py`**
   - Updated to handle `guests` array in player data
   - Shows guest names in detailed reports
   - Shows guest count in summary reports

---

## 6. Backward Compatibility

The changes are **fully backward compatible**:

- Existing players without guests work exactly as before
- Old data migrates seamlessly (NULL for `brought_by_player_id`)
- If migration fails, fallback query is used
- No data loss or disruption

---

## 7. Benefits

### For Users:
✅ See full player list instantly on WhatsApp
✅ Clear expense tracking - guests are billed to the person who brought them
✅ Accurate monthly invoices showing who brought guests
✅ Easy to see participant makeup in notifications

### For Database:
✅ Maintains ACID properties
✅ Referential integrity with foreign keys
✅ Indexed for performance
✅ Backward compatible

### For Reconciliation:
✅ Clear audit trail of who brought each guest
✅ Costs automatically grouped in invoices
✅ Easy to track guest attendance patterns
✅ Simplified end-of-month billing

---

## 8. Testing Checklist

- [ ] Sign up a new regular player
- [ ] Sign up an existing player
- [ ] Sign up a guest (select host player)
- [ ] Check WhatsApp shows full list after signup
- [ ] Generate monthly invoice
- [ ] Verify guest costs are added to host's total
- [ ] Verify guest names appear under host in detailed invoice
- [ ] Remove a player and check WhatsApp update

---

## 9. Future Enhancements (Optional)

1. **Guest History**: Track which guests come frequently
2. **Guest Limits**: Set max guests per player
3. **Guest Discount**: Apply different rates for guests
4. **Guest Reminders**: Send WhatsApp reminders to hosts about their guests

---

## Need Help?

If you encounter any issues:
1. Check database migration ran successfully
2. Verify `brought_by_player_id` column exists in `players` table
3. Check logs for any SQL errors
4. Ensure host is selected when adding guests
