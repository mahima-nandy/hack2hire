from django.urls import re_path

from .consumers import InterviewConsumer

websocket_urlpatterns = [
    re_path(r"ws/interviews/(?P<session_id>\d+)/$", InterviewConsumer.as_asgi()),
]
