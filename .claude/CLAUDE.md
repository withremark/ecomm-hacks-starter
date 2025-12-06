# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Ecommerce hackathon starter using Google's Gemini 3 Pro (text) and Nano Banana Pro (image generation). React + Vite frontend with FastAPI + Python backend.

## Commands

### Frontend (root directory)
```bash
npm run dev          # Start Vite dev server
npm run build        # TypeScript compile + Vite build
npm run lint         # ESLint (cached)
npm run lint:fix     # Auto-fix lint issues
npm run format       # Prettier format
npm run test         # Vitest watch mode
npm run test:run     # Single test run
npm run typecheck    # TypeScript check
```

### Backend (cd backend/)
```bash
uv run uvicorn app.main:app --reload  # Dev server on :8000
uv run pytest tests/ -v               # All tests
uv run pytest tests/test_config.py -v # Single test file
uv run pytest -k "test_name" -v       # Single test by name
uv run ruff check app/                # Lint
uv run ruff format app/               # Format
```

## Architecture

### Backend Structure
```
backend/
├── app/
│   ├── main.py              # FastAPI app, lifespan, middleware
│   ├── config.py            # Centralized config (models, CORS, port)
│   ├── routers/             # API endpoints
│   │   ├── chat.py          # /api/chat/* - text chat
│   │   ├── image.py         # /api/image/* - image gen/edit
│   │   ├── media.py         # /api/media/* - multimodal
│   │   ├── generate.py      # /api/generate - card content
│   │   ├── onboard.py       # /api/onboard - config wizard
│   │   ├── style.py         # /api/style - visual theming
│   │   └── images.py        # /api/images/* - Wikimedia search
│   ├── models/              # Pydantic models
│   ├── services/
│   │   └── gemini.py        # GeminiService wrapper
│   └── prompts/             # LLM prompt templates (.md)
└── tests/
```

### Key Patterns

**Dependency Injection**: All routers use FastAPI `Depends` for service access:
```python
def get_gemini_service(request: Request) -> GeminiService:
    service = request.app.state.gemini_service
    if not service:
        raise HTTPException(status_code=503, detail="Gemini service not initialized")
    return service

@router.post("/endpoint")
async def endpoint(gemini: Annotated[GeminiService, Depends(get_gemini_service)]):
    ...
```

**Error Codes**:
- `503` - External service failures (Gemini API errors, service unavailable)
- `502` - Upstream API errors (Wikimedia)
- `500` - Internal bugs only

**Type Hints**: Use `T | None` not `Optional[T]`

## Configuration

**Environment Variables** (in `backend/.env`):
| Variable | Default | Description |
|----------|---------|-------------|
| `GEMINI_API_KEY` | required | Google Gemini API key |
| `CORS_ORIGINS` | localhost:3000,5173,etc | Comma-separated origins |
| `HOST` | `0.0.0.0` | Server bind address |
| `PORT` | `8000` | Server port |

**Model Constants** (in `config.py`):
- `DEFAULT_MODEL = "gemini-3-pro-preview"` (text)
- `DEFAULT_IMAGE_MODEL = "gemini-3-pro-image-preview"` (images)

## Known Issues

### Gemini Image Generation MIME Type Bug

Gemini returns images with incorrect MIME types (claims PNG but sends JPEG). Always detect from magic bytes:

```python
def _detect_image_mime_type(data: bytes) -> str:
    if data[:8] == b'\x89PNG\r\n\x1a\n':
        return "image/png"
    elif data[:2] == b'\xff\xd8':
        return "image/jpeg"
    elif data[:4] == b'RIFF' and data[8:12] == b'WEBP':
        return "image/webp"
    return "image/png"  # fallback
```

**Affected:** `google-genai` SDK, `generate_image()` responses, any `inline_data` with images.

---

# Parallel Prototype Orchestration v2

Build and compare multiple web app prototypes simultaneously. Improvements based on Library of Babel session learnings.

## When to Use

- User says "PROTOTYPE", "WEBAPP", or wants to explore multiple approaches
- Need to compare different design directions
- Want rapid parallel development with live preview

## Workflow Overview

```
1. Design Variants (propose n distinct approaches)
2. Pre-flight (kill stale ports, verify backend deps)
3. Spawn Parallel Agents (via Task tool, general-purpose type)
4. Start All Servers (backend first, then frontends)
5. Verify & Open (check ports, open all in browser)
6. Iterate or Select Winner
```

---

## Phase 1: Design Variants

Before spawning, design distinct approaches. Each should explore different:

