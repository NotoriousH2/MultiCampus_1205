# CLAUDE.md - AI Assistant Guide

This document provides essential context for AI assistants working with this repository.

## Repository Overview

**Repository:** MultiCampus_1205
**Status:** New repository (initialized December 2024)
**Primary Branch:** `main` (to be established)

### Purpose

> *TODO: Add project description once development begins*

This repository is part of the MultiCampus project ecosystem.

---

## Project Structure

```
MultiCampus_1205/
├── CLAUDE.md          # This file - AI assistant guidance
└── (project files)    # To be added as development begins
```

### Directory Conventions (Recommended)

When adding code to this repository, follow these common patterns:

| Directory | Purpose |
|-----------|---------|
| `src/` | Source code |
| `tests/` | Test files |
| `docs/` | Documentation |
| `config/` | Configuration files |
| `scripts/` | Build/utility scripts |

---

## Development Workflow

### Getting Started

```bash
# Clone the repository
git clone <repository-url>

# Navigate to the project
cd MultiCampus_1205

# Install dependencies (once package manager is set up)
# npm install / yarn install / pip install -r requirements.txt
```

### Git Conventions

**Branch Naming:**
- Feature branches: `feature/<description>`
- Bug fixes: `fix/<description>`
- AI assistant branches: `claude/<session-id>`

**Commit Messages:**
- Use clear, descriptive messages
- Start with a verb (Add, Fix, Update, Remove, Refactor)
- Keep the first line under 72 characters

**Example commits:**
```
Add initial project structure
Fix authentication error handling
Update documentation for API endpoints
Refactor database connection logic
```

---

## Code Conventions

### General Guidelines

1. **Readability First:** Write clear, self-documenting code
2. **Consistent Formatting:** Follow established linting rules
3. **Meaningful Names:** Use descriptive variable and function names
4. **Single Responsibility:** Keep functions focused on one task
5. **Error Handling:** Implement proper error handling and logging

### Documentation

- Add JSDoc/docstrings for public APIs
- Keep README files up to date
- Document non-obvious logic with inline comments

---

## Testing

### Running Tests

> *TODO: Add testing commands once test framework is configured*

```bash
# Run all tests
# npm test / pytest / etc.

# Run specific test file
# npm test -- <filename> / pytest <filename>

# Run with coverage
# npm run test:coverage / pytest --cov
```

### Testing Guidelines

- Write tests for new functionality
- Ensure all tests pass before committing
- Aim for meaningful coverage of critical paths

---

## Build & Deployment

### Building

> *TODO: Add build commands once build system is configured*

```bash
# Development build
# npm run build:dev

# Production build
# npm run build:prod
```

### Deployment

> *TODO: Document deployment process*

---

## AI Assistant Guidelines

### When Working on This Repository

1. **Read First:** Always read existing code before making changes
2. **Understand Context:** Review related files to understand patterns
3. **Minimal Changes:** Make focused, targeted modifications
4. **Test Changes:** Verify changes don't break existing functionality
5. **Document Updates:** Update documentation when changing APIs

### Common Tasks

**Adding a New Feature:**
1. Create a feature branch
2. Implement the feature following existing patterns
3. Add tests for new functionality
4. Update documentation if needed
5. Commit with clear messages

**Fixing a Bug:**
1. Reproduce the issue
2. Identify root cause
3. Implement minimal fix
4. Add regression test
5. Commit with reference to issue (if applicable)

**Refactoring:**
1. Ensure tests exist for code being refactored
2. Make incremental changes
3. Run tests after each change
4. Keep commits atomic

### Things to Avoid

- Don't add unnecessary dependencies
- Don't over-engineer simple solutions
- Don't commit sensitive data (API keys, passwords)
- Don't make changes outside the scope of the task
- Don't skip running tests before committing

---

## Environment Setup

### Prerequisites

> *TODO: List required tools and versions*

```
# Example:
# - Node.js >= 18.x
# - npm >= 9.x
# - Git >= 2.x
```

### Environment Variables

> *TODO: Document required environment variables*

```bash
# Create a .env file (do not commit)
# cp .env.example .env
```

---

## Useful Commands

| Command | Description |
|---------|-------------|
| `git status` | Check working tree status |
| `git diff` | View unstaged changes |
| `git log --oneline -10` | View recent commits |

---

## Additional Resources

- [Project Documentation](./docs/) *(to be created)*
- [Contributing Guidelines](./CONTRIBUTING.md) *(to be created)*
- [Issue Tracker](../../issues)

---

## Changelog

| Date | Change |
|------|--------|
| 2024-12-04 | Initial CLAUDE.md created |

---

*This document should be updated as the project evolves. When adding new technologies, patterns, or conventions, please update the relevant sections.*
