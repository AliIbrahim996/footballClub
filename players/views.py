import math
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.db.models import Avg, Count
from django.utils import timezone
from django.utils.translation import gettext as _
from rest_framework import serializers, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action, api_view, permission_classes, throttle_classes
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle

from .access import ClubScopedMixin, IsClubMember, seed_default_skills
from .models import Category, Club, Membership, Player, PlayerSkills, Plans, Skills
from .serializers import (
    CategorySerializer, EvaluationSerializer, PlanSerializer, PlayerDetailSerializer,
    PlayerSerializer, SkillSerializer,
)


def club_payload(club: Club, membership: Membership) -> dict:
    days_left = 0
    if club.status == Club.TRIALING and club.trial_ends_at:
        days_left = max(0, math.ceil((club.trial_ends_at - timezone.now()).total_seconds() / 86400))
    return {
        "trial_days_left": days_left,
        "name": club.name, "status": club.status, "entitled": club.is_entitled, "role": membership.role,
        "trial_ends_at": club.trial_ends_at, "current_period_end": club.current_period_end,
        "billing_configured": bool(settings.STRIPE_SECRET_KEY and settings.STRIPE_PRICE_ID),
    }


@api_view(["POST"])
@permission_classes([AllowAny])
@throttle_classes([ScopedRateThrottle])
def login(request):
    user = authenticate(username=request.data.get("username"), password=request.data.get("password"))
    if user is None:
        return Response({"detail": _("Invalid username or password.")}, status=status.HTTP_400_BAD_REQUEST)
    token, _created = Token.objects.get_or_create(user=user)
    return Response({"token": token.key, "username": user.username})


login.cls.throttle_scope = "login"


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    club_name = serializers.CharField(max_length=255)

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError(_("This username is already taken."))
        return value

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(_("An account with this email already exists."))
        return value

    def validate(self, attrs):
        try:
            validate_password(attrs["password"], User(username=attrs["username"], email=attrs["email"]))
        except DjangoValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})
        return attrs


@api_view(["POST"])
@permission_classes([AllowAny])
@throttle_classes([ScopedRateThrottle])
def register(request):
    """Create a user, their club (on a free trial) and a starter skill set; sign them in."""
    s = RegisterSerializer(data=request.data)
    s.is_valid(raise_exception=True)
    d = s.validated_data
    with transaction.atomic():
        user = User.objects.create_user(d["username"], d["email"], d["password"])
        club = Club.objects.create(
            name=d["club_name"], status=Club.TRIALING, trial_ends_at=timezone.now() + timedelta(days=settings.TRIAL_DAYS),
        )
        Membership.objects.create(user=user, club=club, role=Membership.OWNER)
        seed_default_skills(club)
        token = Token.objects.create(user=user)
    return Response({"token": token.key, "username": user.username}, status=status.HTTP_201_CREATED)


register.cls.throttle_scope = "register"


@api_view(["POST"])
def logout(request):
    Token.objects.filter(user=request.user).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET"])
@permission_classes([IsClubMember])
def me(request):
    return Response({"username": request.user.username, "club": club_payload(request.club, request.membership)})


@api_view(["GET"])
@permission_classes([ClubScopedMixin.permission_classes[0]])
def dashboard(request):
    """Aggregate numbers for the management dashboard (this club only)."""
    club = request.club
    top = (
        Player.objects.filter(club=club).annotate(avg=Avg("playerskills__value"))
        .filter(avg__isnull=False).order_by("-avg")[:5]
    )
    by_category = (
        PlayerSkills.objects.filter(player__club=club).values("skill__category__name")
        .annotate(avg=Avg("value"), n=Count("id")).order_by("skill__category__name")
    )
    return Response({
        "players": Player.objects.filter(club=club).count(),
        "skills": Skills.objects.filter(club=club).count(),
        "plans": Plans.objects.filter(club=club).count(),
        "evaluations": PlayerSkills.objects.filter(player__club=club).count(),
        "top_players": [
            {"id": p.id, "name": f"{p.first_name} {p.name}", "image": p.image.url if p.image else None, "average": round(p.avg, 2)}
            for p in top
        ],
        "category_averages": [
            {"category": r["skill__category__name"], "average": round(r["avg"], 2), "count": r["n"]} for r in by_category
        ],
        "recent_plans": PlanSerializer(
            Plans.objects.filter(club=club).order_by("-created_at")[:4], many=True, context={"request": request},
        ).data,
    })


class CategoryViewSet(ClubScopedMixin, viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = None


class SkillViewSet(ClubScopedMixin, viewsets.ModelViewSet):
    queryset = Skills.objects.select_related("category")
    serializer_class = SkillSerializer
    filterset_fields = ["category"]
    pagination_class = None


class PlayerViewSet(ClubScopedMixin, viewsets.ModelViewSet):
    queryset = Player.objects.prefetch_related("playerskills_set").order_by("first_name", "name")
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    search_fields = ["name", "first_name", "city", "society", "email_address"]
    ordering_fields = ["name", "first_name", "city", "date_of_birth"]
    filterset_fields = ["city", "society"]

    def get_serializer_class(self):
        return PlayerDetailSerializer if self.action == "retrieve" else PlayerSerializer

    @action(detail=True, methods=["post"])
    def evaluate(self, request, pk=None):
        player = self.get_object()
        serializer = EvaluationSerializer(data=request.data, context={"club": request.club})
        serializer.is_valid(raise_exception=True)
        serializer.save(player, request.user.username)
        return Response(PlayerDetailSerializer(player, context={"request": request}).data)


class PlanViewSet(ClubScopedMixin, viewsets.ModelViewSet):
    queryset = Plans.objects.order_by("-created_at")
    serializer_class = PlanSerializer
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    search_fields = ["comment", "title", "created_by"]
    filterset_fields = {"created_by": ["exact"], "created_at": ["gte", "lte"]}

    def perform_create(self, serializer):
        serializer.save(club=self.request.club, created_by=self.request.user.username)

    @action(detail=False, methods=["get"])
    def managers(self, request):
        return Response(sorted(set(self.get_queryset().values_list("created_by", flat=True))))
