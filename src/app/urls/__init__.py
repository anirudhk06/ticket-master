from .category import urlpatterns as category_urls
from .event import urlpatterns as event_urls

urlpatterns = [
    *category_urls,
    *event_urls
]