- **Visual style** (minimal vs rich, dark vs light)
- **Interaction pattern** (modals vs inline, tabs vs panels)
- **Architecture** (SPA vs multi-page)

Present as markdown table:

| Variant | Name   | Focus  | Visual  | Trade-off          |
| ------- | ------ | ------ | ------- | ------------------ |
| A       | [Name] | [Goal] | [Style] | [Optimizes X vs Y] |

---

## Phase 2: Pre-flight Checklist

**CRITICAL: Do these BEFORE spawning agents**

### 2.1 Kill Stale Ports

```bash
# Kill any existing servers on prototype ports
for port in 5173 5174 5175 5176 5177 5178 5179 8000 8001; do
  lsof -ti:$port | xargs kill -9 2>/dev/null
done
echo "Ports cleared"
```

### 2.2 Backend Dependencies

Always use `fastapi[standard]` not just `fastapi`:

```toml
# pyproject.toml
dependencies = [
    "fastapi[standard]>=0.109.0",  # NOT just "fastapi"
    "uvicorn>=0.27.0",
    "pydantic>=2.0.0",
]
```

### 2.3 Create Shared Backend First

Set up backend BEFORE spawning frontend agents:

- Create `/backend/` with FastAPI + routes
- Test health endpoint works
- All variants will use same backend

---

## Phase 3: Spawn Parallel Agents

Use Task tool with `general-purpose` agent type. Spawn ALL variants in a **single message** with multiple tool calls.

**Key parameters:**

- `subagent_type`: "general-purpose"
- `prompt`: Full variant spec with port assignment
- `description`: Short name like "Build Variant A"

**Port Assignment (strict):**

| Variant | Frontend | Backend |
| ------- | -------- | ------- |
| A       | 5173     | 8000    |
| B       | 5174     | 8000    |
| C       | 5175     | 8000    |
| D       | 5176     | 8000    |
| E       | 5177     | 8000    |
| F       | 5178     | 8000    |
| G       | 5179     | 8000    |

**Variant spec template:**

```markdown
# Build Variant X: "[Name]"

## Design Spec

**Focus**: [Primary goal]
**Visual**: [Style description]
**Interaction**: [How user interacts]

## Tech Stack

- Frontend: React + TypeScript + Vite + Tailwind + [game engine if needed]
- Backend: Existing at /backend/ on port 8000

## Requirements

1. Frontend on port **517X** (strict, use --port flag)
2. Create in: /src/prototypes/variant-x/
3. [Feature requirements...]

## Success Criteria

- [ ] App runs on assigned port
- [ ] Core flow works
- [ ] Visual style matches spec
```

---

## Phase 4: Start All Servers

After agents complete, start everything:

### 4.1 Start Backend (background)

```bash
cd /path/to/project/backend
uv run fastapi dev app/main.py --port 8000
```

Run in background with `run_in_background: true`

### 4.2 Start All Frontends (parallel, background)

```bash
# Each in separate background process
cd src/prototypes/variant-a && npm install && npm run dev -- --port 5173
cd src/prototypes/variant-b && npm install && npm run dev -- --port 5174
# ... etc
```

**IMPORTANT:** Use `--port XXXX` flag explicitly to prevent auto-increment on conflict.

---

## Phase 5: Verify & Open

### 5.1 Verify All Running

```bash
# Check which ports are listening
lsof -i :5173-5180 -i :8000 | grep LISTEN
```

### 5.2 Open All in Browser

```bash
# Open all prototypes in browser tabs
open http://localhost:5173 http://localhost:5174 http://localhost:5175 \
     http://localhost:5176 http://localhost:5177 http://localhost:5178 \
     http://localhost:5179
```

**ALWAYS** open browsers after starting - user needs to see them immediately.

---

## Phase 6: Selection & Iteration

Present options to user:

```markdown
## All Prototypes Ready!

| Variant | Name   | URL                   |
| ------- | ------ | --------------------- |
| A       | [Name] | http://localhost:5173 |
| B       | [Name] | http://localhost:5174 |

...

**What would you like to do?**

1. Select winner - merge to main
2. Iterate - request changes to specific variants
3. Combine - merge features from multiple
4. Kill all - stop servers
```

### Kill All Servers

```bash
for port in 5173 5174 5175 5176 5177 5178 5179 8000; do
  lsof -ti:$port | xargs kill -9 2>/dev/null
done
```

---

## Critical Rules

