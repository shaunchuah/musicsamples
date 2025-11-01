<!-- frontend/README.md -->
<!-- Comprehensive documentation for the Next.js frontend app. -->
<!-- Exists to guide developers on setup, development, and deployment of the modern UI for Music Samples. -->

# Music Samples Frontend

## Description

The Music Samples Frontend is a modern Next.js-based React application that provides a responsive user interface for the Music Samples research data and sample management platform. It replaces legacy Django templates with a component-driven architecture, enabling faster development and better user experience. The app handles secure user authentication via HTTP-only cookies, proxies API requests to the Django backend, and serves as a foundation for features like sample tracking, analytics, and data export.

This frontend exists to modernize the UI, improve performance, and support incremental migration from the existing Django-based system while maintaining compatibility with the backend.

## Features

- **Secure Authentication**: Login/logout via JWT access + refresh cookies with automatic silent rotation handled by Next.js middleware
- **Responsive Design**: Mobile-friendly layouts built with Tailwind CSS v4 and shadcn/ui components
- **API Integration**: Seamless communication with the Django REST API for data operations
- **Type-Safe Development**: Full TypeScript support with strict configuration for better maintainability
- **Modern Build Tools**: Turbopack for fast development, Biome for code quality, Vitest for testing
- **Production Ready**: Configured for deployment with PM2 process management and Nginx reverse proxy
- **Extensible Architecture**: Component-based structure ready for feature migration from Django templates

## Tech Stack

- **Framework**: Next.js 15 (App Router)
- **Runtime**: React 19.1.0 with TypeScript 5
- **Styling**: Tailwind CSS v4, shadcn/ui component library, Phosphor React icons
- **Forms**: React Hook Form with Zod validation
- **Authentication**: HTTP-only cookies (`authToken`, `refreshToken`) managed via Next.js API routes and middleware
- **Build Tools**: Turbopack, Biome (linting/formatting), PostCSS
- **Testing**: Vitest with @testing-library, jsdom environment
- **Package Management**: pnpm
- **Deployment**: PM2 for process management, Nginx for reverse proxy

## Getting Started

### Prerequisites

