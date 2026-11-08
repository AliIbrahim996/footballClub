from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("players", views.PlayerViewSet, basename="player")
router.register("skills", views.SkillViewSet, basename="skill")
router.register("categories", views.CategoryViewSet, basename="category")
router.register("plans", views.PlanViewSet, basename="plan")

urlpatterns = [
    path("auth/login/", views.login),
    path("auth/logout/", views.logout),
    path("auth/me/", views.me),
    path("dashboard/", views.dashboard),
    path("", include(router.urls)),
]
