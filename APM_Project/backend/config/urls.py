"""URL configuration for APM TOPNET."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from apm import views as apm_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('mot-de-passe-oublie/', apm_views.password_reset_request, name='password_reset_request'),
    path('mot-de-passe-oublie/envoye/', apm_views.password_reset_done, name='password_reset_done'),
    path('reinitialiser/<str:token>/', apm_views.password_reset_confirm, name='password_reset_confirm'),
    path('reinitialiser/succes/', apm_views.password_reset_complete, name='password_reset_complete'),
    path('', include('apm.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
