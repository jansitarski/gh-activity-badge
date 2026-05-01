# Contributing to GitHub Stats Badge

Thank you for considering contributing to GitHub Stats Badge! This document provides guidelines and instructions for contributing.

## Code of Conduct

Be respectful, inclusive, and professional. We want this to be a welcoming community for everyone.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- **Clear title** describing the bug
- **Steps to reproduce** the issue
- **Expected behavior** vs actual behavior
- **Environment details** (OS, Python version, etc.)
- **Screenshots** if applicable
- **Logs** or error messages

### Suggesting Features

Feature requests are welcome! Please create an issue with:
- **Clear description** of the feature
- **Use case** - why is this feature needed?
- **Proposed implementation** (if you have ideas)
- **Alternatives considered**

### Submitting Pull Requests

1. **Fork the repository**
   ```bash
   gh repo fork jansitarski/github-stats-badge --clone
   cd github-stats-badge
   ```

2. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/bug-description
   ```

3. **Make your changes**
   - Write clear, readable code
   - Follow existing code style
   - Add comments for complex logic
   - Update documentation if needed

4. **Test your changes**
   ```bash
   # Test locally
   export GITHUB_USERNAME="testuser"
   export GITHUB_TOKEN="your-token"
   python3 src/generate_badge.py
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   # or
   git commit -m "fix: resolve issue with..."
   ```

   Use conventional commit messages:
   - `feat:` - New feature
   - `fix:` - Bug fix
   - `docs:` - Documentation changes
   - `style:` - Code style/formatting
   - `refactor:` - Code refactoring
   - `test:` - Adding tests
   - `chore:` - Maintenance tasks

6. **Push and create PR**
   ```bash
   git push origin your-branch-name
   gh pr create
   ```

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- GitHub account
- Personal Access Token with `repo` and `read:user` scopes

### Local Development

```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/github-stats-badge.git
cd github-stats-badge

# Set up environment
export GITHUB_USERNAME="your-test-username"
export GITHUB_TOKEN="your-pat"

# Make changes to src/generate_badge.py

# Test
python3 src/generate_badge.py

# Check output
ls -la gh_stats.svg
```

### Testing Changes

Before submitting a PR:

1. **Test basic functionality**
   ```bash
   python3 src/generate_badge.py
   ```

2. **Test with different configurations**
   ```bash
   export OUTPUT_PATH="test/badge.svg"
   export README_UPDATE="false"
   python3 src/generate_badge.py
   ```

3. **Verify no personal data leaked**
   ```bash
   grep -r "personal-username" .
   grep -r "specific-token" .
   ```

4. **Check Python syntax**
   ```bash
   python3 -m py_compile src/generate_badge.py
   ```

## Code Style

### Python

- Follow PEP 8 style guide
- Use type hints (Python 3.8+ syntax)
- Write docstrings for functions
- Keep functions focused and small
- Use descriptive variable names

**Example:**

```python
def format_number(value: int) -> str:
    """Format an integer with thousands separators.
    
    Args:
        value: The integer to format
        
    Returns:
        Formatted string with commas (e.g., "1,234")
    """
    return f"{value:,}"
```

### Documentation

- Use clear, concise language
- Include code examples
- Update README if adding features
- Add examples to `examples/` if applicable

## Areas for Contribution

### Good First Issues

- Documentation improvements
- Adding more examples
- Fixing typos
- Improving error messages

### Feature Ideas

- Theme customization (colors, fonts)
- Stat selection (choose which metrics)
- Multiple badge layouts (horizontal, compact)
- Caching to reduce API calls
- Support for organizations
- Language statistics
- Contribution heatmap

### Technical Improvements

- Add unit tests
- Improve error handling
- Optimize API calls
- Add validation for inputs
- Better logging

## Pull Request Process

1. **Create PR** with clear description
2. **Link related issues** if applicable
3. **Wait for review** - maintainer will review within a few days
4. **Address feedback** if requested
5. **Squash commits** if asked
6. **Merge** - maintainer will merge when ready

## Questions?

- **Open an issue** for questions about contributing
- **Check existing issues** - your question might be answered
- **Be patient** - this is maintained by volunteers

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Thank You!

Your contributions make this project better for everyone. Thank you for taking the time to contribute!
