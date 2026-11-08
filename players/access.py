"""Tenant resolution and subscription gating for the API."""
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import APIException
from rest_framework.permissions import SAFE_METHODS, BasePermission

from .models import Club, Membership


class SubscriptionRequired(APIException):
    status_code = 402
    default_detail = _("An active subscription is required.")
    default_code = "subscription_required"


def get_membership(user) -> Membership | None:
    if not user or not user.is_authenticated:
        return None
    try:
        return user.membership
    except Membership.DoesNotExist:
        return None


class IsClubMember(BasePermission):
    """Authenticated user that belongs to a club. Exposes it as request.club."""

    def has_permission(self, request, view):
        membership = get_membership(request.user)
        if membership is None:
            return False
        request.club = membership.club
        request.membership = membership
        return True


class HasEntitlement(IsClubMember):
    """Club members whose club may use the paid features (trial or subscription), with role checks."""

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        if not request.club.is_entitled:
            raise SubscriptionRequired()
        # Viewers are read-only.
        return request.method in SAFE_METHODS or request.membership.role != Membership.VIEWER


class ClubScopedMixin:
    """Restrict a ModelViewSet to the caller's club and stamp new rows with it."""

    permission_classes = [HasEntitlement]

    def get_queryset(self):
        return super().get_queryset().filter(club=self.request.club)

    def perform_create(self, serializer):
        serializer.save(club=self.request.club)


def seed_default_skills(club: Club) -> None:
    """Give a brand-new club a sensible starting set of rating skills."""
    from .models import Category, Skills

    defaults = {
        "Technical": ["Passing", "Dribbling", "First touch", "Shooting"],
        "Physical": ["Speed", "Stamina", "Strength"],
        "Tactical": ["Positioning", "Vision", "Pressing"],
        "Mental": ["Leadership", "Composure"],
    }
    for cat_name, names in defaults.items():
        cat = Category.objects.create(club=club, name=cat_name)
        Skills.objects.bulk_create(Skills(club=club, category=cat, skill_name=n, comment="") for n in names)
