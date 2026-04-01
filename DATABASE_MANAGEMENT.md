# ShopEase E-Commerce Database Management Guide

## Database Overview

The ShopEase application uses **SQLite** for data persistence with the following structure:

### Database Location
```
c:\Users\Home\Downloads\ecommerce\shopease.db
```

### Database Tables

#### 1. **users** Table
Stores all user accounts and login credentials.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER (PK) | Unique user identifier |
| fullname | VARCHAR | User's full name |
| email | VARCHAR (UNIQUE) | User's email (login username) |
| password | VARCHAR | Hashed password (bcrypt) |

#### 2. **orders** Table
Stores all customer orders with complete details.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER (PK) | Unique order identifier |
| user_id | INTEGER (FK) | References users.id |
| total_amount | FLOAT | Order total in INR |
| payment_method | VARCHAR | Payment method used |
| order_date | DATETIME | When order was placed |
| items | TEXT | JSON of order items |
| status | VARCHAR | Order status (completed) |
| street_address | VARCHAR | Delivery street |
| city | VARCHAR | Delivery city |
| state | VARCHAR | Delivery state |
| zip_code | VARCHAR | Delivery zip code |
| phone | VARCHAR | Delivery phone number |

---

## How to Use DB Browser for SQLite

### Step 1: Download DB Browser
1. Visit: https://sqlitebrowser.org/
2. Download the latest version for Windows
3. Install the application

### Step 2: Open Database
1. Launch **DB Browser for SQLite**
2. Go to **File → Open Database**
3. Navigate to: `C:\Users\Home\Downloads\ecommerce\shopease.db`
4. Click **Open**

### Step 3: Browse Users
1. Click on the **"Database Structure"** tab
2. Expand **Tables → users**
3. Click **"Browse Data"** tab to see all registered users
4. View columns: id, fullname, email, password (hashed)

**Sample User View:**
```
id | fullname      | email              | password
1  | John Doe      | john@example.com   | [hashed]
2  | Jane Smith    | jane@example.com   | [hashed]
```

### Step 4: Browse Orders
1. Click on **Tables → orders** in "Database Structure"
2. Click **"Browse Data"** tab
3. View order details: id, user_id, total_amount, payment_method, order_date, etc.

**Sample Order View:**
```
id | user_id | total_amount | payment_method    | order_date              | status
1  | 1       | 25630        | credit_card       | 2026-03-30 10:30:15    | completed
2  | 2       | 15820        | cash_on_delivery  | 2026-03-30 11:45:22    | completed
```

### Step 5: Query Data (Optional)
1. Click **"Execute SQL"** tab
2. Run custom queries:

**Get all users:**
```sql
SELECT id, fullname, email FROM users;
```

**Get orders for specific user:**
```sql
SELECT * FROM orders WHERE user_id = 1;
```

**Get total sales:**
```sql
SELECT SUM(total_amount) as total_sales FROM orders;
```

**Get orders by payment method:**
```sql
SELECT payment_method, COUNT(*) as count, SUM(total_amount) as total 
FROM orders 
GROUP BY payment_method;
```

**Get orders in date range:**
```sql
SELECT * FROM orders 
WHERE order_date >= '2026-03-01' AND order_date <= '2026-03-31';
```

---

## Database Management Features

### View All Users
- See registered user accounts
- Monitor email addresses
- Check when users joined

### View All Orders
- Track all customer orders
- See order dates and times
- Monitor payment methods used
- Check delivery addresses
- View order items (JSON format)

### Export Data
1. Right-click on table → Export
2. Choose format (CSV, JSON, etc.)
3. Save to file

### Add/Edit/Delete Records (Advanced)
1. Select table and click **"Browse Data"**
2. Double-click cells to edit
3. Right-click rows to delete
4. Add new rows with the **"New Record"** button

---

## Key Commands

| Task | Steps |
|------|-------|
| **View all users** | Tables → users → Browse Data |
| **View all orders** | Tables → orders → Browse Data |
| **Export users** | Right-click users → Export |
| **Export orders** | Right-click orders → Export |
| **Search users** | Use filter in Browse Data tab |
| **Sort by date** | Click column header in Browse Data |
| **Backup database** | File → Copy (save shopease.db elsewhere) |

---

## Security Notes

⚠️ **Important:**
- Passwords are **hashed** using bcrypt - cannot be viewed in plain text
- Never share the database file
- Keep backups of the database
- Sensitive data (addresses, phone numbers) should be encrypted for production

---

## Troubleshooting

### Database Not Opening
- Ensure app.py is not currently running
- Check file path is correct
- Try closing DB Browser and reopening

### Changes Not Visible
- Click **"Refresh"** button in DB Browser
- Make sure you're viewing the latest data

### Permission Denied
- Close the DB Browser
- Check Windows file permissions
- Ensure antivirus isn't blocking access

---

## Database Initialization

To reset/reinitialize the database:

```powershell
cd c:\Users\Home\Downloads\ecommerce
Remove-Item shopease.db -Force -ErrorAction SilentlyContinue
python init_db.py
```

---

## Statistics Queries

**Get dashboard statistics:**
```sql
-- Total Users
SELECT COUNT(*) as total_users FROM users;

-- Total Orders
SELECT COUNT(*) as total_orders FROM orders;

-- Total Revenue (INR)
SELECT SUM(total_amount) as total_revenue FROM orders;

-- Average Order Value (INR)
SELECT AVG(total_amount) as avg_order_value FROM orders;

-- Orders by Day
SELECT DATE(order_date) as order_day, COUNT(*) as count, SUM(total_amount) as revenue
FROM orders 
GROUP BY DATE(order_date)
ORDER BY order_day DESC;
```

---

## Next Steps

1. ✅ Download DB Browser for SQLite
2. ✅ Connect to shopease.db
3. ✅ Monitor users and orders in real-time
4. ✅ Run queries for analytics
5. ✅ Export data for reporting

