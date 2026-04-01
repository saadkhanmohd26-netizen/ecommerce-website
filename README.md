# ShopEase - Simple E-Commerce Desktop Application
### College Mini Project (Python + HTML + CSS + JavaScript)

## Technologies Used
- **Backend:** Python 3, Flask
- **Frontend:** HTML5, CSS3, JavaScript
- **Templating:** Jinja2

## How to Run

1. **Install Python 3** (if not already installed)

2. **Install Flask:**
   ```
   pip install flask
   ```

3. **Run the application:**
   ```
   python app.py
   ```

4. **Open in browser:**
   ```
   http://localhost:5000
   ```

## Features
- Browse products with category filtering
- Add products to shopping cart
- Update quantities / remove items from cart
- Order summary with total calculation
- Place order (checkout) with flash notification
- Responsive design with clean CSS
- Session-based cart (no database required)

## Project Structure
```
ecommerce/
├── app.py                  # Flask application (routes & logic)
├── requirements.txt        # Python dependencies
├── README.md
├── static/
│   ├── css/
│   │   └── style.css       # All CSS styles
│   └── images/             # Product images
│       ├── headphones.jpg
│       ├── watch.jpg
│       ├── bag.jpg
│       ├── sneakers.jpg
│       ├── mug.jpg
│       └── speaker.jpg
└── templates/
    ├── base.html            # Base layout template
    ├── index.html           # Product listing page
    └── cart.html            # Shopping cart page
```
