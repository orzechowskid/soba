# Architecture Principles

## 1. Separation of Concerns

- Modules should own one domain of responsibility.
- Extract cross-cutting concerns (logging, auth, validation) rather than duplicating them.

## 2. Dependency Direction

- Dependencies flow inward: infrastructure → application layer → core domain.
- Leaf modules depend on nothing.
- Higher-level modules depend on abstractions, not implementations.

## 3. Interface Stability

- Public interfaces must be stable and backward-compatible.
- Internal implementation changes must not break consumers.
- Version before breaking.

## 4. Data Flow

- Data should flow in one direction through the system.
- Avoid circular data dependencies.
- Prefer explicit data passing over implicit/shared state.

## 5. State Management

- Minimize shared state.
- Prefer stateless services where possible.
- When state is necessary, make it explicit, versioned, and recoverable.

## 6. Scaling

- Design for independent scaling of components.
- Avoid tight coupling between services.
- Prefer horizontal scaling patterns over vertical scaling assumptions.

## 7. Security by Default

- Least privilege everywhere.
- Deny by default, grant explicitly.
- Validate at boundaries.
- Authenticate before authorizing.
- Assume the network is hostile.

## 8. Anti-Patterns

- Avoid: dependency injection abuse, premature optimization, god objects, circular dependencies, permanent feature flags, tight coupling to frameworks.
