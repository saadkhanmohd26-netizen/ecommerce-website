# ShopEase E-Commerce Database Management System

## 📊 Official Database Setup

Your ShopEase application uses a professional **SQLite** database to manage:
- **User Accounts**: Secure login credentials and customer information  
- **Orders**: Complete order history with items, addresses, and payment details

---

## 📁 Database Location

```
instance/shopease.db
```

**Note:** Flask automatically creates an `instance/` folder in the project root for application data.

---

## 💀 Database Schema

### **Users Table**
Stores all registered customer accounts.

```
users
├── id (INTEGER) - Primary Key
├── fullname (VARCHAR) - Customer's full name
├── email (VARCHAR) - Email/Login address (UNIQUE)
└── password (VARCHAR) - Hashed password (bcrypt)
```

### **Orders Table**
Stores complete order information for all purchases.

```
orders
├── id (INTEGER) - Primary Key
├── user_id (INTEGER) - Foreign Key to users
├── total_amount (FLOAT) - Order total amount (in INR)
├── payment_method (VARCHAR) - Payment type used
├── order_date (DATETIME) - When order was placed
├── items (TEXT) - JSON array of ordered items
├── status (VARCHAR) - Order status
├── street_address (VARCHAR) - Delivery street address
├── city (VARCHAR) - City name
├── state (VARCHAR) - State/Province
├── zip_code (VARCHAR) - Postal code
└── phone (VARCHAR) - Contact phone number
```

---

## 🛠️ Two Methods to Manage Database

### **METHOD 1: GUI - DB Browser for SQLite** (Recommended for beginners)

#### Installation
1. Download from: https://sqlitebrowser.org/
2. Install on your Windows machine
3. Launch the application

#### How to Open Database
1. Click **File → Open Database**
2. Navigate to: `C:\Users\Home\Downloads\ecommerce\instance\shopease.db`
3. Click **Open**

#### Viewing Data
- **Browse Users**: Tables → users → Browse Data tab
- **Browse Orders**: Tables → orders → Browse Data tab
- **View Columns**: All fields with actual data displayed in table format

#### Running Queries
1. Click **Execute SQL** tab
2. Enter SQL query
3. Click **Execute**

#### Example Queries

**Get all users:**
```sql
SELECT id, fullname, email FROM users;
```

**Get all orders with customer names:**
```sql
SELECT 
    o.id as order_id,
    u.fullname,
    o.total_amount,
    o.payment_method,
    o.order_date
FROM orders o
JOIN users u ON o.user_id = u.id
ORDER BY o.order_date DESC;
```

**Customer spending summary:**
```sql
SELECT 
    u.fullname,
    COUNT(o.id) as total_orders,
    SUM(o.total_amount) as total_spent
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id
ORDER BY total_spent DESC;
```

**Orders by payment method:**
```sql
SELECT 
    payment_method,
    COUNT(*) as count,
    SUM(total_amount) as total
FROM orders
GROUP BY payment_method;
```

---

### **METHOD 2: CLI - Python Management Script** (Recommended for automation)

#### Using the Database Manager

```powershell
cd c:\Users\Home\Downloads\ecommerce
python manage_db.py
```

This opens an interactive menu with options:

```
1. View All Users
2. View All Orders  
3. View User Details
4. View Order Details
5. Database Statistics
6. Export Users to CSV
7. Export Orders to CSV
8. Exit
```

#### Examples

**View all users:**
```
Select option 1
```

**Export orders to CSV:**
```
Select option 7
→ Creates "orders_export.csv" with all orders
```

**Get statistics:**
```
Select option 5
→ Shows total users, orders, revenue, and payment breakdowns
```

---

## 🔍 Database Management Tasks

### View All Users
**DB Browser:** Tables → users → Browse Data
**Python:** `python manage_db.py` → Option 1

### View All Orders  
**DB Browser:** Tables → orders → Browse Data
**Python:** `python manage_db.py` → Option 2

### Find Orders by User
**DB Browser:**
```sql
SELECT * FROM orders WHERE user_id = 1;
```
**Python:** `python manage_db.py` → Option 4

### Calculate Statistics
**DB Browser:**
```sql
SELECT 
    COUNT(*) as total_orders,
    SUM(total_amount) as revenue,
    COUNT(DISTINCT user_id) as unique_customers
FROM orders;
```
**Python:** `python manage_db.py` → Option 5

### Export Data
**DB Browser:** Right-click table → Export → Choose format
**Python:** `python manage_db.py` → Options 6-7

---

## 🔄 Database Reset/Initialization

If you need to reset the database to start fresh:

```powershell
cd c:\Users\Home\Downloads\ecommerce
python init_db.py
```

**Warning:** This will DELETE all users and orders. Use only if you want to reset the entire system.

---

## 📊 Creating Reports

### Sales Dashboard Query
```sql
SELECT 
    DATE(order_date) as date,
    COUNT(*) as orders,
    SUM(total_amount) as revenue,
    AVG(total_amount) as avg_order
FROM orders
GROUP BY DATE(order_date)
ORDER BY date DESC;
```

