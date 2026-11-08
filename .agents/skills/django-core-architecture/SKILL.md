---
name: django-core-architecture
description: Project structure, clean architecture principles, and the Service Layer pattern
---

# Django Core Architecture

This skill defines the high-level architecture and project structure for Django applications, based on the HackSoft styleguide, domain-driven design principles, and production-hardened practices.

---

## 1. Project Structure

Separate configuration from domain logic. Treat each Django app as a **bounded context** — a self-contained slice of the business domain.

✅ **Recommended Structure:**
```
myproject/
├── config/                   # Django configuration root
│   ├── settings/
│   │   ├── base.py           # Shared settings
│   │   ├── local.py          # Local overrides (DEBUG=True, sqlite)
│   │   └── production.py     # Production overrides
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/                     # All domain apps live here
│   ├── users/
│   │   ├── models.py
│   │   ├── admin.py
│   │   ├── services.py       # Write operations
│   │   ├── selectors.py      # Read operations / QuerySets
│   │   ├── serializers.py    # DRF input serializers
│   │   ├── apis.py           # DRF views (renamed from views.py)
│   │   ├── urls.py
│   │   ├── tasks.py          # Celery tasks
│   │   └── tests/
│   │       ├── test_services.py
│   │       ├── test_selectors.py
│   │       └── test_apis.py
│   ├── billing/
│   └── notifications/
├── common/                   # Cross-cutting infrastructure
│   ├── exceptions.py         # Custom domain exceptions
│   ├── mixins.py             # Reusable admin/view mixins
│   ├── pagination.py
│   └── utils.py
├── requirements/
│   ├── base.txt
│   ├── local.txt
│   └── production.txt
└── manage.py
```

### Why split settings by environment?
- Importing `from config.settings.local import *` in tests prevents production secrets from leaking into test environments.
- `production.py` can enforce `ALLOWED_HOSTS`, `DATABASES` pointing to RDS, and `CACHES` pointing to ElastiCache — all without touching `base.py`.

❌ **Anti-patterns:**
- A single `settings.py` that uses `if DEBUG:` branches everywhere.
- Putting all apps in the project root, mixing business code with `manage.py`.
- Creating an app named `core` or `main` that accumulates unrelated logic over time.

---

## 2. The Service Layer Pattern

Django's MVT encourages putting logic in Models ("Fat Models") or Views ("Fat Views"). Both degrade maintainability and testability as the codebase grows. Extract all business logic into a **Service Layer** instead.

### Rules for Services

1. **Services are module-level functions, not classes.** Classes with methods accumulate state and become god-objects. A function has a clear contract: inputs → side effects → output.

2. **Use keyword-only arguments (`*`).** This forces callers to be explicit, prevents argument-order bugs, and makes refactoring safe.

3. **Never pass `request` or `serializer` into a service.** Pass primitive Python types or model instances instead. The service must not know about HTTP.

4. **Always use type hints.** Services are the most important code in your app. Make the contract explicit.

5. **Wrap in `@transaction.atomic` when writing to multiple tables.** The database must never be left in a partial state.

6. **Never directly trigger Celery tasks from within a service.** Enqueue inside `transaction.on_commit` to avoid race conditions where Celery picks up a task before the DB commit lands.

✅ **Recommended (`apps/billing/services.py`):**
```python
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from apps.billing.models import Invoice, Payment
from apps.notifications.tasks import send_payment_receipt_task

ApplicationError = Exception  # Replace with your custom exception class

@transaction.atomic
def create_payment_for_invoice(
    *,
    invoice: Invoice,
    amount: Decimal,
    payment_method_id: str,
) -> Payment:
    if invoice.is_paid:
        raise ApplicationError(f"Invoice {invoice.id} is already paid.")
    
    if amount != invoice.remaining_balance:
        raise ApplicationError(
            f"Payment amount {amount} does not match invoice balance {invoice.remaining_balance}."
        )
    
    payment = Payment.objects.create(
        invoice=invoice,
        amount=amount,
        payment_method_id=payment_method_id,
        status=Payment.Status.PROCESSING,
    )
    
    invoice.mark_as_paid()  # Simple state transition on model — this is fine
    
    # Enqueue AFTER commit so the Celery worker always finds the Payment record
    transaction.on_commit(
        lambda: send_payment_receipt_task.delay(payment_id=payment.id)
    )
    
    return payment
```

