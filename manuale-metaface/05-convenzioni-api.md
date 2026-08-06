# Convenzioni dell'API

Regole trasversali valide su tutti gli endpoint dell'API applicativa, documentate una volta qui per non doverle ripetere ad ogni voce del catalogo.

## Formati di data, ora e fuso orario

Le date nei filtri e nei payload sono in formato `YYYY-MM-DD` (es. `2026-06-30`). Alcuni campi (es. `mandate_date`, `checkpoint_date`) sono date pure, altri (es. `created`, `updated`) sono timestamp completi in formato ISO 8601. Il fuso orario applicativo non è determinabile con certezza dal solo codice lato client dell'API: <mark>da verificare</mark> se il backend normalizza a UTC o al fuso italiano — trattare le date come locali del cliente salvo evidenza contraria in una risposta specifica.

## Paginazione

**Non è uniforme.** La maggior parte delle risorse non è paginata: una `GET` restituisce un array JSON con tutti i risultati, anche se sono migliaia (il parametro globale `PAGE_SIZE` esiste nella configurazione ma non ha effetto perché non è collegato a nessuna classe di paginazione attiva di default). Fanno eccezione solo `GET /api/v3/sheets/` e `GET /api/v3/backups/`, che usano `LimitOffsetPagination` standard di Django REST Framework:

```json
{"count": 142, "next": "https://.../api/v3/sheets/?limit=30&offset=30", "previous": null, "results": [ ... ]}
```

Parametri: `limit` (default e massimo non documentati nel codice, verificare empiricamente) e `offset`. Per tutte le altre risorse, se il volume di dati è grande, prevedere che una singola chiamata possa restituire una risposta di dimensioni significative.

## Ordinamento

Non c'è un parametro di ordinamento generico (`ordering`) applicato in modo uniforme. Alcune viewset ordinano implicitamente lato server (es. i turni di lavoro sono ordinati per data decrescente), la maggior parte no: se l'ordine conta, va imposto lato client dopo aver ricevuto i dati.

## Filtri

Attenzione: alcuni filtri che sembrano dichiarati nel codice (in particolare su team e location, nella versione v2) non sono effettivamente raggiungibili tramite query string per un bug del backend che sovrascrive i parametri passati dal client con un valore vuoto prima di applicarli. Prima di assumere che un filtro funzioni, verificarlo con una chiamata di prova — il catalogo endpoint di questo manuale segnala dove è nota questa limitazione.

## Formato degli errori

Non c'è un formato di errore unico in tutta l'API: la maggior parte degli endpoint segue lo standard Django REST Framework (`{"campo": ["messaggio di errore"]}` per errori di validazione, `400`), ma alcuni endpoint storici rispondono con formati custom (es. `{"sheet": ..., "errors": ...}` su alcune rotte legate al workflow delle adesioni). Un'insidia concreta, confermata contro l'istanza live: almeno un endpoint (`/api/v3/reports/`) può fallire restituendo una pagina HTML di errore generica dell'applicazione con **status HTTP 200**, non un errore JSON con status coerente. Un client di integrazione robusto deve controllare il `Content-Type` della risposta, non fidarsi del solo status code.

## Rate limit

Non risulta implementato alcun throttling DRF (`DEFAULT_THROTTLE_CLASSES` non configurato) nel codice ricostruito. La documentazione umana preesistente del prodotto menziona un limite di 10 connessioni simultanee per account in caso di attività sospetta, ma questo comportamento non è stato verificato nel codice sorgente in questa ricognizione: <mark>da verificare</mark> se e come è realmente applicato.
