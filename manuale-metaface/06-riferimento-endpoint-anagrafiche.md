# Riferimento endpoint: anagrafiche

Team, location, campagne, progetti, codici di tracciamento, utenti. Tutti richiedono `Authorization: Token <token>` e permesso `IsAuthenticated`, salvo indicazione contraria. Preferire `/api/v3/`.

## Utenti

**`GET /api/v3/users/me/`** — profilo dell'utente autenticato. Campi: `id, last_login, username, first_name, last_name, is_staff, is_superuser, email`. Nessun parametro.

**`GET /api/v3/users/`** — lista utenti. Un utente non-superuser vede solo se stesso; solo un superuser vede l'elenco completo.

```bash
curl https://<cliente>.metaface.it/api/v3/users/me/ -H "Authorization: Token <token>"
```

## Team

**`GET /api/v3/teams/`** — squadre di dialogatori. Nessun filtro server-side realmente raggiungibile (bug noto, i filtri dichiarati nel codice sono sovrascritti prima di essere applicati). Isolato per company dell'utente. Campi risposta (v3): `id, name, company_id`.

**`GET /api/v3/teams/{id}/locations/`**, **`.../fundraisers/`**, **`.../managers/`**, **`.../backofficers/`** — le relazioni del team con location e persone. `PUT .../{pk}/` aggiunge una relazione, `DELETE .../{pk}/` la rimuove: non sono un CRUD su un oggetto, sono azioni di associazione/dissociazione.

```bash
curl https://<cliente>.metaface.it/api/v3/teams/ -H "Authorization: Token <token>"
# [{"id": 4, "name": "Milano Centro", "company_id": 1}]
```

## Location

**`GET /api/v3/locations/`** — sedi/punti di raccolta fisici (piazza, ospedale, evento). Stesso bug dei filtri non raggiungibili visto per i team. **Attenzione**: nella versione v3 il campo `address` è restituito sempre vuoto (bug noto nel serializer, non un problema di dati). Campi risposta: `id, label, code, address, phone, email`.

## Progetti (`SheetProject`)

**`GET /api/v3/projects/`**, **`GET /api/v3/projects/{slug}/`** — configurazione del progetto/campagna a cui appartengono le adesioni: opzioni di validazione (limiti importo, campi obbligatori/nascosti), enum ammessi, campi custom, scadenza mensile per l'invio. Accessibile anche con autenticazione da widget pubblico, non solo da utente loggato.

**`GET /api/v3/projects/{slug}/destinations/`** — le destinazioni di donazione disponibili per quel progetto (causa/progetto a cui viene destinato l'importo), filtrate su `active=True`. Campi: `id, code, label, is_default, default_frequency, amounts`.

Nota: l'equivalente `topics` (sotto-tema della destinazione) esiste in v2 (`/api/v2/projects/{slug}/topics/`) ma **non ha un corrispondente in v3** — se serve, va richiamato su v2.

## Campagne

**`GET /api/v3/campaigns/`**, **`GET /api/v3/campaigns/{id}/`** — configurazione completa della campagna scaricata dall'app: slide di presentazione, prodotti/destinazioni proposti, clausole contrattuali/privacy, opzioni (limiti su carte di credito, blacklist IBAN, metodi di pagamento abilitati, stati di riferimento del workflow). Filtrata per campagne con almeno uno slide e un prodotto configurati, attive, appartenenti a una company dell'utente.

```bash
curl https://<cliente>.metaface.it/api/v3/campaigns/ -H "Authorization: Token <token>"
```

Risposta (estratto): `{"id": 12, "name": "Adozioni 2026", "hash": "a1b2...", "cover_url": "https://...", "options": {"min_annual_donation": 60, "payment_methods": ["CC","BW"], ...}, "slides": [...], "products": [...], "clauses": [...]}`.

## Codici di tracciamento

**`GET /api/v3/trackings/`** — codici di tracciamento marketing/campagna riusabili su più progetti. Campi: `id, label, code, is_active`. CRUD completo (create/update/delete), senza restrizioni di ruolo specifiche oltre l'appartenenza a company — chiunque autenticato con accesso alla company può crearne/modificarne.

```bash
curl https://<cliente>.metaface.it/api/v3/trackings/ -H "Authorization: Token <token>"
# [{"id": 1, "label": "Campagna Facebook giugno", "code": "FB2606", "is_active": true}]
```
