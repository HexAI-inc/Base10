# Backend Takeover – Issue Timeline

This document outlines the issues identified during the backend takeover and the plan for resolving them.

| Priority | Description | Files/Modules Involved | Risk Level | Impact | Expected Outcome |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | **ImportError: `AssignmentResponse` missing** | `app/api/v1/teacher.py`, `app/schemas/schemas.py` | Critical | System fails to start. | Application starts and tests can run. |
| 2 | **Circular/Redundant Schema Definitions** | `app/api/v1/teacher.py` | Medium | Confusion and potential bugs in data validation. | Clean imports and single source of truth for schemas. |
| 3 | **Inline Schemas in Routers** | `app/api/v1/classrooms.py`, `app/api/v1/teacher.py`, `app/api/v1/ai.py` | Medium | Poor maintainability and violation of separation of concerns. | All schemas moved to `app/schemas/schemas.py`. |
| 4 | **Monolithic Router Files** | `app/api/v1/classrooms.py` | Low | Hard to navigate and maintain. | Router split into smaller, logical modules. |
| 5 | **Database Creation in Lifespan** | `app/main.py` | Medium | Potential conflicts with Alembic migrations in production. | Database creation handled solely by migrations in production. |
| 6 | **Missing Environment Variables Handling** | `app/core/config.py`, `.env` | Low | Startup warnings and disabled features. | Clearer documentation and better fallback/validation for required env vars. |
| 7 | **Inconsistent `UserRole` Definitions** | `app/models/enums.py`, `app/core/rbac.py` | High | Authentication and authorization bugs due to case mismatch ("STUDENT" vs "student"). | Unified `UserRole` enum used everywhere. |

## Detailed Plan

### Step 1: Fix Critical Import Errors
- Move `AssignmentResponse` and other missing schemas to `app/schemas/schemas.py`.
- Fix imports in `app/api/v1/teacher.py`.

### Step 2: Refactor Schemas
- Identify all inline schemas in `classrooms.py`, `teacher.py`, and `ai.py`.
- Move them to `app/schemas/schemas.py` or a dedicated `app/schemas/` directory if it gets too large.

### Step 3: Split Large Routers
- Break down `app/api/v1/classrooms.py` into smaller files (e.g., `stream.py`, `assignments.py`, `members.py`).

### Step 4: Improve Database Initialization
- Remove `Base.metadata.create_all` from `main.py` for non-development environments.
- Ensure `create_tables.py` or Alembic is used for local setup.

### Step 5: Verify and Test
- Run all tests and verify all API endpoints.
