import json
import logging
from pydantic import BaseModel, EmailStr, Field
from fastapi.responses import StreamingResponse
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from mysql.connector import Error
import os
import uvicorn
import socket

# Import custom modules
from config import settings
from db import get_db_connection, init_connection_pool
from auth import hash_password, verify_password
from utils import login_limiter, register_limiter

from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.debug else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan."""
    # Startup
    init_connection_pool()
    logger.info("Application started successfully")
    yield
    # Shutdown (if needed in the future)
    logger.info("Application shutting down")


app = FastAPI(title="Clothing Shop", debug=settings.debug, lifespan=lifespan)

# Tạo thư mục
os.makedirs("static/css", exist_ok=True)
os.makedirs("static/js", exist_ok=True)
os.makedirs("templates", exist_ok=True)
os.makedirs("templates/admin", exist_ok=True)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def get_current_user(request: Request) -> Optional[Dict[str, str]]:
    """Get current authenticated user from cookies.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Dictionary with user_id, username, and role if authenticated, None otherwise
    """
    user_id = request.cookies.get("user_id")
    username = request.cookies.get("username")
    role = request.cookies.get("role")

    if user_id and username and role:
        return {"user_id": user_id, "username": username, "role": role}
    return None


# ===== ROUTES =====

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the home page with featured products.
    
    Args:
        request: FastAPI request object
        
    Returns:
        HTML response with home page
    """
    current_user = get_current_user(request)

    featured_products = []
    db = get_db_connection()
    if db:
        try:
            cursor = db.cursor(dictionary=True)
            cursor.execute("""
                           SELECT sp.*, dm.ten as ten_danhmuc, th.ten as ten_thuonghieu
                           FROM sanpham sp
                                    LEFT JOIN danhmuc dm ON sp.maDM = dm.maDM
                                    LEFT JOIN thuonghieu th ON sp.maTH = th.maTH
                           ORDER BY sp.maSP DESC LIMIT 8
                           """)
            featured_products = cursor.fetchall()
            cursor.close()
        except Error as e:
            logger.error(f"Error fetching products: {e}")
        finally:
            if db.is_connected():
                db.close()

    return templates.TemplateResponse("index.html", {
        "request": request,
        "current_user": current_user,
        "featured_products": featured_products
    })


@app.get("/products", response_class=HTMLResponse)
async def products(
        request: Request,
        category: Optional[str] = None,
        brand: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        per_page: int = 12
):
    """Render products page with filtering and pagination.
    
    Args:
        request: FastAPI request object
        category: Filter by category name
        brand: Filter by brand name
        search: Search term for product name
        page: Page number for pagination (default 1)
        per_page: Items per page (default 12)
        
    Returns:
        HTML response with products page
    """
    current_user = get_current_user(request)
    products_list = []
    categories = []
    brands = []
    total_products = 0
    total_pages = 0

    db = get_db_connection()
    if db:
        try:
            cursor = db.cursor(dictionary=True)

            # Build base query
            query = """
                    SELECT sp.*, dm.ten as ten_danhmuc, th.ten as ten_thuonghieu
                    FROM sanpham sp
                             LEFT JOIN danhmuc dm ON sp.maDM = dm.maDM
                             LEFT JOIN thuonghieu th ON sp.maTH = th.maTH
                    WHERE 1 = 1
                    """
            count_query = "SELECT COUNT(*) as total FROM sanpham sp LEFT JOIN danhmuc dm ON sp.maDM = dm.maDM LEFT JOIN thuonghieu th ON sp.maTH = th.maTH WHERE 1 = 1"
            params = []

            if category:
                query += " AND dm.ten = %s"
                count_query += " AND dm.ten = %s"
                params.append(category)

            if brand:
                query += " AND th.ten = %s"
                count_query += " AND th.ten = %s"
                params.append(brand)

            if search:
                query += " AND sp.ten LIKE %s"
                count_query += " AND sp.ten LIKE %s"
                params.append(f"%{search}%")

            # Get total count
            cursor.execute(count_query, params)
            total_products = cursor.fetchone()['total']
            total_pages = (total_products + per_page - 1) // per_page

            # Add pagination
            offset = (page - 1) * per_page
            query += " ORDER BY sp.maSP DESC LIMIT %s OFFSET %s"
            
            cursor.execute(query, params + [per_page, offset])
            products_list = cursor.fetchall()

            cursor.execute("SELECT ten FROM danhmuc")
            categories = [row['ten'] for row in cursor.fetchall()]

            cursor.execute("SELECT ten FROM thuonghieu")
            brands = [row['ten'] for row in cursor.fetchall()]

            cursor.close()

        except Error as e:
            logger.error(f"Error fetching products: {e}")
        finally:
            if db.is_connected():
                db.close()

    return templates.TemplateResponse("products.html", {
        "request": request,
        "current_user": current_user,
        "products": products_list,
        "categories": categories,
        "brands": brands,
        "selected_category": category,
        "selected_brand": brand,
        "search_query": search,
        "page": page,
        "total_pages": total_pages,
        "total_products": total_products
    })


