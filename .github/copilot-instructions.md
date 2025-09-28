# Copilot Project Context

**Mestring**: Educational mastery tracking app with Django backend + Svelte frontend. Tracks student competency via Goals/Observations across Schools/Groups synchronized from Feide (Norwegian education identity provider).

## Mode Selection

Determine mode by the active file extension:

- If current file ends with `.py` -> Backend Mode
- If current file ends with `.ts`, `.js`, `.svelte` -> Frontend Mode
- If neither (e.g. docs) pick the most recently edited code mode.

---

## Backend Mode: Priority Scan Order

Open / search in this exact order until sufficient context is found:

1. `backend/mastery/models.py` (data model & relations)
2. `backend/mastery/serializers.py`
3. `backend/mastery/access_policies/` (all relevant policy files)
4. `backend/mastery/api/` (endpoint views + auth flows)
5. `backend/settings.py` (settings & installed apps)
6. `backend/urls.py` and `backend/mastery/urls.py`
7. Import / sync pipeline:
   - `backend/mastery/data_import/`
8. `backend/mastery/middleware.py` & `authentication.py`
9. Relevant migration (latest) if schema ambiguity
10. `backend/pyproject.toml` for dependencies (only if needed)

### Backend Architecture Insights

**Domain Model**: Users ↔ Groups ↔ Schools (via Feide sync) + Goals/Observations for mastery tracking. All models use nanoid PKs, not integers.

**Access Control**: Role-based via `drf-access-policy`. Roles: student/teacher (via UserGroup), school admin (via UserSchool), superadmin. Always check access policy before endpoint changes.

**Data Sync**: Feide integration via `data_import/` with background task system (`DataMaintenanceTask` model). Feide-synced data (groups, subjects) vs. locally-owned data (goals, observations).

**Authentication**: Session-based via `SessionUserIdAuthentication` - no JWT/tokens. User ID stored in session after Feide callback.

### Backend Conventions

- Keep business rules near models or dedicated helpers, not in views.
- Always verify corresponding access policy before altering an endpoint.
- Prefer reusing existing serializer fields; avoid silent duplication.
- For cross-model logic, stop and get approval from the developer.
- Use NanoID, not auto-increment integers for primary keys.

---

## Frontend Mode: Priority Scan Order

1. `frontend/src/generated/` (OpenAPI client – source of types & calls)
2. `frontend/src/stores/` (state management & derived data)
3. `frontend/src/types/` (shared domain types / augmentations)
4. `frontend/src/utils/` (helpers, formatting, API wrappers)
5. `frontend/src/views/` (page-level components)
6. `frontend/src/components/` (reusable UI pieces)
7. `frontend/src/App.svelte` & `frontend/src/main.ts`
8. Build/config roots: `openapi-ts.config.ts`, `vite.config.ts`, `svelte.config.js`
9. `frontend/package.json` (scripts & deps) if tooling/context needed

### Frontend Architecture Insights

**Type Safety**: Fully generated from OpenAPI schema via `@hey-api/openapi-ts`. Run `npm run generate-client` after backend schema changes.

**State Management**: Svelte stores in `src/stores/` - lean stores with heavy logic in utils.

**Styling**: Oslo Kommune's Punkt CSS framework + Bootstrap. Check `src/styles/` before adding custom styles.

### Frontend Conventions

- Derive as much as possible from generated OpenAPI types; avoid manual drift.
- Centralize API interaction helpers; don't sprinkle raw fetch in views.
- Keep stores lean: computation-heavy logic belongs in functions/utils.
- Use new Svelte 5 runes syntax for reactive declarations, avoid onMount and `$:`

### Frontend Quick Checks

- Unsure of an API field? Inspect generated client file first.
- Styling? Check `frontend/src/styles/` for tokens/global rules before adding inline styles

---

## Development Workflow

**Backend Setup**:

```bash
cd backend && poetry install && python manage.py migrate
```

**Frontend Setup**:

```bash
cd frontend && npm install && npm run generate-client
```

**Docker Development**: `docker-compose --profile dev up` (includes Postgres + Adminer)

**Data Import Pipeline**: Check README.md for Feide import commands. Import order: groups → users → Excel data.

---

## When Unsure

State what you're missing, then propose targeted files to open. Do not guess silently.

## Do Not

- Invent endpoints or model fields not present in code.
- Introduce business logic directly into frontend view components if it belongs server-side.
- Add dependencies without checking existing tooling.

## Minimal Output Preference

- When responding, reference only files actually consulted or explicitly requested.
- Do not refactor or restructure code unless explicitly asked.
