import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.contrib.auth.models import User
from .models import Messaggio

class ChatConsumer(AsyncWebsocketConsumer):
    """
    Gestisce le connessioni WebSocket per la chat in tempo reale
    tra due utenti per una specifica asta collegando la logica
    asincrona alle query sincrone del DB.
    """
    
    async def connect(self):
        """
        Gestisce la connessione di un nuovo client alla stanza WebSocket.
        Calcola un nome univoco per la stanza in base agli ID dei partecipanti.
        """
        self.asta_id = self.scope['url_route']['kwargs']['asta_id']
        self.altro_utente_id = self.scope['url_route']['kwargs']['altro_utente_id']
        self.mio_id = self.scope['user'].id

        low_id = min(self.mio_id, int(self.altro_utente_id))
        high_id = max(self.mio_id, int(self.altro_utente_id))
        self.room_name = f"chat_asta_{self.asta_id}_{low_id}_{high_id}"
        
        self.room_group_name = self.room_name

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        """
        Rimuove il client dal gruppo al termine della connessione.
        """
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """
        Riceve i messaggi inviati dal client (browser) tramite WebSocket,
        ne delega il salvataggio asincrono sul database ed emette l'evento
        di invio verso il gruppo della chat.
        """
        text_data_json = json.loads(text_data)
        messaggio = text_data_json['message']

        await self.salva_messaggio(self.mio_id, self.altro_utente_id, self.asta_id, messaggio)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': messaggio,
                'mittente': self.scope['user'].username
            }
        )

    async def chat_message(self, event):
        """
        Riceve i messaggi delegati dal channel layer alla stanza
        e li inoltra effettivamente al WebSocket del client connesso.
        """
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'mittente': event['mittente']
        }))

    @sync_to_async
    def salva_messaggio(self, mittente_id, destinatario_id, asta_id, testo):
        """
        Interazione sicura (con @sync_to_async) verso il database relazionale (sincrono).
        Recupera le referenze agli oggetti User e Asta per storicizzare il testo.
        """
        from .models import Asta
        mittente = User.objects.get(id=mittente_id)
        destinatario = User.objects.get(id=destinatario_id)
        asta = Asta.objects.get(id=asta_id)
        Messaggio.objects.create(mittente=mittente, destinatario=destinatario, contenuto=testo, asta=asta)
