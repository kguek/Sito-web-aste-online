from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator,MaxValueValidator

#Creazione del modello Asta ereditando da models.Model

class Asta(models.Model):
    titolo = models.CharField(max_length=200)
    descrizione = models.TextField()
    preferiti=models.ManyToManyField(User,related_name='aste_preferite',blank=True)
    
    #Creiamo un cartella specifica per le immagini uploadate
    immagine = models.ImageField(upload_to='immagini_aste/', blank=True, null=True)
    prezzo_iniziale = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    prezzo_corrente = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    data_creazione=models.DateTimeField(auto_now_add=True)
    data_scadenza=models.DateTimeField()
    
    #Creiamo un campo per il creatore dell'asta, in questo caso l'utente loggato
    creatore=models.ForeignKey(User, on_delete=models.CASCADE, related_name='aste_create')
    attiva=models.BooleanField(default=True)    

    categoria=models.ForeignKey('Categoria', on_delete=models.SET_NULL, null=True, blank=True)

    #Creiamo un metodo per visualizzare il titolo dell'asta
    def __str__(self):
        return f"{self.titolo} - Creata da: {self.creatore}" 

    def save(self, *args, **kwargs):
        if not self.pk and self.prezzo_corrente == 0.00:
            self.prezzo_corrente = self.prezzo_iniziale
        super().save(*args, **kwargs)


class Offerta(models.Model):
    asta=models.ForeignKey(Asta, on_delete=models.CASCADE, related_name='offerte')
    offerente=models.ForeignKey(User, on_delete=models.CASCADE, related_name='offerte_create')
    importo=models.DecimalField(max_digits=10, decimal_places=2)
    data_offerta=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Offerta di {self.importo} per l'asta {self.asta.titolo} da {self.offerente.username}"

class Categoria(models.Model):
    nome=models.CharField(max_length=100,unique=True)
    descrizione=models.TextField(blank=True,null=True)

    def __str__(self):
        return self.nome

class Recensione(models.Model):
    autore=models.ForeignKey(User,on_delete=models.CASCADE,related_name='recensioni_create')
    destinatario=models.ForeignKey(User,on_delete=models.CASCADE,related_name='recensioni_ricevute')
    asta=models.OneToOneField(Asta, on_delete=models.CASCADE, related_name='recensione', null=True, blank=True)
    voto=models.IntegerField(validators=[MinValueValidator(1),MaxValueValidator(5)])
    commento=models.TextField(blank=True,null=True)
    data_recensione=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Recensione di {self.autore.username} per {self.destinatario.username} sull'asta {self.asta.titolo if self.asta else 'N/A'}"

    
    
    
            
