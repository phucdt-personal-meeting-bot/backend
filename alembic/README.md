# Alembic Migration Commands

All commands should be run from the `backend/` directory using the `.venv` Python.

## Generate a new migration

```bash
.venv/Scripts/python -m alembic revision --autogenerate -m "describe your change"
```

## Apply all pending migrations

```bash
.venv/Scripts/python -m alembic upgrade head
```

## Rollback one migration

```bash
.venv/Scripts/python -m alembic downgrade -1
```

## Rollback to a specific revision

```bash
.venv/Scripts/python -m alembic downgrade <revision_id>
```

## Show current revision

```bash
.venv/Scripts/python -m alembic current
```

## Show migration history

```bash
.venv/Scripts/python -m alembic history --verbose
```
