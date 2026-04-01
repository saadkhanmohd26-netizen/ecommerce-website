# 📊 ShopEase Database Management - Complete Guide

## Quick Links

| Document | Purpose |
|----------|---------|
| [README_DATABASE.md](README_DATABASE.md) | 📖 Full database guide with queries |
| [DATABASE_MANAGEMENT.md](DATABASE_MANAGEMENT.md) | 🔍 Detailed DB Browser instructions |
| [DB_QUICK_START.md](DB_QUICK_START.md) | ⚡ Quick reference guide |
| [manage_db.py](manage_db.py) | 🛠️ CLI database manager |
| [init_db.py](init_db.py) | 🔄 Database initialization |
| [test_db.py](test_db.py) | ✅ Database status checker |

---

## 🎯 Quick Start (Choose Your Method)

### For Non-Technical Users (Easiest)
**Use DB Browser for SQLite (GUI)**

1. Download from https://sqlitebrowser.org/
2. Install and launch
3. File → Open Database
4. Select: `instance/shopease.db`
5. Browse users and orders visually

### For Developers (Most Powerful)
**Use Python CLI Manager**

```powershell
python manage_db.py
```

Menu options:
- View all users/orders
- Search by ID
- Get statistics
- Export to CSV

### For Power Users (Most Control)
**Use DB Browser with SQL Queries**

Examples:
```sql
-- All users
SELECT * FROM users;

-- All orders
SELECT * FROM orders;

-- Customer spending
SELECT u.fullname, SUM(o.total_amount) FROM users u 
LEFT JOIN orders o ON u.id = o.user_id GROUP BY u.id;
```

---

## 📍 Database Location

```
C:\Users\Home\Downloads\ecommerce\instance\shopease.db
```

**Why 'instance' folder?**
- Flask automatically creates this for app data
- Keeps database separate from code
- Easy to backup and restore

---

## 🗂️ Database Tables

### **users** Table
```
Columns: id, fullname, email, password (hashed)
Purpose: Store customer accounts
```

### **orders** Table
```
Columns: id, user_id, total_amount, payment_method,
         order_date, items (JSON), status,
         street_address, city, state, zip_code, phone
Purpose: Store all customer orders
```

---

## 🚀 Three Ways to Manage Your Database

### 1️⃣ **DB Browser (GUI) - Easiest for Browsing**
```
Best for: Visual exploration, simple searches
Setup: Download and install from sqlitebrowser.org
Time: 2 minutes to get started
```

👉 [See detailed instructions](DATABASE_MANAGEMENT.md)

### 2️⃣ **Python CLI - Best for Automation**
```
Best for: Exports, statistics, batch operations
Setup: python manage_db.py
Time: Install Python (usually already done)
```

👉 [See available commands](manage_db.py)

### 3️⃣ **SQL Queries - Most Powerful**
```
Best for: Complex analysis, custom reports
Tools: DB Browser or Python
Time: Learn SQL (optional, basic queries provided)
```

👉 [See example queries](README_DATABASE.md#-analytics-queries)

---

## 📋 Common Tasks

### View All Users
**DB Browser:** Tables → users → Browse Data
**CLI:** `python manage_db.py` → Option 1
**SQL:** `SELECT * FROM users;`

### View All Orders
**DB Browser:** Tables → orders → Browse Data
**CLI:** `python manage_db.py` → Option 2
**SQL:** `SELECT * FROM orders;`

### Get Total Sales
**DB Browser:** Execute SQL → `SELECT SUM(total_amount) FROM orders;`
**CLI:** `python manage_db.py` → Option 5
**SQL:** 
```sql
SELECT COUNT(*) as orders, SUM(total_amount) as revenue;
```

### Export Data
**DB Browser:** Right-click → Export → Select format
**CLI:** `python manage_db.py` → Options 6-7
**Result:** CSV files with all data

---

## 🔐 Security & Backups

### Backup Database
```powershell
copy instance\shopease.db instance\shopease_backup.db
```

### Restore from Backup
```powershell
copy instance\shopease_backup.db instance\shopease.db
```

### Secure Your Database
- ✅ Keep backups in safe location
- ✅ Don't share shopease.db file
- ✅ Passwords are hashed (secure)
- ✅ Regular backups = peace of mind

---

## 🆘 Need Help?

### Database won't open?
→ Make sure Flask app is NOT running
→ Check file path: `instance/shopease.db`

### No data visible?
→ Make sure users registered and placed orders
→ Try refreshing in DB Browser

### Want to reset?
```powershell
python init_db.py
```
⚠️ Warning: Deletes all users and orders!

### Need SQL help?
→ See [README_DATABASE.md](README_DATABASE.md) for examples
→ Visit w3schools.com/sql for SQL tutorial

---

## 📊 What Data You Can Track

### User Information
- ✅ Name and email
- ✅ Account creation date (from first order)
- ✅ Total purchases
- ✅ Shopping history

### Order Information
- ✅ Order total and date
- ✅ Payment method used
- ✅ Items purchased (product names, prices, quantities)
- ✅ Delivery address
- ✅ Contact phone number

### Business Analytics
- ✅ Total revenue
- ✅ Average order value
- ✅ Most popular payment methods
- ✅ Customer spending patterns
- ✅ Revenue by date/week/month

---

## ✅ Installation Checklist

- [ ] Database file exists: `instance/shopease.db`
- [ ] Flask app runs: `python app.py`
- [ ] Can connect with `test_db.py`
- [ ] DB Browser installed (optional but recommended)
- [ ] Can run `python manage_db.py`
- [ ] Backup created
- [ ] Read [README_DATABASE.md](README_DATABASE.md)

---

## 🎯 Next Steps

### Immediate (Do First)
1. Run `python test_db.py` to verify setup
2. Test one method: CLI or DB Browser
3. View some data

### Short Term (This Week)
1. Explore all tables and data
2. Try 2-3 SQL queries
3. Export data to CSV

### Long Term (Ongoing)
1. Regular backups (weekly)
2. Monitor statistics
3. Export reports for analysis

---

## 📞 Reference Materials

**In This Project:**
- [README_DATABASE.md](README_DATABASE.md) - Complete guide
- [DATABASE_MANAGEMENT.md](DATABASE_MANAGEMENT.md) - DB Browser tutorial
- [DB_QUICK_START.md](DB_QUICK_START.md) - Quick reference
- [manage_db.py](manage_db.py) - Python CLI tool

**External Resources:**
- DB Browser: https://sqlitebrowser.org/
- SQLite: https://www.sqlite.org/
- SQL Basics: https://www.w3schools.com/sql/
- Flask-SQLAlchemy: https://flask-sqlalchemy.palletsprojects.com/

---

## 💡 Pro Tips

✨ **Tip 1:** Use DB Browser in "Browse Data" mode for quick exploration  
✨ **Tip 2:** Export to CSV for sharing reports with others  
✨ **Tip 3:** Create backups before making any changes  
✨ **Tip 4:** Use Python script for automation and scheduled tasks  
✨ **Tip 5:** Save useful SQL queries in a text file for reuse

---

## 🎉 You're All Set!

Your ShopEase database is officially set up and ready to manage:
- ✅ User accounts (login management)
- ✅ All customer orders
- ✅ Payment information
- ✅ Delivery addresses
- ✅ Business analytics

**Choose your tool and start managing your e-commerce data today!**

---

**Last Updated:** March 30, 2026  
**Database Version:** 2.0 (SQLite 3)  
**Status:** ✅ Production Ready

