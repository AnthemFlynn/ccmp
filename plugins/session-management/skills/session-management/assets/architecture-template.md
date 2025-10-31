# Project Architecture

## Architecture Pattern

**Pattern**: [Hexagonal / Layered / Microservices / MVC / Clean / DDD]

### Core Principles
- [Principle 1]
- [Principle 2]
- [Principle 3]

## Project Structure

```
[Your project structure here]

Example for hexagonal:
src/
├── domain/         # Business logic (no external dependencies)
│   ├── models/     # Domain models
│   ├── services/   # Business services
│   └── exceptions/ # Domain exceptions
├── ports/          # Interface definitions (contracts)
│   ├── repositories/  # Data access interfaces
│   └── providers/     # External service interfaces
├── adapters/       # External integrations
│   ├── database/   # Database implementations
│   ├── api/        # External API clients
│   └── messaging/  # Message queue adapters
└── application/    # Use case orchestration
    └── usecases/   # Application use cases
```

## Key Interfaces

List the important interfaces/contracts in your system:

- **[IRepository]**: [Description]
- **[IService]**: [Description]
- **[IProvider]**: [Description]

## Architectural Decisions

Document major architectural decisions:

### Decision 1: [Title]
**Date**: [YYYY-MM-DD]  
**Context**: [Why this was needed]  
**Decision**: [What was decided]  
**Rationale**: [Why this approach]

### Decision 2: [Title]
**Date**: [YYYY-MM-DD]  
**Context**: [Why this was needed]  
**Decision**: [What was decided]  
**Rationale**: [Why this approach]

## Patterns & Practices

### Design Patterns Used
- **[Pattern Name]**: [Where and why used]
- **[Pattern Name]**: [Where and why used]

### Best Practices
- [Practice 1]
- [Practice 2]
- [Practice 3]

## Dependencies Flow

Describe how dependencies flow in your architecture:

```
[Dependency flow diagram or description]

Example for hexagonal:
Outside → Adapters → Ports → Domain
         ↑                    ↓
         ← Application ←──────
```

## Testing Strategy

- **Unit Tests**: [What to unit test and how]
- **Integration Tests**: [Integration boundaries]
- **E2E Tests**: [End-to-end scenarios]

## Notes for Developers

Additional guidance for developers working in this codebase:

- [Important note 1]
- [Important note 2]
- [Important note 3]
