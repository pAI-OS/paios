# Alembic

Alembic is used to manage database versioning using migrations.

## Upgrade schema

`alembic upgrade head`

## Downgrade schema

`alembic downgrade -1`

## Update schema

Update backend/models.py then run:

`alembic revision --autogenerate -m "added asset table"`
