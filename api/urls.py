from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    SentenceViewSet,
    UserViewSet,
    auto_annotate,
    AnnotationViewSet,
)

router = DefaultRouter()
router.register(r"annotations", AnnotationViewSet, basename="annotations")



router.register(r"get_corrections", SentenceViewSet)
router.register(r"get_user_info", UserViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("auto_annotate/", auto_annotate, name="auto_annotate"),
]
