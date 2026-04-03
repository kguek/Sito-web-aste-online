from django.urls import path
from . import views

urlpatterns = [
    path('', views.AstaListView.as_view(), name='home'),
    path('registrazione/', views.RegistrazioneView.as_view(), name='registrazione'),
    path('asta-nuova/', views.AstaCreateView.as_view(), name='asta-nuova'),   
    path('asta/<int:pk>/', views.AstaDetailView.as_view(), name='dettaglio_asta'),   
    path('asta/<int:pk>/offri/', views.OffertaCreateView.as_view(), name='fai_offerta'),
]
