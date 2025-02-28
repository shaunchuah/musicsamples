# To-Do List

1. Create a overview display for study_id, showing all available sample types and file categories.

After reviewing your repository, I can see that you're working with a Django-based sample tracking system called G-Trac that appears to be used for tracking research samples across multiple sites. The repository has both a traditional Django backend and a Next.js frontend.

## Current Structure Overview

Your repository is structured as follows:

1. **Django Backend**:
   - app: Main application logic for sample tracking
   - users: Authentication handling
   - datasets: Frontend for data platform
   - config: Configuration files
   - templates: Django HTML templates
   - static: Static assets

2. **Next.js Frontend**:
   - frontend: Next.js application with components and pages

3. **Support Files**:
   - .github: GitHub workflows for CI/CD
   - docs, mkdocs.yml: Documentation
   - Various configuration files (`.pre-commit-config.yaml`, .env, etc.)

## Recommendations for Improvement

### 1. Backend Structure Refinements

- **Split views into Smaller Modules**:
  The views in views appear to be quite large and handle multiple responsibilities. Consider further splitting these into more specific modules like `app/views/barcode_views.py`, `app/views/analytics_views.py`, etc.

- **Create a Core App for Common Functionality**:
  Consider creating a `core/` app that contains shared utilities, middleware, and base models that other apps can inherit from.

- **Separate API Endpoints**:
  Move all API endpoints into a dedicated `api/` app with proper versioning (e.g., `api/v1/`), which would make API evolution easier to manage.

### 2. Frontend Improvements

- **Frontend-Backend Separation**:
  The Django templates and Next.js frontend seem to overlap in functionality. Consider a clearer separation:
  - Make the Django backend a pure API server
  - Have the Next.js frontend consume these APIs
  - Move all templates to either one system or the other

- **Organize Static Assets**:
  The JS files in js could be better organized by feature or functionality rather than having all scripts in a flat directory.

### 3. Testing and Documentation

- **Improve Test Coverage**:
  The tests folder contains some tests, but you might want to expand coverage and organize tests mirroring your app structure.

- **API Documentation**:
  Consider adding [drf-spectacular](https://github.com/tfranzel/drf-spectacular) or [drf-yasg](https://github.com/axnsan12/drf-yasg) for OpenAPI documentation of your endpoints.

- **Component Documentation**:
  For your React components in the frontend, consider adding Storybook to document and showcase UI components.

### 4. DevOps Improvements

- **Docker Setup**:
  Consider providing Docker and docker-compose files for easier development and deployment setup.

- **Environment Configuration**:
  Create a more comprehensive `.env.example` file with all required environment variables documented.

### 5. Security Considerations

- **Move Sensitive Info to Environment Variables**:
  Ensure no hardcoded tokens or credentials remain in the codebase (I didn't see any obvious issues here, but it's a good practice to review).

- **Implement API Rate Limiting**:
  Consider adding rate limiting to your API endpoints to prevent abuse.

### 6. General Code Organization

- **Consistent Naming Conventions**:
  Standardize on either snake_case or camelCase within each language context.

- **Consolidate Duplicate Templates**:
  There appears to be some duplication in templates, especially in barcode handling pages that could be refactored to use shared components.

- **Update TODO List**:
  Your TODO.md file contains only two items. Consider expanding this or moving to GitHub issues for better tracking.

## Summary

Overall, the repository appears well-structured for a Django application, but could benefit from clearer separation between frontend and backend, better organization of API endpoints, and expanded documentation. These changes would make the codebase more maintainable and easier for new developers to onboard.

Prioritization for Codebase Improvements
Based on the codebase structure and the suggestions in your TODO.md, here are the priority areas I recommend focusing on:

High Priority
Backend API Organization

Create a dedicated api/ app with versioning
Move existing API endpoints from autocomplete_views.py and other similar files
This will provide a clean foundation for the Next.js frontend
Split Large View Files

Refactor sample_views.py which contains many unrelated views
Create separate modules like barcode_views.py, analytics_views.py based on functionality
This improves maintainability and readability
Frontend-Backend Separation Strategy

Decide whether to: a) Keep Django templates for admin/internal use and Next.js for public-facing pages b) Migrate completely to Next.js and make Django a pure API server
Document this decision for the team
Medium Priority
Test Coverage

Add tests for critical functionality, especially the sample tracking features
Organize tests to mirror the application structure
API Documentation

Add drf-spectacular to document API endpoints
Focus on documenting endpoints used by the Next.js frontend first
Environment Configuration

Create a comprehensive .env.example file based on your example.env
Document all required variables and their purpose
Lower Priority
Create Core App

Move common utilities and middleware to a new core/ app
Static Asset Organization

Organize JS files by feature/functionality
DevOps Improvements

Add Docker configuration
Immediate Tasks
From your original TODO items, I'd prioritize:

Create the study_id overview display (showing sample types and file categories)
Add sampling_date to the datastore object
These should be addressed in parallel with the high-priority architectural improvements.
