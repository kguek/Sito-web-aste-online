from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.forms import UserCreationForm

class RegistrazioneView(CreateView):

     #Utilizziamo il form di default di Django per la registrazione
     form_class=UserCreationForm

     #il file HTML che verrà renderizzato
     template_name='registration/registrazione.html'

     #URL a cui reindirizzare l'utente dopo la registrazione
     success_url=reverse_lazy('login')
    