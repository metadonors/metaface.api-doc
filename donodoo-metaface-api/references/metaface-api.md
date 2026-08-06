# Metaface API — riferimento denso (v3 preferita, v2 legacy)

Fonte: ricognizione codice `metadonors/metaface` (6 ago 2026) + verifica live `arca.metaface.it`. Ogni endpoint richiede `Authorization: Token <token>` salvo indicato. Base URL: `https://<cliente>.metaface.it`.

## Autenticazione

`POST /api/v3/auth/token/` `{"username","password"}` → `{"token":"..."}`. Nessuna scadenza codificata. Header: `Authorization: Token <token>` (non Bearer).

`GET /api/v3/ping/` — nessuna auth richiesta, ma se si passa il token: `{"status":"OK","customer":"<nome>","localization":"it","currency":"€","valid_token":true|false}`. Usare per verificare rapidamente se un token è ancora valido.

`GET /api/v2/ping/` — solo `{"status":"OK"}`, nessuna auth, nessuna info cliente.

## Multi-tenant

Un cliente = un host (`<cliente>.metaface.it`) = un'istanza/DB separato. Nessun modo di enumerare i clienti via API. L'host è configurazione del client, non un dato che l'API espone.

## Paginazione — ATTENZIONE

Quasi tutte le risorse **non sono paginate** (`DEFAULT_PAGINATION_CLASS` è commentato nei settings): rispondono con un array JSON piatto, anche se ce ne sono migliaia. Fanno eccezione **solo**:
- `GET /api/v3/sheets/` → `{"count":N,"next":"url|null","previous":"url|null","results":[...]}` (LimitOffsetPagination, param `limit`/`offset`)
- `GET /api/v3/backups/` → stessa forma

## Sheets — l'adesione/donazione (risorsa centrale)

Un "sheet" = una scheda di adesione raccolta sul campo da un dialogatore: donatore + importo/frequenza + metodo di pagamento + stato di workflow.

| Metodo | Path | Note |
|---|---|---|
| GET | `/api/v3/sheets/` | Filtri: `id_in` (csv), `created_gte/lte`, `updated_gte/lte`, `mandate_date_gte/lte`, `checkpoint_date_gte/lte`, `state` (match esatto su `state.label`, case-sensitive). Isolato per company dell'utente. |
| POST | `/api/v3/sheets/` | Crea. Idempotente su `uuid` (stesso uuid → diventa update, non duplica). `author`/`creator` forzati all'utente loggato. |
| PUT/PATCH | `/api/v3/sheets/{pk}/` | Aggiorna (lookup per id numerico, non uuid, nonostante create/update logico lavori per uuid — incoerenza nota). |
| POST | `/api/v3/sheets/{uuid}/move/` | Avanza stato workflow: body `{"state": "<label>"}`. |
| DELETE | `/api/v3/sheets/{uuid}/` | **Rotto**: bug nel codice (`NameError` su variabile non definita), aspettarsi errore server, non un 403/204 pulito. |

Campi principali risposta (`SheetSerializerV3`): `id, code, uuid, author, creator, state, tracking_code, company, outcome, project, campaign, campaign_product, compiled_on, created, updated, error_log, creditcard_transaction, checkpoint_date, incomplete, reject, signature (base64 o null), team, donor{...}, beneficiary{...}, donation{...}, payment{...}`.

`donor`/`beneficiary` (`PersonSerializer`): `business_name, first_name, last_name, sex(M/F/N/C), dob, pob, job, ssn, vat, contacts{phone,mobile,fax,email,privacy,sms_privacy,phone_privacy,mail_privacy,paper_privacy,profilation_privacy,profilation_third_party_privacy,social_privacy,address{...}}`.

`donation`: `frequency(0=oneoff,1=annuale,2=semestrale,3=quadrimestrale,4=trimestrale,6=bimestrale,12=mensile), amount, mandate_date, first_payment, destination(id), topic(id), topic_code, sad_code, state(UPGRADE/DOWNGRADE)`.

`payment`: `method(BW=SDD,DD=direct debit,CC=carta,TTL=SDD via TTL,POS,PP=paypal), holder_same_as_donor, creditcard{...}, bankwire{iban,holder{...}}, pos{...}, ttl{...}, directdebit{...}`.

Esempio:
```bash
curl "https://<cliente>.metaface.it/api/v3/sheets/?mandate_date_gte=2026-06-01&mandate_date_lte=2026-06-30" \
  -H "Authorization: Token <token>"
```

