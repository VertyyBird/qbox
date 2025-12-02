# Repository Guidelines

## Project Structure & Module Organization
- `app.py` is the Flask entrypoint with routes, filters, and app config; supporting modules live in `models.py`, `forms.py`, and `extensions.py`.
- Templates are under `templates/` and extend `base.html`; static assets live in `static/css` and `static/js`. Asset allowlists live in `config/avatar_hosts.txt`.
- Database schema migrations are tracked in `migrations/` (Flask-Migrate). Tests are under `tests/` with fixtures in `conftest.py`.

## Build, Test, and Development Commands
- Create a venv and install deps: `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`.
- Configure secrets in `.env` (at minimum `SECRET_KEY`).
- Run the app locally: `python app.py` then visit `http://127.0.0.1:5000/`.
- Apply migrations when the schema changes: `FLASK_APP=app.py flask db upgrade` (use `flask db migrate -m "msg"` to generate revisions).
- Do not delete/recreate the DB when models change; generate a migration, upgrade locally, and call this out in summaries so others run `flask db upgrade` after pulling.
- Run tests: `pytest` (uses in-memory SQLite and disables CSRF via the `client` fixture).

## Coding Style & Naming Conventions
- Follow PEP 8: 4-space indents, snake_case functions/routes, PascalCase models/forms. Keep template blocks and context variables in snake_case.
- Keep view logic thin; push validation into WTForms and model helpers.
- Include the AGPLv3 notice at the top of new source or test files, matching existing headers.
- Jinja templates should extend `base.html`; avoid inline script/style when possible—prefer `static/js` and `static/css`.

## Testing Guidelines
- Place new tests in `tests/test_*.py`; reuse the `client` fixture for requests and DB setup/teardown.
- Assert both HTTP status and rendered content (e.g., feed ordering expectations in `test_feed_order_and_content`).
- Use `monkeypatch` to isolate external checks (e.g., avatar URL availability) and keep tests deterministic.
- Add coverage for new routes, form validation paths, and migrations before opening a PR.

## Commit & Pull Request Guidelines
- Use short, imperative commit messages similar to recent history (e.g., "add 404 page", "added content to main page").
- For PRs, describe the user-facing change, note DB migration impacts, and list key test commands run.
- Link related issues/tasks and include screenshots or HTML snippets for UI changes (templates under `templates/`).
- Keep changes small and focused; favor follow-up PRs over large mixed updates.

## Security & Configuration Tips
- Do not commit `.env` or secrets; rotate `SECRET_KEY` for deployments. Prefer environment variables over hard-coding.
- When adding new endpoints, require authentication where appropriate and reuse existing forms to benefit from validation.
- If enabling avatar sources, update `config/avatar_hosts.txt` and validate extensions as done in dashboard flows.