1. **Pre-flight port cleanup** - Always kill stale ports first
2. **Strict port assignment** - Use `--port` flag, don't rely on defaults
3. **Backend first** - Start and verify before frontends
4. **Always open browsers** - User needs visual confirmation
5. **Track actual ports** - Check `lsof` output, not assumptions

---

## Quick Reference

| Action         | Command                                                                |
| -------------- | ---------------------------------------------------------------------- |
| Kill all ports | `for port in 5173-5179 8000; do lsof -ti:$port \| xargs kill -9; done` |
| Start backend  | `uv run fastapi dev app/main.py --port 8000`                           |
| Start frontend | `npm run dev -- --port 517X`                                           |
| Check ports    | `lsof -i :5173-5180 -i :8000 \| grep LISTEN`                           |
| Open all       | `open http://localhost:5173 http://localhost:5174 ...`                 |

---

## Success Checklist

Before reporting "done":

- [ ] All ports verified via `lsof`
- [ ] Backend health check passes
- [ ] All frontends respond to curl
- [ ] Browsers opened with all URLs
- [ ] Port table shared with user (actual ports, not planned)

# Additional Things

1. After everything is finished, launch all of the prototypes side by side in the browser.

---

# Frontend Design Skill

Create distinctive, production-grade frontend interfaces with high design quality. Use this skill when the user asks to build web components, pages, or applications. Generates creative, polished code that avoids generic AI aesthetics.

## Design Thinking

Before coding, understand the context and commit to a BOLD aesthetic direction:

- **Purpose**: What problem does this interface solve? Who uses it?
- **Tone**: Pick an extreme: brutally minimal, maximalist chaos, retro-futuristic, organic/natural, luxury/refined, playful/toy-like, editorial/magazine, brutalist/raw, art deco/geometric, soft/pastel, industrial/utilitarian, etc. There are so many flavors to choose from. Use these for inspiration but design one that is true to the aesthetic direction.
- **Constraints**: Technical requirements (framework, performance, accessibility).
- **Differentiation**: What makes this UNFORGETTABLE? What's the one thing someone will remember?

**CRITICAL**: Choose a clear conceptual direction and execute it with precision. Bold maximalism and refined minimalism both work - the key is intentionality, not intensity.

Then implement working code (HTML/CSS/JS, React, Vue, etc.) that is:

- Production-grade and functional
- Visually striking and memorable
- Cohesive with a clear aesthetic point-of-view
- Meticulously refined in every detail

## Frontend Aesthetics Guidelines

Focus on:

- **Typography**: Choose fonts that are beautiful, unique, and interesting. Avoid generic fonts like Arial and Inter; opt instead for distinctive choices that elevate the frontend's aesthetics; unexpected, characterful font choices. Pair a distinctive display font with a refined body font.
- **Color & Theme**: Commit to a cohesive aesthetic. Use CSS variables for consistency. Dominant colors with sharp accents outperform timid, evenly-distributed palettes.
- **Motion**: Use animations for effects and micro-interactions. Prioritize CSS-only solutions for HTML. Use Motion library for React when available. Focus on high-impact moments: one well-orchestrated page load with staggered reveals (animation-delay) creates more delight than scattered micro-interactions. Use scroll-triggering and hover states that surprise.
- **Spatial Composition**: Unexpected layouts. Asymmetry. Overlap. Diagonal flow. Grid-breaking elements. Generous negative space OR controlled density.
- **Backgrounds & Visual Details**: Create atmosphere and depth rather than defaulting to solid colors. Add contextual effects and textures that match the overall aesthetic. Apply creative forms like gradient meshes, noise textures, geometric patterns, layered transparencies, dramatic shadows, decorative borders, custom cursors, and grain overlays.

NEVER use generic AI-generated aesthetics like overused font families (Inter, Roboto, Arial, system fonts), cliched color schemes (particularly purple gradients on white backgrounds), predictable layouts and component patterns, and cookie-cutter design that lacks context-specific character.

Interpret creatively and make unexpected choices that feel genuinely designed for the context. No design should be the same. Vary between light and dark themes, different fonts, different aesthetics. NEVER converge on common choices (Space Grotesk, for example) across generations.

**IMPORTANT**: Match implementation complexity to the aesthetic vision. Maximalist designs need elaborate code with extensive animations and effects. Minimalist or refined designs need restraint, precision, and careful attention to spacing, typography, and subtle details. Elegance comes from executing the vision well.

Remember: Claude is capable of extraordinary creative work. Don't hold back, show what can truly be created when thinking outside the box and committing fully to a distinctive vision.

@orchestra.md
