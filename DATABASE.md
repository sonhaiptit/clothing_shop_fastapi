# Database Schema Documentation

## Overview
This document describes the database schema for the Clothing Shop application.

## Tables

### nguoidung (Users)
Stores all user accounts.

| Column | Type | Description |
|--------|------|-------------|
| maND | INT | Primary key, user ID |
| tenDangNhap | VARCHAR | Username (unique) |
| matKhau | VARCHAR | Hashed password (bcrypt) |
| ten | VARCHAR | Full name |
| soDienThoai | VARCHAR | Phone number |
| vaiTro | ENUM('USER', 'ADMIN') | User role |

**Indexes recommended:**
- PRIMARY KEY on `maND`
- UNIQUE INDEX on `tenDangNhap`
- INDEX on `vaiTro` for role-based queries

### khachhang (Customers)
Links to users table for customer-specific data.

| Column | Type | Description |
|--------|------|-------------|
| maKH | INT | Primary key, customer ID |
| maND | INT | Foreign key to nguoidung |

**Indexes recommended:**
- PRIMARY KEY on `maKH`
- UNIQUE INDEX on `maND`
- FOREIGN KEY constraint on `maND` → `nguoidung(maND)`

### sanpham (Products)
Stores product information.

| Column | Type | Description |
|--------|------|-------------|
| maSP | INT | Primary key, product ID |
| ten | VARCHAR | Product name |
| gia | DECIMAL | Product price |
| soLuong | INT | Stock quantity |
| hinhAnh | VARCHAR | Image URL/path |
| moTa | TEXT | Product description |
| maDM | INT | Foreign key to danhmuc |
| maTH | INT | Foreign key to thuonghieu |

**Indexes recommended:**
- PRIMARY KEY on `maSP`
- INDEX on `maDM` for category filtering
- INDEX on `maTH` for brand filtering
- INDEX on `ten` for product search
- FOREIGN KEY constraints

### danhmuc (Categories)
Product categories.

| Column | Type | Description |
|--------|------|-------------|
| maDM | INT | Primary key, category ID |
| ten | VARCHAR | Category name |

**Indexes recommended:**
- PRIMARY KEY on `maDM`
- UNIQUE INDEX on `ten`

### thuonghieu (Brands)
Product brands.

| Column | Type | Description |
|--------|------|-------------|
| maTH | INT | Primary key, brand ID |
| ten | VARCHAR | Brand name |

**Indexes recommended:**
- PRIMARY KEY on `maTH`
- UNIQUE INDEX on `ten`

### giohang (Shopping Carts)
Shopping cart instances.

| Column | Type | Description |
|--------|------|-------------|
| maGH | INT | Primary key, cart ID |
| maKH | INT | Foreign key to khachhang |
| trangThai | VARCHAR | Cart status ('Đang mua', 'Đã thanh toán') |

**Indexes recommended:**
- PRIMARY KEY on `maGH`
- INDEX on `maKH` and `trangThai` for active cart lookup
- FOREIGN KEY on `maKH` → `khachhang(maKH)`

### chitietgiohang (Cart Items)
Items in shopping carts.

| Column | Type | Description |
|--------|------|-------------|
| maCTGH | INT | Primary key, cart item ID |
| maGH | INT | Foreign key to giohang |
| maSP | INT | Foreign key to sanpham |
| soLuong | INT | Quantity |

**Indexes recommended:**
- PRIMARY KEY on `maCTGH`
- INDEX on `maGH` for cart item lookup
- INDEX on `maSP` for product references
- FOREIGN KEY constraints

## Example Schema Creation

```sql
-- Create database
CREATE DATABASE IF NOT EXISTS clothing_shop 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE clothing_shop;

-- Users table
CREATE TABLE nguoidung (
    maND INT AUTO_INCREMENT PRIMARY KEY,
    tenDangNhap VARCHAR(50) NOT NULL UNIQUE,
    matKhau VARCHAR(255) NOT NULL,  -- bcrypt hashes are ~60 chars
    ten VARCHAR(100) NOT NULL,
    soDienThoai VARCHAR(15),
    vaiTro ENUM('USER', 'ADMIN') DEFAULT 'USER',
    INDEX idx_role (vaiTro)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Categories
CREATE TABLE danhmuc (
    maDM INT AUTO_INCREMENT PRIMARY KEY,
    ten VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Brands
CREATE TABLE thuonghieu (
    maTH INT AUTO_INCREMENT PRIMARY KEY,
    ten VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Products
CREATE TABLE sanpham (
    maSP INT AUTO_INCREMENT PRIMARY KEY,
    ten VARCHAR(200) NOT NULL,
    gia DECIMAL(10, 2) NOT NULL,
    soLuong INT DEFAULT 0,
    hinhAnh VARCHAR(255),
    moTa TEXT,
    maDM INT,
    maTH INT,
    FOREIGN KEY (maDM) REFERENCES danhmuc(maDM) ON DELETE SET NULL,
    FOREIGN KEY (maTH) REFERENCES thuonghieu(maTH) ON DELETE SET NULL,
    INDEX idx_category (maDM),
    INDEX idx_brand (maTH),
    INDEX idx_name (ten)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Customers
CREATE TABLE khachhang (
    maKH INT AUTO_INCREMENT PRIMARY KEY,
    maND INT NOT NULL UNIQUE,
    FOREIGN KEY (maND) REFERENCES nguoidung(maND) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Shopping carts
CREATE TABLE giohang (
    maGH INT AUTO_INCREMENT PRIMARY KEY,
    maKH INT NOT NULL,
    trangThai VARCHAR(50) DEFAULT 'Đang mua',
    FOREIGN KEY (maKH) REFERENCES khachhang(maKH) ON DELETE CASCADE,
    INDEX idx_customer_status (maKH, trangThai)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Cart items
CREATE TABLE chitietgiohang (
    maCTGH INT AUTO_INCREMENT PRIMARY KEY,
    maGH INT NOT NULL,
    maSP INT NOT NULL,
    soLuong INT DEFAULT 1,
    FOREIGN KEY (maGH) REFERENCES giohang(maGH) ON DELETE CASCADE,
    FOREIGN KEY (maSP) REFERENCES sanpham(maSP) ON DELETE CASCADE,
    INDEX idx_cart (maGH),
    INDEX idx_product (maSP)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

## Notes

1. **Character Set**: All tables use `utf8mb4` for proper Vietnamese character support
2. **Password Storage**: The `matKhau` column must be VARCHAR(255) to accommodate bcrypt hashes
3. **Foreign Keys**: Use ON DELETE CASCADE/SET NULL appropriately
4. **Indexes**: Recommended indexes improve query performance
5. **Existing Data**: If migrating from plain text passwords, use `migrate_passwords.py`
