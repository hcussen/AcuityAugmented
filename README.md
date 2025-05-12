# AcuityAugmented

A full-stack application for tracking and visualizing near-real-time schedule changes from Acuity Scheduling. The system captures a daily schedule snapshot, then listens for schedule changes to provide an easy-to-read view of additions, cancellations, and modificatiosn to the schedule. 

## Key Features

- 📅 Daily schedule snapshots
- ⚡ Webhook processing for immediate updates
- 🔄 Intuitive diff view for schedule changes
- 📱 Responsive UI built with TailwindCSS and shadcn/ui components
- 📝 Backend test suite with Pytest 

Note that some features, like creating a new account, are purposefully disabled since this was created for my workplace. 

## Project Structure

```
/
├── backend/      # FastAPI backend
├── frontend/     # Next.js frontend
└── setup.sh      # Development environment setup script
```

## Tech Stack
- API: FastAPI deployed using Docker and Fly.io
- Database: Supabase (hosted Postgres)
- ORM: SQL Alchemy + Alembic for database migrations 
- Test Suite: Pytest with mock Postgres database and mock external Acuity client

- Frontend: Next.JS in Typescript with TailwindCSS and shadcn/ui components, deployed using Vercel 
- Authentication: Supabase Auth

## Prerequisites

- Python 3.13+
- Node.js 18+
- pnpm (for frontend package management)
- Docker (for postgres database in test suite)
- Acuity Scheduling API credentials
- Supabase account
- ngrok (for tunneling to local development servers)

## Getting Started

1. Clone the repository

2. Set up the backend:

   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env
   ```

   Update `.env` with your Acuity API credentials, Supabase connection string, and a manually generated API key. I used the python `secrets.token_urlsafe()` to generate one.

3. Set up the frontend:

   ```bash
   cd frontend
   pnpm install
   cp .env.example .env
   ```

   Update `.env` with the API key you generated in step 2, and Supabase credentials. You can add the API's deployment URL later.

4. Start the development environment:

   Option 1 - Using the setup script (macOS with iTerm2):

   ```bash
   ./setup.sh
   ```

   This will create an iTerm2 window with 4 panes:
   ```
   ┌─────────────────────────┬─────────────────────────┐
   │                         │                         │
   │   Frontend Development  │   ngrok Tunnel          │
   │   Server                │                         │
   │   (pnpm dev)            │                         │
   │                         │                         │
   ├─────────────────────────┼─────────────────────────┤
   │                         │                         │
   │   Backend Development   │   Backend Virtual       │
   │   Server                │   Environment           │
   │   (fastapi dev main.py) │                         │
   │                         │                         │
   └─────────────────────────┴─────────────────────────┘
   ```

   Option 2 - Manual setup:

   Terminal 1 (Backend):

   ```bash
   cd backend
   source .venv/bin/activate
   fastapi dev main.py
   ```

   Terminal 2 (Frontend):

   ```bash
   cd frontend
   pnpm dev
   ```

   Terminal 3 (ngrok):

   ```bash
   ngrok http --url=<your-ngrok-url> 8000
   ```

5. Access the applications:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Testing
Within the backend virtual environment, run the test suite with 
```
pytest
```

Make sure the Docker daemon is open before running the test suite, since the test suite uses a postgres image in a Docker container to run database integration tests. 
