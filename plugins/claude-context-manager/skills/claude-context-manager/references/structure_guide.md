# Claude.md Structure Guide

This guide explains what makes an effective `claude.md` file and how to structure documentation for maximum utility when working with Claude.

## Purpose of claude.md Files

A `claude.md` file serves as context documentation that helps Claude (and humans) understand:

1. **What this directory contains** - Purpose and scope
2. **How code is organized** - Structure and patterns
3. **Key relationships** - Dependencies and connections
4. **Important context** - Gotchas, conventions, and decisions

## Core Principles

### 1. Be Specific and Concrete

❌ **Avoid vague descriptions:**
```markdown
## Overview
This directory contains utilities.
```

✅ **Be specific:**
```markdown
## Overview
This directory contains database utility functions for connection pooling,
query building, and transaction management. These utilities are used across
all services to ensure consistent database interactions.
```

### 2. Prioritize Actionable Information

Focus on information that helps someone understand how to work with the code:

- **Entry points** - Where to start reading/editing
- **Key patterns** - How things are typically done
- **Dependencies** - What relies on what
- **Gotchas** - Non-obvious behavior or limitations

### 3. Keep it Current

A stale `claude.md` is worse than none at all. Include:

- Maintenance notes ("Last updated: 2025-10-21")
- Who maintains this area
- How to update the documentation

## Recommended Structure

### Essential Sections

#### 1. Header and Overview (Required)

Start with a clear title and 1-3 sentence overview:

```markdown
# src/api/

This directory implements the REST API layer, handling HTTP requests,
validation, and response formatting. All endpoints follow OpenAPI 3.0
specification defined in `openapi.yaml`.
```

#### 2. Directory Structure (If Complex)

Show the layout with brief descriptions:

```markdown
## Directory Structure

```
api/
├── routes/        # Route handlers grouped by resource
├── middleware/    # Express middleware (auth, validation, logging)
├── validators/    # Request/response validation schemas
└── serializers/   # Response formatting utilities
```
```

#### 3. Key Files (If Applicable)

Highlight important files and their roles:

```markdown
## Key Files

- **index.ts**: API server initialization and middleware setup
- **routes.ts**: Central route registration
- **error-handler.ts**: Global error handling middleware
- **openapi.yaml**: API specification (source of truth for endpoints)
```

#### 4. Important Patterns (Critical)

Document conventions and patterns used in this directory:

```markdown
## Important Patterns

### Route Handler Structure

All route handlers follow this pattern:
1. Validate request (using Zod schemas in `validators/`)
2. Call service layer (never direct database access)
3. Serialize response (using serializers)
4. Handle errors (throw specific error types)

### Error Handling

- Use `ApiError` class for all API errors
- Status codes: 400 (validation), 401 (auth), 404 (not found), 500 (server)
- Errors are caught by global error handler middleware

### Naming Conventions

- Routes: kebab-case (`/user-profiles`)
- Files: kebab-case (`user-profile-routes.ts`)
- Handlers: camelCase (`getUserProfile`)
```

#### 5. Dependencies (Important)

Explain relationships with other parts of the codebase:

```markdown
## Dependencies

### Imports From
- `src/services/` - Business logic layer
- `src/models/` - Data models and types
- `src/lib/` - Shared utilities (logger, config)

### Used By
- All services make HTTP requests to these endpoints
- Frontend application at `/frontend`

### External Dependencies
- Express.js for routing
- Zod for validation
- OpenAPI Tools for spec validation
```

#### 6. Usage/Getting Started (For Complex Areas)

Help someone get started quickly:

```markdown
## Usage

### Adding a New Endpoint

1. Define the route in `openapi.yaml`
2. Create handler in `routes/{resource}-routes.ts`
3. Add validation schema in `validators/{resource}-validator.ts`
4. Add serializer in `serializers/{resource}-serializer.ts`
5. Register route in `routes.ts`

Example:
[Include minimal working example]

### Testing

Run API tests:
```bash
npm run test:api
```

Test single endpoint:
```bash
npm run test:api -- --grep "GET /users"
```
```

### Optional Sections

#### Architecture Decisions

Document important "why" decisions:

```markdown
## Architecture Decisions

### Why Express over Fastify?
- Team familiarity
- Better TypeScript support at time of decision
- Larger middleware ecosystem

### Why Separate Validators?
- Reusable across routes and tests
- Type inference for request/response objects
- Easier to maintain OpenAPI spec sync
```

#### Gotchas and Known Issues

Save others from pain:

```markdown
## Gotchas

- **Async Handler Wrapping**: All async route handlers must be wrapped with
  `asyncHandler()` or errors won't be caught properly
  
- **Query Parameter Parsing**: Express doesn't parse nested query params by
  default. Use `qs` library for complex queries.
  
- **Rate Limiting**: Applied at middleware level, not per-route. See
  `middleware/rate-limiter.ts` for configuration.
```

## What NOT to Include

Avoid these common pitfalls:

❌ **Don't duplicate what's obvious from code:**
```markdown
## Files
- user.ts - Contains user-related code
- product.ts - Contains product-related code
```

❌ **Don't write tutorials for basics:**
```markdown
## What is an API?
An API is an Application Programming Interface...
```

❌ **Don't include things that change frequently:**
```markdown
## Team
Current maintainers:
- Alice (alice@company.com) - Lead
- Bob (bob@company.com) - Backend
[This will be stale immediately]
```

✅ **Instead, link to maintained sources:**
```markdown
## Maintenance
See [CODEOWNERS](../../CODEOWNERS) for current maintainers.
```

## Hierarchy and Inheritance

### Root claude.md

The root `claude.md` provides high-level project context:

```markdown
# Project Name

## Overview
[High-level description of the entire project]

## Architecture
[System architecture overview]

## Directory Guide
- `/src` - Application source code ([claude.md](src/claude.md))
- `/tests` - Test suite ([claude.md](tests/claude.md))
- `/docs` - Documentation ([claude.md](docs/claude.md))

## Getting Started
[Setup and development workflow]
```

### Child claude.md Files

Child files inherit context from parent, so avoid repetition:

```markdown
# src/api/routes/

Specific information about route handlers only. See parent
[src/api/claude.md](../claude.md) for overall API structure.
```

## Maintenance

### Keep It Fresh

Add maintenance metadata:

```markdown
---
Last Updated: 2025-10-21
Maintainer: API Team (@api-team)
---
```

### Update Triggers

Update `claude.md` when:

- Major architectural changes occur
- New patterns are introduced
- Important files are added/removed/renamed
- Gotchas are discovered
- Team conventions change

### Review Regularly

- Quarterly reviews of all `claude.md` files
- Update during major refactors
- Validate during onboarding (new team members test docs)

## Templates by Directory Type

See [examples.md](examples.md) for complete templates for:
- Source code directories
- Test directories
- API/Service layers
- Configuration directories
- Documentation directories
- Library/utility directories
