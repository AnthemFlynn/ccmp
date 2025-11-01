# tests/[test-type]/

<!-- Replace [test-type] with: unit, integration, e2e, etc. -->

This directory contains [test type] tests for [what is being tested].

## Overview

<!-- Explain what these tests cover and their purpose -->

## Test Structure

```
[test-type]/
├── subdirectory1/    # Tests for X
├── subdirectory2/    # Tests for Y
└── helpers/          # Test utilities and fixtures
```

## Running Tests

```bash
# All tests in this directory
npm run test:[test-type]

# Specific test file
npm run test:[test-type] -- path/to/test.test.ts

# Watch mode
npm run test:[test-type]:watch
```

## Test Environment

<!-- Describe the test environment setup -->

These tests use:
- **Database**: [Description]
- **External Services**: [How mocked/handled]
- **Test Data**: [Where fixtures are located]

## Patterns

### Test Structure

<!-- Show the typical test structure -->

```typescript
describe('Feature Name', () => {
  beforeEach(() => {
    // Setup
  });

  afterEach(() => {
    // Cleanup
  });

  it('should do something', () => {
    // Arrange
    // Act
    // Assert
  });
});
```

### Fixtures and Factories

<!-- How to use test data -->

```typescript
import { fixtures } from './fixtures';

const user = fixtures.user();
const admin = fixtures.user({ role: 'admin' });
```

## Common Patterns

<!-- Document common testing patterns used -->

- Pattern 1: Description
- Pattern 2: Description

## Troubleshooting

<!-- Common issues and solutions -->

### Issue 1

Problem description and solution.

### Issue 2

Problem description and solution.

## Notes

<!-- Additional context -->

- Important note about test conventions
- Known limitations

---

*Last Updated: YYYY-MM-DD*
