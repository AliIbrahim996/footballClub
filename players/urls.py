from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import billing, contact, team, views

router = DefaultRouter()
router.register("players", views.PlayerViewSet, basename="player")
router.register("skills", views.SkillViewSet, basename="skill")
router.register("categories", views.CategoryViewSet, basename="category")
router.register("plans", views.PlanViewSet, basename="plan")

urlpatterns = [
    path("auth/login/", views.login),
    path("auth/register/", views.register),
    path("auth/logout/", views.logout),
    path("auth/me/", views.me),
    path("dashboard/", views.dashboard),
    path("contact/", contact.contact),
    path("auth/invite/", team.invite_info),
    path("auth/accept-invite/", team.accept_invite),
    path("team/", team.team),
    path("team/invites/", team.invite),
    path("team/invites/<int:pk>/", team.remove_invite),
    path("team/members/<int:pk>/", team.remove_member),
    path("plans/<int:pk>/share/", team.share_plan),
    path("shared/<str:token>/", team.shared_plan),
    path("billing/checkout/", billing.checkout),
    path("billing/portal/", billing.portal),
    path("billing/webhook/", billing.webhook),
    path("", include(router.urls)),
]
