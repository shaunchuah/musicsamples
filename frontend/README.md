<!-- frontend/README.md -->
<!-- Comprehensive documentation for the Next.js frontend app. -->
<!-- Exists to guide developers on setup, development, and deployment of the modern UI for G-Trac. -->

# G-Trac v3 Frontend

## Description

The G-Trac v3 Frontend is a Next.js-based React application that provides a modern, responsive user interface for the G-Trac sample management system. It replaces legacy Django templates with a component-driven architecture, enabling faster development and better user experience. The app handles user authentication via HTTP-only cookies, proxies API requests to the Django backend, and serves as a foundation for migrating features like sample tracking, analytics, and data export.

This frontend exists to modernize the UI, improve performance, and support incremental migration from the existing Django-based system while maintaining compatibility with the backend.

## Features

- **Authentication**: Secure login/logout via JWT access + refresh cookies with silent rotation handled by middleware.
- **Responsive Design**: Built with Tailwind CSS for mobile-friendly layouts.
- **API Integration**: Seamless communication with the Django REST API for data operations.
- **TypeScript Support**: Type-safe development for better maintainability.
- **Deployment Ready**: Configured for production with PM2 and Nginx, as detailed in `frontend_deployment.md`.
- **Extensible**: Placeholder pages (e.g., home dashboard) ready for feature migration from Django templates.

## Tech Stack

- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS, shadcn/ui components, phosphor-react icons
- **Authentication**: HTTP-only cookies (`authToken`, `refreshToken`) managed via Next.js API routes
- **Build Tools**: Biome, PostCSS, Tailwind
- **Deployment**: PM2 for process management, Nginx for reverse proxy

## Getting Started

### Prerequisites

- Node.js 20.x or later (use nvm for version management)
- pnpm (recommended) or npm
- Access to the Django backend (running on `http://localhost:8000` for development or `https://samples.musicstudy.uk` for production)

### Installation

1. Clone the repository and navigate to the frontend directory:

   ```bash
   cd frontend
   ```

2. Install dependencies:

   ```bash
   pnpm install
   # or npm install
   ```

3. Set up environment variables by copying the example file:

   ```bash
   cp .env.example .env.local
   ```

   Edit `.env.local` to configure:
   - `BACKEND_URL`: URL of the Django backend (e.g., `http://localhost:8000` for dev, `https://samples.musicstudy.uk` for prod)
   - Other variables as needed (see `frontend/lib/auth.ts` for defaults)

### Development

1. Start the development server:

   ```bash
   pnpm dev
   # or npm run dev
   ```

   The app will run at `http://localhost:3000`.

2. Open your browser and navigate to the app. It will redirect to `/login` if not authenticated.

3. For backend integration, ensure the Django server is running and accessible.

### Building for Production

1. Build the app:

   ```bash
   pnpm build
   # or npm run build
   ```

2. Start the production server:

   ```bash
   pnpm start
   # or npm start
   ```

For full deployment steps, refer to `frontend_deployment.md`.

## Project Structure

- `app/`: Next.js App Router pages and layouts
  - `api/`: API routes (e.g., auth proxy)
  - `layout.tsx`: Root layout with fonts and global styles
  - `page.tsx`: Home page with authentication check
  - `login/page.tsx`: Login page
- `components/`: Reusable React components (e.g., auth forms)
- `lib/`: Utilities (e.g., auth helpers)
- `ecosystem.config.js`: PM2 configuration for production
- `tailwind.config.ts`: Tailwind CSS configuration

## API Routes

- `/api/auth/login`: Proxies login requests to Django and sets auth cookies.
- `/api/auth/refresh`: Rotates expiring JWTs using the refresh token cookie.
- `/api/auth/logout`: Clears auth cookies and blacklists the refresh token.

All other data requests should proxy through these or directly to the backend via `lib/auth.ts`.

## Contributing

1. Follow the existing code style (Biome config in `biome.json`).
2. Use TypeScript for all new components.
3. Test authentication flows thoroughly, as they integrate with the Django backend.
4. For UI changes, reference `codex_frontend_review.md` for modernization guidelines.
5. Commit small, focused changes to align with project guidelines.

## Testing

Run linting and type checks:

```bash
pnpm lint
```

```bash
pnpm type-check
```

Run the Vitest-powered unit tests for client components:

```bash
pnpm test
```

## Deployment

See `frontend_deployment.md` for detailed VM setup, CI/CD with GitHub Actions, and production runtime with PM2/Nginx.

## Troubleshooting

- **Authentication Issues**: Ensure `BACKEND_URL` is correct and the Django server is running. Confirm the browser has valid `authToken` and `refreshToken` cookies.
- **Build Errors**: Verify Node.js version and dependencies (`pnpm install`).
- **Proxy Failures**: Confirm CORS settings in Django (`config/settings/base.py`).

## License

This project is licensed under the same terms as the main G-Trac repository (see root `LICENSE.md`).

## Contact

For questions, reach out to [Shaun Chuah](mailto:shaun.chuah@glasgow.ac.uk) or via the main repository issues.
