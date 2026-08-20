# Coding Standards

## 1. NAMING

- Use descriptive, unambiguous names.
- Match language idioms.
- No abbreviations unless universally recognized.
- No trailing type suffixes (e.g., `UserDto`, `AuthService`). Prefer clear, semantic names.

## 2. FILE & MODULE STRUCTURE

- One primary concept per file.
- Co-locate related code (handlers, validators, types for the same domain in the same directory).
- Keep import chains shallow. Prefer explicit imports over barrel exports.

## 3. FUNCTION SIZE

- Single responsibility per function.
- Split if function exceeds ~30 lines or performs multiple distinct operations.
- Prefer many small, composable functions over few large ones.

## 4. ERROR HANDLING

- Fail fast, close to the source.
- Use specific error types.
- Never swallow errors silently.
- Log errors with context (what was attempted, what failed, current state).
- Distinguish recoverable vs. fatal errors.

## 5. COMMENTS & DOCUMENTATION

- Comments explain why, not what. Code should be self-documenting.
- Inline documentation required for public APIs and exported functions.
- Remove stale comments.

## 6. IMPORT ORDERING

- Group imports: standard library → third-party → internal.
- Alphabetize within groups.
- Remove unused imports.

## 7. DEAD CODE

- Delete commented-out code blocks.
- Delete unused functions, types, and constants.
- Version control preserves history; dead code does not.

## 8. DATA & STATE

- Keep state close to where it's used.
- Avoid shared mutable state where possible.
- Prefer immutable data structures for data that flows across boundaries.
