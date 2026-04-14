import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import gestione_aste.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_aste.settings')

application = ProtocolTypeRouter({
    # Il traffico HTTP normale (caricamento pagine) va a Django standard
    "http": get_asgi_application(),
    
    # Il traffico WebSocket (la chat) va a Channels!
    "websocket": AuthMiddlewareStack(
        URLRouter(
            gestione_aste.routing.websocket_urlpatterns
        )
    ),
})