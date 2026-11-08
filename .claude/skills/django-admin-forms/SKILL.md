---
name: django-admin-forms
description: admin.py, forms.py, file uploads, and the Django admin performance guide
---

# Django Admin & Forms

The Django Admin is designed for internal tooling, not production user-facing interfaces. Its default behavior, however, introduces several serious performance pitfalls and code quality issues that must be explicitly addressed.

---

## 1. The N+1 Problem in Django Admin

Django Admin's list view iterates over a queryset and calls `list_display` columns on each row. Any column that accesses a related object (FK, reverse FK, `__str__` methods that access relations) will fire an additional SQL query per row.

### `get_queryset` Override — Mandatory for Any Relational Field in `list_display`

```python
@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user_email", "plan_name", "status", "created_at")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("user", "plan")

    # These display methods access pre-fetched data — zero extra queries
    @admin.display(description="User Email", ordering="user__email")
    def user_email(self, obj):
        return obj.user.email

    @admin.display(description="Plan", ordering="plan__name")
    def plan_name(self, obj):
        return obj.plan.name
```

> ⚠️ **Always use `@admin.display(ordering=...)` on computed columns.** Without it, clicking the column header in the admin list view will raise an error or produce a wrong sort order.

### `raw_id_fields` and `autocomplete_fields` — Mandatory for Large Tables

Django's default FK widget renders a `<select>` HTML element populated by `SELECT * FROM table` with no `LIMIT`. On a table with 100,000+ users, this will:
1. Execute a full-table scan.
2. Serialize all rows into HTML.
3. Send megabytes of HTML to the browser.
4. Crash the browser tab.

✅ **Recommended:**
```python
class SubscriptionAdmin(admin.ModelAdmin):
    # Shows a text input with a magnifier icon to search in a popup
    raw_id_fields = ("user",)
    
    # Preferred over raw_id_fields — shows a search-as-you-type dropdown (requires search_fields on target admin)
    autocomplete_fields = ("plan",)
```

For `autocomplete_fields` to work, the referenced model's `ModelAdmin` must define `search_fields`:
```python
@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    search_fields = ["name"]
```

---

## 2. Admin Mixins for Reusable Behavior

Django's admin framework is built on Python's MRO (Method Resolution Order) and uses mixins extensively. This is the correct Django-native pattern for sharing behavior across `ModelAdmin` and `InlineAdmin` classes.

✅ **Recommended (Mixin for FK filtering):**
```python
class QuestionFormfieldMixin:
    """
    Restricts parent_question and conditional_on_question FK dropdowns
    to only show Questions belonging to the current Form being edited.
    
    Prevents the default behavior of loading ALL questions from ALL forms
    into the dropdown, which is both a UX problem and a performance problem
    at scale.
    
    MRO requirement: Place this mixin BEFORE admin.ModelAdmin or admin.StackedInline
    in the class definition to ensure its formfield_for_foreignkey is called first.
    """
    FILTERED_FK_FIELDS = ("parent_question", "conditional_on_question")

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name not in self.FILTERED_FK_FIELDS or not request.resolver_match:
            return super().formfield_for_foreignkey(db_field, request, **kwargs)

        url_name = request.resolver_match.url_name
        obj_id = request.resolver_match.kwargs.get("object_id")

        if url_name in ("app_form_add", "app_question_add"):
            kwargs["queryset"] = Question.objects.none()
        elif url_name == "app_form_change" and obj_id:
            kwargs["queryset"] = Question.objects.filter(form_id=obj_id)
        elif url_name == "app_question_change" and obj_id:
            q = Question.objects.filter(pk=obj_id).only("form_id").first()
            kwargs["queryset"] = (
                Question.objects.filter(form_id=q.form_id) if (q and q.form_id)
                else Question.objects.none()
            )

        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# Now all three classes share the behavior with zero duplication
class QuestionInline(QuestionFormfieldMixin, admin.StackedInline):
    model = Question
    form = QuestionForm

class RepeatableQuestionInline(QuestionFormfieldMixin, admin.StackedInline):
    model = Question
    fk_name = "parent_question"
    form = QuestionForm

class QuestionAdmin(QuestionFormfieldMixin, admin.ModelAdmin):
    pass
```

