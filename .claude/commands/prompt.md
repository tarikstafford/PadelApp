---
allowed-tools: all
description: Synthesize a complete PadelGo prompt by combining next.md with your arguments
---

## 🎯 PADEL GO PROMPT SYNTHESIZER

You will create a **complete, ready-to-copy prompt** by combining:
1. The next.md command template from .claude/commands/next.md (PadelGo-specific)
2. The specific task details provided here: $ARGUMENTS

### 📋 YOUR TASK:

1. **READ** the next.md command file at .claude/commands/next.md
2. **EXTRACT** the core prompt structure and PadelGo requirements
3. **INTEGRATE** the user's arguments seamlessly into the prompt
4. **OUTPUT** a complete prompt in a code block that can be easily copied

### 🎨 OUTPUT FORMAT:

Present the synthesized prompt in a markdown code block like this:

```
[The complete synthesized prompt that combines next.md PadelGo instructions with the user's specific task]
```

### ⚡ SYNTHESIS RULES:

1. **Preserve Structure** - Maintain the workflow, checkpoints, and PadelGo requirements from next.md
2. **Integrate Naturally** - Replace `$ARGUMENTS` placeholder with the actual task details
3. **Context Aware** - Emphasize relevant PadelGo app sections (API/web/club-admin)
4. **Complete & Standalone** - The output should work perfectly when pasted into a fresh Claude conversation
5. **No Meta-Commentary** - Don't explain what you're doing, just output the synthesized prompt

### 🔧 PADEL GO ENHANCEMENT GUIDELINES:

- **Frontend Tasks**: Emphasize Next.js/TypeScript patterns, shadcn/ui, AuthContext
- **Backend Tasks**: Emphasize FastAPI/Python patterns, SQLAlchemy, Pydantic schemas
- **Database Tasks**: Emphasize Alembic migrations, PostgreSQL patterns
- **Full-Stack Tasks**: Ensure all three apps (api, web, club-admin) are considered
- **Complex Tasks**: Ensure "ultrathink" and "multiple agents" sections are prominent
- Keep ALL critical PadelGo quality requirements (TypeScript checks, Python linting, testing)

### 🏗️ PADEL GO ARCHITECTURE AWARENESS:

When synthesizing, consider:
- **Monorepo Structure**: Turborepo with pnpm workspaces
- **Frontend Apps**: Next.js 14+ with TypeScript, Tailwind, shadcn/ui
- **Backend**: FastAPI with Python 3.9+, SQLAlchemy 2.0, PostgreSQL
- **Testing**: Pytest (API), Cypress (E2E), Jest/Testing Library
- **Quality Tools**: ESLint, ruff, black, mypy

### 📦 EXAMPLE BEHAVIOR:

If user provides: "add tournament bracket management to the club admin dashboard"

You would:
1. Read next.md (PadelGo-specific)
2. Replace $ARGUMENTS with the tournament task
3. Emphasize club-admin app, backend tournament service, database migrations
4. Include relevant quality commands for affected apps
5. Output the complete, integrated PadelGo prompt

**BEGIN SYNTHESIS NOW** - Read next.md and create the perfect PadelGo prompt!
