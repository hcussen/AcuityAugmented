# AcuityAugmented

A monorepo for tracking and visualizing real-time schedule changes from Acuity Scheduling. The system takes daily snapshots of the schedule and tracks changes through webhooks, providing an hourly diff view of additions and cancellations.

## Structure

```
/
├── backend/      # FastAPI application with SQLite
├── frontend/     # Next.js application
└── shared/       # Shared TypeScript types
```

## Features

- Daily schedule snapshots (3:30 PM)
- Real-time webhook processing
- Hourly diff view
- Responsive UI
- Local SQLite database

## Prerequisites

- Python 3.11+
- Node.js 18+
- pnpm (for frontend package management)
- Acuity Scheduling API credentials

## Getting Started

1. Clone the repository

2. Set up the backend:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env
   ```
   Update `.env` with your Acuity API credentials

3. Set up the frontend:
   ```bash
   cd frontend
   pnpm install
   cp .env.example .env.local
   ```

4. Start the development environment:

   Option 1 - Using the setup script (macOS with iTerm2):
   ```bash
   ./setup.sh
   ```
   This will create an iTerm2 window with 4 panes:
   - Top Left: Frontend development server
   - Bottom Left: Backend development server
   - Top Right: Backend virtual environment shell
   - Bottom Right: Git management

   Option 2 - Manual setup:

   Terminal 1 (Backend):
   ```bash
   cd backend
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   uvicorn app.main:app --reload --port 8000
   ```

   Terminal 2 (Frontend):
   ```bash
   cd frontend
   pnpm dev
   ```

5. Access the applications:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Development

### Backend (FastAPI)

- REST API endpoints for webhooks and diffs
- SQLite database for simple, local storage
- APScheduler for daily snapshots (3:30 PM)
- Pydantic for data validation
- Automatic database creation and migrations

### Frontend (Next.js)

- Modern React with TypeScript
- Real-time updates (1-minute polling)
- Responsive two-column diff view
- Shared type definitions

### Database (Supabase)

- Local Supabase instance for development
- PostgreSQL 15 with extensions
- Supabase Studio for database management
- Automatic migrations (coming soon)

## License

MIT
