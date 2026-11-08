---
name: django-models-orm
description: Models, Django ORM, query optimization, and transactions
---

# Django Models & ORM

Models are the data contract with the database. They should enforce data integrity, expose simple state transitions, and provide clean query interfaces — without leaking business logic or touching external systems.

---

## 1. Model Design Principles

### Use `TextChoices` for Enumerated Fields

❌ **Anti-pattern:** Plain string constants scattered across the codebase.
```python
SUBSCRIPTION_STATUS_ACTIVE = 'active'
subscription.status = SUBSCRIPTION_STATUS_ACTIVE
```

✅ **Recommended:**
```python
class Subscription(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        CANCELED = "canceled", "Canceled"
        PAST_DUE = "past_due", "Past Due"

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True,   # Index if you filter on status frequently
    )
```
`TextChoices` integrates with Django admin dropdowns, serializer validation, and provides `Subscription.Status.ACTIVE` — readable, refactorable, and self-documenting.

### Prefer `update_fields` on `.save()`

Calling `instance.save()` always issues an `UPDATE` for every field. If only one field changed, this causes unnecessary writes and can trigger race conditions with concurrent saves.

✅ **Recommended:**
```python
def mark_as_canceled(self) -> None:
    self.status = self.Status.CANCELED
    self.save(update_fields=["status", "canceled_at"])
```

### Use `select_for_update()` for Concurrent Writes

When multiple processes might update the same row (e.g., processing a payment), use `select_for_update()` to acquire a row-level lock.

✅ **Recommended:**
```python
from django.db import transaction

@transaction.atomic
def charge_subscription(subscription_id: int) -> None:
    # Lock the row so no concurrent process can charge simultaneously
    subscription = (
        Subscription.objects
        .select_for_update()
        .get(id=subscription_id, status=Subscription.Status.ACTIVE)
    )
    # ... proceed with charge
```

### Custom `QuerySet` and `Manager`

When a `QuerySet` filter is used in more than one place, promote it to a named method on a custom Manager. This prevents duplication and centralizes query logic.

✅ **Recommended:**
```python
class SubscriptionQuerySet(models.QuerySet):
    def active(self):
        return self.filter(status=Subscription.Status.ACTIVE)
    
    def past_due(self):
        return self.filter(status=Subscription.Status.PAST_DUE)
    
    def for_user(self, user_id: int):
        return self.filter(user_id=user_id)

class Subscription(models.Model):
    objects = SubscriptionQuerySet.as_manager()
    # Usage: Subscription.objects.active().for_user(user_id=1)
```

---

## 2. Query Optimization

### The N+1 Problem

The Django ORM is lazy. If you access a related object inside a loop without pre-fetching, Django executes one query per iteration.

❌ **Anti-pattern (N+1):**
```python
# 1 query for subscriptions + N queries for each user's profile
subscriptions = Subscription.objects.all()
for sub in subscriptions:
    print(sub.user.email)  # Triggers a new SELECT per row
```

✅ **`select_related`** — Use for `ForeignKey` and `OneToOneField` (generates a SQL `JOIN`):
```python
subscriptions = Subscription.objects.select_related("user", "plan").all()
for sub in subscriptions:
    print(sub.user.email)  # No extra query — joined in SQL
```

✅ **`prefetch_related`** — Use for `ManyToManyField` and reverse `ForeignKey` (executes a second query and joins in Python):
```python
users = User.objects.prefetch_related("subscription_set").all()
for user in users:
    for sub in user.subscription_set.all():  # No extra query per user
        print(sub.status)
```

✅ **`Prefetch` object** — Use when you need to filter or annotate the prefetched queryset:
```python
from django.db.models import Prefetch

active_subs = Prefetch(
    "subscriptions",
    queryset=Subscription.objects.active().select_related("plan"),
    to_attr="active_subscriptions",
)
users = User.objects.prefetch_related(active_subs)
# Access as: user.active_subscriptions (a list, not a QuerySet)
```

> ⚠️ **Pitfall:** `prefetch_related` caches the result. If you call `user.subscription_set.filter(status="active")` after a `prefetch_related("subscription_set")`, Django will execute a **new** query, ignoring the cache. Use `Prefetch(to_attr=...)` and access the `to_attr` attribute instead.

### Annotations over Python Aggregation

Instead of loading rows and aggregating in Python, push aggregation to the database.

❌ **Anti-pattern:**
```python
# Loads every payment object into memory
total = sum(p.amount for p in Payment.objects.filter(user=user))
```

✅ **Recommended:**
```python
from django.db.models import Sum, DecimalField
from django.db.models.functions import Coalesce
from decimal import Decimal

total = Payment.objects.filter(user=user).aggregate(
    total=Coalesce(Sum("amount"), Decimal("0.00"), output_field=DecimalField())
)["total"]
```

### `only()` and `defer()` for Large Models

If a model has large fields (e.g., `TextField` with rich content) that you don't need in a list view, use `defer()` or `only()` to avoid fetching them.

```python
# Only fetch id and title — defer the large body field
posts = Post.objects.only("id", "title").all()
```

