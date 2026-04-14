from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy,reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
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


@login_required
def chat_view(request, asta_id, altro_utente_id):
    """
    Gestisce la visualizzazione della pagina di chat tra venditore e acquirente.
    Effettua controlli di sicurezza stringenti prima di esporre lo storico dei messaggi.
    """
    asta = get_object_or_404(Asta, pk=asta_id)
    altro_utente = get_object_or_404(User, pk=altro_utente_id)
    
    partecipanti = [request.user.id, altro_utente.id]
    if asta.creatore.id not in partecipanti:
         return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
         
    if request.user == altro_utente:
         return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    storico_messaggi = Messaggio.objects.filter(
        asta=asta,
        mittente__in=[request.user, altro_utente],
        destinatario__in=[request.user, altro_utente]
    ).order_by('data_invio')

    return render(request, 'gestione_aste/chat.html', {
        'asta': asta,
        'altro_utente': altro_utente,
        'storico_messaggi': storico_messaggi
    })

class InboxView(LoginRequiredMixin, TemplateView):
     """
     Raggruppa le varie chat in cui è coinvolto l'utente, creando 
     una casella di posta strutturata clusterizzando per Asta.
     """
     template_name = 'gestione_aste/inbox.html'

     def get_context_data(self, **kwargs):
          """
          Estrae i messaggi e costruisce delle conversazioni uniche visualizzando
          solo l'ultimo messaggio scambiato.
          """
          context = super().get_context_data(**kwargs)
          
          messaggi = Messaggio.objects.filter(
               Q(mittente=self.request.user) | Q(destinatario=self.request.user)
          ).select_related('asta', 'mittente', 'destinatario').order_by('-data_invio')
          
          conversazioni = {}
          for msg in messaggi:
               altro_utente = msg.destinatario if msg.mittente == self.request.user else msg.mittente
               chiave = (msg.asta.id, altro_utente.id)
               
               if chiave not in conversazioni:
                    conversazioni[chiave] = {
                         'asta': msg.asta,
                         'altro_utente': altro_utente,
                         'ultimo_messaggio': msg,
                    }
                    
          context['conversazioni'] = list(conversazioni.values())
          return context
     
class RegistrazioneView(CreateView):
     """
     Gestisce la registrazione di un nuovo utente utilizzando
     il form nativo UserCreationForm di Django.
     """
     form_class = UserCreationForm
     template_name = 'registration/registrazione.html'
     success_url = reverse_lazy('login')

class AstaListView(ListView):
    """
    Mostra la lista delle aste attive in homepage, integrando la logica
    di eventuale ricerca testuale per titolo o filtro per categoria.
    """
    model = Asta
    template_name = 'gestione_aste/asta_list.html'
    context_object_name = 'aste'
    
    def get_queryset(self):
       """
       Filtra il QuerySet di base in modo da esporre solo le aste non scadute e non ritirate.
       Applica in coda la ricerca keyword (q) e il filtro (categoria), se forniti.
       """
       queryset = Asta.objects.filter(attiva=True, data_scadenza__gte=timezone.now()).order_by('-data_scadenza')

       query_testo = self.request.GET.get('q')
       query_categoria = self.request.GET.get('categoria')

       if query_testo:
            queryset = queryset.filter(titolo__icontains=query_testo)

       if query_categoria and query_categoria != '':
            queryset = queryset.filter(categoria_id=query_categoria)

       return queryset

    def get_context_data(self, **kwargs):
        """
        Popola le categorie per il form della barra di ricerca.
        """
        context = super().get_context_data(**kwargs)
        context['categorie'] = Categoria.objects.all()
        return context


class AstaCreateView(LoginRequiredMixin, CreateView):
    """
    Gestisce la creazione di una nuova Asta attraverso un form generato automaticamente dai Model fields.
    """
    model = Asta
    fields = ['titolo', 'descrizione', 'categoria', 'immagine', 'prezzo_iniziale', 'data_scadenza']
    template_name = 'gestione_aste/asta_create.html'
    success_url = reverse_lazy('home')

    def get_form(self, form_class=None):
        """
        Migliora l'interfaccia utente impostando un widget DateTime nativo
        per il campo immissione data_scadenza.
        """
        form = super().get_form(form_class)
        form.fields['data_scadenza'].widget = forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'})
        return form

    def form_valid(self, form):
        """
        Inietta automaticamente l'utente loggato come creatore dell'Asta.
        """
        form.instance.creatore = self.request.user
        return super().form_valid(form)
    
