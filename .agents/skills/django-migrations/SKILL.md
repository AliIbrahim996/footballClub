---
name: django-migrations
description: Database migrations best practices, NEVER editing old migrations, and generating data migrations.
---

# Django Migrations

Migrations represent the state of the database schema. They should be append-only and deterministic. Never modify old migrations.

---

## 1. Golden Rules for Migrations

### ALWAYS Commit Migrations to Git

❌ **Anti-pattern:** Adding `migrations/` to `.gitignore`.

**Why?**
Migrations act as version control for your database. If they are ignored, each developer generates conflicting schema changes (e.g., `0002_userA.py` vs `0002_userB.py`), leading to massive team conflicts and breaking your ability to rollback deployments safely.

✅ **Recommended:**
Treat migrations as production code. Always commit them to your repository to guarantee a deterministic, linear schema history across the entire team and production environments.

### NEVER Edit Old Migrations

❌ **Anti-pattern:** Editing an old, already-committed migration file when you want to change a field (e.g. changing `max_length` in `0001_initial.py`).

**Why?**
If you modify an existing migration file, it causes a mismatch between your database state, the state on other developers' machines, and the state in production. Django tracks which migrations have been applied using the `django_migrations` table. Altering a file that has already been applied will lead to severe inconsistencies and "InconsistentMigrationHistory" errors.

✅ **Recommended:**
Always create a *new* migration for any schema change.

1. Update your `models.py`.
2. Run `python manage.py makemigrations <app_name>`.
3. Let Django generate a new migration file (e.g., `0002_new_migration.py`).

### Naming Migrations

Always give migrations descriptive names using the `--name` (or `-n`) flag.

✅ **Recommended:**
```bash
python manage.py makemigrations users --name add_stripe_customer_id
```
This generates a file like `0003_add_stripe_customer_id.py` instead of `0003_auto_20260715_1200.py`.

## 2. Data Migrations

When you need to backfill or migrate data in the database, do not write a standalone script. Write a Data Migration using `RunPython`.

✅ **Recommended Workflow:**

1. Create an empty migration:
   ```bash
   python manage.py makemigrations myapp --empty --name backfill_data
   ```

2. Open the generated file and add a `RunPython` operation:
   ```python
   # myapp/migrations/0004_backfill_data.py
   from django.db import migrations

   def backfill_data_forward(apps, schema_editor):
       # Always use apps.get_model in migrations!
       MyModel = apps.get_model('myapp', 'MyModel')
       for obj in MyModel.objects.iterator():
           obj.new_field = obj.old_field.upper()
           obj.save(update_fields=['new_field'])

   def backfill_data_reverse(apps, schema_editor):
       # Optional: define how to reverse the migration
       pass

   class Migration(migrations.Migration):
       dependencies = [
           ('myapp', '0003_add_new_field'),
       ]

       operations = [
           migrations.RunPython(backfill_data_forward, backfill_data_reverse),
       ]
   ```

**Important:** Always use `apps.get_model('app_name', 'ModelName')` inside a `RunPython` function instead of importing the model directly. This ensures you are querying against the schema state as it existed at the time of the migration.

## Navigation
- [Core Architecture](../django-core-architecture/SKILL.md)
- [Models & ORM](../django-models-orm/SKILL.md)
