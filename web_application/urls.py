from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from . import views as my_views
from django.contrib.auth import views

urlpatterns = i18n_patterns(
    path('', my_views.home, name='home'),
    path('admin/', admin.site.urls, name='admin'),
    path('login/', views.LoginView.as_view(redirect_authenticated_user=True), name='login'),
    path('player/', include('players.urls')),
    path('i18n/', include('django.conf.urls.i18n')),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
