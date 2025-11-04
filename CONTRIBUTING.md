# Contributing Guide

## Development Setup

### Prerequisites
- Python 3.8 or higher
- MySQL 8.x
- Git

### Initial Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/sonhaiptit/clothing_shop_fastapi.git
   cd clothing_shop_fastapi
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Set up database**
   - See DATABASE.md for schema
   - Run migrate_passwords.py if you have existing data

## Code Style

### Python
- Follow PEP 8
- Use type hints where appropriate
- Add docstrings to functions
- Keep functions focused and small

### Example
```python
def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Get user by ID from database.
    
    Args:
        user_id: User ID to look up
        
    Returns:
        User dictionary or None if not found
    """
    # Implementation
```

## Testing

### Running Tests
```bash
# Run all tests
pytest test_main.py -v

# Run specific test class
pytest test_main.py::TestAuth -v

# Run with coverage
pytest --cov=. test_main.py
```

### Writing Tests
- Add tests for new features
- Test both success and error cases
- Use descriptive test names

```python
def test_user_registration_with_valid_data(self, client):
    """Test that user can register with valid data."""
    # Test implementation
```

## Security

### Before Committing
1. **Run security check**
   ```bash
   python security_check.py
   ```

2. **Check for sensitive data**
   - No passwords or API keys in code
   - Use environment variables
   - Check .gitignore includes .env

3. **Verify password hashing**
   - All passwords must use bcrypt
   - Never store plain text passwords

## Making Changes

### Workflow
1. Create a feature branch
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes
   - Keep commits focused
   - Write clear commit messages

3. Test your changes
   ```bash
   python security_check.py
   pytest test_main.py -v
   ```

4. Commit and push
   ```bash
   git add .
   git commit -m "Add feature: description"
   git push origin feature/your-feature-name
   ```

5. Create a Pull Request

### Commit Messages
- Use present tense ("Add feature" not "Added feature")
- Be descriptive but concise
- Reference issues if applicable

Good:
```
Add pagination to product listing
Fix SQL injection vulnerability in search
Update password hashing to use bcrypt
```

Bad:
```
Fixed stuff
Update
Changes
```

## Database Changes

1. Document schema changes in DATABASE.md
2. Create migration script if needed
3. Test on local database first
4. Consider backward compatibility

## Adding New Features

### Checklist
- [ ] Code follows style guide
- [ ] Tests added for new functionality
- [ ] Documentation updated (README.md, docstrings)
- [ ] Security check passes
- [ ] No sensitive data in code
- [ ] Database changes documented

### Security Considerations
When adding features:
- Validate all user inputs
- Use parameterized SQL queries
- Add rate limiting for sensitive endpoints
- Use proper authentication/authorization
- Log security-relevant events

## Common Tasks

### Adding a New Endpoint
```python
@app.get("/new-endpoint", response_class=HTMLResponse)
async def new_endpoint(request: Request):
    """Endpoint description.
    
    Args:
        request: FastAPI request object
        
    Returns:
        HTML response
    """
    current_user = get_current_user(request)
    # Implementation
    return templates.TemplateResponse("template.html", {
        "request": request,
        "current_user": current_user
    })
```

### Adding Password Validation
```python
from utils import validate_phone_number

phone = Form(...)
if not validate_phone_number(phone):
    # Handle error
```

### Adding Rate Limiting
```python
from utils import api_limiter

@app.post("/endpoint")
async def endpoint(request: Request):
    client_ip = request.client.host if request.client else "unknown"
    
    if not api_limiter.is_allowed(client_ip):
        raise HTTPException(status_code=429, detail="Too many requests")
    
    # Process request
```

## Troubleshooting

### Common Issues

**Database Connection Failed**
- Check .env configuration
- Verify MySQL is running
- Check credentials

**Import Errors**
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`

**Tests Failing**
- Check database is set up
- Verify .env file exists
- Check for deprecated dependencies

## Getting Help

1. Check documentation (README.md, DATABASE.md)
2. Look at existing code examples
3. Run security and syntax checks
4. Open an issue on GitHub

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [MySQL Documentation](https://dev.mysql.com/doc/)
- [Python Best Practices](https://docs.python-guide.org/)
