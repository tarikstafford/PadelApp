# PadelGo Quality Hooks

This directory contains hooks and scripts for maintaining code quality in the PadelGo project.

## Available Hooks

### `pre-commit`
**Git Hook**: Runs before each commit
- TypeScript type checking for web and club-admin apps
- ESLint linting for all frontend code
- Python linting (ruff, black, mypy) for API
- Build verification

**Usage**: Install as git hook:
```bash
ln -sf ../../.claude/hooks/pre-commit .git/hooks/pre-commit
```

### `pre-push`
**Git Hook**: Runs before pushing to remote
- Full test suite (pytest for API)
- E2E tests (Cypress for club-admin)
- Security scan for potential secrets
- All pre-commit checks

**Usage**: Install as git hook:
```bash
ln -sf ../../.claude/hooks/pre-push .git/hooks/pre-push
```

### `post-merge`
**Git Hook**: Runs after merging branches
- Dependency updates when package files change
- Migration notifications
- Cleanup tasks

**Usage**: Install as git hook:
```bash
ln -sf ../../.claude/hooks/post-merge .git/hooks/post-merge
```

### `quality-check`
**Manual Script**: Complete quality verification
- All linting and type checks
- Full test suite with coverage
- Database migration verification
- Security scanning
- Build verification

**Usage**: Run manually:
```bash
./.claude/hooks/quality-check
```

### `fix-formatting`
**Manual Script**: Auto-fix formatting issues
- Prettier formatting for frontend
- ESLint auto-fix
- Black formatting for Python
- Ruff auto-fix

**Usage**: Run manually:
```bash
./.claude/hooks/fix-formatting
```

## Installation

To install all git hooks at once:

```bash
cd /path/to/PadelApp
ln -sf ../../.claude/hooks/pre-commit .git/hooks/pre-commit
ln -sf ../../.claude/hooks/pre-push .git/hooks/pre-push
ln -sf ../../.claude/hooks/post-merge .git/hooks/post-merge
```

## Quality Standards

### Frontend (TypeScript/Next.js)
- Zero TypeScript errors
- Zero ESLint warnings
- Proper shadcn/ui component usage
- No `any` types unless necessary
- Proper error boundaries

### Backend (Python/FastAPI)
- Zero ruff violations
- Black formatting compliance
- MyPy type checking passed
- 80%+ test coverage
- No hardcoded secrets

### Database
- Reversible migrations
- Migration status verification
- No orphaned migration files

## Troubleshooting

### Hook Failures
If a hook fails:
1. Fix the reported issues
2. Use `fix-formatting` for auto-fixable issues
3. Re-run the hook or commit again
4. For persistent issues, run `quality-check` for detailed output

### Performance
Hooks cache dependencies when possible. If experiencing slow hook execution:
- Ensure `pnpm` is using cache
- Check for large dependency updates
- Consider skipping hooks temporarily with `--no-verify` (not recommended)

## Integration with Claude Code

These hooks are designed to work with the Claude Code workflow:
- `next.md` command references these quality standards
- `check.md` command uses similar verification steps
- All hooks enforce the same standards as the command templates