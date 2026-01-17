# Project Delay Risk AI - Frontend

Modern React frontend for the AI-powered Project Delay Risk & Decision Intelligence System.

## Tech Stack

- **React 18** + TypeScript
- **Vite** - Fast build tool
- **Tailwind CSS** - Utility-first styling
- **React Query** - Server state management
- **Recharts** - Data visualization
- **Lucide React** - Icons
- **react-error-boundary** - Error resilience

## Quick Start

```bash
# Install dependencies
npm install

# Start development server (requires backend running)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Backend Connection

The frontend expects the backend API at `http://localhost:8000`.

Start the backend first:
```bash
cd ../
python -m uvicorn backend.app:app --reload
```

Or set a custom API URL:
```bash
VITE_API_URL=http://custom-api:8000 npm run dev
```

## Project Structure

```
src/
├── api/           # API client, types, functions
├── components/    # Reusable UI components
│   ├── badges/    # Risk badges
│   ├── charts/    # Recharts visualizations
│   ├── common/    # Shared components
│   └── tables/    # Data tables
├── config/        # App configuration
├── hooks/         # Custom React hooks
└── pages/         # Route pages
```

## Key Features

- **Dashboard** - Overview stats, risk distribution chart, quick actions
- **Analysis** - Run risk analysis, filter by level, keyboard navigation
- **History** - Past analyses, load and compare
- **What-If** - Scenario simulation with before/after comparison

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `↓` / `↑` | Navigate table rows |
| `Enter` | Open task details |
| `Esc` | Close panel / Clear focus |
| `Home` / `End` | Jump to first/last row |

## Configuration

Edit `src/config/app.config.ts` to change:
- App version
- API settings
- Feature flags
- UI defaults

## License

MIT
