from django.test import TestCase
from django.contrib.auth.models import User
from .models import Asta, Offerta
from django.utils import timezone
from django.urls import reverse
from datetime import timedelta


class AstaModelTest(TestCase):
    def setUp(self):
        self.utente_test= User.objects.create_user(username='testuser', password='password')
        
        scadenza=timezone.now() + timedelta(days=7)
        self.asta_test=Asta.objects.create(
            titolo='Asta di prova',
            descrizione='Descrizione di prova',
            prezzo_iniziale=10.00,
            data_scadenza=scadenza,
            creatore=self.utente_test,
        )
    
    def test_asta_creata_correttamente(self):
        self.assertEqual(self.asta_test.titolo, 'Asta di prova')
        self.assertEqual(self.asta_test.descrizione, 'Descrizione di prova')
        self.assertEqual(self.asta_test.prezzo_iniziale, 10.00)
        self.assertEqual(self.asta_test.creatore.username, 'testuser')
        self.assertEqual(self.asta_test.attiva, True)
        self.assertEqual(self.asta_test.data_scadenza > timezone.now(), True)

    def test_protezione_vista_nuova_asta_non_loggato(self):
        response=self.client.get(reverse('asta-nuova'))
        if response.status_code != 302:
            print('ERRORS REG:', response.context['form'].errors)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)
    
    def test_registrazione_nuovo_utente(self):
        response=self.client.post(reverse('registrazione'), {
            'username':'nuovoutente',
            'password1':'UnaPasswordSicura123!',
            'password2':'UnaPasswordSicura123!',
        })
        if response.status_code != 302:
            print('ERRORS REG:', response.context['form'].errors)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_creazione_asta_loggato(self):
        self.client.login(username='testuser', password='password')
        response=self.client.post(reverse('asta-nuova'), {
            'titolo':'Asta di prova loggato',
            'descrizione':'Descrizione di prova',
            'prezzo_iniziale':10.00,
            'data_scadenza':(timezone.now() + timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S'),
        })
        
        nuova_asta = Asta.objects.get(titolo='Asta di prova loggato')
        self.assertEqual(nuova_asta.descrizione, 'Descrizione di prova')
        self.assertEqual(nuova_asta.prezzo_iniziale, 10.00)
        self.assertEqual(nuova_asta.creatore.username, 'testuser')
        self.assertTrue(nuova_asta.attiva)
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))

    def test_creazione_asta_con_immagine(self):
        self.client.login(username='testuser', password='password')
        
        from django.core.files.uploadedfile import SimpleUploadedFile
        immagine_finta = SimpleUploadedFile(
            name='test_img.gif', 
            content=b'GIF89a\x01\x00\x01\x00\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;', 
            content_type='image/gif'
        )
        
        response = self.client.post(reverse('asta-nuova'), {
            'titolo': 'Asta Immagine',
            'descrizione': 'Test con immagine',
            'prezzo_iniziale': 5.00,
            'data_scadenza': (timezone.now() + timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S'),
            'immagine': immagine_finta
        })
        
        if response.status_code != 302:
            print('ERRORS IMG:', response.context['form'].errors)
        self.assertEqual(response.status_code, 302)
        asta_salvata = Asta.objects.get(titolo='Asta Immagine')
        self.assertTrue(asta_salvata.immagine.name.startswith('immagini_aste/test_img'))
