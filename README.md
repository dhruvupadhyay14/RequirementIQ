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

## AI Engine Architecture

The AI engine is implemented as a modular pipeline that:
- accepts meeting context or transcript text,
- extracts functional, non-functional, business, and technical requirements,
- detects missing information such as target users, roles, integrations, and timeline,
- generates follow-up questions for requirement gathering,
- persists the results in the requirements and ai_questions tables.

## Supported Models

The initial production-ready implementation uses a deterministic fallback engine so the workflow remains usable without external API keys. The architecture is compatible with OpenAI, Google Gemini, and Claude-style providers through the AI_PROVIDER setting.

## Environment Variables

Set the following values before running the API:
- DATABASE_URL
- JWT_SECRET
- AI_PROVIDER
- OPENAI_API_KEY (optional)
- GOOGLE_API_KEY (optional)
- ANTHROPIC_API_KEY (optional)

## Documentation Engine

Generate versioned SRS, BRD, Minutes of Meeting, Client Requirement Summary, and Technical Requirement documents from meeting metadata, transcripts, approved requirements, and answered discovery questions. Documents can be approved, regenerated without losing earlier versions, and exported as PDF, DOCX, or Markdown.
