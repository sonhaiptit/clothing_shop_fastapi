"""
Security checklist script for the Clothing Shop application.

This script checks for common security issues in the codebase.
"""

import os
import re
import sys
from pathlib import Path


class SecurityChecker:
    """Check for security issues in the codebase."""
    
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.ok = []
    
    def check_env_file(self):
        """Check if .env file exists and is in .gitignore."""
        if os.path.exists('.env'):
            self.warnings.append(".env file exists (good for development, ensure it's in .gitignore)")
        
        if os.path.exists('.env.example'):
            self.ok.append("✓ .env.example template exists")
        else:
            self.warnings.append(".env.example template not found")
        
        if os.path.exists('.gitignore'):
            with open('.gitignore', 'r') as f:
                gitignore_content = f.read()
                if '.env' in gitignore_content:
                    self.ok.append("✓ .env is in .gitignore")
                else:
                    self.issues.append("CRITICAL: .env file not in .gitignore!")
    
    def check_hardcoded_secrets(self):
        """Check for hardcoded secrets in Python files."""
        patterns = [
            (r'password\s*=\s*["\'][^"\']+["\']', 'Possible hardcoded password'),
            (r'secret\s*=\s*["\'][^"\']+["\']', 'Possible hardcoded secret'),
            (r'api_key\s*=\s*["\'][^"\']+["\']', 'Possible hardcoded API key'),
        ]
        
        python_files = Path('.').rglob('*.py')
        found_issues = False
        
        for file_path in python_files:
            if 'venv' in str(file_path) or '__pycache__' in str(file_path):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    for pattern, description in patterns:
                        matches = re.finditer(pattern, content, re.IGNORECASE)
                        for match in matches:
                            # Skip if it's in a comment or uses settings
                            line = content[max(0, match.start()-100):match.end()+20]
                            if '#' in line or 'settings.' in line or 'config.' in line:
                                continue
                            
                            self.warnings.append(f"{description} in {file_path}: {match.group()[:50]}...")
                            found_issues = True
            except Exception as e:
                pass
        
        if not found_issues:
            self.ok.append("✓ No obvious hardcoded secrets found")
    
    def check_sql_injection(self):
        """Check for potential SQL injection vulnerabilities."""
        python_files = Path('.').rglob('*.py')
        found_issues = False
        
        for file_path in python_files:
            if 'venv' in str(file_path) or '__pycache__' in str(file_path):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Look for string formatting in SQL queries
                    sql_format_patterns = [
                        r'execute\([^)]*%[^)]*\)',  # Should be using %s with params
                        r'execute\([^)]*f["\']',     # f-strings in SQL (dangerous)
                        r'execute\([^)]*\+',         # String concatenation (dangerous)
                    ]
                    
                    for pattern in sql_format_patterns:
                        if re.search(pattern, content):
                            # Check if it's using parameterized queries correctly
                            if 'execute(' in content and ', (' in content:
                                continue  # Likely using parameterized queries
                            
                            self.warnings.append(f"Potential SQL injection risk in {file_path}")
                            found_issues = True
                            break
            except Exception as e:
                pass
        
        if not found_issues:
            self.ok.append("✓ SQL queries appear to use parameterized statements")
    
    def check_password_hashing(self):
        """Check if password hashing is implemented."""
        if os.path.exists('auth.py'):
            with open('auth.py', 'r') as f:
                content = f.read()
                if 'bcrypt' in content or 'passlib' in content:
                    self.ok.append("✓ Password hashing is implemented")
                else:
                    self.issues.append("Password hashing not found in auth.py")
        else:
            self.warnings.append("auth.py not found - check password hashing implementation")
    
    def check_secure_cookies(self):
        """Check for secure cookie settings."""
        python_files = Path('.').rglob('*.py')
        
        for file_path in python_files:
            if 'venv' in str(file_path):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    if 'set_cookie' in content:
                        if 'httponly=True' in content:
                            self.ok.append("✓ Cookies use httponly flag")
                        else:
                            self.warnings.append("Cookies should use httponly=True")
                        break
            except Exception:
                pass
    
    def check_dependencies(self):
        """Check if requirements.txt has security-related packages."""
        if os.path.exists('requirements.txt'):
            with open('requirements.txt', 'r') as f:
                content = f.read()
                
                if 'passlib' in content or 'bcrypt' in content:
                    self.ok.append("✓ Password hashing library present")
                else:
                    self.issues.append("Missing password hashing library in requirements.txt")
                
                if 'pydantic' in content:
                    self.ok.append("✓ Pydantic for validation present")
        else:
            self.warnings.append("requirements.txt not found")
    
    def run_all_checks(self):
        """Run all security checks."""
        print("=" * 70)
        print("Security Checklist for Clothing Shop FastAPI")
        print("=" * 70)
        print()
        
        self.check_env_file()
        self.check_hardcoded_secrets()
        self.check_sql_injection()
        self.check_password_hashing()
        self.check_secure_cookies()
        self.check_dependencies()
        
        print("PASSED CHECKS:")
        print("-" * 70)
        for item in self.ok:
            print(f"  {item}")
        
        if self.warnings:
            print()
            print("WARNINGS:")
            print("-" * 70)
            for item in self.warnings:
                print(f"  ⚠ {item}")
        
        if self.issues:
            print()
            print("CRITICAL ISSUES:")
            print("-" * 70)
            for item in self.issues:
                print(f"  ✗ {item}")
        
        print()
        print("=" * 70)
        print(f"Summary: {len(self.ok)} passed, {len(self.warnings)} warnings, {len(self.issues)} critical issues")
        print("=" * 70)
        
        return len(self.issues) == 0


if __name__ == "__main__":
    checker = SecurityChecker()
    success = checker.run_all_checks()
    sys.exit(0 if success else 1)