@app.get("/product/{product_id}", response_class=HTMLResponse)
async def product_detail(request: Request, product_id: int):
    current_user = get_current_user(request)
    product = None

    db = get_db_connection()
    if db:
        try:
            cursor = db.cursor(dictionary=True)
            cursor.execute("""
                           SELECT sp.*, dm.ten as ten_danhmuc, th.ten as ten_thuonghieu
                           FROM sanpham sp
                                    LEFT JOIN danhmuc dm ON sp.maDM = dm.maDM
                                    LEFT JOIN thuonghieu th ON sp.maTH = th.maTH
                           WHERE sp.maSP = %s
                           """, (product_id,))
            product = cursor.fetchone()
            cursor.close()
        except Error as e:
            logger.error(f"Error fetching product detail: {e}")
        finally:
            if db.is_connected():
                db.close()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return templates.TemplateResponse("product_detail.html", {
        "request": request,
        "current_user": current_user,
        "product": product
    })


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def login(
        request: Request,
        username: str = Form(...),
        password: str = Form(...)
):
    """Handle user login with rate limiting.
    
    Args:
        request: FastAPI request object
        username: Username from form
        password: Password from form
        
    Returns:
        Redirect to home or login page with error
    """
    # Get client IP for rate limiting
    client_ip = request.client.host if request.client else "unknown"
    
    # Check rate limit
    if not login_limiter.is_allowed(client_ip):
        logger.warning(f"Rate limit exceeded for IP: {client_ip}")
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Quá nhiều lần thử đăng nhập. Vui lòng thử lại sau 5 phút."
        })
    
    db = get_db_connection()
    if not db:
        logger.error("Database connection failed during login")
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Database connection failed"
        })

    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM nguoidung WHERE tenDangNhap = %s", (username,))
        user = cursor.fetchone()
        cursor.close()

        if user and verify_password(password, user['matKhau']):
            response = RedirectResponse(url="/", status_code=302)
            response.set_cookie(key="user_id", value=str(user['maND']), httponly=True, samesite="lax")
            response.set_cookie(key="username", value=username, httponly=True, samesite="lax")
            response.set_cookie(key="role", value=user['vaiTro'], httponly=True, samesite="lax")
            logger.info(f"User {username} logged in successfully")
            return response
        else:
            logger.warning(f"Failed login attempt for username: {username}")
            return templates.TemplateResponse("login.html", {
                "request": request,
                "error": "Tên đăng nhập hoặc mật khẩu không đúng"
            })
    except Error as e:
        logger.error(f"Login error: {e}")
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Đăng nhập thất bại"
        })
    finally:
        if db.is_connected():
            db.close()


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register")
async def register(
        request: Request,
        username: str = Form(...),
        password: str = Form(...),
        confirm_password: str = Form(...),
        fullname: str = Form(...),
        phone: str = Form(...)
):
    """Handle user registration with rate limiting.
    
    Args:
        request: FastAPI request object
        username: Desired username
        password: Password
        confirm_password: Password confirmation
        fullname: User's full name
        phone: Phone number
        
    Returns:
        Redirect to login or register page with error
    """
    # Get client IP for rate limiting
    client_ip = request.client.host if request.client else "unknown"
    
    # Check rate limit
    if not register_limiter.is_allowed(client_ip):
        logger.warning(f"Registration rate limit exceeded for IP: {client_ip}")
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Quá nhiều lần đăng ký. Vui lòng thử lại sau 1 giờ."
        })
    
    if password != confirm_password:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Mật khẩu xác nhận không khớp"
        })

    # Validate password strength
    if len(password) < 6:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Mật khẩu phải có ít nhất 6 ký tự"
        })

    db = get_db_connection()
    if not db:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Database connection failed"
        })

    try:
        cursor = db.cursor()

        cursor.execute("SELECT maND FROM nguoidung WHERE tenDangNhap = %s", (username,))
        if cursor.fetchone():
            return templates.TemplateResponse("register.html", {
                "request": request,
                "error": "Tên đăng nhập đã tồn tại"
            })

        # Hash the password before storing
        hashed_password = hash_password(password)

        cursor.execute("""
                       INSERT INTO nguoidung (tenDangNhap, matKhau, ten, soDienThoai, vaiTro)
                       VALUES (%s, %s, %s, %s, 'USER')
                       """, (username, hashed_password, fullname, phone))

        user_id = cursor.lastrowid
        cursor.execute("INSERT INTO khachhang (maND) VALUES (%s)", (user_id,))

        db.commit()
        logger.info(f"New user registered: {username}")

        response = RedirectResponse(url="/login", status_code=302)
        return response

    except Error as e:
        db.rollback()
        logger.error(f"Registration error: {e}")
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Đăng ký thất bại"
        })
    finally:
        if db.is_connected():
            db.close()


