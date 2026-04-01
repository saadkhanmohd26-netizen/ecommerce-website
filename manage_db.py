"""
Database Management Script for ShopEase E-Commerce
Manage users and orders directly from CLI
"""
from app import app, db, User, Order
from datetime import datetime
import json

def print_header(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def view_all_users():
    """Display all registered users"""
    print_header("ALL REGISTERED USERS")
    users = User.query.all()
    
    if not users:
        print("\n✗ No users found")
        return
    
    print(f"\n{'ID':<4} {'Full Name':<20} {'Email':<30} {'Joined':<15}")
    print("-"*70)
    
    for user in users:
        email = user.email[:28] + ".." if len(user.email) > 30 else user.email
        print(f"{user.id:<4} {user.fullname:<20} {email:<30}")

def view_all_orders():
    """Display all orders"""
    print_header("ALL CUSTOMER ORDERS")
    orders = Order.query.all()
    
    if not orders:
        print("\n✗ No orders found")
        return
    
    print(f"\n{'Order#':<8} {'User ID':<8} {'Amount':<12} {'Method':<15} {'Date':<18}")
    print("-"*65)
    
    for order in orders:
        date_str = order.order_date.strftime("%Y-%m-%d %H:%M")
        method = order.payment_method.replace("_", " ").title()[:14]
        print(f"{order.id:<8} {order.user_id:<8} ₹{order.total_amount:<10,.0f} {method:<15} {date_str:<18}")

def view_user_details(user_id):
    """View detailed information for a specific user"""
    user = User.query.get(user_id)
    
    if not user:
        print(f"\n✗ User with ID {user_id} not found")
        return
    
    print_header(f"USER DETAILS - ID: {user_id}")
    print(f"\nFull Name:  {user.fullname}")
    print(f"Email:      {user.email}")
    print(f"User ID:    {user.id}")
    
    # Get user's orders
    user_orders = Order.query.filter_by(user_id=user_id).all()
    print(f"\nTotal Orders: {len(user_orders)}")
    
    if user_orders:
        total_spent = sum(order.total_amount for order in user_orders)
        print(f"Total Spent:  ₹{total_spent:,.0f}")
        print(f"\nOrder History:")
        print("-"*60)
        
        for order in user_orders:
            date_str = order.order_date.strftime("%Y-%m-%d %H:%M")
            method = order.payment_method.replace("_", " ").title()
            print(f"  Order #{order.id} - {date_str} - ₹{order.total_amount:,.0f} ({method})")

def view_order_details(order_id):
    """View detailed information for a specific order"""
    order = Order.query.get(order_id)
    
    if not order:
        print(f"\n✗ Order with ID {order_id} not found")
        return
    
    user = User.query.get(order.user_id)
    items = json.loads(order.items)
    
    print_header(f"ORDER DETAILS - ORDER #{order_id}")
    
    print(f"\nCustomer Information:")
    print(f"  Name:   {user.fullname}")
    print(f"  Email:  {user.email}")
    
    print(f"\nOrder Information:")
    print(f"  Order ID:      #{order.id}")
    print(f"  Order Date:    {order.order_date.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Status:        {order.status.upper()}")
    
    print(f"\nDelivery Address:")
    print(f"  {order.street_address}")
    print(f"  {order.city}, {order.state} {order.zip_code}")
    print(f"  Phone: {order.phone}")
    
    print(f"\nOrder Items:")
    print("-"*60)
    for i, item in enumerate(items, 1):
        subtotal = item["price"] * item["quantity"]
        print(f"  {i}. {item['name']}")
        print(f"     Qty: {item['quantity']} × ₹{item['price']:,.0f} = ₹{subtotal:,.0f}")
    
    print(f"\nPayment Summary:")
    print(f"  Total Amount:  ₹{order.total_amount:,.0f}")
    print(f"  Payment Method: {order.payment_method.replace('_', ' ').title()}")

def get_statistics():
    """Show database statistics"""
    print_header("DATABASE STATISTICS")
    
    total_users = db.session.query(User).count()
    total_orders = db.session.query(Order).count()
    
    print(f"\nUsers:")
    print(f"  Total Registered Users: {total_users}")
    
    print(f"\nOrders:")
    print(f"  Total Orders Placed: {total_orders}")
    
    if total_orders > 0:
        total_revenue = db.session.query(db.func.sum(Order.total_amount)).scalar()
        avg_order = db.session.query(db.func.avg(Order.total_amount)).scalar()
        
        print(f"  Total Revenue: ₹{total_revenue:,.0f}")
        print(f"  Average Order Value: ₹{avg_order:,.0f}")
        
        # Payment method breakdown
        payment_stats = db.session.query(
            Order.payment_method,
            db.func.count(Order.id).label('count'),
            db.func.sum(Order.total_amount).label('total')
        ).group_by(Order.payment_method).all()
        
        print(f"\nPayment Methods:")
        for method, count, total in payment_stats:
            method_name = method.replace("_", " ").title()
            print(f"  {method_name}: {count} orders, ₹{total:,.0f}")

def export_users_csv():
    """Export all users to CSV"""
    import csv
    
    users = User.query.all()
    filename = "users_export.csv"
    
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'Full Name', 'Email'])
        for user in users:
            writer.writerow([user.id, user.fullname, user.email])
    
    print(f"\n✓ Users exported to {filename}")

def export_orders_csv():
    """Export all orders to CSV"""
    import csv
    
    orders = Order.query.all()
    filename = "orders_export.csv"
    
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Order ID', 'User ID', 'Customer Name', 'Amount', 'Payment Method', 'Order Date', 'Status'])
        for order in orders:
            user = User.query.get(order.user_id)
            writer.writerow([
                order.id, 
                order.user_id, 
                user.fullname,
                f"₹{order.total_amount:,.0f}",
                order.payment_method.replace("_", " ").title(),
                order.order_date.strftime('%Y-%m-%d %H:%M:%S'),
                order.status.upper()
            ])
    
    print(f"\n✓ Orders exported to {filename}")

def main_menu():
    """Display main menu"""
    while True:
        print("\n" + "="*60)
        print("  SHOPEASE DATABASE MANAGEMENT SYSTEM")
        print("="*60)
        print("""
  1. View All Users
  2. View All Orders
  3. View User Details
  4. View Order Details
  5. Database Statistics
  6. Export Users to CSV
  7. Export Orders to CSV
  8. Exit
        """)
        
        choice = input("Enter your choice (1-8): ").strip()
        
        if choice == '1':
            view_all_users()
        elif choice == '2':
            view_all_orders()
        elif choice == '3':
            user_id = input("Enter User ID: ").strip()
            try:
                view_user_details(int(user_id))
            except ValueError:
                print("✗ Invalid User ID")
        elif choice == '4':
            order_id = input("Enter Order ID: ").strip()
            try:
                view_order_details(int(order_id))
            except ValueError:
                print("✗ Invalid Order ID")
        elif choice == '5':
            get_statistics()
        elif choice == '6':
            export_users_csv()
        elif choice == '7':
            export_orders_csv()
        elif choice == '8':
            print("\n✓ Goodbye!\n")
            break
        else:
            print("\n✗ Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")

if __name__ == '__main__':
    with app.app_context():
        main_menu()
