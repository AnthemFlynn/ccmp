# Code Conventions

## Language & Framework

**Primary Language**: [Python / JavaScript / TypeScript / etc.]  
**Version**: [Version number]  
**Framework**: [Framework name and version]

## Code Style

### Naming Conventions

**Variables & Functions**:
- Style: [snake_case / camelCase / PascalCase]
- Examples: `user_name`, `calculate_total`, `process_payment`

**Classes**:
- Style: [PascalCase / snake_case]
- Examples: `UserService`, `PaymentProcessor`, `OrderRepository`

**Constants**:
- Style: [UPPER_SNAKE_CASE / camelCase]
- Examples: `MAX_RETRIES`, `API_BASE_URL`, `DEFAULT_TIMEOUT`

**Files**:
- Style: [snake_case / kebab-case]
- Examples: `user_service.py`, `payment-processor.ts`

### Formatting

- **Line Length**: [80 / 100 / 120] characters maximum
- **Indentation**: [2 / 4] spaces (no tabs)
- **String Quotes**: [single / double / either] quotes
- **Trailing Commas**: [required / optional / never]

## Type Safety

**Type Hints/Annotations**: [Required / Encouraged / Optional]

```python
# Example for Python
def process_user(user_id: int, name: str) -> User:
    """Process user with given ID and name."""
    pass
```

**Type Checking**: [Tool name: mypy / TypeScript / Flow / None]

## Documentation

### Docstrings

**Style**: [Google / NumPy / Sphinx / JSDoc]

**Required for**:
- [ ] Public functions
- [ ] Public classes
- [ ] Modules
- [ ] Complex algorithms

**Example**:
```python
def calculate_total(items: List[Item], tax_rate: float) -> Decimal:
    """
    Calculate total price including tax.
    
    Args:
        items: List of items to total
        tax_rate: Tax rate as decimal (e.g., 0.08 for 8%)
    
    Returns:
        Total price including tax
    
    Raises:
        ValueError: If tax_rate is negative
    """
    pass
```

### Comments

**When to Comment**:
- Complex algorithms
- Non-obvious business logic
- Workarounds or hacks
- TODOs and FIXMEs

**What NOT to Comment**:
- Self-explanatory code
- What code does (let code be self-documenting)
- Commented-out code (delete instead)

## Testing

### Test Coverage

- **Minimum Coverage**: [85 / 90 / 95]%
- **New Code Coverage**: [90 / 95 / 100]%

### Test Organization

```
tests/
├── unit/           # Unit tests
│   └── test_[module].py
├── integration/    # Integration tests
│   └── test_[feature].py
└── e2e/           # End-to-end tests
    └── test_[scenario].py
```

### Test Naming

Pattern: `test_[what]_[condition]_[expected]`

Examples:
- `test_user_creation_with_valid_data_succeeds`
- `test_payment_processing_with_insufficient_funds_raises_error`
- `test_order_total_calculation_with_discount_returns_correct_amount`

### Test Structure

```python
def test_something():
    # Arrange - Set up test data
    user = User(name="John")
    
    # Act - Perform the action
    result = process_user(user)
    
    # Assert - Verify results
    assert result.processed == True
```

## Error Handling

### Exception Handling

- **Custom Exceptions**: [Required / Optional] for domain errors
- **Logging**: [Always / Sometimes / Never] log exceptions
- **Re-raising**: [Wrap / Re-raise / Handle] exceptions appropriately

**Example**:
```python
try:
    result = risky_operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}")
    raise DomainError("User-friendly message") from e
```

## Git Conventions

### Commit Messages

**Format**: [Conventional Commits / Custom / Free-form]

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Test additions or changes
- `chore`: Build process or auxiliary tool changes

**Examples**:
```
feat(auth): Add JWT token generation
fix(payments): Correct tax calculation for international orders
docs(api): Update authentication endpoint documentation
```

### Branch Naming

**Format**: `<type>/<description>`

**Types**:
- `feature/` - New features
- `bugfix/` - Bug fixes
- `hotfix/` - Urgent production fixes
- `refactor/` - Code refactoring
- `docs/` - Documentation updates

**Examples**:
- `feature/user-authentication`
- `bugfix/payment-calculation-error`
- `hotfix/security-vulnerability`

## Code Review

### Review Checklist

- [ ] Code follows style guidelines
- [ ] Tests included and passing
- [ ] Documentation updated
- [ ] No commented-out code
- [ ] Error handling appropriate
- [ ] Performance considerations addressed
- [ ] Security implications reviewed

### Review Standards

- **Required Approvals**: [1 / 2 / 3]
- **Automated Checks**: [Must pass / Should pass]
- **Response Time**: [24 / 48 / 72] hours

## Security

### Security Practices

- [ ] No secrets in code
- [ ] Input validation on all external data
- [ ] SQL injection prevention
- [ ] XSS prevention (for web apps)
- [ ] CSRF protection (for web apps)
- [ ] Proper authentication and authorization

### Sensitive Data

- Use environment variables for secrets
- Never log sensitive information
- Sanitize error messages sent to users

## Performance

### Performance Guidelines

- [ ] Avoid N+1 queries
- [ ] Use appropriate data structures
- [ ] Cache when beneficial
- [ ] Profile before optimizing
- [ ] Document performance-critical code

## Accessibility (for web projects)

- [ ] Semantic HTML
- [ ] ARIA labels where needed
- [ ] Keyboard navigation support
- [ ] Screen reader compatibility
- [ ] Color contrast compliance

## Additional Guidelines

[Add any project-specific conventions here]

---

**Last Updated**: [YYYY-MM-DD]  
**Maintained By**: [Team/Person]
