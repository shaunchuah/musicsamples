# MUSIC Samples Web Application

## Current Development Goals

- We are migrating the legacy django template frontend into a new next.js frontend app located in the `frontend/` folder.
- All new APIs for the frontend app should be created as REST APIs using Django REST Framework and should be located in the `api_v3/` folder.
- The existing django template based views and urls should remain unchanged for now to support legacy usage.
- New features and changes should be implemented in the new frontend app and corresponding REST APIs.

## Do

- Activate the virtual environment before running any terminal commands:

  ```bash
  source .venv/bin/activate
  ```

- default to small diffs
- Prioritize simplicity and minimalism in your solutions.
- if you want to make any Database-related change, suggest it first to the User
- once you have completed the entire task, run `source .venv/bin/activate && pytest` to check the backend and `pnpm qc` in the `frontend/` folder to check the frontend
- ask clarifying questions if any part of the task is unclear or if a design decision needs to be made

## Don't

- Do not run the development server unless asked to.
- Do not run any DB migrations, or make any database changes. this is strictly prohibited.

## Commands

To run the django development server:

```bash
source .venv/bin/activate && python manage.py runserver
```

To run tests:

```bash
source .venv/bin/activate && pytest
```

For the frontend app in `frontend/`:

QC (runs typecheck, lint, and tests):

```bash
pnpm qc
```

## Tech Stack

Django with django templates
Sqlite
Bootstrap template known as black dashboard
Next.js for the new frontend app
Shadcn/ui for the new frontend app

## Comments

EVERY new file HAS TO start with "header comments":

1. Relative file location in codebase
2. clear description of what this file does
3. clear description of WHY this file exists

- all comments should be clear, simple and easy-to-understand
- when writing code, make sure to add comments to the most complex / non-obvious parts of the code
- NEVER delete these "header comments" from the files you're editing.
