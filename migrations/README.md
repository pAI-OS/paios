# Alembic

Alembic is used to manage database versioning using migrations.

## Apply schema

`alembic upgrade head`

## Update schema

Update backend/models.py then run:

`alembic revision --autogenerate -m "added asset table"`

