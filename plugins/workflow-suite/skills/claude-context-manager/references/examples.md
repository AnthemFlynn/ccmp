# Claude.md Examples

This file provides concrete examples of well-structured `claude.md` files for different types of directories.

## Example 1: Source Code Directory

### src/services/

```markdown
# src/services/

This directory contains the business logic layer that sits between API routes
and the database. Services handle complex operations, business rules, and
orchestrate multiple database operations.

## Purpose

Services provide:
- Business logic implementation
- Transaction management
- Data validation and transformation
- Integration with external APIs
- Caching logic

## Directory Structure

```
services/
├── user-service.ts      # User management and authentication
├── order-service.ts     # Order processing and fulfillment
├── payment-service.ts   # Payment processing with Stripe
├── email-service.ts     # Email sending via SendGrid
└── cache-service.ts     # Redis caching utilities
```
```

## Key Patterns

### Service Class Structure

All services follow this pattern:

```typescript
export class UserService {
  constructor(
    private db: Database,
    private cache: CacheService,
    private logger: Logger
  ) {}

  async getUser(id: string): Promise<User> {
    // 1. Check cache
    // 2. Query database if cache miss
    // 3. Transform data
    // 4. Update cache
    // 5. Return result
  }
}
```

### Error Handling

Services throw domain-specific errors:
- `NotFoundError` - Resource doesn't exist
- `ValidationError` - Business rule violation
- `ConflictError` - Duplicate or conflicting resource
- `ExternalServiceError` - Third-party API failure

### Transaction Management

Multi-step operations use database transactions:

```typescript
async transferFunds(from: string, to: string, amount: number) {
  return this.db.transaction(async (trx) => {
    await this.debit(from, amount, trx);
    await this.credit(to, amount, trx);
  });
}
```

## Dependencies

### Internal
- `src/database/` - Database client and models
- `src/lib/logger` - Logging utilities
- `src/lib/config` - Configuration management

### External
- Stripe SDK - Payment processing
- SendGrid - Email delivery
- Redis - Caching layer

## Testing

Service tests are in `tests/services/`:
```bash
npm run test:services
```

Each service has:
- Unit tests with mocked dependencies
- Integration tests with test database

## Notes

- Services never directly access HTTP request/response objects
- All external API calls should have timeout and retry logic
- Cache invalidation happens within the service that modifies data
```

---

## Example 2: Test Directory

### tests/integration/

```markdown
# tests/integration/

Integration tests that verify multiple components working together, including
database operations, API endpoints, and external service integrations.

## Overview

These tests use a real test database and mock external services. They run
slower than unit tests but provide higher confidence in system behavior.

## Structure

```
integration/
├── api/           # Full API endpoint tests
├── services/      # Service layer with real database
├── workflows/     # End-to-end user workflows
└── fixtures/      # Shared test data and utilities
```
```

## Running Tests

```bash
# All integration tests (takes ~5 minutes)
npm run test:integration

# Specific test file
npm run test:integration -- api/user-endpoints.test.ts

# Watch mode for development
npm run test:integration:watch
```

## Test Environment

Integration tests use:
- **Database**: PostgreSQL test database (auto-created/destroyed)
- **Cache**: In-memory Redis
- **External APIs**: Mocked using `nock`
- **Time**: Frozen at `2025-01-01T00:00:00Z` using `timekeeper`

## Patterns

### Test Structure

```typescript
describe('User Registration Flow', () => {
  beforeAll(async () => {
    await setupTestDatabase();
  });

  afterAll(async () => {
    await teardownTestDatabase();
  });

  beforeEach(async () => {
    await clearTestData();
  });

  it('should create user and send welcome email', async () => {
    // Arrange
    const userData = fixtures.newUser();
    
    // Act
    const response = await api.post('/users', userData);
    
    // Assert
    expect(response.status).toBe(201);
    expect(emailMock).toHaveBeenCalledWith(
      expect.objectContaining({ to: userData.email })
    );
  });
});
```

### Fixtures

Use shared fixtures for consistency:
```typescript
import { fixtures } from './fixtures';