### Top Customers Report
```sql
SELECT 
    u.id,
    u.fullname,
    u.email,
    COUNT(o.id) as purchases,
    SUM(o.total_amount) as lifetime_value
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id
HAVING purchases > 0
ORDER BY lifetime_value DESC;
```

### Product Performance (from order items)
```sql
SELECT * FROM orders WHERE order_date >= '2026-03-01';
-- Note: Items are stored as JSON in the 'items' column
```

---

## 🔐 Security Best Practices

⚠️ **Important Security Notes:**

1. **Passwords are Hashed**
   - Passwords use bcrypt hashing
   - Cannot be viewed or recovered in plain text
   - Reset via application interface only

2. **Data Protection**
   - Never share the shopease.db file publicly
   - Contains sensitive customer information
   - Keep regular backups

3. **Access Control**
   - Restrict database access to authorized personnel only
   - Store backups in secure locations
   - Monitor database changes

4. **For Production**
   - Consider PostgreSQL or MySQL for production
   - Implement database encryption
   - Use connection pooling
   - Enable SSL/TLS for remote access

---

## 💾 Backup & Recovery

### Create Backup
```powershell
Copy-Item instance\shopease.db instance\shopease_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').db
```

### Automatic Backup Script
Save as `backup_db.ps1`:
```powershell
$timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$source = "instance\shopease.db"
$destination = "backups\shopease_backup_$timestamp.db"
Copy-Item $source $destination -Force
Write-Host "✓ Database backed up to $destination"
```

### Restore from Backup
```powershell
Copy-Item instance\shopease_backup_20260330_120000.db instance\shopease.db -Force
```

---

## 📈 Analytics Queries

### Monthly Revenue
```sql
SELECT 
    strftime('%Y-%m', order_date) as month,
    COUNT(*) as orders,
    SUM(total_amount) as revenue
FROM orders
GROUP BY month
ORDER BY month DESC;
```

### Customer Retention
```sql
SELECT 
    u.id,
    u.fullname,
    COUNT(o.id) as repeat_purchases,
    MIN(o.order_date) as first_order,
    MAX(o.order_date) as last_order
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id
HAVING repeat_purchases > 1;
```

### Average Order Value by Payment Method
```sql
SELECT 
    payment_method,
    AVG(total_amount) as avg_value,
    MIN(total_amount) as min_value,
    MAX(total_amount) as max_value
FROM orders
GROUP BY payment_method;
```

---

## 🆘 Troubleshooting

### Database Won't Open in DB Browser
- Ensure Flask app is not running
- Check file path is correct: `instance/shopease.db`
- Try running with administrator privileges

### "No such table" Error
- Database may be corrupted
- Run: `python init_db.py` to reset
- All data will be lost

### Changes Not Visible
- Click **Refresh** button in DB Browser
- Close and reopen the database
- Restart Flask application

### Permission Denied
- Close DB Browser
- Check Windows file permissions
- Try moving file to different location
- Disable antivirus temporarily for testing

---

## 📚 File Structure

```
ecommerce/
├── shopease.db              [Created automatically in instance/]
├── instance/
│   └── shopease.db          ← Database file location
├── app.py                   [Main Flask application]
├── init_db.py              [Database initialization script]
├── manage_db.py            [CLI database manager]
├── DATABASE_MANAGEMENT.md  [Detailed guide]
├── DB_QUICK_START.md       [Quick reference]
└── README.md              [This file]
```

---

## ✅ Getting Started Checklist

- [ ] Database file located at: `instance/shopease.db`
- [ ] Flask app running: `python app.py`
- [ ] DB Browser for SQLite downloaded and installed
- [ ] Can open database in DB Browser
- [ ] Can view users and orders tables
- [ ] Ran `python manage_db.py` successfully
- [ ] Created first database backup
- [ ] Understand SQL query basics
- [ ] Familiar with export functionality

---

## 🎯 Next Steps

1. **Start the Application**
   ```powershell
   python app.py
   ```

2. **Test with DB Browser**
   - Open `instance/shopease.db`
   - Browse the users and orders tables
   - Run a simple query

3. **Use Python Manager**
   ```powershell
   python manage_db.py
   ```
   - View statistics
   - Export data
   - Automate tasks

4. **Backup Your Data**
   ```powershell
   Copy-Item instance\shopease.db instance\shopease_backup.db
   ```

5. **Monitor & Maintain**
   - Regular backups
   - Query for analytics
   - Track business metrics

---

## 📞 Support Resources

- **DB Browser Help**: https://sqlitebrowser.org/docs/
- **SQLite Documentation**: https://www.sqlite.org/docs.html
- **Flask-SQLAlchemy**: https://flask-sqlalchemy.palletsprojects.com/
- **SQL Tutorial**: https://www.w3schools.com/sql/default.asp

---

**Your E-Commerce database is now professionally managed and ready for production!** 🚀