**Why this is the right design:**
- **MRO Composability:** Python's C3 linearization ensures `QuestionFormfieldMixin.formfield_for_foreignkey` is always called before Django's base implementation. Calling `super()` chains correctly.
- **Open/Closed Principle:** Adding a new Inline class only requires inheriting from the Mixin — no changes to existing code.
- **Zero Coupling:** The mixin knows nothing about the specific admin classes that use it. It only cares about `db_field.name` and `request.resolver_match`.

### Other Useful Admin Mixins

```python
class ReadonlyAdminMixin:
    """Makes the entire admin model read-only (no add/change/delete)."""
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False

class TimestampAdminMixin:
    """Adds created_at and updated_at to readonly_fields automatically."""
    readonly_fields = ("created_at", "updated_at")
```

---

## 3. Forms: The Validation Layer

Django's `Form` and `ModelForm` are validation contracts, not execution engines. Follow the same principle as DRF serializers: validate in the form, act in the service/view.

### Custom `clean_<field>` and `clean()`

```python
class TransferForm(forms.Form):
    from_account = forms.ModelChoiceField(queryset=Account.objects.all())
    to_account = forms.ModelChoiceField(queryset=Account.objects.all())
    amount = forms.DecimalField(min_value=Decimal("0.01"), decimal_places=2)

    def clean_amount(self):
        amount = self.cleaned_data["amount"]
        if amount > settings.MAX_TRANSFER_AMOUNT:
            raise forms.ValidationError(f"Amount exceeds max transfer limit of {settings.MAX_TRANSFER_AMOUNT}.")
        return amount

    def clean(self):
        cleaned_data = super().clean()
        from_account = cleaned_data.get("from_account")
        to_account = cleaned_data.get("to_account")

        if from_account and to_account and from_account == to_account:
            raise forms.ValidationError("Source and destination accounts must be different.")

        return cleaned_data

    # ❌ No .save() method! The view calls the service after form.is_valid()
```

✅ **View using the form correctly:**
```python
def transfer_funds_view(request):
    form = TransferForm(request.POST or None)
    if form.is_valid():
        transfer_funds_service(
            from_account=form.cleaned_data["from_account"],
            to_account=form.cleaned_data["to_account"],
            amount=form.cleaned_data["amount"],
        )
        return redirect("success")
    return render(request, "transfer.html", {"form": form})
```

---

## 4. File Uploads

### Never Serve Uploads from the Application Server in Production

In production, uploaded files should live on a dedicated object store (S3, GCS, Azure Blob). Django's `FileField` and `ImageField` store only the **path** in the database; actual bytes go to the configured storage backend.

✅ **Recommended (`django-storages` + S3):**
```python
# config/settings/production.py
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME")
AWS_S3_FILE_OVERWRITE = False   # Prevents overwriting files with the same name
```

### Validate File Content, Not Just Extension

File extensions are trivially spoofed. Always validate the MIME type by reading the file's magic bytes.

✅ **Recommended (in a form or serializer):**
```python
import magic  # python-magic library

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "application/pdf"}

def validate_file_content_type(file):
    mime = magic.from_buffer(file.read(2048), mime=True)
    file.seek(0)  # Reset file pointer after reading
    if mime not in ALLOWED_MIME_TYPES:
        raise forms.ValidationError(f"File type '{mime}' is not allowed.")

class DocumentUploadForm(forms.Form):
    document = forms.FileField(validators=[validate_file_content_type])
```

### Enforce File Size Limits

Django does not enforce file size limits by default. Enforce them at the form/serializer level and at the web server level (Nginx's `client_max_body_size`).

```python
MAX_UPLOAD_SIZE_MB = 10

def validate_file_size(file):
    if file.size > MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise forms.ValidationError(f"File size exceeds {MAX_UPLOAD_SIZE_MB}MB limit.")
```

### Sanitize Filenames

`werkzeug.utils.secure_filename` or Django's `FileSystemStorage.get_valid_name` should be used to strip path separators and dangerous characters from user-provided filenames.

```python
from django.utils.text import get_valid_filename

safe_name = get_valid_filename(uploaded_file.name)
# "../../etc/passwd" -> "....etcpasswd"
```

## Navigation
- [Models & ORM](../django-models-orm/SKILL.md)
- [Views & APIs](../django-views-apis/SKILL.md)
- [Production Ops](../django-production-ops/SKILL.md)
