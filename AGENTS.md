# MUSIC Samples Web Application

## Do

- Activate the virtual environment before running any terminal commands:

  ```bash
  source venv/bin/activate
  ```

- default to small diffs
- Prioritize simplicity and minimalism in your solutions.
- if you want to make any Database-related change, suggest it first to the User

## Don't

- Do not run the development server unless asked to.
- Do not run any DB migrations, or make any database changes. this is strictly prohibited.

## Commands

To run the django development server:

```bash
source venv/bin/activate && python manage.py runserver
```

To run tests:

```bash
source venv/bin/activate && pytest
```

## Tech Stack

Django with django templates
Sqlite
Bootstrap template known as black dashboard

## Comments

EVERY new file HAS TO start with "header comments":

1. Relative file location in codebase
2. clear description of what this file does
3. clear description of WHY this file exists

- all comments should be clear, simple and easy-to-understand
- when writing code, make sure to add comments to the most complex / non-obvious parts of the code
- NEVER delete these "header comments" from the files you're editing.
