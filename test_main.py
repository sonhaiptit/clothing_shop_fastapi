"""Basic tests for the Clothing Shop application."""
import pytest
from fastapi.testclient import TestClient
from main import app
from auth import hash_password, verify_password


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


class TestAuth:
    """Test authentication utilities."""
    
    def test_password_hashing(self):
        """Test password hashing and verification."""
        password = "test_password_123"
        hashed = hash_password(password)
        
        # Check that password is hashed
        assert hashed != password
        assert hashed.startswith('$2b$')
        
        # Check that verification works
        assert verify_password(password, hashed) is True
        assert verify_password("wrong_password", hashed) is False
    
    def test_different_hashes(self):
        """Test that same password produces different hashes."""
        password = "same_password"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        # Different hashes for same password (salt)
        assert hash1 != hash2
        
        # But both verify correctly
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestRoutes:
    """Test application routes."""
    
    def test_home_page(self, client):
        """Test home page loads."""
        response = client.get("/")
        assert response.status_code == 200
        assert b"Clothing Shop" in response.content
    
    def test_products_page(self, client):
        """Test products page loads."""
        response = client.get("/products")
        assert response.status_code == 200
    
    def test_login_page(self, client):
        """Test login page loads."""
        response = client.get("/login")
        assert response.status_code == 200
        assert b"login" in response.content.lower()
    
    def test_register_page(self, client):
        """Test register page loads."""
        response = client.get("/register")
        assert response.status_code == 200
        # Check for register-related content
        content = response.content.decode('utf-8').lower()
        assert "register" in content or "đăng ký" in content
    
    def test_product_detail_not_found(self, client):
        """Test product detail with invalid ID."""
        response = client.get("/product/999999")
        # Should return 404 or redirect
        assert response.status_code in [404, 302]
    
    def test_cart_requires_auth(self, client):
        """Test cart page requires authentication."""
        response = client.get("/cart", follow_redirects=False)
        # Should redirect to login
        assert response.status_code == 302
        assert "/login" in response.headers.get("location", "")
    
    def test_profile_requires_auth(self, client):
        """Test profile page requires authentication."""
        response = client.get("/profile", follow_redirects=False)
        # Should redirect to login
        assert response.status_code == 302
        assert "/login" in response.headers.get("location", "")
    
    def test_pagination_parameters(self, client):
        """Test products page with pagination."""
        response = client.get("/products?page=1&per_page=12")
        assert response.status_code == 200
        
        response = client.get("/products?page=2")
        assert response.status_code == 200


class TestConfig:
    """Test configuration."""
    
    def test_config_loads(self):
        """Test that configuration loads."""
        from config import settings
        
        assert settings.db_host is not None
        assert settings.db_name is not None
        assert settings.secret_key is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
