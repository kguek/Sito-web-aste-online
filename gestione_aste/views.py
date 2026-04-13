from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy,reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.forms import UserCreationForm
from .models import *
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Q
from django import forms

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
       # Mostriamo nella home solo aste attive e non ancora scadute
       queryset=Asta.objects.filter(attiva=True, data_scadenza__gte=timezone.now()).order_by('-data_scadenza')

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

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Sostituiamo l'input testuale libero con un comodo picker del calendario HTML5
        form.fields['data_scadenza'].widget = forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'})
        return form

    def form_valid(self, form):
        form.instance.creatore = self.request.user
        return super().form_valid(form)
    
class AstaDetailView(LoginRequiredMixin, DetailView):
    model = Asta
    template_name = 'gestione_aste/asta_detail.html'

    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        from django import forms
        from django.utils import timezone
        
        class FormVuoto(forms.ModelForm):
            class Meta:
                model=Offerta
                fields=['importo']
        context['form_offerta']=FormVuoto()
        
        asta = self.object
        context['is_conclusa'] = not asta.attiva or asta.data_scadenza < timezone.now()
        
        return context

class AreaPersonaleView(LoginRequiredMixin,ListView):
     model=Asta
     template_name='gestione_aste/area_personale.html'
     context_object_name='aste_attive_utente'

     def get_queryset(self):
          return Asta.objects.filter(creatore=self.request.user, attiva=True, data_scadenza__gte=timezone.now()).order_by('-data_scadenza')

     def get_context_data(self, **kwargs):
          context = super().get_context_data(**kwargs)
          
          # Statistiche venditore dell'utente loggato
          media_voto=Recensione.objects.filter(destinatario=self.request.user).aggregate(Avg('voto'))['voto__avg']
          context['media_voto']=round(media_voto, 1) if media_voto else 0
          context['numero_recensioni']=Recensione.objects.filter(destinatario=self.request.user).count()
          
          aste_finite_utente = Asta.objects.filter(creatore=self.request.user).filter(
               Q(attiva=False) | Q(data_scadenza__lt=timezone.now())
          ).order_by('-data_scadenza')
          context['aste_finite_utente'] = aste_finite_utente
          
          aste_vinte = []
          tutte_aste_concluse = Asta.objects.filter(
               Q(data_scadenza__lt=timezone.now()) | Q(attiva=False)
          ).order_by('-data_scadenza')
          for a in tutte_aste_concluse:
               ultima = a.offerte.order_by('-data_offerta').first()
               if ultima and ultima.offerente == self.request.user:
                    aste_vinte.append(a)
          
          context['aste_vinte'] = aste_vinte
          return context

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
          
          if not asta.attiva or asta.data_scadenza < timezone.now():
               form.add_error(None, "Errore: L'asta si è già conclusa.")
               return self.form_invalid(form)
               
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

@login_required

def toggle_preferito(request, pk):
     asta=get_object_or_404(Asta, pk=pk)
     user=request.user
     
     if asta.preferiti.filter(id=request.user.id).exists():
          asta.preferiti.remove(user)
     else:
          asta.preferiti.add(user)

     return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

class ListaPreferitiView(LoginRequiredMixin, ListView):
     model=Asta
     template_name='gestione_aste/aste_preferite.html'
     
     def get_queryset(self):
          return self.request.user.aste_preferite.order_by('-data_scadenza')

class ProfiloVenditoreView(DetailView):
     model=User
     template_name='gestione_aste/profilo_venditore.html'
     context_object_name='venditore'

     def get_context_data(self, **kwargs):
          context=super().get_context_data(**kwargs)
          venditore=self.get_object()
          
          media_voto=Recensione.objects.filter(destinatario=venditore).aggregate(Avg('voto'))['voto__avg']
          context['media_voto']=round(media_voto, 1) if media_voto else 0
          context['numero_recensioni']=Recensione.objects.filter(destinatario=venditore).count()
          context['aste_attive']=Asta.objects.filter(creatore=venditore, attiva=True, data_scadenza__gte=timezone.now()).order_by('-data_scadenza')
          return context
          
class HaCompratoMixin(UserPassesTestMixin):
     def test_func(self):
          asta = get_object_or_404(Asta, pk=self.kwargs['pk'])
          if self.request.user == asta.creatore:
               return False
          
          # Verifica che l'asta sia finita
          if asta.attiva and asta.data_scadenza >= timezone.now():
               return False
               
          # Verifica che la recensione non esista già
          if hasattr(asta, 'recensione'):
               return False
          
          # Verifica che l'utente sia l'ultimo offerente
          ultima_offerta = asta.offerte.order_by('-data_offerta').first()
          if ultima_offerta and ultima_offerta.offerente == self.request.user:
               return True
               
          return False

class CreaRecensioneView(LoginRequiredMixin, HaCompratoMixin, CreateView):
     model=Recensione
     fields=['voto', 'commento']
     template_name='gestione_aste/crea_recensione.html'

     def get_context_data(self, **kwargs):
          context = super().get_context_data(**kwargs)
          asta = get_object_or_404(Asta, pk=self.kwargs['pk'])
          context['asta'] = asta
          context['venditore'] = asta.creatore
          return context

     def form_valid(self, form):
          asta = get_object_or_404(Asta, pk=self.kwargs['pk'])
          form.instance.autore=self.request.user
          form.instance.destinatario=asta.creatore
          form.instance.asta=asta
          return super().form_valid(form)

     def get_success_url(self):
          asta = get_object_or_404(Asta, pk=self.kwargs['pk'])
          return reverse('profilo_venditore', kwargs={'pk':asta.creatore.pk})