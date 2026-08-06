# Riferimento endpoint: adesioni e turni

## Sheets — l'adesione/donazione (la risorsa più importante)

Un "sheet" contiene i dati del donatore, dell'importo/frequenza, del metodo di pagamento e dello stato nel workflow di validazione. È l'oggetto che, una volta completato, viene inviato a Donodoo (vedi il capitolo sull'integrazione).

**`GET /api/v3/sheets/`** — lista, **paginata** (`LimitOffsetPagination`: `{"count","next","previous","results"}`). Filtri realmente funzionanti: `id_in` (lista id separati da virgola), `created_gte`/`created_lte`, `updated_gte`/`updated_lte`, `mandate_date_gte`/`mandate_date_lte`, `checkpoint_date_gte`/`checkpoint_date_lte`, `state` (match esatto sull'etichetta testuale dello stato, case-sensitive — non un id). Isolata sempre per company dell'utente.

```bash
curl "https://<cliente>.metaface.it/api/v3/sheets/?mandate_date_gte=2026-06-01&mandate_date_lte=2026-06-30" \
  -H "Authorization: Token <token>"
```

Risposta (estratto):
```json
{
  "count": 12, "next": null, "previous": null,
  "results": [{
    "id": 501, "code": "SC00501", "uuid": "b2b0...", "state": {"id": 4, "label": "Completata", "checkpoint": true},
    "checkpoint_date": "2026-06-15T10:22:00Z", "team": 4, "company": 1,
    "donor": {"first_name": "Anna", "last_name": "Bianchi", "ssn": "...", "contacts": {"email": "...", "phone": "..."}},
    "donation": {"frequency": 12, "amount": 20.0, "mandate_date": "2026-06-15", "destination": 3},
    "payment": {"method": "BW", "bankwire": {"iban": "IT...", "holder": {...}}},
    "signature": "data:image/png;base64,...",
    "reject": null
  }]
}
```

**`POST /api/v3/sheets/`** — crea una nuova adesione. Idempotente su `uuid`: se il payload contiene un `uuid` già esistente, l'operazione diventa un aggiornamento invece di creare un duplicato. `author`/`creator` vengono sempre forzati all'utente autenticato, ignorando eventuali valori diversi nel payload.

**`PUT`/`PATCH /api/v3/sheets/{pk}/`** — aggiornamento (lookup per id numerico).

**`POST /api/v3/sheets/{uuid}/move/`** — avanza lo stato nel workflow: `{"state": "<etichetta stato>"}`. Le transizioni ammesse dipendono dalla configurazione del workflow del progetto, non da una lista fissa.

**`DELETE /api/v3/sheets/{uuid}/`** — **non usare**: bug noto nel codice (riferimento a una variabile non definita), l'esito osservabile è un errore server generico invece del `403`/`204` che il comportamento suggerirebbe.

**`GET /api/v3/reports/`** — inaffidabile, vedi il capitolo sui limiti noti: fallisce sia senza parametri sia con `?year=YYYY`, restituendo una pagina di errore HTML con status `200`. Non costruire logica di business su questo endpoint finché non viene corretto.

## Turni di lavoro

**`GET/POST/PATCH/DELETE /api/v3/workedshifts/{uuid}/`** — CRUD completo dei turni di lavoro/presenza dei dialogatori. Filtri: `from_date`, `to_date`, `staff`. Sempre limitato ai turni del proprio staff (protezione contro l'accesso a turni di altri, anche passando un id diverso).

```bash
curl "https://<cliente>.metaface.it/api/v3/workedshifts/?from_date=2026-06-01&to_date=2026-06-30" \
  -H "Authorization: Token <token>"
# [{"id": 88, "uuid": "...", "date": "2026-06-12", "team_label": "Milano Centro", "location_label": "Piazza Duomo", "staff_label": "Mario Rossi", "timeround_label": "1 ora"}]
```

**`GET /api/v3/shifts/`** — tipi di turno configurati (fasce orarie standard). Campi: `id, name, duration`.

```bash
curl https://<cliente>.metaface.it/api/v3/shifts/ -H "Authorization: Token <token>"
# [{"id": 2, "name": "giornata", "duration": 1.0}]
```

## Firma e allegati

In v3, la firma grafica del donatore è incorporata direttamente nel serializer della sheet come stringa base64 (campo `signature`), non richiede una chiamata separata. In v2 esiste invece un endpoint dedicato (`/api/v2/sheets/{campaign_id}/signatures/`), mantenuto per compatibilità.

**`GET/POST/PATCH/DELETE /api/v3/sheet_media/`** — foto/allegati collegati a una sheet (es. foto del documento d'identità). Filtro: `sheet` (accetta anche una lista di id separati da virgola nonostante il nome al singolare).
