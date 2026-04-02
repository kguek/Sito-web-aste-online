from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

#Creazione del modello Asta ereditando da models.Model

class Asta(models.Model):
    titolo = models.CharField(max_length=200)
    descrizione = models.TextField()
    
    #Creiamo un cartella specifica per le immagini uploadate
    imagine= models.ImageField(upload_to='immagini_aste/', blank=True, null=True)
    data_scadenza=models.DateTimeField()
    
    #Creiamo un campo per il creatore dell'asta, in questo caso l'utente loggato
    creatore=models.ForeignKey(User, on_delete=models.CASCADE, related_name='aste_create')
    attiva=models.BooleanField(default=True)    

    #Creiamo un metodo per visualizzare il titolo dell'asta
    def __str__(self):
        return f"{self.titolo} - Creata da: {self.creatore}" 


class Offerta(models.Model):
    asta=models.ForeignKey(Asta, on_delete=models.CASCADE, related_name='offerte')
    offerente=models.ForeignKey(User, on_delete=models.CASCADE, related_name='offerte_create')
    importo=models.DecimalField(max_digits=10, decimal_places=2)
    data_offerta=models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Offerta di {self.importo} per l'asta {self.asta.titolo} da {self.offerente.username}"
            
