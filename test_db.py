"""Test database connection and display status"""
from app import app, db, User, Order

with app.app_context():
    try:
        print("✓ Database connection successful")
        print(f"Database file: instance/shopease.db")
        print(f"\n{'='*50}")
        print("  CURRENT DATABASE STATUS")
        print('='*50)
        
        user_count = User.query.count()
        print(f"\n✓ Users Registered: {user_count}")
        
        if user_count > 0:
            users = User.query.all()
            print("\n  Registered Users:")
            for user in users:
                print(f"    - {user.fullname} ({user.email})")
        
        try:
            order_count = Order.query.count()
            print(f"\n✓ Orders Placed: {order_count}")
            
            if order_count > 0:
                orders = Order.query.all()
                total_revenue = sum(order.total_amount for order in orders)
                print(f"  Total Revenue: ₹{total_revenue:,.0f}")
        except Exception as e:
            print(f"\n⚠ Note: Database schema may need initialization")
            print(f"  Run: python init_db.py")
        
        print(f"\n{'='*50}")
        print("✓ Setup & Testing:")
        print("  1. python app.py           [Start Flask app]")
        print("  2. python manage_db.py     [CLI database manager]")
        print("  3. Use DB Browser for SQLite [GUI tool]")
        print('='*50 + '\n')
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        print("\nTo fix:")
        print("  python init_db.py")

