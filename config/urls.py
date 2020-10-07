from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

urlpatterns = [
                  path('buckets/', include('bucket.urls')),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
              + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)