"""Stripe subscription plumbing. Inert (HTTP 501) until STRIPE_* settings are provided."""
from datetime import datetime, timezone as dt_tz

from django.conf import settings
from django.utils.translation import gettext as _
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .access import IsClubMember
from .models import Club, Membership

LOCALES = {"en", "ar"}
STATUS_MAP = {
    "active": Club.ACTIVE, "trialing": Club.ACTIVE, "past_due": Club.PAST_DUE, "unpaid": Club.PAST_DUE,
    "canceled": Club.CANCELED, "incomplete_expired": Club.CANCELED,
}


def configured() -> bool:
    return bool(settings.STRIPE_SECRET_KEY and settings.STRIPE_PRICE_ID)


def _stripe():
    import stripe

    stripe.api_key = settings.STRIPE_SECRET_KEY
    return stripe


def _locale(request) -> str:
    lang = (request.headers.get("Accept-Language") or "en")[:2].lower()
    return lang if lang in LOCALES else "en"


def _not_configured():
    return Response({"detail": _("Billing is not configured on this server.")}, status=status.HTTP_501_NOT_IMPLEMENTED)


def _owner_only(request):
    return request.membership.role == Membership.OWNER


@api_view(["POST"])
@permission_classes([IsClubMember])
def checkout(request):
    if not configured():
        return _not_configured()
    if not _owner_only(request):
        return Response({"detail": _("Only the club owner can manage billing.")}, status=status.HTTP_403_FORBIDDEN)
    club, loc = request.club, _locale(request)
    params = {
        "mode": "subscription",
        "line_items": [{"price": settings.STRIPE_PRICE_ID, "quantity": 1}],
        "client_reference_id": str(club.id),
        "allow_promotion_codes": True,
        "success_url": f"{settings.FRONTEND_URL}/{loc}/billing?checkout=success",
        "cancel_url": f"{settings.FRONTEND_URL}/{loc}/billing?checkout=cancelled",
        "locale": loc if loc != "ar" else "auto",
    }
    if club.stripe_customer_id:
        params["customer"] = club.stripe_customer_id
    elif request.user.email:
        params["customer_email"] = request.user.email
    session = _stripe().checkout.Session.create(**params)
    return Response({"url": session.url})


@api_view(["POST"])
@permission_classes([IsClubMember])
def portal(request):
    if not configured():
        return _not_configured()
    if not _owner_only(request) or not request.club.stripe_customer_id:
        return Response({"detail": _("No billing account to manage yet.")}, status=status.HTTP_400_BAD_REQUEST)
    session = _stripe().billing_portal.Session.create(
        customer=request.club.stripe_customer_id, return_url=f"{settings.FRONTEND_URL}/{_locale(request)}/billing",
    )
    return Response({"url": session.url})


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def webhook(request):
    if not (settings.STRIPE_WEBHOOK_SECRET and settings.STRIPE_SECRET_KEY):
        return _not_configured()
    stripe = _stripe()
    try:
        event = stripe.Webhook.construct_event(
            request.body, request.headers.get("Stripe-Signature", ""), settings.STRIPE_WEBHOOK_SECRET,
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return Response(status=status.HTTP_400_BAD_REQUEST)
    apply_event(event.to_dict() if hasattr(event, "to_dict") else dict(event))
    return Response({"received": True})


def _period_end(sub: dict):
    ts = sub.get("current_period_end")
    if ts is None:  # newer API versions put it on the subscription item
        items = (sub.get("items") or {}).get("data") or []
        ts = items[0].get("current_period_end") if items else None
    return datetime.fromtimestamp(ts, tz=dt_tz.utc) if ts else None


def apply_event(event: dict) -> None:
    """Update the club that an (already verified) Stripe event refers to. Idempotent."""
    kind, obj = event.get("type"), (event.get("data") or {}).get("object") or {}
    if kind == "checkout.session.completed":
        club = Club.objects.filter(pk=obj.get("client_reference_id") or 0).first()
        if club:
            club.stripe_customer_id = obj.get("customer") or club.stripe_customer_id
            club.stripe_subscription_id = obj.get("subscription") or club.stripe_subscription_id
            club.status = Club.ACTIVE
            club.save()
    elif kind in ("customer.subscription.created", "customer.subscription.updated", "customer.subscription.deleted"):
        club = (
            Club.objects.filter(stripe_subscription_id=obj.get("id")).first()
            or Club.objects.filter(stripe_customer_id=obj.get("customer") or "none").first()
        )
        if club:
            club.stripe_subscription_id = obj.get("id", club.stripe_subscription_id)
            club.status = Club.CANCELED if kind.endswith("deleted") else STATUS_MAP.get(obj.get("status"), club.status)
            club.current_period_end = _period_end(obj) or club.current_period_end
            club.save()
