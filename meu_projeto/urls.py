from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("trabalhos.urls")),  # rotas da sua app “trabalhos”
]

# Se estiver em DEBUG, permite servir MEDIA durante dev:

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
