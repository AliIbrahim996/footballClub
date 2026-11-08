"""Multi-coach features: invitations, team management and public plan sharing."""
import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext as _
from rest_framework import serializers, status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle

from .access import HasEntitlement
from .models import Invitation, Membership, Plans
from .serializers import PlanSerializer

INVITE_TTL = timedelta(days=14)


def _owner_required(request):
    if request.membership.role != Membership.OWNER:
        return Response({"detail": _("Only the club owner can manage the team.")}, status=status.HTTP_403_FORBIDDEN)
    return None


def _seats_used(club) -> int:
    return club.memberships.count() + club.invitations.filter(accepted_at__isnull=True).count()


def _member(m: Membership) -> dict:
    return {"id": m.id, "username": m.user.username, "email": m.user.email, "role": m.role}


def _invite(i: Invitation, include_token: bool = False) -> dict:
    data = {"id": i.id, "email": i.email, "role": i.role, "created_at": i.created_at}
    if include_token:  # the token is a credential for joining the club: only the owner may see it
        data["token"] = i.token
    return data


@api_view(["GET"])
@permission_classes([HasEntitlement])
def team(request):
    club = request.club
    return Response({
        "seats_limit": settings.MAX_SEATS,
        "seats_used": _seats_used(club),
        "members": [_member(m) for m in club.memberships.select_related("user").order_by("id")],
        "invites": [
            _invite(i, include_token=request.membership.role == Membership.OWNER)
            for i in club.invitations.filter(accepted_at__isnull=True).order_by("-created_at")
        ],
    })


class InviteSerializer(serializers.Serializer):
    email = serializers.EmailField()
    role = serializers.ChoiceField(choices=[Membership.COACH, Membership.VIEWER], default=Membership.COACH)


@api_view(["POST"])
@permission_classes([HasEntitlement])
def invite(request):
    denied = _owner_required(request)
    if denied:
        return denied
    s = InviteSerializer(data=request.data)
    s.is_valid(raise_exception=True)
    club, email = request.club, s.validated_data["email"].lower()
    if _seats_used(club) >= settings.MAX_SEATS:
        return Response({"detail": _("Seat limit reached for your plan.")}, status=status.HTTP_400_BAD_REQUEST)
    if User.objects.filter(email__iexact=email).exists():
        return Response({"email": [_("An account with this email already exists.")]}, status=status.HTTP_400_BAD_REQUEST)
    inv = Invitation.objects.create(
        club=club, email=email, role=s.validated_data["role"], token=secrets.token_urlsafe(24), invited_by=request.user,
    )
    lang = (request.headers.get("Accept-Language") or "en")[:2].lower()
    link = f"{settings.FRONTEND_URL}/{lang if lang in ('en', 'ar') else 'en'}/join?token={inv.token}"
    # Best effort: the owner also gets the link back and can share it manually.
    send_mail(
        _("You're invited to %(club)s on Pitchside") % {"club": club.name},
        _("Join %(club)s: %(link)s") % {"club": club.name, "link": link},
        None, [email], fail_silently=True,
    )
    return Response({**_invite(inv, include_token=True), "link": link}, status=status.HTTP_201_CREATED)


@api_view(["DELETE"])
@permission_classes([HasEntitlement])
def remove_invite(request, pk):
    denied = _owner_required(request)
    if denied:
        return denied
    request.club.invitations.filter(pk=pk, accepted_at__isnull=True).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["DELETE"])
@permission_classes([HasEntitlement])
def remove_member(request, pk):
    denied = _owner_required(request)
    if denied:
        return denied
    target = request.club.memberships.filter(pk=pk).select_related("user").first()
    if target is None:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if target.role == Membership.OWNER:
        return Response({"detail": _("The owner cannot be removed.")}, status=status.HTTP_400_BAD_REQUEST)
    Token.objects.filter(user=target.user).delete()
    target.user.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


def _valid_invite(token: str):
    inv = Invitation.objects.select_related("club").filter(token=token or "", accepted_at__isnull=True).first()
    if inv and timezone.now() - inv.created_at > INVITE_TTL:
        return None
    return inv


@api_view(["GET"])
@permission_classes([AllowAny])
@throttle_classes([ScopedRateThrottle])
def invite_info(request):
    inv = _valid_invite(request.query_params.get("token"))
    if inv is None:
        return Response({"detail": _("This invitation is invalid or has expired.")}, status=status.HTTP_404_NOT_FOUND)
    return Response({"club_name": inv.club.name, "email": inv.email, "role": inv.role})


invite_info.cls.throttle_scope = "register"


class AcceptSerializer(serializers.Serializer):
    token = serializers.CharField()
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)


@api_view(["POST"])
@permission_classes([AllowAny])
@throttle_classes([ScopedRateThrottle])
def accept_invite(request):
    s = AcceptSerializer(data=request.data)
    s.is_valid(raise_exception=True)
    d = s.validated_data
    inv = _valid_invite(d["token"])
    if inv is None:
        return Response({"detail": _("This invitation is invalid or has expired.")}, status=status.HTTP_404_NOT_FOUND)
    if User.objects.filter(username__iexact=d["username"]).exists():
        return Response({"username": [_("This username is already taken.")]}, status=status.HTTP_400_BAD_REQUEST)
    try:
        validate_password(d["password"], User(username=d["username"], email=inv.email))
    except DjangoValidationError as e:
        return Response({"password": list(e.messages)}, status=status.HTTP_400_BAD_REQUEST)
    with transaction.atomic():
        user = User.objects.create_user(d["username"], inv.email, d["password"])
        Membership.objects.create(user=user, club=inv.club, role=inv.role)
        inv.accepted_at = timezone.now()
        inv.save(update_fields=["accepted_at"])
        token = Token.objects.create(user=user)
    return Response({"token": token.key, "username": user.username}, status=status.HTTP_201_CREATED)


accept_invite.cls.throttle_scope = "register"


# --- public plan sharing ---------------------------------------------------------

@api_view(["POST", "DELETE"])
@permission_classes([HasEntitlement])
def share_plan(request, pk):
    """POST creates (or returns) a public read-only link for a plan; DELETE revokes it."""
    plan = Plans.objects.filter(club=request.club, pk=pk).first()
    if plan is None:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == "DELETE":
        plan.share_token = None
        plan.save(update_fields=["share_token"])
        return Response(status=status.HTTP_204_NO_CONTENT)
    if not plan.share_token:
        plan.share_token = secrets.token_urlsafe(16)
        plan.save(update_fields=["share_token"])
    return Response({"share_token": plan.share_token})


@api_view(["GET"])
@permission_classes([AllowAny])
def shared_plan(request, token):
    plan = Plans.objects.select_related("club").filter(share_token=token).first()
    if plan is None:
        return Response({"detail": _("Not found.")}, status=status.HTTP_404_NOT_FOUND)
    data = PlanSerializer(plan, context={"request": request}).data
    return Response({
        "title": data["title"], "comment": data["comment"], "image": data["image"], "board": data["board"],
        "created_at": data["created_at"], "club_name": plan.club.name,
    })