> ⚠️ Accessing a deferred field on an instance triggers a new query per instance. Be deliberate.

### `bulk_create` and `bulk_update` for Batch Operations

❌ **Anti-pattern (O(N) queries):**
```python
for item in data:
    MyModel.objects.create(**item)
```

✅ **Recommended:**
```python
objs = [MyModel(**item) for item in data]
MyModel.objects.bulk_create(objs, batch_size=500)
```

For updates:
```python
MyModel.objects.bulk_update(instances, fields=["status", "updated_at"], batch_size=500)
```

> ⚠️ `bulk_create` does not fire `post_save` signals. If you have signal listeners that must run, you must handle this explicitly.

---

## 3. Indexing Strategy

Indexes are the single most impactful database performance tool. Every field you filter on frequently in production must have an index.

```python
class Article(models.Model):
    status = models.CharField(max_length=20, db_index=True)   # Single-column index
    author = models.ForeignKey(User, on_delete=models.CASCADE) # FK already indexed

    class Meta:
        indexes = [
            # Composite index: only useful if you filter on both status AND author together
            models.Index(fields=["status", "author"], name="article_status_author_idx"),
            # Partial index (PostgreSQL only): index only published articles
            models.Index(
                fields=["created_at"],
                condition=Q(status="published"),
                name="article_published_created_idx",
            ),
        ]
```

> ⚠️ Every index slows down `INSERT`/`UPDATE`/`DELETE`. Don't index speculatively. Add indexes when `EXPLAIN ANALYZE` shows a sequential scan on a large table.

---

## 4. Transactions

### `@transaction.atomic` as a Decorator

Use on service functions that write to multiple tables to guarantee all-or-nothing execution.

```python
from django.db import transaction

@transaction.atomic
def transfer_funds(*, from_account: Account, to_account: Account, amount: Decimal) -> None:
    from_account.balance = F("balance") - amount
    from_account.save(update_fields=["balance"])
    
    to_account.balance = F("balance") + amount
    to_account.save(update_fields=["balance"])
    
    TransactionLog.objects.create(
        from_account=from_account,
        to_account=to_account,
        amount=amount,
    )
```

### `transaction.on_commit` — Critical for Celery

If you call `my_task.delay()` inside an `@transaction.atomic` block, Celery may pick up the task before the transaction commits, causing `DoesNotExist` errors.

✅ **Mandatory pattern for task dispatch:**
```python
@transaction.atomic
def create_report(*, user: User) -> Report:
    report = Report.objects.create(user=user, status=Report.Status.PENDING)
    
    # ✅ Task is only dispatched AFTER the transaction commits
    transaction.on_commit(lambda: generate_report_task.delay(report_id=report.id))
    
    return report
```

### Savepoints for Partial Rollbacks

Nested `atomic()` blocks create **savepoints** — you can roll back part of a transaction.

```python
with transaction.atomic():   # Outer transaction
    process_payment(order)
    
    with transaction.atomic():  # Savepoint
        try:
            send_slack_notification(order)
        except SlackApiError:
            # This only rolls back the Slack notification, not the payment
            pass  # transaction.atomic raises on exception by default — catch to suppress
```

---

## 5. Migrations

### Schema vs. Data Migrations

Never mix schema changes (`AddField`, `AlterField`) with data migrations (`RunPython`) in the same file.

✅ **Recommended:**
```
0012_add_subscription_plan_field.py    # Schema only — AddField
0013_populate_subscription_plan.py     # Data only — RunPython
```

Separating them allows rolling back `0013` (data) without touching the schema in `0012`, which is critical for safe production deployments.

### Writing Safe Data Migrations

Always use `apps.get_model()` inside `RunPython` instead of importing the model directly. Direct imports use the current model state, which may be incompatible with an older migration state.

✅ **Recommended:**
```python
def populate_plan(apps, schema_editor):
    Subscription = apps.get_model("billing", "Subscription")
    Plan = apps.get_model("billing", "Plan")
    default_plan = Plan.objects.get(name="basic")
    Subscription.objects.filter(plan__isnull=True).update(plan=default_plan)

class Migration(migrations.Migration):
    operations = [
        migrations.RunPython(populate_plan, reverse_code=migrations.RunPython.noop),
    ]
```

### Zero-Downtime Migration Checklist

For large tables in production, these operations require care to avoid locking the table:

| Operation | Risk | Solution |
|---|---|---|
| `AddField(default=...)` | Rewrites entire table | Use `AddField(null=True)` + data migration + `AlterField` |
| `AlterField` (type change) | Full table lock | Use `django-pg-zero-downtime-migrations` |
| `AddIndex` | Locks table | Use `migrations.AddIndex` with `SeparateDatabaseAndState` and `CREATE INDEX CONCURRENTLY` |
| `RemoveField` | Safe (ignored by ORM) | Remove from code first, then add migration |

## Navigation
- [Core Architecture](../django-core-architecture/SKILL.md)
- [Views & APIs](../django-views-apis/SKILL.md)
- [Business Logic](../django-business-logic/SKILL.md)
- [Migrations](../django-migrations/SKILL.md)