`GET /api/v3/reports/` — **non affidabile**: fallisce (pagina HTML errore, status 200!) sia senza parametri sia con `?year=YYYY`. Non usare in integrazioni fino a chiarimento.

## Anagrafiche

| Endpoint | Descrizione | Filtri reali |
|---|---|---|
| `GET /api/v3/teams/` | Squadre dialogatori | Nessuno (filtri dichiarati non raggiungibili, bug noto) |
| `GET /api/v3/locations/` | Sedi/punti raccolta | Nessuno (stesso bug); campo `address` in v3 sempre vuoto |
| `GET /api/v3/campaigns/` | Campagne (slide, prodotti, clausole, limiti validazione) | — |
| `GET /api/v3/trackings/` | Codici tracking marketing | Nessuno |
| `GET /api/v3/users/me/` | Profilo utente loggato | — |
| `GET /api/v3/projects/{slug}/` | Configurazione progetto (opzioni validazione, enum, custom field) | — |

## Turni di lavoro

| Endpoint | Note |
|---|---|
| `GET/POST/PATCH/DELETE /api/v3/workedshifts/{uuid}/` | Filtri: `from_date`, `to_date`, `staff`. Solo propri turni. Campi: `id,uuid,company,team,location,staff,date,timeround,note` + label leggibili `*_label`. |
| `GET /api/v3/shifts/` | Tipi di turno configurati: `id,name,duration`. |

## API widget pubblica (donazioni online, NESSUN login utente)

Prefisso `/api/widget/v2/`. Identificazione tramite `token` (apikey del widget) nel body (o path per `ping`). Nessuna `Authorization` header.

| Endpoint | Metodo | Scopo |
|---|---|---|
| `ping/{token}` | GET | Config pubblica widget (colori, campi richiesti, metodi pagamento) |
| `donor/` | POST | Anagrafica donatore. Richiede `first_name+last_name` OPPURE `business_name`, più `email` |
| `donation/` | POST | `amount`, `frequency` (0=oneoff) |
| `confirm/` | POST | Avanza lo stato a `widget.checkpoint_state` |
| `stripe/create_intent/` + `stripe/confirm/` | POST | PaymentIntent/Subscription Stripe |
| `paypal/checkout/` + `paypal/redirect/{token}/{uuid}/` | POST/GET | Ordine/subscription PayPal, redirect di ritorno |
| `sdd/create_account/` | POST | Mandato SEPA: `iban` (validato), `ssn` opzionale (validato) |

Widget v1 (`/api/widget/`, legacy): `ping/{apikey}/`, `donation_sheet/`, `donor_sheet/`, `payment_sheet/`, `payment_intent_sheet/` — stesso concetto, meno gateway supportati (solo Stripe manuale + bankwire).

## Rotte interne/fragili — NON costruire integrazioni stabili su queste

- `mobilehelp/`, `backups/` — dump log/db locale app tablet.
- `hooks/{apikey}/` — canale widget "legacy", dipende da header proprietario `Metaface-Client-Version` per il formato risposta (a volte wrappato in `{"sheet":...,"errors":...}`, a volte risposta DRF standard).
- `credit_card_check/` (`POST /api/v3/credit_card_check/`) — verifica anti-frode carta, richiede comunque autenticazione nonostante `csrf_exempt`.
- `set_contact_state` (v2, su sheet) — bug: risponde sempre `"KO"` anche in caso di successo.

## Errori HTTP tipici

| Situazione | v2 | v3 |
|---|---|---|
| Token assente/non valido | 401 | 401 |
| Apikey widget non trovata | 404 (`ValidationError` code 404) o 400 secondo endpoint | 400 `{"token":["Widget not found"]}` |
| Validazione campi | 400 standard DRF | 400 standard DRF |
| Stato workflow non raggiungibile (`move`/`try_proceed`) | 400 | 400 |
| Endpoint rotto internamente (es. `reports/`) | — | **200 con pagina HTML di errore**, non 500: controllare sempre il `Content-Type`/forma del body, non solo lo status |

## DA VERIFICARE (rilevante per uso runtime)

- Frequenza di sync verso Donodoo: dato di configurazione, non nel codice.
- Etichette esatte degli stati di workflow (`state.label`) per "firmata"/"attivata"/"annullata": variano per cliente/progetto, sono dati non codice. Se la skill deve rispondere a "quante adesioni FIRMATE", chiedere all'utente qual è il criterio (checkpoint raggiunto? esito registrato? entrambi?) prima di calcolare un numero.