@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("user_id")
    response.delete_cookie("username")
    response.delete_cookie("role")
    return response


@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    # 1. Kiểm tra xem người dùng đã đăng nhập chưa
    current_user = get_current_user(request)
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)

    user_details = None
    db = get_db_connection()
    if db:
        try:
            cursor = db.cursor(dictionary=True)

            # 2. Lấy thông tin chi tiết của người dùng từ database
            cursor.execute(
                "SELECT tenDangNhap, ten, soDienThoai, vaiTro FROM nguoidung WHERE maND = %s",
                (current_user['user_id'],)
            )
            user_details = cursor.fetchone()
            cursor.close()
        except Error as e:
            logger.error(f"Error fetching user profile: {e}")
        finally:
            if db.is_connected():
                db.close()

    if not user_details:
        # Nếu không tìm thấy thông tin (dù đã đăng nhập) thì báo lỗi
        raise HTTPException(status_code=404, detail="User not found")

    # 3. Trả về file profile.html và gửi dữ liệu user_details qua
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "current_user": current_user,
        "user_details": user_details
    })


# Hiển thị trang/form để chỉnh sửa thông tin
@app.get("/edit_profile", response_class=HTMLResponse)
async def edit_profile_page(request: Request):
    current_user = get_current_user(request)
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)

    user_details = None
    db = get_db_connection()
    if db:
        try:
            cursor = db.cursor(dictionary=True)
            # Lấy thông tin hiện tại để điền vào form
            cursor.execute(
                "SELECT ten, soDienThoai FROM nguoidung WHERE maND = %s",
                (current_user['user_id'],)
            )
            user_details = cursor.fetchone()
            cursor.close()
        except Error as e:
            logger.error(f"Error fetching user details for edit: {e}")
        finally:
            if db.is_connected():
                db.close()

    if not user_details:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")

    return templates.TemplateResponse("edit_profile.html", {
        "request": request,
        "current_user": current_user,
        "user_details": user_details
    })


