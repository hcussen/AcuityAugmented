# AcuityAugmented

A modern full-stack application for tracking and visualizing real-time schedule changes from Acuity Scheduling. The system captures daily schedule snapshots and processes real-time webhook events to provide an intuitive diff view of appointments, helping you monitor additions, cancellations, and modifications to your schedule.

## Project Structure

```
/
├── backend/      # FastAPI application (Python 3.11+)
├── frontend/     # Next.js 15.3 application
└── setup.sh      # Development environment setup script
```

## Key Features

- 📅 Daily schedule snapshots with automatic synchronization
- ⚡ Real-time webhook processing for immediate updates
- 🔄 Intuitive diff view for schedule changes
- 📱 Responsive modern UI built with React 19 and TailwindCSS

## Prerequisites

- Python 3.11+
- Node.js 18+
- pnpm (for frontend package management)
- Acuity Scheduling API credentials
- ngrok (for tunneling to local development servers)

## Getting Started

1. Clone the repository

2. Set up the backend:

   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .\.venv\Scripts\activate
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
   ./setup.sh && ngrok http --url=<your-ngrok-url> 8000
   ```

   This will create an iTerm2 window with 4 panes:

   - Top Left: Frontend development server
   - Bottom Left: Backend development server
   - Top Right: Git management
   - Bottom Right: Backend virtual environment shell

   Option 2 - Manual setup:

   Terminal 1 (Backend):

   ```bash
   cd backend
   source .venv/bin/activate  # On Windows: .\.venv\Scripts\activate
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

## Development

### Backend (FastAPI)

- REST API endpoints for webhooks and diffs
- SQLite database for simple local storage

### Frontend (Next.js)

- Modern React with TypeScript
- Real-time updates (1-minute polling)
- Responsive two-column diff view

## License

MIT
