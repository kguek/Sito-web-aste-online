from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy,reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.forms import UserCreationForm
from .models import *
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin
from django.http import JsonResponse


class RegistrazioneView(CreateView):

     #Utilizziamo il form di default di Django per la registrazione
     form_class=UserCreationForm

     #il file HTML che verrà renderizzato
     template_name='registration/registrazione.html'

     #URL a cui reindirizzare l'utente dopo la registrazione
     success_url=reverse_lazy('login')

class AstaListView(ListView):
    model = Asta
    template_name = 'gestione_aste/asta_list.html'
    context_object_name = 'aste'
    
    def get_queryset(self):
       queryset=Asta.objects.filter(attiva=True).order_by('-data_scadenza')

       query_testo=self.request.GET.get('q')
       query_categoria=self.request.GET.get('categoria')

       if query_testo:
            queryset=queryset.filter(titolo__icontains=query_testo)

       if query_categoria and query_categoria != '':
            queryset=queryset.filter(categoria_id=query_categoria)

       return queryset

    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        context['categorie']=Categoria.objects.all()
        return context


class AstaCreateView(LoginRequiredMixin, CreateView):
    model = Asta
    fields=['titolo', 'descrizione', 'categoria', 'immagine','prezzo_iniziale', 'data_scadenza']
    template_name='gestione_aste/asta_create.html'
    success_url=reverse_lazy('home')

    def form_valid(self, form):
        form.instance.creatore = self.request.user
        return super().form_valid(form)
    
class AstaDetailView(LoginRequiredMixin, DetailView):
    model = Asta
    template_name = 'gestione_aste/asta_detail.html'

    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        from django import forms
        class FormVuoto(forms.ModelForm):
            class Meta:
                model=Offerta
                fields=['importo']
        context['form_offerta']=FormVuoto()
        return context

class AreaPersonaleView(LoginRequiredMixin,ListView):
     model=Asta
     template_name='gestione_aste/area_personale.html'
     context_object_name='aste_utente'

     def get_queryset(self):
          return Asta.objects.filter(creatore=self.request.user).order_by('-data_scadenza')

class AstaDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
     model=Asta
     template_name='gestione_aste/asta_delete.html'
     success_url=reverse_lazy('area_personale')

     def test_func(self):
          asta=self.get_object()
          return self.request.user==asta.creatore

class OffertaCreateView(LoginRequiredMixin, CreateView):
     model = Offerta
     fields=['importo']
     template_name='gestione_aste/asta_detail.html'

     def form_valid(self, form):
          
          asta=get_object_or_404(Asta, pk=self.kwargs['pk'])
          importo_offerto=form.cleaned_data['importo']
          
          
          offerta_massima=asta.offerte.order_by('-importo').first()
          if offerta_massima:
               minimo_richiesto=offerta_massima.importo + 1
          else:
               minimo_richiesto=asta.prezzo_iniziale

          if importo_offerto < minimo_richiesto:
               form.add_error('importo', f"Errore: L'offerta minima è {minimo_richiesto}")
               return self.form_invalid(form)
          
          form.instance.offerente=self.request.user
          form.instance.asta=asta
          
          # Aggiorna il prezzo corrente dell'asta globale col nuovo importo
          asta.prezzo_corrente = importo_offerto
          asta.save()
          
          return super().form_valid(form)

     def get_success_url(self):
          return reverse('dettaglio_asta', kwargs={'pk':self.kwargs['pk']})
          
def api_max_offerta(request, pk):
     asta=get_object_or_404(Asta, pk=pk)
     offerte=asta.offerte.order_by('-importo')
     
     storico=[]
     for off in offerte:
          storico.append({
               'importo':str(off.importo),
               'offerente':off.offerente.username,
               'data':off.data_offerta.strftime('%d/%m/%Y %H:%M')
          })

     if offerte.exists():
          offerta_massima=offerte.first()
          dati={
               'importo': str(offerta_massima.importo),
               'offerente': offerta_massima.offerente.username,
               'minimo_richiesto': str(offerta_massima.importo + 1),
               'storico':storico,
          }
     else:
          dati={
               'importo': str(asta.prezzo_iniziale),
               'offerente': 'Nessuna offerta',
               'minimo_richiesto': str(asta.prezzo_iniziale),
               'storico': storico,
          }
     return JsonResponse(dati)
     
    
    