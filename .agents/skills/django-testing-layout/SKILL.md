---
name: django-testing-layout
description: Test layout, factory_boy over fixtures, and conftest.py structure.
---

# Django Testing Layout

A well-structured testing setup prevents flaky tests, reduces boilerplate, and ensures test suites remain fast and maintainable.

---

## 1. Project Test Structure

Tests should live inside the app they are testing, separated by layer.

✅ **Recommended Layout:**
```text
apps/billing/
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # App-specific Pytest fixtures
│   ├── factories.py         # factory_boy definitions
│   ├── test_models.py
│   ├── test_services.py     # Pure Python unit tests for business logic
│   ├── test_selectors.py
│   └── test_views.py        # APIClient / WebTest integration tests
```

### Global Fixtures
For project-wide fixtures (e.g. creating authenticated API clients, or global mock setup), use a root-level `conftest.py`:
```text
myproject/
├── conftest.py              # Root conftest (global fixtures)
├── apps/
│   ├── billing/
│   └── users/
```

## 2. factory_boy vs. Fixtures

❌ **Anti-pattern:** Using Django JSON/YAML fixtures (`fixtures/data.json`).
**Why?**
Static fixtures are notoriously brittle. If you add a required field to a model or change the schema, you must manually update every static fixture file. They also obscure test data from the test itself, making it hard to read.

✅ **Recommended:** Use `factory_boy`.
Factories generate dynamic test data on the fly and are resilient to schema changes.

```python
# apps/users/tests/factories.py
import factory
from django.contrib.auth import get_user_model

User = get_user_model()

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user_{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    is_active = True
```

In your tests:
```python
# apps/users/tests/test_services.py
from apps.users.tests.factories import UserFactory

def test_deactivate_user(db):
    # Generates a user in the DB dynamically
    user = UserFactory(is_active=True)
    
    deactivate_user(user)
    
    assert not user.is_active
```

## 3. Pytest `conftest.py`

Use `conftest.py` to share setup logic seamlessly across tests via Pytest fixtures, instead of using `setUp` in class-based tests.

✅ **Recommended `conftest.py`:**
```python
# conftest.py
import pytest
from rest_framework.test import APIClient
from apps.users.tests.factories import UserFactory

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user():
    return UserFactory()

@pytest.fixture
def auth_client(api_client, user):
    """Returns an APIClient authenticated as a normal user."""
    api_client.force_authenticate(user=user)
    return api_client
```

Usage in tests:
```python
def test_authenticated_endpoint(auth_client):
    response = auth_client.get('/api/billing/invoices/')
    assert response.status_code == 200
```

## Navigation
- [Production Ops](../django-production-ops/SKILL.md)
- [Views & APIs](../django-views-apis/SKILL.md)
