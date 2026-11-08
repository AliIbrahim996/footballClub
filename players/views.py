from django.contrib.auth import authenticate
from django.db.models import Avg, Count
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Category, Player, PlayerSkills, Plans, Skills
from .serializers import (
    CategorySerializer, EvaluationSerializer, PlanSerializer, PlayerDetailSerializer,
    PlayerSerializer, SkillSerializer,
)


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    user = authenticate(username=request.data.get("username"), password=request.data.get("password"))
    if user is None:
        return Response({"detail": "Invalid username or password."}, status=status.HTTP_400_BAD_REQUEST)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({"token": token.key, "username": user.username})


@api_view(["POST"])
def logout(request):
    Token.objects.filter(user=request.user).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET"])
def me(request):
    return Response({"username": request.user.username, "is_staff": request.user.is_staff})


@api_view(["GET"])
def dashboard(request):
    """Aggregate numbers for the management dashboard."""
    top = (
        Player.objects.annotate(avg=Avg("playerskills__value"))
        .filter(avg__isnull=False).order_by("-avg")[:5]
    )
    by_category = (
        PlayerSkills.objects.values("skill__category__name").annotate(avg=Avg("value"), n=Count("id"))
        .order_by("skill__category__name")
    )
    return Response({
        "players": Player.objects.count(),
        "skills": Skills.objects.count(),
        "plans": Plans.objects.count(),
        "evaluations": PlayerSkills.objects.count(),
        "top_players": [
            {"id": p.id, "name": f"{p.first_name} {p.name}", "image": request.build_absolute_uri(p.image.url) if p.image else None,
             "average": round(p.avg, 2)} for p in top
        ],
        "category_averages": [
            {"category": r["skill__category__name"], "average": round(r["avg"], 2), "count": r["n"]}
            for r in by_category
        ],
        "recent_plans": PlanSerializer(Plans.objects.order_by("-created_at")[:4], many=True,
                                       context={"request": request}).data,
    })


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = None


class SkillViewSet(viewsets.ModelViewSet):
    queryset = Skills.objects.select_related("category")
    serializer_class = SkillSerializer
    filterset_fields = ["category"]
    pagination_class = None


class PlayerViewSet(viewsets.ModelViewSet):
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
        serializer = EvaluationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(player, request.user.username)
        return Response(PlayerDetailSerializer(player, context={"request": request}).data)


class PlanViewSet(viewsets.ModelViewSet):
    queryset = Plans.objects.order_by("-created_at")
    serializer_class = PlanSerializer
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    search_fields = ["comment", "title", "created_by"]
    filterset_fields = {"created_by": ["exact"], "created_at": ["gte", "lte"]}

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user.username)

    @action(detail=False, methods=["get"])
    def managers(self, request):
        return Response(sorted(set(Plans.objects.values_list("created_by", flat=True))))
