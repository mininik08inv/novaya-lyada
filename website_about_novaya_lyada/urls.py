from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls', namespace='core')),
    path('profile/', include('accounts.urls', namespace='accounts')),
    path('events/', include('events.urls', namespace="events")),
    path('about-village/', include('about_village.urls', namespace="about_village")),
    path('places/', include('places.urls', namespace="places")),
    path('ideas/', include('ideas.urls', namespace="ideas")),
    path('advertisement/', include('advertisement.urls', namespace="advertisement")),
    path('accounts/', include('allauth.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Подача статических файлов из STATICFILES_DIRS
    from django.contrib.staticfiles.views import serve
    from django.urls import re_path
    import os
    
    # Добавляем обслуживание статических файлов
    urlpatterns += [
        re_path(r'^static/(?P<path>.*)$', serve, {'document_root': os.path.join(settings.BASE_DIR, 'static')}),
    ]