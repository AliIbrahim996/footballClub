---
name: django-views-apis
description: views.py, API design, DRF serializers, error handling, and pagination
---

# Django Views & APIs

Views are protocol adapters: they translate HTTP inputs into domain calls and domain outputs into HTTP responses. They must contain zero business logic.

---

## 1. The 3-Step View Pattern

Every DRF view must follow this exact pattern — no exceptions:

```
1. Deserialize + Validate input (Serializer)
2. Call Service or Selector
3. Serialize output and return Response
```

✅ **Recommended (`apps/billing/apis.py`):**
```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status

from apps.billing.services import create_payment_for_invoice
from apps.billing.selectors import get_invoice_or_404

class InvoicePaymentApi(APIView):
    class InputSerializer(serializers.Serializer):
        amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0.01)
        payment_method_id = serializers.CharField(max_length=50)

    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        status = serializers.CharField()
        amount = serializers.DecimalField(max_digits=10, decimal_places=2)
        created_at = serializers.DateTimeField()

    def post(self, request, invoice_id: int):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        invoice = get_invoice_or_404(id=invoice_id, user=request.user)

        payment = create_payment_for_invoice(
            invoice=invoice,
            **serializer.validated_data,
        )

        return Response(
            self.OutputSerializer(payment).data,
            status=status.HTTP_201_CREATED,
        )
```

**Why inline `InputSerializer` and `OutputSerializer` as nested classes:**
- High structural cohesion — the serializer is exactly where it is consumed.
- Eliminates the need to navigate to a separate `serializers.py` file.
- When the endpoint is deleted, the serializer is deleted with it. No orphaned code.
- The naming is unambiguous: `InvoicePaymentApi.InputSerializer` vs a generic `InvoicePaymentSerializer`.

---

## 2. Serializers: Input Validation Contract

Serializers in DRF serve as the **validation layer** only. Treat them like a schema: they parse raw input, validate it, and return typed `validated_data`. They do not write to the database.

### Use `serializers.Serializer` for Writes, Not `ModelSerializer`

`ModelSerializer` works for trivial CRUD but encourages bad habits:
- Its auto-generated `create()` and `update()` bypass the service layer.
- Overriding `.save()` hides side effects from the calling view.
- Fields are implicit — the `Meta.fields` list doesn't show types or constraints.

❌ **Anti-pattern (Fat Serializer with hidden logic):**
```python
class InvoicePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["amount", "payment_method_id"]

    def create(self, validated_data):
        # This bypasses the service layer completely
        payment = super().create(validated_data)
        send_receipt_email(payment)   # Hidden side effect!
        return payment
```

✅ **Recommended (Pure validation contract):**
```python
class InvoicePaymentSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    payment_method_id = serializers.CharField()

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive.")
        return value

    def validate(self, data):
        # Cross-field validation belongs here, not in the view
        if data["amount"] > settings.MAX_SINGLE_PAYMENT:
            raise serializers.ValidationError("Amount exceeds single-payment limit.")
        return data
    # No .create() or .save() method defined.
```

### `SerializerMethodField` for Computed Properties

Use `SerializerMethodField` for derived values that don't exist as model fields.

```python
class SubscriptionOutputSerializer(serializers.ModelSerializer):
    days_remaining = serializers.SerializerMethodField()
    plan_name = serializers.CharField(source="plan.name")  # Follows FK without SerializerMethodField

    class Meta:
        model = Subscription
        fields = ["id", "status", "expires_at", "days_remaining", "plan_name"]

    def get_days_remaining(self, obj: Subscription) -> int:
        return (obj.expires_at - timezone.now()).days
```

---

## 3. Class-Based vs. Function-Based Views

| Scenario | Recommendation |
|---|---|
| Standard REST endpoint (GET/POST/PUT/DELETE) | `APIView` subclass |
| Simple utility webhook (single method, no auth) | `@api_view(["POST"])` FBV |
| Generic CRUD with pagination | `ListCreateAPIView` is acceptable if no custom logic |
| Complex business logic inside the view | `APIView` — never `ModelViewSet` |

**Why to avoid `ModelViewSet` for complex logic:**
- `ModelViewSet` magically routes HTTP methods to `create`, `retrieve`, `update`, `destroy`.
- When you override `perform_create` to call a service, the control flow is buried in the parent class.
- It couples your URL routing to REST conventions (you can't easily add non-CRUD actions without `@action`).
- Any team member must understand Django REST Framework internals to trace the request lifecycle.

`APIView` is explicit. Any reader can follow the request from `def post(self, request)` to the return statement without knowing DRF internals.

---

## 4. Pagination

Never return unbounded querysets. Always paginate list endpoints.

✅ **Recommended (reusable pagination class):**
```python
# common/pagination.py
from rest_framework.pagination import PageNumberPagination

class StandardResultsPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 200
```

✅ **Recommended (in the view):**
```python
class SubscriptionListApi(APIView):
    class OutputSerializer(serializers.ModelSerializer):
        class Meta:
            model = Subscription
            fields = ["id", "status", "created_at"]

    def get(self, request):
        subscriptions = get_active_subscriptions_for_user(user_id=request.user.id)

        paginator = StandardResultsPagination()
        page = paginator.paginate_queryset(subscriptions, request)

        return paginator.get_paginated_response(
            self.OutputSerializer(page, many=True).data
        )
```

---

## 5. Permissions

DRF's permission classes are the correct place for access control decisions — not inside the service.

✅ **Recommended:**
```python
from rest_framework.permissions import IsAuthenticated
from apps.users.permissions import IsSubscriptionOwner

class SubscriptionDetailApi(APIView):
    permission_classes = [IsAuthenticated, IsSubscriptionOwner]

    def get(self, request, subscription_id):
        subscription = get_subscription_or_404(id=subscription_id)
        return Response(self.OutputSerializer(subscription).data)
```

```python
# apps/users/permissions.py
from rest_framework.permissions import BasePermission

class IsSubscriptionOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user_id == request.user.id
```

> ⚠️ `has_permission` runs before `get_object()`. `has_object_permission` runs after. You must call `self.check_object_permissions(request, obj)` explicitly in the view if you're not using a Generic View.

---

## 6. API Error Handling

Use a global DRF exception handler to convert domain exceptions into structured HTTP responses.

✅ **Recommended (`common/exceptions.py` + `config/settings/base.py`):**
```python
# common/exceptions.py
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

from common.exceptions import ApplicationError

def custom_exception_handler(exc, context):
    if isinstance(exc, ApplicationError):
        return Response(
            {"detail": exc.message, "extra": exc.extra},
            status=status.HTTP_400_BAD_REQUEST,
        )
    return exception_handler(exc, context)
```

```python
# config/settings/base.py
REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "common.exceptions.custom_exception_handler",
}
```

This means views never need `try/except` blocks for domain errors — they propagate up automatically.

## Navigation
- [Core Architecture](../django-core-architecture/SKILL.md)
- [Business Logic](../django-business-logic/SKILL.md)
- [Production Ops](../django-production-ops/SKILL.md)
