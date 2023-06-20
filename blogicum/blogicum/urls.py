from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LogoutView
from django.urls import path, include, reverse_lazy
from django.views.generic import CreateView


urlpatterns = [
    path('', include('blog.urls')),
    path('auth/registration/',
         CreateView.as_view(
            template_name='registration/registration_form.html',
            form_class=UserCreationForm,
            success_url=reverse_lazy('blog:index')
         ),
         name='registration'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('admin/', admin.site.urls),
    path('category/', include('blog.urls')),
    path('pages/', include('pages.urls')),
    path('auth/', include('django.contrib.auth.urls')),
]

# Добавьте пути отладочной панели только в режиме DEBUG
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'core.views.page_not_found'
handler500 = 'core.views.internal_server_error'
