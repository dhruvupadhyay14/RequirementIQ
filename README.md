# RequirementIQ

AI-powered Project Discovery Platform.

## Authentication and company workspace module

### Backend
- FastAPI authentication endpoints for register, login, logout, refresh, current-user, forgot password, and reset password placeholders.
- SQLAlchemy models for companies, workspaces, and users with JWT-based session handling.
- Password hashing with bcrypt and validation for strong passwords.

### Frontend
- React and TypeScript auth pages for login, registration, forgot password, dashboard, and profile.
- Zustand auth store for current user and token persistence.
- Axios instance with JWT and refresh-token handling.

### API endpoints
- POST /auth/register
- POST /auth/login
- POST /auth/logout
- POST /auth/refresh
- GET /auth/me
- PUT /users/profile

### Folder structure
- apps/api/app/models
- apps/api/app/schemas
- apps/api/app/repositories
- apps/api/app/services
- apps/api/app/routers
- apps/api/app/validation
- apps/web/src/pages
- apps/web/src/store
- apps/web/src/lib
