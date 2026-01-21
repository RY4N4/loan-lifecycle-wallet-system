# Contributing to Loan Lifecycle & Wallet System

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to this project.

## 🌟 How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates.

**When reporting a bug, please include:**
- Clear description of the issue
- Steps to reproduce
- Expected behavior
- Actual behavior
- Screenshots (if applicable)
- Environment details (OS, Python version, database)
- Error messages/logs

**Example:**
```markdown
**Bug**: EMI calculator shows NaN

**Steps to reproduce:**
1. Go to Apply for Loan tab
2. Enter amount: -1000
3. EMI shows NaN

**Expected**: Should show error message for negative amount

**Environment**: macOS 13, Python 3.11, Chrome 120
```

### Suggesting Enhancements

Enhancement suggestions are welcome! Please include:
- Clear description of the enhancement
- Why it would be useful
- Possible implementation approach
- Mockups/examples (if applicable)

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow the code style guidelines below
   - Add tests if applicable
   - Update documentation

4. **Commit your changes**
   ```bash
   git commit -m "feat: add amazing feature"
   ```
   
   Use conventional commits:
   - `feat:` - New feature
   - `fix:` - Bug fix
   - `docs:` - Documentation changes
   - `style:` - Code style changes (formatting)
   - `refactor:` - Code refactoring
   - `test:` - Adding tests
   - `chore:` - Maintenance tasks

5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Open a Pull Request**
   - Provide a clear title and description
   - Reference any related issues
   - Include screenshots for UI changes

## 💻 Development Setup

### Prerequisites
- Python 3.9+
- Git
- Virtual environment tool

### Setup Steps

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/loan-lifecycle-backend.git
cd loan-lifecycle-backend

# Add upstream remote
git remote add upstream https://github.com/ORIGINAL_OWNER/loan-lifecycle-backend.git

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your settings

# Initialize database
python seed_data.py

# Run backend
uvicorn app.main:app --reload --port 8000

# In another terminal, run frontend
cd frontend
python3 serve.py
```

## 📝 Code Style Guidelines

### Python (Backend)

**Follow PEP 8:**
```python
# Good
def calculate_emi(principal: float, rate: float, tenure: int) -> float:
    """Calculate EMI using standard formula."""
    monthly_rate = rate / 12 / 100
    emi = principal * monthly_rate * ((1 + monthly_rate) ** tenure) / (((1 + monthly_rate) ** tenure) - 1)
    return round(emi, 2)

# Bad
def calc_emi(p,r,t):
    return p*r*t  # Wrong formula, no types, unclear
```

**Key principles:**
- Use type hints
- Write docstrings for functions/classes
- Keep functions small and focused
- Use meaningful variable names
- Add comments for complex logic

### JavaScript (Frontend)

**Follow modern JS conventions:**
```javascript
// Good
async function loadUserLoans() {
    showLoading();
    try {
        const response = await fetch(`${API_BASE_URL}/api/loans/my-loans`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        const loans = await response.json();
        displayLoans(loans);
    } catch (error) {
        showToast('Failed to load loans', 'error');
    } finally {
        hideLoading();
    }
}

// Bad
function getLoans() {
    fetch('http://localhost:8000/api/loans/my-loans').then(r => r.json()).then(d => console.log(d))
}
```

**Key principles:**
- Use `async/await` over promises
- Handle errors gracefully
- Use `const` and `let`, avoid `var`
- Use template literals
- Add JSDoc comments

### CSS

```css
/* Good - Use CSS variables and clear naming */
.loan-card {
    background: var(--card-background);
    border-radius: var(--border-radius);
    padding: 1.5rem;
    transition: transform 0.2s;
}

.loan-card:hover {
    transform: translateY(-2px);
}

/* Bad - Magic numbers and unclear names */
.card {
    background: #fff;
    border-radius: 8px;
    padding: 24px;
}
```

## 🧪 Testing

### Backend Tests

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_loans.py

# Run with coverage
python -m pytest --cov=app tests/
```

### Frontend Tests

```bash
# Open browser console and check for errors
# Test all user flows manually
```

### Test Checklist
- [ ] All existing tests pass
- [ ] New tests added for new features
- [ ] Edge cases covered
- [ ] Error handling tested
- [ ] UI tested on Chrome, Firefox, Safari

## 📚 Documentation

### When to Update Documentation

- Adding new features
- Changing API endpoints
- Modifying configuration
- Changing setup process
- Fixing bugs that affect usage

### Documentation Files

- `README.md` - Main project documentation
- `EASY_SETUP.md` - Setup instructions
- `API_REFERENCE.md` - API documentation
- `frontend/README.md` - Frontend guide
- `ARCHITECTURE.md` - System design

## 🎯 Areas for Contribution

### High Priority
- [ ] Unit tests for services
- [ ] Integration tests for API
- [ ] Docker containerization
- [ ] CI/CD pipeline
- [ ] Error monitoring
- [ ] Performance optimization

### Medium Priority
- [ ] Email notifications
- [ ] Export transactions (CSV/PDF)
- [ ] Advanced search/filters
- [ ] Charts and analytics
- [ ] Dark mode
- [ ] Multi-language support

### Low Priority
- [ ] Mobile app
- [ ] PWA features
- [ ] Real-time notifications (WebSocket)
- [ ] Social authentication
- [ ] Credit score integration

## 🚫 What Not to Do

- Don't commit sensitive data (.env files, credentials)
- Don't commit generated files (*.pyc, __pycache__)
- Don't make unrelated changes in a single PR
- Don't copy-paste code without attribution
- Don't ignore existing code style
- Don't submit untested code

## ✅ Pull Request Checklist

Before submitting your PR, make sure:

- [ ] Code follows project style guidelines
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Commit messages are clear
- [ ] Branch is up-to-date with main
- [ ] No merge conflicts
- [ ] Screenshots included (for UI changes)
- [ ] Tested on multiple browsers (for frontend)

## 🤝 Code Review Process

1. **Automated Checks**: CI/CD runs tests and linters
2. **Peer Review**: Maintainers review code
3. **Feedback**: Requested changes or approval
4. **Merge**: Approved PRs are merged

**Review criteria:**
- Code quality and style
- Test coverage
- Documentation
- Performance impact
- Security considerations

## 💬 Communication

- **Issues**: For bug reports and feature requests
- **Pull Requests**: For code contributions
- **Discussions**: For general questions and ideas

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 🙏 Thank You!

Your contributions make this project better for everyone. We appreciate your time and effort!

---

**Questions?** Open an issue or reach out to the maintainers.

**Happy coding!** 🚀
