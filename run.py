import uvicorn
import socket

def find_available_port(start_port=8000, max_port=8010):
    for port in range(start_port, max_port + 1):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return port
        except OSError:
            continue
    return start_port

if __name__ == "__main__":
    port = find_available_port()
    print(f"   Starting Clothing Shop on http://localhost:{port}")
    print(f"   Available routes:")
    print(f"   http://localhost:{port} - Trang chủ")
    print(f"   http://localhost:{port}/products - Sản phẩm")
    print(f"   http://localhost:{port}/login - Đăng nhập")
    print(f"   http://localhost:{port}/register - Đăng ký")
    uvicorn.run("main:app", host="127.0.0.1", port=port, reload=True)