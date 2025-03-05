from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'files', views.FileViewSet)
router.register(r'nodes', views.StorageNodeViewSet)

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('api/', include(router.urls)),
]