# Xử lý dữ liệu khi người dùng nhấn "Lưu thay đổi"
@app.post("/edit_profile")
async def handle_edit_profile(
        request: Request,
        fullname: str = Form(...),  # Lấy "Họ và tên" từ form
        phone: str = Form(...)  # Lấy "Số điện thoại" từ form
):
    current_user = get_current_user(request)
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)

    db = get_db_connection()
    if not db:
        raise HTTPException(status_code=500, detail="Lỗi kết nối database")

    try:
        cursor = db.cursor()
        # Câu lệnh UPDATE để cập nhật database
        cursor.execute(
            "UPDATE nguoidung SET ten = %s, soDienThoai = %s WHERE maND = %s",
            (fullname, phone, current_user['user_id'])
        )
        db.commit()  # Lưu thay đổi
        cursor.close()
    except Error as e:
        logger.error(f"Error updating profile: {e}")
        db.rollback()  # Hoàn tác nếu có lỗi
    finally:
        if db.is_connected():
            db.close()

    # Sau khi cập nhật xong, chuyển hướng người dùng về trang profile
    return RedirectResponse(url="/profile", status_code=302)


@app.get("/cart", response_class=HTMLResponse)
async def cart_page(request: Request):
    current_user = get_current_user(request)
    if not current_user:
        return RedirectResponse(url="/login")

    cart_items = []
    total = 0

    db = get_db_connection()
    if db:
        try:
            cursor = db.cursor(dictionary=True)

            cursor.execute("""
                           SELECT gh.maGH
                           FROM giohang gh
                                    JOIN khachhang kh ON gh.maKH = kh.maKH
                                    JOIN nguoidung nd ON kh.maND = nd.maND
                           WHERE nd.maND = %s
                             AND gh.trangThai = 'Đang mua'
                           """, (current_user['user_id'],))
            cart = cursor.fetchone()

            if cart:
                cursor.execute("""
                               SELECT ctgh.*, sp.ten, sp.gia, sp.hinhAnh, sp.soLuong as stock
                               FROM chitietgiohang ctgh
                                        JOIN sanpham sp ON ctgh.maSP = sp.maSP
                               WHERE ctgh.maGH = %s
                               """, (cart['maGH'],))
                cart_items = cursor.fetchall()

                for item in cart_items:
                    item['subtotal'] = item['soLuong'] * item['gia']
                    total += item['subtotal']

            cursor.close()

        except Error as e:
            logger.error(f"Error fetching cart: {e}")
        finally:
            if db.is_connected():
                db.close()

    return templates.TemplateResponse("cart.html", {
        "request": request,
        "current_user": current_user,
        "cart_items": cart_items,
        "total": total
    })


@app.post("/cart/add/{product_id}")
async def add_to_cart(
        request: Request,
        product_id: int,
        quantity: int = Form(1)
):
    current_user = get_current_user(request)
    if not current_user:
        return RedirectResponse(url="/login")

    db = get_db_connection()
    if db:
        try:
            cursor = db.cursor()

            cursor.execute("SELECT maKH FROM khachhang WHERE maND = %s", (current_user['user_id'],))
            customer = cursor.fetchone()
            if not customer:
                cursor.close()
                raise HTTPException(status_code=404, detail="Customer not found")

            customer_id = customer[0]

            cursor.execute("SELECT maGH FROM giohang WHERE maKH = %s AND trangThai = 'Đang mua'", (customer_id,))
            cart = cursor.fetchone()

            if not cart:
                cursor.execute("INSERT INTO giohang (maKH) VALUES (%s)", (customer_id,))
                cart_id = cursor.lastrowid
            else:
                cart_id = cart[0]

            cursor.execute("SELECT maCTGH, soLuong FROM chitietgiohang WHERE maGH = %s AND maSP = %s",
                           (cart_id, product_id))
            existing_item = cursor.fetchone()

            if existing_item:
                new_quantity = existing_item[1] + quantity
                cursor.execute("UPDATE chitietgiohang SET soLuong = %s WHERE maCTGH = %s",
                               (new_quantity, existing_item[0]))
            else:
                cursor.execute("INSERT INTO chitietgiohang (maGH, maSP, soLuong) VALUES (%s, %s, %s)",
                               (cart_id, product_id, quantity))

            db.commit()
            cursor.close()

        except Error as e:
            logger.error(f"Error adding to cart: {e}")
        finally:
            if db.is_connected():
                db.close()

    return RedirectResponse(url="/cart", status_code=302)


