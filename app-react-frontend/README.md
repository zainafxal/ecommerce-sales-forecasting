# React Frontend

This folder contains the React + Vite frontend for the e-commerce sales forecasting experience.

## Current UI Capabilities

- Transaction input form for product, pricing, customer, country, date, and hour
- Backend status indicator based on the API health endpoint
- Prediction result card with demand band messaging
- Notebook access button linking users to the GitHub notebooks
- Model limitations and disclaimer section
- Responsive layout for desktop and small mobile screens

## Tech Stack

- React
- Vite
- Native CSS

## Environment Variable

Copy `.env.example` to `.env` and set the API base URL:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

The app now uses this env variable for both predictions and backend health checks, so the same frontend can point to local or deployed APIs without code changes.

## Local Development

```bash
cd app-react-frontend
npm install
npm run dev
```

Default local URL:

- [http://localhost:5173](http://localhost:5173)

## Production Build

```bash
cd app-react-frontend
npm run build
npm run preview
```

The production build output is generated in `dist/`.

## Vercel Deployment

Recommended settings:

- Root directory: `app-react-frontend`
- Build command: `npm run build`
- Output directory: `dist`
- Environment variable: `VITE_API_BASE_URL=https://your-hf-space-url/api/v1`

## Project Notes

- The frontend is intentionally notebook-aware because the project is strongly data-science-oriented
- The API health indicator helps users understand whether the backend is reachable before they submit predictions
- Rate limiting is enforced on the backend, so the UI should surface API errors cleanly when traffic limits are exceeded