class AstaDetailView(LoginRequiredMixin, DetailView):
    """
    Mostra i dettagli completi di una singola asta.
    """
    model = Asta
    template_name = 'gestione_aste/asta_detail.html'

    def get_context_data(self, **kwargs):
        """
        Passa al template un form vuoto per permettere agli utenti
        di scommettere, e una variabile per indicare se l'asta
        è scaduta, disabilitando eventuali form.
        """
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
     """
     Mostra la dashboard per l'utente loggato, suddividendo le sue
     aste create (attive o concluse) e le aste a cui ha partecipato vincendo.
     """
     model=Asta
     template_name='gestione_aste/area_personale.html'
     context_object_name='aste_attive_utente'

     def get_queryset(self):
          return Asta.objects.filter(creatore=self.request.user, attiva=True, data_scadenza__gte=timezone.now()).order_by('-data_scadenza')

     def get_context_data(self, **kwargs):
          """
          Aggrega e restituisce statistiche base (media voti) e suddivide
          nel contesto le aste dell'utente tra concluse e vinte.
          """
          context = super().get_context_data(**kwargs)
          
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
     """
     Permette l'eliminazione/ritiro della propria asta.
     Garantisce che solo il creatore possa compiere l'azione.
     """
     model=Asta
     template_name='gestione_aste/asta_delete.html'
     success_url=reverse_lazy('area_personale')

     def test_func(self):
          """
          Verifica UserPassesTestMixin. Ritorna True solo se l'utente
          eseguente coincide con il creatore dell'asta.
          """
          asta=self.get_object()
          return self.request.user==asta.creatore

class OffertaCreateView(LoginRequiredMixin, CreateView):
     """
     Processa la sottoscrizione di una nuova offerta ed esegue i controlli
     di coerenza economica prima di registrare il record.
     """
     model = Offerta
     fields=['importo']
     template_name='gestione_aste/asta_detail.html'

     def form_valid(self, form):
          """
          Verifica che l'asta sia tuttora attiva, assicura che l'importo
          offerto sia maggiore o uguale al minimo e allinea il prezzo corrente globale.
          """
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
          
          asta.prezzo_corrente = importo_offerto
          asta.save()
          
          return super().form_valid(form)

     def get_success_url(self):
          return reverse('dettaglio_asta', kwargs={'pk':self.kwargs['pk']})
          
def api_max_offerta(request, pk):
     """
     Endpoint API RESTful che restituisce lo storico formattato ed il prezzo live
     di un'asta rimpacchettati in JSON. È chiamato in pooling (AJAX) dal frontend.
     """
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
     """
     Aziona o rimuove con un interruttore logico l'aggiunta di un'asta ai preferiti
     personali di un utente per poi fare un redirect alla pagina precedentemente visitata.
     """
     asta=get_object_or_404(Asta, pk=pk)
     user=request.user
     
     if asta.preferiti.filter(id=request.user.id).exists():
          asta.preferiti.remove(user)
     else:
          asta.preferiti.add(user)

     return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

class ListaPreferitiView(LoginRequiredMixin, ListView):
     """
     Mostra la raccolta di tutte le aste marcate come preferite dall'utente.
     """
     model=Asta
     template_name='gestione_aste/aste_preferite.html'
     
     def get_queryset(self):
          return self.request.user.aste_preferite.order_by('-data_scadenza')

class ProfiloVenditoreView(DetailView):
     """
     Visualizza la pagina vetrina pubblica per un dato utente venditore,
     comprensiva di statistiche pubbliche, recensioni e relative aste ancora attive.
     """
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
     """
     Restrizione di sicurezza che sovrascrive UserPassesTestMixin bloccando
     la creazione della recensione solo agli utenti che hanno effettivamente
     vinto l'asta di competenza.
     """
     def test_func(self):
          asta = get_object_or_404(Asta, pk=self.kwargs['pk'])
          if self.request.user == asta.creatore:
               return False
          
          if asta.attiva and asta.data_scadenza >= timezone.now():
               return False
               
          if hasattr(asta, 'recensione'):
               return False
          
          ultima_offerta = asta.offerte.order_by('-data_offerta').first()
          if ultima_offerta and ultima_offerta.offerente == self.request.user:
               return True
               
          return False

class CreaRecensioneView(LoginRequiredMixin, HaCompratoMixin, CreateView):
     """
     Consente la compilazione del form di giudizio e stelle (1 a 5) associandolo
     in maniera sicura sia all'asta competente che all'utente giudicato (venditore).
     """
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