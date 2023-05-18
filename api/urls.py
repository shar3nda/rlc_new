from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    AnnotationListCreateViewSet,
    SentenceViewSet,
    UserViewSet,
    auto_annotate,
    AnnotationRetrieveUpdateDestroyViewSet,
)

router = DefaultRouter()
router.register(
    r"annotations/(?P<sentence_id>\d+)/(?P<alt>\w+)",
    AnnotationListCreateViewSet,
    basename="annotations",
)
router.register(
    r"annotations/(?P<guid>\w+)",
    AnnotationRetrieveUpdateDestroyViewSet,
    basename="annotations",
)

router.register(r"get_corrections", SentenceViewSet)
router.register(r"get_user_info", UserViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("auto_annotate/", auto_annotate, name="auto_annotate"),
]
