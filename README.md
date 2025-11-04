# Clothing Shop - FastAPI E-commerce Application

A modern e-commerce web application built with FastAPI, MySQL, and Bootstrap for managing a clothing store.

## Features

- 🛍️ Product catalog with categories and brands
- 🔐 User authentication and authorization (Customer & Admin roles)
- 🛒 Shopping cart functionality
- 👤 User profile management
- 🔒 Secure password hashing with bcrypt
- 📱 Responsive design with Bootstrap
- 🤖 AI chatbot integration (ChatBoxAI)

## Technology Stack

- **Backend**: FastAPI 0.104.1
- **Database**: MySQL 8.x
- **Template Engine**: Jinja2
- **Authentication**: Password hashing with Passlib/bcrypt
- **Frontend**: Bootstrap 5.1.3, Font Awesome
- **Server**: Uvicorn

## Prerequisites

- Python 3.8+
- MySQL 8.x
- pip (Python package manager)

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/sonhaiptit/clothing_shop_fastapi.git
   cd clothing_shop_fastapi
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   - Copy `.env.example` to `.env`
   ```bash
   cp .env.example .env
   ```
   - Edit `.env` file and update your database credentials:
   ```env
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=your_password_here
   DB_NAME=clothing_shop
   DB_CHARSET=utf8mb4
   SECRET_KEY=your-secret-key-here
   ```

5. **Set up the database**
   - Create MySQL database:
   ```sql
   CREATE DATABASE clothing_shop CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
   - Import your database schema (if you have a SQL dump file)

## Database Schema

The application requires the following main tables:
- `nguoidung` - User accounts
- `khachhang` - Customer profiles
- `sanpham` - Products
- `danhmuc` - Categories
- `thuonghieu` - Brands
- `giohang` - Shopping carts
- `chitietgiohang` - Cart items

## Running the Application

1. **Start the development server**
   ```bash
   python main.py
   ```
   or
   ```bash
   python run.py
   ```

2. **Access the application**
   - Open your browser and navigate to: `http://localhost:8000`
   - The application will automatically find an available port if 8000 is busy

## Project Structure

```
clothing_shop_fastapi/
├── main.py              # Main application file with routes
├── run.py              # Alternative entry point
├── config.py           # Configuration management
├── db.py               # Database connection and pooling
├── auth.py             # Authentication utilities
├── models.py           # Pydantic models for validation
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
├── .gitignore         # Git ignore rules
├── templates/         # HTML templates (Jinja2)
│   ├── base.html
│   ├── index.html
│   ├── products.html
│   ├── product_detail.html
│   ├── login.html
│   ├── register.html
│   ├── cart.html
│   ├── profile.html
│   ├── edit_profile.html
│   └── admin/         # Admin templates
│       ├── dashboard.html
│       ├── products.html
│       └── orders.html
└── static/            # Static files (CSS, JS, images)
    ├── css/
    ├── js/
    └── img/
```

## API Endpoints

### Public Routes
- `GET /` - Home page
- `GET /products` - Product listing (with filtering)
- `GET /product/{product_id}` - Product detail
- `GET /login` - Login page
- `POST /login` - Login submission
- `GET /register` - Registration page
- `POST /register` - Registration submission

### Protected Routes (Require Authentication)
- `GET /profile` - User profile
- `GET /edit_profile` - Edit profile page
- `POST /edit_profile` - Update profile
- `GET /cart` - Shopping cart
- `POST /cart/add/{product_id}` - Add to cart
- `POST /cart/update/{cart_item_id}` - Update cart quantity
- `POST /cart/remove/{cart_item_id}` - Remove from cart
- `GET /logout` - Logout

## Security Features

- ✅ Password hashing with bcrypt
- ✅ Secure cookie handling (httponly, samesite, secure in production)
- ✅ SQL injection prevention with parameterized queries
- ✅ Environment-based configuration
- ✅ Connection pooling for database
- ✅ Input validation with Pydantic
- ✅ Rate limiting (5 login attempts/5min, 3 registrations/hour)
- ✅ Proper error logging

**Important for Production:**
- Set `DEBUG=False` in .env
- Use HTTPS in production (required for secure cookies)
- Change `SECRET_KEY` to a strong random value
- Enable secure cookie flag (automatically enabled when DEBUG=False)

## Development

### Code Quality
- Follow PEP 8 style guide
- Use type hints for better code clarity
- Implement proper error handling and logging

### Security Best Practices
- Never commit `.env` file to version control
- Use strong, unique passwords for database
- Change the `SECRET_KEY` in production
- Keep dependencies up to date
- Implement rate limiting for production

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is open source and available under the MIT License.

## Support

For support, email sonhaiptit@example.com or open an issue in the GitHub repository.

## Acknowledgments

- FastAPI framework
- Bootstrap for UI components
- Font Awesome for icons
- MySQL community
