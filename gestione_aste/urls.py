from django.urls import path
from . import views

urlpatterns = [
    path('', views.AstaListView.as_view(), name='home'),
    path('registrazione/', views.RegistrazioneView.as_view(), name='registrazione'),
    path('asta-nuova/', views.AstaCreateView.as_view(), name='asta-nuova'),   
    path('asta/<int:pk>/', views.AstaDetailView.as_view(), name='dettaglio_asta'),   
    path('asta/<int:pk>/offri/', views.OffertaCreateView.as_view(), name='fai_offerta'),
    path('api/asta/<int:pk>/max-offerta/', views.api_max_offerta, name='api_max_offerta'),
    path('area-personale/', views.AreaPersonaleView.as_view(), name='area_personale'),
    path('asta/<int:pk>/elimina/', views.AstaDeleteView.as_view(), name='elimina_asta'),
    path('asta/<int:pk>/preferito/', views.toggle_preferito, name='toggle_preferito'),
    path('i-miei-preferiti/', views.ListaPreferitiView.as_view(), name='aste_preferite'),
    path('venditore/<int:pk>/', views.ProfiloVenditoreView.as_view(), name='profilo_venditore'),
    path('asta/<int:pk>/recensione/', views.CreaRecensioneView.as_view(), name='crea_recensione'),
    path('asta/<int:asta_id>/chat/<int:altro_utente_id>/', views.chat_view, name='chat'),
    path('inbox/', views.InboxView.as_view(), name='inbox'),
]
