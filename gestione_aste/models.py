from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator,MaxValueValidator

class Asta(models.Model):
    """
    Rappresenta un'asta nel sistema.
    Gestisce i dati principali dell'oggetto in vendita, i prezzi,
    le date di validità e la relazione con il creatore e i preferiti.
    """
    titolo = models.CharField(max_length=200)
    descrizione = models.TextField()
    preferiti = models.ManyToManyField(User, related_name='aste_preferite', blank=True)
    immagine = models.ImageField(upload_to='immagini_aste/', blank=True, null=True)
    prezzo_iniziale = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    prezzo_corrente = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    data_creazione = models.DateTimeField(auto_now_add=True)
    data_scadenza = models.DateTimeField()
    creatore = models.ForeignKey(User, on_delete=models.CASCADE, related_name='aste_create')
    attiva = models.BooleanField(default=True)
    categoria = models.ForeignKey('Categoria', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        """
        Rappresentazione testuale dell'asta.
        """
        return f"{self.titolo} - Creata da: {self.creatore}"

    def save(self, *args, **kwargs):
        """
        Salva l'entità Asta assicurandosi che, al momento della creazione,
        il prezzo corrente coincida con il prezzo iniziale.
        """
        if not self.pk and self.prezzo_corrente == 0.00:
            self.prezzo_corrente = self.prezzo_iniziale
        super().save(*args, **kwargs)


class Offerta(models.Model):
    """
    Rappresenta una singola offerta economica piazzata su un'asta.
    """
    asta = models.ForeignKey(Asta, on_delete=models.CASCADE, related_name='offerte')
    offerente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='offerte_create')
    importo = models.DecimalField(max_digits=10, decimal_places=2)
    data_offerta = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Rappresentazione testuale dell'offerta.
        """
        return f"Offerta di {self.importo} per l'asta {self.asta.titolo} da {self.offerente.username}"

class Categoria(models.Model):
    """
    Categoria merceologica per classificare le aste.
    """
    nome = models.CharField(max_length=100, unique=True)
    descrizione = models.TextField(blank=True, null=True)

    def __str__(self):
        """
        Rappresentazione testuale della categoria.
        """
        return self.nome

class Recensione(models.Model):
    """
    Rappresenta una recensione lasciata dall'acquirente (vincitore) verso il venditore dell'asta.
    """
    autore = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recensioni_create')
    destinatario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recensioni_ricevute')
    asta = models.OneToOneField(Asta, on_delete=models.CASCADE, related_name='recensione', null=True, blank=True)
    voto = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    commento = models.TextField(blank=True, null=True)
    data_recensione = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Rappresentazione testuale della recensione.
        """
        return f"Recensione di {self.autore.username} per {self.destinatario.username} sull'asta {self.asta.titolo if self.asta else 'N/A'}"

    
class Messaggio(models.Model):
    """
    Messaggio privato scambiato nella chat integrata tra gli utenti (acquirente e venditore) per una specifica asta.
    """
    mittente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messaggi_inviati')
    destinatario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messaggi_ricevuti')
    asta = models.ForeignKey('Asta', on_delete=models.CASCADE, related_name='messaggi', null=True, blank=True)
    contenuto = models.TextField()
    data_invio = models.DateTimeField(auto_now_add=True)
    letto = models.BooleanField(default=False)

    class Meta:
        ordering = ['-data_invio']
        
    def __str__(self):
        """
        Rappresentazione testuale del messaggio.
        """
        return f"Da {self.mittente.username} a {self.destinatario.username} - {self.data_invio.strftime('%d/%m/%Y %H:%M')}"

            