@app.post("/cart/update/{cart_item_id}")
async def update_cart_item(
        request: Request,
        cart_item_id: int,
        action: str = Form(...)  # Sẽ nhận giá trị "increase" hoặc "decrease"
):
    current_user = get_current_user(request)
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)

    db = get_db_connection()
    if not db:
        raise HTTPException(status_code=500, detail="Database connection failed")

    try:
        cursor = db.cursor(dictionary=True)

        # Lấy số lượng hiện tại của item và số lượng tồn kho (stock)
        cursor.execute("""
                       SELECT ctgh.soLuong, sp.soLuong as stock
                       FROM chitietgiohang ctgh
                                JOIN sanpham sp ON ctgh.maSP = sp.maSP
                       WHERE ctgh.maCTGH = %s
                       """, (cart_item_id,))
        item = cursor.fetchone()

        if not item:
            raise HTTPException(status_code=404, detail="Item not found")

        new_quantity = item['soLuong']

        # Logic tăng/giảm
        if action == "increase" and item['soLuong'] < item['stock']:
            new_quantity += 1
        elif action == "decrease" and item['soLuong'] > 1:
            new_quantity -= 1

        # Cập nhật số lượng mới vào database
        cursor.execute(
            "UPDATE chitietgiohang SET soLuong = %s WHERE maCTGH = %s",
            (new_quantity, cart_item_id)
        )

        db.commit()
        cursor.close()

    except Error as e:
        logger.error(f"Error updating cart: {e}")
        db.rollback()
    finally:
        if db.is_connected():
            db.close()

    # Tải lại trang giỏ hàng
    return RedirectResponse(url="/cart", status_code=302)


@app.post("/cart/remove/{cart_item_id}")
async def remove_from_cart(
        request: Request,
        cart_item_id: int
):
    current_user = get_current_user(request)
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)

    db = get_db_connection()
    if not db:
        raise HTTPException(status_code=500, detail="Database connection failed")

    try:
        cursor = db.cursor()

        # Xóa thẳng item khỏi chi tiết giỏ hàng
        cursor.execute("DELETE FROM chitietgiohang WHERE maCTGH = %s", (cart_item_id,))

        db.commit()
        cursor.close()

    except Error as e:
        logger.error(f"Error removing from cart: {e}")
        db.rollback()
    finally:
        if db.is_connected():
            db.close()

    # Tải lại trang giỏ hàng
    return RedirectResponse(url="/cart", status_code=302)


def find_available_port(start_port=8000, max_port=8010) -> int:
    """Find an available port to run the server.
    
    Args:
        start_port: Starting port number to check
        max_port: Maximum port number to check
        
    Returns:
        Available port number
    """
    for port in range(start_port, max_port + 1):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return port
        except OSError:
            continue
    return start_port


if __name__ == "__main__":
    port = find_available_port(settings.port, settings.port + 10)
    logger.info(f"Starting Clothing Shop on http://{settings.host}:{port}")
    print(f"   Starting Clothing Shop on http://{settings.host}:{port}")
    print(f"   Available routes:")
    print(f"   http://{settings.host}:{port} - Trang chủ")
    print(f"   http://{settings.host}:{port}/products - Sản phẩm")
    print(f"   http://{settings.host}:{port}/login - Đăng nhập")
    print(f"   http://{settings.host}:{port}/register - Đăng ký")
    uvicorn.run(app, host=settings.host, port=port, reload=settings.debug)