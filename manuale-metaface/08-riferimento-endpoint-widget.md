# Riferimento endpoint: widget di donazione pubblico

API separata da quella applicativa, pensata per form di donazione online embeddabili su siti terzi (`<script src="https://widget.metaface.it/shim.js" domain="..." token="...">`). Nessuna `Authorization` header: l'identificazione avviene tramite il `token` (l'apikey del widget configurato) passato nel body della richiesta, o nel path per l'endpoint di configurazione.

## Configurazione del widget

**`GET /api/widget/v2/ping/{token}`** — restituisce la configurazione pubblica del widget: colori, valuta, campi richiesti, importi/frequenze proposti, metodi di pagamento disponibili.

```bash
curl https://<cliente>.metaface.it/api/widget/v2/ping/abc123token
# {"options": {"colors": {...}, "currency": "EUR", "payment": {"methods": ["CC","BW"]}, ...}}
```

Se il token non corrisponde a nessun widget: `404` con corpo `"Not found"`.

## Raccogliere una donazione, passo per passo (v2)

Ogni chiamata successiva richiede `uuid` (lo stesso, generato dal client all'inizio del flusso) e `token` nel body — se lo sheet con quell'`uuid` non esiste ancora, viene creato automaticamente alla prima chiamata.

```bash
# 1. Dati del donatore
curl -X POST https://<cliente>.metaface.it/api/widget/v2/donor/ \
  -H "Content-Type: application/json" \
  -d '{"uuid":"<uuid-generato-dal-client>","token":"abc123token","first_name":"Anna","last_name":"Bianchi","email":"anna@example.com"}'

# 2. Dati della donazione
curl -X POST https://<cliente>.metaface.it/api/widget/v2/donation/ \
  -H "Content-Type: application/json" \
  -d '{"uuid":"<stesso-uuid>","token":"abc123token","amount":20,"frequency":12}'

# 3a. Pagamento con carta (Stripe)
curl -X POST https://<cliente>.metaface.it/api/widget/v2/stripe/create_intent/ \
  -d '{"uuid":"<stesso-uuid>","token":"abc123token"}'
# -> {"client_secret": "pi_..._secret_..."}  # usato lato client per confermare il pagamento con Stripe.js
curl -X POST https://<cliente>.metaface.it/api/widget/v2/stripe/confirm/ \
  -d '{"uuid":"<stesso-uuid>","token":"abc123token","payment_intent_id":"pi_..."}'

# 3b. In alternativa, mandato SEPA (SDD)
curl -X POST https://<cliente>.metaface.it/api/widget/v2/sdd/create_account/ \
  -d '{"uuid":"<stesso-uuid>","token":"abc123token","iban":"IT60X0542811101000000123456"}'

# 4. Conferma finale (avanza lo stato configurato sul widget)
curl -X POST https://<cliente>.metaface.it/api/widget/v2/confirm/ \
  -d '{"uuid":"<stesso-uuid>","token":"abc123token"}'
```

`donor` richiede `first_name`+`last_name` oppure `business_name`, più `email`. `donation.frequency`: `0` = donazione singola, qualsiasi altro valore = ricorrente (12=mensile, 1=annuale, ecc. — vedi il capitolo sul modello dati).

## Gateway di pagamento supportati

| Ramo | Endpoint | Gateway |
|---|---|---|
| Carta di credito | `stripe/create_intent/`, `stripe/confirm/` | Stripe |
| PayPal | `paypal/checkout/`, `paypal/redirect/{token}/{uuid}/` | PayPal (redirect esterno, poi ritorno) |
| SEPA Direct Debit | `sdd/create_account/` | Nessun gateway esterno: crea solo il mandato locale (IBAN + validazione codice fiscale) |

`paypal/checkout/` restituisce un `checkout_url` su cui redirigere il donatore; dopo l'approvazione PayPal richiama `paypal/redirect/{token}/{sheet_uuid}/`, che verifica l'esito e reindirizza al link configurato sul widget.

## Widget v1 (legacy, `/api/widget/`)

Versione precedente, ancora attiva per compatibilità: `ping/{apikey}/`, `donation_sheet/`, `donor_sheet/`, `payment_sheet/`, `payment_intent_sheet/`. Stesso concetto di v2 ma meno gateway supportati (solo carta via Stripe manuale e bonifico/SDD), e formato dei campi leggermente diverso (es. il donatore in v1 non espone `business_name`/`vat`). Per un'integrazione nuova, usare v2.

## Errori tipici

| Situazione | v1 | v2 |
|---|---|---|
| Apikey/token non trovato | `404` (creazione) o comportamento non gestito su alcuni endpoint | `400` con `{"token": ["Widget not found"]}` (scritture), `404` con corpo `"Not found"` (ping) |
| Validazione campi | `400` standard | `400` standard |
| Gateway di pagamento non configurato sul progetto | **Non gestito esplicitamente** in `payment_intent_sheet` (v1): rischio di errore server non pulito | Gestito: `400` con messaggio esplicito |

## Multi-tenant per il widget

Non è multi-tenant a livello di installazione (un'istanza Metaface = un cliente), ma dentro la stessa installazione un cliente può avere più widget configurati (per progetto, per pagina, per campagna): il tenant "logico" per questa API è il singolo widget, identificato dal suo `apikey`. Non esiste un vincolo di unicità a livello di database sull'apikey: l'unicità è garantita solo per costruzione (generata come UUID casuale alla creazione del widget).
