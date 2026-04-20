# Descrizione Progetto: Piattaforma Aste Online
**Tecnologia Backend:** Django (Python) con sistema di templating server-side.
**Obiettivo:** Creare un'esperienza utente moderna, dinamica e sicura per la compravendita di oggetti all'asta.

### 1. Struttura Globale (Layout & Navigazione)
*   **Header:** Logo, Home, Inserisci Asta, Area Personale, Messaggi, Wishlist. Barra di ricerca con filtri categorie.
### 2. Directory Aste / Homepage (`asta_list.html`)
*   Griglia di aste in corso: Titolo, immagine, prezzo attuale, scadenza, venditore.
### 3. Scheda Dettaglio Asta (`asta_detail.html`)
*   Immagine HD, descrizione, prezzo live (AJAX), countdown, cronologia offerte, modulo rilancio.
### 4. Area Personale / Dashboard Utente (`area_personale.html`)
*   Profilo (rating), Aste in vendita, Aste vinte, Storico vendite.
### 5. Sistema di Messaggistica (`inbox.html` e `chat.html`)
*   Lista conversazioni per asta e interfaccia chat a bolle.
### 6. Creazione Asta & Recensioni
*   Form inserimento dati e sistema rating 1-5 stelle.
### 7. Profilo Pubblico Venditore
*   Reputazione e vetrina aste attive.