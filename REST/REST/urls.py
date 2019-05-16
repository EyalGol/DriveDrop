from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('admin/', admin.site.urls),
    url(r'^rest-auth/', include('rest_auth.urls'))
]
