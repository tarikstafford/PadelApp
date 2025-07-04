# Python Linting Configuration

This FastAPI backend now has comprehensive Python linting configured with modern tools.

## Linting Tools

### 1. Ruff
- **Purpose**: Fast Python linter that replaces many tools (flake8, isort, etc.)
- **Features**: 
  - Code style checking (pycodestyle)
  - Import sorting
  - Security checks (bandit)
  - Complexity analysis
  - Type checking suggestions
  - Performance improvements
  - And many more rules

### 2. Black
- **Purpose**: Opinionated Python code formatter
- **Features**: Automatically formats code to consistent style

### 3. MyPy
- **Purpose**: Static type checker for Python
- **Features**: Catches type-related errors before runtime

## Available Commands

### Main Commands
```bash
# Run all linting checks (ruff + black)
npm run lint

# Auto-fix issues where possible
npm run lint:fix

# Format code with black and auto-fix ruff issues
npm run format
```

### Individual Tools
```bash
# Ruff only
npm run lint:ruff          # Check with ruff
npm run lint:ruff:fix      # Auto-fix ruff issues

# Black only  
npm run lint:black         # Check formatting
npm run lint:black:fix     # Auto-format code

# MyPy only
npm run lint:mypy          # Type checking
```

## Configuration Files

### pyproject.toml
Contains all tool configurations:
- `[tool.ruff]` - Ruff linter settings
- `[tool.black]` - Black formatter settings  
- `[tool.mypy]` - MyPy type checker settings

### .ruff.toml
Standalone ruff configuration for better IDE integration.

## Ruff Rules Enabled

The configuration includes comprehensive rule sets:
- **E/W**: pycodestyle errors and warnings
- **F**: pyflakes
- **I**: isort (import sorting)
- **B**: flake8-bugbear
- **C4**: flake8-comprehensions
- **UP**: pyupgrade (modern Python syntax)
- **ARG**: unused arguments
- **C90**: mccabe complexity
- **S**: bandit security
- **N**: PEP8 naming conventions
- **SIM**: simplify suggestions
- **PT**: pytest style
- **PL**: pylint rules
- **RUF**: ruff-specific rules

## Ignored Rules

Some rules are intentionally ignored for FastAPI projects:
- `S101`: Use of assert (common in tests)
- `B008`: Function calls in argument defaults (common in FastAPI)
- `PLR2004`: Magic values (common in configuration)

## Per-File Ignores

- **Tests**: More lenient rules for test files
- **Migrations**: Database migration files ignored
- **Seeds**: Seed data files have relaxed rules

## IDE Integration

Most modern IDEs can use the configuration files:
- VS Code: Install Python and Ruff extensions
- PyCharm: Enable external tools or use plugins
- Vim/Neovim: Use appropriate plugins

## Pre-commit Hooks (Optional)

You can set up pre-commit hooks to run linting automatically:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
```

## Fixing Issues

1. **Auto-fixable issues**: Run `npm run format` or `npm run lint:fix`
2. **Manual fixes**: Review the output and fix issues manually
3. **Gradual adoption**: You can disable specific rules temporarily if needed

## Configuration Customization

To modify linting rules:
1. Edit `pyproject.toml` under the `[tool.ruff]` section
2. Add rules to `ignore` list to disable them
3. Add rules to `select` list to enable additional checks
4. Modify per-file ignores for specific file patterns

## Current Status

- ✅ Ruff: Configured and working
- ✅ Black: Configured and working  
- ✅ MyPy: Configured but finds many type errors (use `npm run lint:mypy` to see them)

The codebase currently has linting issues that can be gradually fixed. Start with auto-fixable issues using `npm run format`.