const user = fixtures.user();  // Random valid user
const admin = fixtures.user({ role: 'admin' });  // Admin user
```

## Database Management

### Test Database Setup

Test database is created automatically but can be manually reset:

```bash
npm run test:db:reset
```

### Migrations

Integration tests run against the latest schema. If migrations change:

1. Stop running tests
2. Run `npm run test:db:reset`
3. Restart tests

## Common Issues

- **Timeout errors**: Increase timeout for slow operations
  ```typescript
  it('slow operation', async () => {
    // ...
  }, 10000); // 10 second timeout
  ```

- **Port conflicts**: Tests use port 3001. Ensure nothing else uses it.

- **Database locks**: Tests should clean up connections. If stuck:
  ```bash
  npm run test:db:kill-connections
  ```

## Notes

- Integration tests should NOT make real external API calls
- Each test should be independent (no shared state)
- Use transactions for faster test data cleanup when possible
```

---

## Example 3: Configuration Directory

### config/

```markdown
# config/

Configuration management for all environments (development, staging, production).
Uses environment variables with typed validation and sensible defaults.

## Overview

Configuration is loaded from:
1. Environment variables (highest priority)
2. `.env` file (development only)
3. Default values (fallback)

## Files

- **index.ts**: Main config loader and validation
- **schema.ts**: Zod schemas for type-safe config
- **defaults.ts**: Default values for all settings
- **database.ts**: Database connection configuration
- **redis.ts**: Redis connection configuration
- **stripe.ts**: Stripe API configuration

## Usage

```typescript
import { config } from '@/config';

// Type-safe access
const dbUrl = config.database.url;
const stripeKey = config.stripe.apiKey;

// Environment check
if (config.isProduction) {
  // Production-specific logic
}
```

## Environment Variables

### Required (No Defaults)

These MUST be set in production:

```bash
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://host:6379
STRIPE_API_KEY=sk_live_xxxxx
JWT_SECRET=your-secret-key
```

### Optional (With Defaults)

```bash
# Server
PORT=3000
HOST=0.0.0.0
NODE_ENV=development

# Logging
LOG_LEVEL=info
LOG_FORMAT=json

# Features
ENABLE_RATE_LIMITING=true
ENABLE_ANALYTICS=false
```

### Development Setup

Copy example file:
```bash
cp .env.example .env
```

Then edit `.env` with your local values.

## Validation

Config is validated on startup using Zod schemas. Invalid config causes
immediate application failure with clear error messages:

```
❌ Configuration Error:
  - DATABASE_URL is required
  - STRIPE_API_KEY must start with 'sk_'
  - PORT must be a number between 1024 and 65535
```

## Adding New Config

1. Add schema to `schema.ts`:
```typescript
export const newFeatureSchema = z.object({
  enabled: z.boolean().default(false),
  apiKey: z.string().min(1),
});
```

2. Add to main config schema in `index.ts`

3. Update `.env.example` with documentation

4. Add to TypeScript types (auto-generated from schema)

## Security

- **Never commit .env files** (in .gitignore)
- **Never log sensitive config values**
- **Use separate keys per environment**
- **Rotate secrets regularly**

## Notes

- Config is loaded once at startup and cached
- Changes require application restart
- Use feature flags for runtime configuration changes
```

---

## Example 4: API Routes Directory

### src/api/routes/

```markdown
# src/api/routes/

HTTP route handlers that process requests, validate input, call services,
and format responses. All routes follow RESTful conventions.

## Structure

Routes are organized by resource:

```
routes/
├── users.ts         # User CRUD operations
├── posts.ts         # Post management
├── comments.ts      # Comment operations
├── auth.ts          # Authentication endpoints
└── health.ts        # Health check endpoints
```
```

## Route Pattern

Every route file exports a router:

```typescript
import { Router } from 'express';
import { authenticate, validate } from '../middleware';
import { userService } from '@/services';
import { createUserSchema, updateUserSchema } from '@/validators';

const router = Router();

// GET /users/:id
router.get('/:id', 
  authenticate,
  asyncHandler(async (req, res) => {
    const user = await userService.getUser(req.params.id);
    res.json(serialize.user(user));
  })
);

// POST /users
router.post('/',
  validate(createUserSchema),
  asyncHandler(async (req, res) => {
    const user = await userService.createUser(req.body);
    res.status(201).json(serialize.user(user));
  })
);

export default router;
```

## Conventions

### HTTP Methods
- `GET` - Retrieve resources (idempotent)
- `POST` - Create new resources
- `PUT` - Replace entire resource
- `PATCH` - Partial update
- `DELETE` - Remove resource

### Status Codes
- `200` - Success with body
- `201` - Resource created
- `204` - Success without body
- `400` - Bad request (validation error)
- `401` - Unauthorized (not logged in)
- `403` - Forbidden (logged in but no permission)
- `404` - Not found
- `409` - Conflict (duplicate resource)
- `500` - Server error

