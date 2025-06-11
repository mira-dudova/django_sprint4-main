"""blogicum URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Приложение blog (все URL из blog.urls)
    path('', include('blog.urls')),

    # Приложение pages (статичные страницы)
    path('pages/', include('pages.urls')),

    # Админка
    path('admin/', admin.site.urls),

    # Встроенные пути для аутентификации (логин, логаут, смена пароля)
    path('auth/', include('django.contrib.auth.urls')),

    path('', include('blog.auth_urls')),
]

# Обработчики ошибок с кастомными страницами
handler403 = 'pages.views.page_403'
handler404 = 'pages.views.page_404'
handler500 = 'pages.views.page_500'
