"""
Definisce l'instradamento (routing) per le connessioni WebSocket dell'applicazione gestione_aste.
Associa i path URL asincroni ai relativi Consumer.
"""
from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/chat/<int:asta_id>/<int:altro_utente_id>/', consumers.ChatConsumer.as_asgi()),
]