- **Node.js**: 20.x or later (use [nvm](https://github.com/nvm-sh/nvm) for version management)
- **Package Manager**: pnpm (recommended) or npm
- **Backend Access**: Django backend running on `http://localhost:8000` (dev) or `https://samples.musicstudy.uk` (prod)

### Installation

1. **Clone and navigate**:

   ```bash
   cd frontend
   ```

2. **Install dependencies**:

   ```bash
   pnpm install
   # or npm install
   ```

3. **Environment configuration**:
   Create a `.env.local` file in the frontend directory:

   ```bash
   # Backend API URL
   BACKEND_URL=http://localhost:8000
   # Or for production
   # BACKEND_URL=https://samples.musicstudy.uk
   ```

### Development

1. **Start development server**:

   ```bash
   pnpm dev
   # or npm run dev
   ```

   The app runs at `http://localhost:3000`.

2. **Access the application**:
   - Visit `http://localhost:3000`
   - Unauthenticated users are redirected to `/login`
   - Ensure the Django backend is running for authentication

3. **Available scripts**:

   ```bash
   pnpm dev          # Start development server with Turbopack
   pnpm build        # Build for production
   pnpm start        # Start production server
   pnpm lint         # Run Biome linting and formatting
   pnpm type-check   # Run TypeScript type checking
   pnpm test         # Run Vitest unit tests
   ```

### Building for Production

1. **Build the application**:

   ```bash
   pnpm build
   ```

2. **Start production server**:

   ```bash
   pnpm start
   ```

For complete deployment instructions including VM setup, CI/CD, and PM2/Nginx configuration, see `../codex/frontend_deployment.md`.

## Project Structure

```text
frontend/
├── app/                          # Next.js App Router
│   ├── api/auth/                 # Authentication API routes
│   │   ├── login/               # POST /api/auth/login
│   │   ├── logout/              # POST /api/auth/logout
│   │   ├── refresh/             # POST /api/auth/refresh
│   │   ├── forgot-password/     # POST /api/auth/forgot-password
│   │   └── reset-password/      # POST /api/auth/reset-password
│   ├── login/                   # Login page (/login)
│   ├── forgot-password/         # Forgot password page (/forgot-password)
│   ├── reset-password/          # Reset password page (/reset-password)
│   ├── layout.tsx               # Root layout with fonts and global styles
│   ├── page.tsx                 # Home dashboard page (/)
│   ├── globals.css              # Global Tailwind CSS styles
│   └── favicon.ico              # App favicon
├── components/                  # Reusable React components
│   ├── auth/                    # Authentication components
│   │   ├── login-form.tsx       # Login form with validation
│   │   ├── logout-button.tsx    # Logout button component
│   │   ├── forgot-password-form.tsx
│   │   └── reset-password-form.tsx
│   └── ui/                      # shadcn/ui components
│       ├── button.tsx
│       ├── form.tsx
│       ├── input.tsx
│       └── ...
├── hooks/                       # Custom React hooks
│   └── use-mobile.ts            # Mobile device detection hook
├── lib/                         # Utility libraries
│   ├── auth.ts                  # Authentication helpers and constants
│   ├── jwt.ts                   # JWT parsing and validation utilities
│   └── utils.ts                 # General utility functions
├── tests/                       # Test files organized by type
│   ├── unit/                    # Unit tests
│   │   ├── api/                 # API route tests
│   │   └── components/          # Component tests
│   ├── integration/             # Integration tests
│   └── e2e/                     # End-to-end tests
├── public/                      # Static assets
│   ├── next.svg
│   ├── vercel.svg
│   └── ...
├── biome.jsonc                  # Biome linting and formatting configuration
├── components.json              # shadcn/ui configuration
├── ecosystem.config.js          # PM2 production configuration
├── next.config.ts               # Next.js configuration
├── package.json                 # Dependencies and scripts
├── postcss.config.mjs           # PostCSS configuration for Tailwind
├── tailwind.config.ts           # Tailwind CSS configuration
├── tsconfig.json                # TypeScript configuration
├── vitest.config.ts             # Vitest testing configuration
├── vitest.setup.ts              # Vitest global setup
└── README.md                    # This file
```

## API Routes

The frontend includes Next.js API routes that proxy authentication requests to the Django backend:

- `POST /api/auth/login` - Authenticates user credentials and sets HTTP-only auth cookies
- `POST /api/auth/logout` - Clears auth cookies and blacklists refresh tokens on the backend
- `POST /api/auth/refresh` - Silently rotates expiring JWT access tokens using refresh tokens
- `POST /api/auth/forgot-password` - Initiates password reset flow
- `POST /api/auth/reset-password` - Completes password reset with token validation

All routes handle errors gracefully and return consistent JSON responses. For data API calls, use the utilities in `lib/auth.ts` to build backend URLs and include authentication headers.

## Contributing

### Code Standards

- Follow the existing code style enforced by Biome (`biome.jsonc`)
- Use TypeScript for all new components and utilities
- Maintain consistent naming conventions (`kebab-case` for files, `camelCase` for variables)
- Add JSDoc comments for complex functions and components

### Development Workflow

1. **Branch from `dev`**: Create feature branches from the `dev` branch
2. **Code Quality**: Run `pnpm lint` and `pnpm type-check` before committing
3. **Testing**: Write tests for new features and ensure existing tests pass
4. **Commits**: Use clear, descriptive commit messages

### Authentication Guidelines

- Test authentication flows thoroughly - they integrate with the Django backend
- Handle both success and error states in auth forms
- Preserve redirect URLs for post-login navigation
- Ensure middleware handles token refresh correctly

### UI/UX Guidelines

- Reference `../codex/frontend_review.md` for modernization guidelines
- Use shadcn/ui components for consistency
- Ensure responsive design works on mobile devices
- Follow accessibility best practices (WCAG guidelines)

### API Integration

- Use `lib/auth.ts` utilities for backend communication
- Handle API errors gracefully with user-friendly messages
- Implement proper loading states for async operations
- Validate API responses and handle edge cases

## Testing

The project uses Vitest for fast, modern testing with jsdom environment simulation.

### Available Commands

```bash
pnpm lint         # Run Biome linting and auto-fix issues
pnpm type-check   # Run TypeScript compiler for type checking
pnpm test         # Run all unit tests
pnpm test:watch   # Run tests in watch mode
pnpm test:ui      # Run tests with Vitest UI
```

### Test Structure

- **Unit Tests** (`tests/unit/`): Component and utility function tests
  - Component tests use `@testing-library/react` with user-event simulation
  - API route tests validate request handling and responses
- **Integration Tests** (`tests/integration/`): Cross-component interaction tests
- **E2E Tests** (`tests/e2e/`): Full application flow tests (when implemented)

### Testing Guidelines

- Write tests for all auth flows and form validations
- Mock external dependencies (API calls, Next.js router)
- Use descriptive test names and organize by feature
- Aim for high coverage of critical user paths

## Deployment

See `../codex/frontend_deployment.md` for detailed deployment instructions including:

- VM setup and security configuration
- CI/CD pipeline with GitHub Actions
- Production runtime with PM2 process management
- Nginx reverse proxy configuration
- SSL/TLS certificate setup
- Environment-specific configuration

The `ecosystem.config.js` file contains PM2 configuration for production deployment.

## Troubleshooting

### Common Issues

#### Authentication Problems

- **Issue**: "Invalid email or password" errors
- **Solution**: Verify Django backend is running and credentials are correct. Check `BACKEND_URL` in `.env.local`

- **Issue**: Redirect loop between login and home page
- **Solution**: Clear browser cookies for `localhost:3000` or check JWT token expiry

- **Issue**: "Authentication service is unavailable"
- **Solution**: Ensure Django server is accessible and CORS is configured properly

#### Build/Development Issues

- **Issue**: TypeScript errors during development
- **Solution**: Run `pnpm type-check` to see detailed errors, or `pnpm lint` for code quality issues

- **Issue**: "Module not found" errors
- **Solution**: Run `pnpm install` to ensure all dependencies are installed

- **Issue**: Port 3000 already in use
- **Solution**: Kill existing process or use `pnpm dev --port 3001`

#### Styling Issues

- **Issue**: Tailwind classes not applying
- **Solution**: Verify `globals.css` is imported in `layout.tsx` and PostCSS is configured

#### Testing Issues

- **Issue**: Tests failing with network errors
- **Solution**: Ensure mocks are properly set up for API calls and Next.js router

### Development Tips

- Use browser developer tools to inspect HTTP-only cookies
- Check browser network tab for API request/response details
- Use `console.log` in middleware to debug authentication flow
- Run `pnpm lint` before committing to catch code quality issues

### Getting Help

- Check existing GitHub issues for similar problems
- Review `../codex/` documentation for additional context
- Contact the development team for backend-related authentication issues

## License

This project is licensed under the same terms as the main G-Trac repository (see root `LICENSE.md`).

## Contact

For questions, reach out to [Shaun Chuah](mailto:shaun.chuah@glasgow.ac.uk) or via the main repository issues.