**What this service does NOT do:**
- It does not parse `request.data` or know about HTTP.
- It does not call `serializer.save()` or reference DRF.
- It does not contain email-sending logic directly — that belongs to the Celery task.

---

## 3. The Selectors Layer

Selectors encapsulate all complex `QuerySet` composition (multi-table joins, annotations, filters) into named, testable functions. They are the read-side equivalent of Services.

### Rules for Selectors

1. **Always return a `QuerySet` — do not call `.first()` or iterate inside.** This keeps selectors composable and lets the caller decide how to paginate or filter further.

2. **Name selectors after what they return, not the filters.** `get_active_subscriptions_for_user` is better than `filter_subscriptions_by_status_and_user`.

3. **Use `Prefetch` objects for complex prefetch logic.** `prefetch_related("books")` is a shortcut; `Prefetch("books", queryset=Book.objects.filter(published=True))` gives you precise control.

✅ **Recommended (`apps/billing/selectors.py`):**
```python
from django.db.models import QuerySet, Prefetch, Sum, Value
from django.db.models.functions import Coalesce
from apps.billing.models import Subscription, Invoice

def get_active_subscriptions_for_user(*, user_id: int) -> QuerySet[Subscription]:
    return (
        Subscription.objects
        .filter(user_id=user_id, status=Subscription.Status.ACTIVE)
        .select_related("plan", "user__profile")
        .prefetch_related(
            Prefetch(
                "invoices",
                queryset=Invoice.objects.filter(status=Invoice.Status.UNPAID).order_by("-due_date"),
                to_attr="unpaid_invoices",
            )
        )
        .annotate(
            total_paid=Coalesce(
                Sum("payments__amount", filter=Q(payments__status="SUCCESS")),
                Value(Decimal("0.00")),
            )
        )
    )
```

---

## 4. Exceptions as Domain Contracts

Define a hierarchy of domain exceptions in `common/exceptions.py`. Never `raise Exception(...)` with free-form strings from a service — that makes catching specific errors impossible.

✅ **Recommended (`common/exceptions.py`):**
```python
class ApplicationError(Exception):
    """Base class for all domain exceptions. Caught by the global exception handler."""
    def __init__(self, message: str, extra: dict | None = None):
        super().__init__(message)
        self.message = message
        self.extra = extra or {}

class PermissionDenied(ApplicationError):
    pass

class InsufficientFunds(ApplicationError):
    pass
```

The DRF exception handler in `django-production-ops` maps these to HTTP 400 responses automatically.

---

## 5. App-level URL Configuration

Never define all URLs in a single `config/urls.py`. Each app owns its URL patterns.

✅ **Recommended (`apps/users/urls.py`):**
```python
from django.urls import path
from apps.users.apis import UserRegistrationApi, UserDetailApi

urlpatterns = [
    path("register/", UserRegistrationApi.as_view(), name="user-register"),
    path("<int:user_id>/", UserDetailApi.as_view(), name="user-detail"),
]
```

```python
# config/urls.py
from django.urls import path, include

urlpatterns = [
    path("api/users/", include("apps.users.urls")),
    path("api/billing/", include("apps.billing.urls")),
]
```

## Navigation
- [Models & ORM](../django-models-orm/SKILL.md)
- [Views & APIs](../django-views-apis/SKILL.md)
- [Business Logic](../django-business-logic/SKILL.md)
- [Production Ops](../django-production-ops/SKILL.md)
