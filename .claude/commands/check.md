---
allowed-tools: all
description: Verify code quality, run tests, and ensure production readiness for Padel App
---

# 🚨🚨🚨 CRITICAL REQUIREMENT: FIX ALL ERRORS! 🚨🚨🚨

**THIS IS NOT A REPORTING TASK - THIS IS A FIXING TASK!**

When you run `/check`, you are REQUIRED to:

1. **IDENTIFY** all errors, warnings, and issues
2. **FIX EVERY SINGLE ONE** - not just report them!
3. **USE MULTIPLE AGENTS** to fix issues in parallel:
   - Spawn one agent to fix linting issues
   - Spawn another to fix test failures
   - Spawn more agents for different files/modules
   - Say: "I'll spawn multiple agents to fix all these issues in parallel"
4. **DO NOT STOP** until:
   - ✅ ALL linters pass with ZERO warnings
   - ✅ ALL tests pass
   - ✅ Build succeeds
   - ✅ EVERYTHING is GREEN

**FORBIDDEN BEHAVIORS:**
- ❌ "Here are the issues I found" → NO! FIX THEM!
- ❌ "The linter reports these problems" → NO! RESOLVE THEM!
- ❌ "Tests are failing because..." → NO! MAKE THEM PASS!
- ❌ Stopping after listing issues → NO! KEEP WORKING!

**MANDATORY WORKFLOW:**
```
1. Run checks → Find issues
2. IMMEDIATELY spawn agents to fix ALL issues
3. Re-run checks → Find remaining issues
4. Fix those too
5. REPEAT until EVERYTHING passes
```

**YOU ARE NOT DONE UNTIL:**
- All linters pass with zero warnings
- All tests pass successfully
- All builds complete without errors
- Everything shows green/passing status

---

🛑 **PADEL APP QUALITY VERIFICATION PROTOCOL** 🛑

**Project Structure:**
- **Frontend Apps**: Next.js apps (web, club-admin) with TypeScript
- **Backend API**: FastAPI with Python 3.11, SQLAlchemy, PostgreSQL
- **Monorepo**: Turborepo with pnpm workspaces
- **Testing**: Pytest (API), Cypress (E2E), Jest/Testing Library

**Step 1: Pre-Check Analysis**
- Review recent changes to understand scope
- Check for any outstanding TODOs or temporary code
- Verify all dependencies are installed

**Step 2: Build System Verification**
Run from `padel-app/` directory:
```bash
pnpm install              # Install all dependencies
pnpm build               # Build all apps (via turbo)
```
**REQUIREMENT**: Build MUST succeed with ZERO errors

**Step 3: Linting & Type Checking**
From `padel-app/` directory:
```bash
pnpm lint                # Lint all packages (via turbo)
```

Individual app checks:
```bash
# Web app
cd apps/web
pnpm typecheck          # TypeScript checking
pnpm lint               # ESLint
pnpm lint:fix           # Auto-fix issues

# Club Admin app  
cd apps/club-admin
pnpm typecheck          # TypeScript checking
pnpm lint               # ESLint
pnpm lint:fix           # Auto-fix issues

# API (Python)
cd apps/api
python -m pytest --version  # Verify pytest works
python -m app.main --help   # Verify app starts
```

**Frontend Quality Requirements:**
- [ ] ZERO TypeScript errors (`pnpm typecheck`)
- [ ] ZERO ESLint warnings (`pnpm lint`)
- [ ] All React components properly typed
- [ ] No `any` types unless absolutely necessary
- [ ] Proper error boundaries in place
- [ ] No console.log statements in production code
- [ ] All imports are used
- [ ] No deprecated API usage
- [ ] Proper Next.js conventions followed

**Backend (FastAPI) Quality Requirements:**
- [ ] ZERO Python syntax errors
- [ ] All Pydantic models properly typed
- [ ] Database migrations are up-to-date
- [ ] All API endpoints have proper schemas
- [ ] No hardcoded secrets or credentials
- [ ] Proper error handling and HTTP status codes
- [ ] SQLAlchemy queries are optimized
- [ ] Alembic migrations are reversible

**Step 4: Test Verification**

**API Tests:**
```bash
cd apps/api
python -m pytest tests/ -v     # Run all tests
python -m pytest tests/ --cov  # With coverage
```

**E2E Tests (Club Admin):**
```bash
cd apps/club-admin
pnpm cy:run    # Run Cypress tests headless
```

**Testing Requirements:**
- [ ] ALL tests pass without flakiness
- [ ] API test coverage > 80% for critical paths
- [ ] E2E tests cover main user journeys
- [ ] No skipped tests without justification
- [ ] Tests use proper fixtures and mocking
- [ ] Database tests use transactions/rollback

**Step 5: Database & Migration Verification**
```bash
cd apps/api
# Check migration status
alembic current
alembic check  # Verify migrations are up-to-date
```

**Database Requirements:**
- [ ] All migrations apply cleanly
- [ ] No orphaned migration files
- [ ] Database constraints are properly defined
- [ ] Foreign keys are correctly set up
- [ ] Indexes are in place for performance

**Step 6: Security Audit**
- [ ] No hardcoded secrets in code
- [ ] Environment variables used for config
- [ ] API endpoints have proper authentication
- [ ] SQL injection prevention (SQLAlchemy ORM)
- [ ] CORS properly configured
- [ ] Input validation on all endpoints
- [ ] Proper password hashing (bcrypt)

**Step 7: Performance Verification**
- [ ] Next.js builds are optimized
- [ ] No bundle size issues
- [ ] Database queries are efficient
- [ ] No N+1 query problems
- [ ] API response times reasonable
- [ ] Proper caching where appropriate

**Failure Response Protocol:**
When issues are found:
1. **IMMEDIATELY SPAWN AGENTS** to fix issues in parallel:
   ```
   "I found linting issues in web app and test failures in API. I'll spawn agents:
   - Agent 1: Fix TypeScript/ESLint issues in apps/web and apps/club-admin
   - Agent 2: Fix Python test failures in apps/api
   - Agent 3: Fix database migration issues
   Let me tackle all of these in parallel..."
   ```
2. **FIX EVERYTHING** - Address EVERY issue, no matter how "minor"
3. **VERIFY** - Re-run all checks after fixes
4. **REPEAT** - If new issues found, spawn more agents and fix those too
5. **NO STOPPING** - Keep working until ALL checks show ✅ GREEN

**Final Verification Commands:**
```bash
cd padel-app/
pnpm build     # ✓ Must succeed
pnpm lint      # ✓ Must show zero warnings

cd apps/api
python -m pytest tests/ -v  # ✓ All tests pass

cd apps/club-admin  
pnpm typecheck  # ✓ Zero TypeScript errors

cd apps/web
pnpm typecheck  # ✓ Zero TypeScript errors
```

**Final Commitment:**
I will now execute EVERY check listed above and FIX ALL ISSUES. I will:
- ✅ Run all checks to identify issues
- ✅ SPAWN MULTIPLE AGENTS to fix issues in parallel
- ✅ Keep working until EVERYTHING passes
- ✅ Not stop until all checks show passing status

I will NOT:
- ❌ Just report issues without fixing them
- ❌ Skip any checks
- ❌ Rationalize away issues
- ❌ Declare "good enough"
- ❌ Stop at "mostly passing"

**REMEMBER: This is a FIXING task, not a reporting task!**

The Padel App is ready ONLY when every single check shows ✅ GREEN.

**Executing comprehensive Padel App validation and FIXING ALL ISSUES NOW...**