# ShopEase Database - Quick Start Guide

## 📊 Database Overview

Your ShopEase E-Commerce application uses **SQLite** database to store:
- **Users**: Login credentials and customer information
- **Orders**: All purchase orders with items, addresses, and payment details

Database file: `shopease.db` (in the project root directory)

---

## 🛠️ Two Ways to Manage Your Database

### Option 1: GUI - DB Browser for SQLite (RECOMMENDED FOR BEGINNERS)

**Best for:** Visual browsing, easy searching, point-and-click management

#### Setup:
1. Download from: https://sqlitebrowser.org/
2. Install the application
3. Open the application
4. Go to **File → Open Database**
5. Select: `C:\Users\Home\Downloads\ecommerce\shopease.db`

#### Common Tasks:
- **View Users**: Tables → users → Browse Data
- **View Orders**: Tables → orders → Browse Data
- **Run Queries**: Execute SQL tab → Write custom SQL

---

### Option 2: CLI - Python Script (RECOMMENDED FOR DEVELOPERS)

**Best for:** Quick exports, batch operations, automation

#### Setup:
```powershell
cd c:\Users\Home\Downloads\ecommerce
python manage_db.py
```

#### Features:
1. View all users
2. View all orders
3. Search user details
4. View order details
5. Get database statistics
6. Export users to CSV
7. Export orders to CSV

---

## 📋 Database Schema

### Users Table
| Column | Type | Example |
|--------|------|---------|
| id | INTEGER | 1 |
| fullname | TEXT | John Doe |
| email | TEXT | john@example.com |
| password | TEXT | [hashed] |

### Orders Table
| Column | Type | Example |
|--------|------|---------|
| id | INTEGER | 1 |
| user_id | INTEGER | 1 |
| total_amount | FLOAT | 25630 |
| payment_method | TEXT | credit_card |
| order_date | DATETIME | 2026-03-30 10:30:15 |
| items | TEXT | [JSON] |
| status | TEXT | completed |
| street_address | TEXT | 123 Main St |
| city | TEXT | New York |
| state | TEXT | NY |
| zip_code | TEXT | 10001 |
| phone | TEXT | 9876543210 |

---

## 🔍 Example Queries (For DB Browser)

### Get All Users
```sql
SELECT id, fullname, email FROM users ORDER BY id;
```

### Get All Orders
```sql
SELECT 
    id, 
    user_id, 
    total_amount, 
    payment_method, 
    order_date 
FROM orders 
ORDER BY order_date DESC;
```

### Get Orders for Specific User
```sql
SELECT * FROM orders WHERE user_id = 1;
```

### Get Total Sales
```sql
SELECT 
    COUNT(*) as total_orders,
    SUM(total_amount) as total_revenue,
    AVG(total_amount) as avg_order
FROM orders;
```

### Get Top Customers
```sql
SELECT 
    u.fullname, 
    u.email, 
    COUNT(o.id) as order_count,
    SUM(o.total_amount) as total_spent
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id
ORDER BY total_spent DESC;
```

### Payment Method Breakdown
```sql
SELECT 
    payment_method,
    COUNT(*) as count,
    SUM(total_amount) as total,
    AVG(total_amount) as average
FROM orders
GROUP BY payment_method;
```

---

## 💾 Backing Up Your Database

### Manual Backup (Windows)
```powershell
# Copy the database file
Copy-Item shopease.db shopease_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').db
```

### Restore Database
1. Delete current `shopease.db`
2. Rename backup file to `shopease.db`
3. Restart the app

---

## 🔄 Reset Database

If you need to start fresh:

```powershell
cd c:\Users\Home\Downloads\ecommerce
Remove-Item shopease.db
python init_db.py
```

---

## 📁 File Locations

| Item | Location |
|------|----------|
| **Database** | `shopease.db` |
| **GUI Guide** | `DATABASE_MANAGEMENT.md` |
| **CLI Tool** | `manage_db.py` |
| **This Guide** | `DB_QUICK_START.md` |

---

## ✅ Checklist

- [ ] Database file exists at `c:\Users\Home\Downloads\ecommerce\shopease.db`
- [ ] Downloaded DB Browser for SQLite
- [ ] Can open the database in DB Browser
- [ ] Can see users table and orders table
- [ ] Can run the Python CLI script with `python manage_db.py`
- [ ] Created a backup of your database

---

## 🆘 Troubleshooting

### Database Won't Open
- Make sure the Flask app is not running
- Check file permissions
- Try opening with DB Browser

### Can't See Any Data
- Ensure you've registered users and placed orders in the app
- Try refreshing in DB Browser

### Need More Help?
1. See `DATABASE_MANAGEMENT.md` for detailed guide
2. Run `python manage_db.py` for CLI tools
3. Check Flask app logs for database errors

---

## 🎯 Next Steps

1. ✅ Download and install DB Browser for SQLite
2. ✅ Connect to your database
3. ✅ Explore the users and orders tables
4. ✅ Try running some SQL queries
5. ✅ Use `manage_db.py` for automation

Enjoy managing your ShopEase database! 🚀