### URL Structure
- Plural nouns: `/users`, `/posts`
- Resource IDs: `/users/123`
- Nested resources: `/posts/123/comments`
- Actions as verbs: `/users/123/activate`

## Middleware Order

1. **Global middleware** (in app.ts)
   - Logging
   - CORS
   - Body parsing

2. **Route-specific middleware**
   - Authentication
   - Validation
   - Rate limiting

3. **Handler**
   - Business logic call
   - Response formatting

## Response Format

All JSON responses follow this structure:

```typescript
// Success
{
  "data": { /* resource or array */ },
  "meta": { /* pagination, etc */ }
}

// Error
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input",
    "details": [/* field errors */]
  }
}
```

## Adding New Routes

1. Create route file in this directory
2. Define handlers with validation
3. Register in `src/api/index.ts`:
   ```typescript
   app.use('/api/resource', resourceRoutes);
   ```
4. Add tests in `tests/api/`
5. Update OpenAPI spec in `docs/openapi.yaml`

## Testing Routes

```bash
# All route tests
npm run test:routes

# Specific route file
npm run test:routes -- users.test.ts
```

## Dependencies

- **Express Router** - Routing
- **express-validator** - Input validation
- **Services** - Business logic (in `src/services/`)
- **Serializers** - Response formatting (in `src/serializers/`)
```

---

## Example 5: Database/Models Directory

### src/models/

```markdown
# src/models/

TypeScript interfaces and Prisma schema definitions that define the data
models used throughout the application.

## Overview

Models are the single source of truth for data structure. They are used by:
- Database operations (Prisma)
- API validation
- Service layer type checking
- Response serialization

## Structure

```
models/
├── user.ts          # User model and types
├── post.ts          # Post model and types
├── comment.ts       # Comment model and types
└── index.ts         # Re-exports all models
```
```

The actual database schema is in `prisma/schema.prisma`.

## Model Pattern

```typescript
// Database model (from Prisma)
export type User = {
  id: string;
  email: string;
  passwordHash: string;
  createdAt: Date;
  updatedAt: Date;
};

// API representation (subset, no sensitive fields)
export type PublicUser = Omit<User, 'passwordHash'>;

// Creation input
export type CreateUserInput = {
  email: string;
  password: string;
};

// Update input (all optional)
export type UpdateUserInput = Partial<{
  email: string;
  password: string;
}>;
```

## Database Schema

The source of truth is `prisma/schema.prisma`:

```prisma
model User {
  id           String   @id @default(uuid())
  email        String   @unique
  passwordHash String
  createdAt    DateTime @default(now())
  updatedAt    DateTime @updatedAt
  posts        Post[]
}
```

Generate TypeScript types after schema changes:
```bash
npm run prisma:generate
```

## Relationships

- **User** → has many → **Post**
- **Post** → has many → **Comment**
- **Comment** → belongs to → **User**

Query with relations:
```typescript
const user = await prisma.user.findUnique({
  where: { id },
  include: { posts: true }
});
```

## Migrations

After modifying `schema.prisma`:

```bash
# Create migration
npm run prisma:migrate:dev

# Apply to production
npm run prisma:migrate:deploy
```

## Type Generation

After database changes, regenerate Prisma types:
```bash
npm run prisma:generate
```

This updates types in `node_modules/.prisma/client/` used throughout the app.

## Best Practices

- Keep models focused (single responsibility)
- Use explicit types for inputs/outputs
- Never expose `passwordHash` or other sensitive fields
- Use unions for status enums:
  ```typescript
  export type PostStatus = 'draft' | 'published' | 'archived';
  ```

## Notes

- Models are pure data structures (no methods)
- Business logic belongs in services, not models
- Use Prisma for all database operations (no raw SQL unless necessary)
```

---

## Template: Generic Directory

For directories that don't fit other categories:

```markdown
# [directory-name]/

[One sentence describing what this directory contains]

## Overview

[2-3 sentences explaining the purpose and scope of this directory]

## Structure

[If complex, show directory tree with brief descriptions]

## Key Files

[Highlight 3-5 most important files and their roles]

## Important Patterns

[Document any conventions, patterns, or standards used here]

## Dependencies

[What this depends on and what depends on this]

## Usage

[How to work with code in this directory, with examples if helpful]

## Notes

[Any gotchas, known issues, or additional context]
```

Use this template as a starting point and customize based on the specific directory's needs.
