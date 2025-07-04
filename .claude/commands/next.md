---
allowed-tools: all
description: Execute production-quality implementation for PadelGo with strict standards
---

🚨 **CRITICAL WORKFLOW - NO SHORTCUTS!** 🚨

You are tasked with implementing: $ARGUMENTS

**MANDATORY SEQUENCE:**
1. 🔍 **RESEARCH FIRST** - "Let me research the codebase and create a plan before implementing"
2. 📋 **PLAN** - Present a detailed plan and verify approach
3. ✅ **IMPLEMENT** - Execute with validation checkpoints

**YOU MUST SAY:** "Let me research the codebase and create a plan before implementing."

For complex tasks, say: "Let me ultrathink about this architecture before proposing a solution."

**USE MULTIPLE AGENTS** when the task has independent parts:
"I'll spawn agents to tackle different aspects of this problem"

Consult ~/.claude/CLAUDE.md IMMEDIATELY and follow it EXACTLY.

**Critical Requirements:**

🛑 **PADEL GO QUALITY STANDARDS** 🛑
ALL quality checks must pass:
- TypeScript/ESLint checks for frontend apps
- Python linting (ruff, black, mypy) for API
- All tests passing (pytest for API, Cypress for E2E)
- Build succeeds for all apps

**PadelGo Architecture Overview:**
- **Monorepo**: Turborepo with pnpm workspaces
- **Frontend**: Next.js 14+ apps (web, club-admin) with TypeScript, Tailwind, shadcn/ui
- **Backend**: FastAPI with Python 3.9+, SQLAlchemy 2.0, PostgreSQL
- **Testing**: Pytest (API), Cypress (E2E), Jest/Testing Library (components)
- **Database**: PostgreSQL with Alembic migrations

**Working Directories:**
- Root: `/Users/tarikstafford/Desktop/Projects/PadelApp/padel-app/`
- API: `apps/api/` (FastAPI Python)
- Web App: `apps/web/` (Next.js TypeScript)
- Club Admin: `apps/club-admin/` (Next.js TypeScript)

**Quality Commands (run from padel-app/):**
```bash
# Install dependencies
pnpm install

# Build all apps
pnpm build

# Lint all packages
pnpm lint

# Format code
pnpm format

# Individual app checks
cd apps/api && python -m pytest tests/ -v
cd apps/api && ruff check . && black --check . && mypy .
cd apps/web && pnpm typecheck && pnpm lint
cd apps/club-admin && pnpm typecheck && pnpm lint
```

**Completion Standards (NOT NEGOTIABLE):**
- ALL TypeScript errors resolved (`pnpm typecheck`)
- ALL ESLint issues fixed (`pnpm lint`)
- ALL Python linting passes (ruff, black, mypy)
- ALL tests pass with meaningful coverage
- Feature works end-to-end in all affected apps
- No placeholder comments, TODOs, or "good enough" compromises

**Reality Checkpoints (MANDATORY):**
- After EVERY 3 file edits: Run relevant linters
- After implementing each component: Validate it works
- Before saying "done": Run FULL test suite
- If quality checks fail: STOP and fix immediately

**PadelGo-Specific Patterns:**

**Frontend (Next.js/TypeScript):**
- Use shadcn/ui components consistently
- Follow existing TypeScript patterns
- Proper error boundaries and loading states
- API calls via centralized `/lib/api.ts`
- Authentication via `AuthContext`
- NO `any` types unless absolutely necessary
- Proper Next.js 14+ conventions (app router)

**Backend (FastAPI/Python):**
- Follow existing SQLAlchemy 2.0 patterns
- Use Pydantic schemas for validation
- Proper dependency injection patterns
- Database operations via CRUD modules
- Authentication via JWT middleware
- NO hardcoded secrets (use environment variables)
- Follow existing router patterns

**Database (PostgreSQL/Alembic):**
- Use Alembic for all schema changes
- Proper foreign key relationships
- Index optimization for queries
- Reversible migrations

**Testing Standards:**
- API: pytest with fixtures, proper mocking
- Frontend: Jest/Testing Library for components
- E2E: Cypress for critical user flows
- Coverage requirements as defined in pyproject.toml

**Code Evolution Rules:**
- This is a feature branch - implement the NEW solution directly
- DELETE old code when replacing it - no keeping both versions
- NO migration functions, compatibility layers, or deprecated methods
- When refactoring, replace the existing implementation entirely
- Update all affected imports and references

**Implementation Approach:**
- Start by outlining the complete solution architecture
- Consider impact on all three apps (api, web, club-admin)
- Run linters after EVERY file creation/modification
- If a linter fails, fix it immediately before proceeding
- Write meaningful tests for business logic
- Ensure database migrations are included if needed

**Procrastination Patterns (FORBIDDEN):**
- "I'll fix the TypeScript errors at the end" → NO, fix immediately
- "Let me get it working first" → NO, write clean code from the start
- "This is good enough for now" → NO, do it right the first time
- "The tests can come later" → NO, test as you go
- "I'll handle the other apps later" → NO, consider all affected apps

**Completion Checklist (ALL must be ✅):**
- [ ] Research phase completed with codebase understanding
- [ ] Plan reviewed and approach validated  
- [ ] ALL TypeScript checks pass (`pnpm typecheck`)
- [ ] ALL ESLint checks pass (`pnpm lint`)
- [ ] ALL Python linting passes (ruff, black, mypy)
- [ ] ALL tests pass (pytest + coverage requirements)
- [ ] Build succeeds (`pnpm build`)
- [ ] Feature works end-to-end in all affected apps
- [ ] Database migrations created if needed
- [ ] Old/replaced code is DELETED
- [ ] NO TODOs, FIXMEs, or "temporary" code remains

**STARTING NOW** with research phase to understand the PadelGo codebase...

(Remember: Quality checks will verify everything. No excuses. No shortcuts.)