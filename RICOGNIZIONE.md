# RICOGNIZIONE — API Metaface e integrazione Donodoo

Documento di ricognizione tecnica, prodotto ricostruendo il codice sorgente dei repository:

- `metadonors/metaface` — backend Django/DRF (monolite, non ci sono altri repo backend: `metaface-base-docker` è solo l'immagine Docker base, `metaface-widget` è il bundle JS front-end del widget, `web_metaface-it` è il sito marketing).
- `metadonors/metaface-mobile` — app tablet React Native realmente in uso dai dialogatori.
- `metadonors/metaface-app` — **scheletro Expo mai avviato** (solo `App.tsx` di default, nessuna logica). Non è l'app in produzione: ignorato nel resto della ricognizione.
- `metadonors/donodoo` — CRM Odoo 14, per la parte di modello dati custom fundraising (`addons/ngo_addons/*`) coinvolta dall'integrazione.

Verifica live eseguita contro `<cliente>.metaface.it` (credenziali di test read-only fornite dall'utente) e contro `<cliente>.donodoo.it` (verifica parziale: solo la versione del server, login non riuscito — vedi sezione dedicata).

Data ricognizione: 6 agosto 2026.

## 1. Stack e versioni

| Componente | Versione/dettaglio | Fonte |
|---|---|---|
| Python/Django | Django legacy (uso di `django.conf.urls`, `detail_route`/`list_route` deprecati, `request.user.is_authenticated()` chiamato come metodo) | `metaface/metaface/urls.py:1`, `api/v2/views.py` |
| Django REST Framework | `rest_framework` + `rest_framework.authtoken` + `rest_framework_tracking` (audit log su alcune viewset) | `metaface/metaface/settings.py:132-134` |
| Filtri | `django_filters` (`DjangoFilterBackend`) | `settings.py:86-88` |
| Async | Celery 4.1.1 + `django_celery_beat` (scheduler DB-based) | `requirements.txt`, `docker/entrypoint.sh:64,68` |
| Realtime | Django Channels (`channels_redis`) | `settings.py:386-395` |
| App tablet | React Native puro (non Expo), Odoo/Metaface non centrale qui | `metaface-mobile/package.json` |
| Odoo/Donodoo collegato | **14.0-20231106** confermato live (`xmlrpc/2/common.version()` su `<cliente>.donodoo.it`) — coincide con quanto riportato nel brief iniziale | verifica live |

## 2. Albero delle rotte (ROOT_URLCONF)

`ROOT_URLCONF = 'metaface.urls'` (`metaface/settings.py:382`). File `metaface/metaface/urls.py`. Rotte API (le uniche rilevanti per l'integrazione esterna):

```
/api/v2/            -> api.v2.urls       (urls.py:24)
/api/v3/            -> api.v3.urls       (urls.py:25)
/api/widget/        -> api.widget.urls   (urls.py:26)
/api/widget/v2/     -> api.widget_v2.urls (urls.py:27)
```

Tutte le altre rotte (`/sheet/`, `/campaigns/`, `/hr/`, `/settings/`, `/admin/`, ecc.) sono l'interfaccia web Django, non API.

Root `/api/` e `/api/v1/` **non esistono** (404 confermato sia da codice sia live) — la premessa del brief («le rotte di scoperta standard sono tutte 404») è confermata: le rotte API esistono, ma solo sotto un prefisso versionato esplicito (`/api/v2/`, `/api/v3/`), non discoverable dalla root. `/api/v3/` senza risorsa restituisce 401 (vista radice del router, protetta da autenticazione) — confermato live.

### api/v2/ (router DRF, prefisso completo `/api/v2/...`)
`auth/token/`, `auth/` (login/logout sessione), `ping/`, `users/`, `teams/`, `teams/{id}/locations|fundraisers|managers|backofficers/`, `companies/` (+`set_company`), `locations/`, `image/`, `slide/`, `campaigns/`, `projects/` (+`destinations`, +`topics`), `trackings/`, `sheets/{campaign_id}/signatures/`, `sheets/transactions/`, `sheets/{project_slug}/` (+`move`, +`set_contact_state`), `hooks/{apikey}/`, `deadline/{campaign_id}/`, `stats/{project_id}/`, `timeusage/`, `rounds/`, `mobilehelp/`, `widgets/`, `mapping/`, `email_templates/` (fuori scope, definito in `notification.viewsets`), `missingsignatures/`.

### api/v3/ (prefisso completo `/api/v3/...`)
`auth/token/`, `credit_card_check/`, `ping/`, più le stesse risorse di v2 (spesso con classi Python condivise) `users/`, `teams/`, `locations/`, `companies/`, `image/`, `slide/`, `campaigns/`, `projects/` (senza `topics`, lacuna rispetto a v2), `trackings/`, `sheets/` (piatta, non annidata sotto project, +`move`), `sheet_media/`, `hooks/{apikey}/`, `deadline/{campaign_id}/`, `stats/{project_id}/`, `reports/`, `workedshifts/`, `shifts/`, `mobilehelp/`, `widgets/`, `mapping/`, `backups/`, `missingsignatures/`.

### api/widget/ e api/widget/v2/ (pubbliche, nessuna autenticazione DRF)
v1: `ping/{apikey}/`, `donation_sheet/`, `donor_sheet/`, `payment_sheet/`, `payment_intent_sheet/`.
v2: `ping/{token}`, `donor/`, `donation/`, `confirm/`, `stripe/create_intent/`, `stripe/confirm/`, `paypal/checkout/`, `paypal/redirect/{token}/{sheet_uuid}/`, `sdd/create_account/`.

**Confronto con l'app mobile reale**: `metaface-mobile/src/data/network/*` chiama esclusivamente `/api/v3/`: `ping/`, `auth/token/`, `users/me/`, `backups/`, `teams/`, `locations/`, `campaigns/`, `trackings/`, `shifts/`, `workedshifts/`, `reports/`, `credit_card_check/`, `sheets/`, `sheets/{id}/move/`. **Nessuna divergenza**: tutte le chiamate dell'app corrispondono a endpoint effettivamente presenti nel backend, e l'app non usa mai v2. Questo conferma che v3 è l'API "viva" da preferire per qualsiasi nuova integrazione.

## 3. Autenticazione

- **API applicativa** (`/api/v2/`, `/api/v3/`): DRF `TokenAuthentication` + `SessionAuthentication` (`settings.py:79-82`), permesso default `IsAuthenticated` (`settings.py:83-85`). Token ottenuto via `POST /api/v3/auth/token/` con `{"username","password"}` → `{"token": "..."}`. Header: `Authorization: Token <token>`. **Confermato live**: un token esistente funziona, `GET /api/v3/ping/` con token valido risponde `valid_token: true` insieme a nome cliente/localizzazione/valuta.
- Il token DRF standard **non ha scadenza** codificata (nessun meccanismo di expiry/refresh nel codice): resta valido finché non rigenerato manualmente.
- **API widget pubblica**: nessuna `TokenAuthentication`/`SessionAuthentication` — identificazione manuale via `Widget.objects.get(apikey=...)`, apikey passata nel body (`token`) o nel path secondo l'endpoint.
- **Multi-tenant**: determinato dall'**host** (`<cliente>.metaface.it` = un'istanza/DB separato), non da un campo utente né da un header. Nessun endpoint per enumerare i clienti disponibili.
- **Permessi/ruoli**: nessun uso di Django Groups. Ruoli determinati da: FK diretti su `Team` (`leader`, `team_leader`, `supervisor`), relazioni through-table storicizzate (`TeamUsers`=dialogatore, `TeamManagers`=manager, `TeamOfficer`=backofficer) e permessi Django puntuali (es. `sheet.add_as_another_user` per i backofficer, `team.can_manage_teams` per i manager). Il campo `Staff.role` (Trainer/Frontliner/Coach/City-Regional-National coordinator) è una classificazione HR libera, non collegata a questi meccanismi di autorizzazione.

## 4. Punti DA VERIFICARE (con la domanda precisa da girare a chi ha scritto il codice)

1. **`sale.subscription` vs `ngo.subscription`** (priorità alta): `libs/donodoo/donodoo.py:36` usa `_obj = 'sale.subscription'` per la classe `SubscriptionsResource`, ma il modello Odoo reale usato dal modulo fundraising per le adesioni ricorrenti è `ngo.subscription` (`addons/ngo_addons/ngo_payment/models/ngo_subscription.py:56`). `sale.subscription` esiste in Donodoo solo come modulo Enterprise standard, scollegato dal flusso fundraising. **Domanda**: il codice Metaface chiama davvero la stringa `"sale.subscription"` via RPC? Se sì, cosa succede in pratica quando `donodoo_sync_jobs`/`odoo_sync_jobs` tenta di leggere `subscription.code` dopo il completamento di un job — e perché non è mai stato notato (le eccezioni in quel punto sono solo loggate in debug, non sollevate)?
2. **Frequenza di sincronizzazione Metaface→Donodoo**: il task `donodoo_sync_jobs` non è nel `beat_schedule` statico di `metaface/celery.py`. Con `django_celery_beat`/`DatabaseScheduler` attivo, la schedulazione (se esiste) vive nella tabella `django_celery_beat_periodictask` del DB di produzione. **Domanda**: con quale frequenza viene eseguito realmente `odoo_sync_jobs` per i clienti attivi? È un cron esterno o una periodic task DB?
3. **Task celery `send_sheet_to_donodoo` mai invocato**: definito in `integrations/donodoo/tasks.py:10-23` ma le chiamate a `.delay()`/diretta sono commentate in `integrations/donodoo/models.py:449-450`; oggi la creazione del job Donodoo è **sincrona** nel ciclo di cambio stato della sheet. **Domanda**: è un fix intenzionale (per gestire meglio gli errori sincroni) o un refactor incompleto? Impatta le prestazioni percepite dall'utente se Donodoo è lento.
4. **Configurazione multi-server/trigger Donodoo effettiva**: `DonodooServer`/`DonodooTrigger` sono record DB, non deducibili dal codice. **Domanda**: quanti server e trigger sono configurati oggi, per quali progetti/clienti, con quali stati di successo/fallimento?
5. **`SheetProject.checkpoint_state`/`fail_state`/`contact_state`** (`sheet/models/common.py:90-92`): definiti sul modello ma non risultano letti a runtime in nessun punto trovato oltre alla loro definizione. **Domanda**: sono dead code residuo o letti da una vista non coperta in questa ricognizione (es. form di configurazione admin)?
6. **Etichette testuali reali degli stati di workflow** (`State.label`) usate da ciascun cliente per "firmata"/"attivata"/"annullata": sono dati di configurazione per progetto, non fixture. **Domanda**: per un cliente specifico, quali sono gli state label esatti che corrispondono a questi tre concetti?
7. **Differenza semantica `Team.leader` vs `Team.team_leader`**: due FK distinte senza commenti che ne chiariscano l'uso differenziato (`team/models.py:926,928`). **Domanda**: qual è la differenza operativa tra i due ruoli?
8. **`TeamOfficer` (appartenenza team come backofficer) vs permesso Django `sheet.add_as_another_user`** (usato da `Staff.is_backofficer()`): non risulta un meccanismo di sincronizzazione automatica tra i due. **Domanda**: un utente aggiunto a `TeamOfficer` riceve automaticamente questo permesso, o sono gestiti indipendentemente (rischio di incoerenza)?
9. **`stripe_*`/`paypal_*` come chiavi di `ngo.job`**: il codice Metaface (`integrations/donodoo/models.py`, metodi `_prepare_job_donation_vals`/`_prepare_job_subscription_vals`) prepara chiavi come `stripe_intent_id`, `paypal_token` ecc. per il dizionario passato a `odoo.jobs.create(vals)`, ma questi campi **non esistono** sul modello `ngo.job` in nessun modulo Donodoo grepato. **Domanda**: queste chiavi vengono davvero inviate? Se sì, come le gestisce Odoo (silenziosamente ignorate, o causano errore)?
10. **`TriggerRegistry.trigger_type`** (`registry/models.py:148`) elenca solo `[('redmine','Redmine')]`, mentre esistono trigger concreti per Donodoo/webhook/payments/mf/directchannel. **Domanda**: questi trigger passano realmente dal registry (con l'enum da estendere) o restano sottoclassi Python indipendenti, rendendo l'enum incompleto per design?

## 5. Divergenze codice vs istanza live

| Cosa | Dal codice | Dal live | |
|---|---|---|---|
| `GET /api/v3/reports/` senza parametri | `UnboundLocalError` (bug nel branch else di `get_filter_data`) | Confermato: errore, ma la risposta è una pagina HTML "Ops!" con **status 200**, non 500 | Divergenza aggravante: un client che guarda solo lo status code non nota l'errore |
| `GET /api/v3/reports/?year=2026` | Nel codice sembrava un percorso valido (branch "solo anno") | **Fallisce anche con `year` valorizzato**, stessa pagina di errore HTML/200 | L'endpoint risulta rotto anche nel caso "documentato" come funzionante — non affidabile in questa versione live |
| Paginazione `/api/v3/sheets/` | `LimitOffsetPagination` dichiarata nel codice | Confermata: `{"count","next","previous","results"}` | Nessuna divergenza |
| `GET /api/v2/ping/` | `View` semplice, nessuna auth, solo `{"status":"OK"}` | Confermato | Nessuna divergenza |
| `GET /api/v3/ping/` | Espone `customer.name/localization/currency`, `valid_token` | Confermato (`"customer": "<nome cliente>", "localization": "it", "currency": "€"`) | Nessuna divergenza |
| Versione Odoo/Donodoo collegata | Attesa 14.x per compatibilità con `odoorpc` | Confermata **14.0-20231106** | Nessuna divergenza |
| Isolamento company su `teams/locations/campaigns/trackings/workedshifts` | Filtro per company/staff dell'utente | Confermato indirettamente: l'utente di test (senza company associata) riceve array vuoti su tutti questi endpoint | Nessuna divergenza, ma nota bene per capire risposte vuote in test |

**Verifica Donodoo — parziale**: confermata solo la versione del server (14.0-20231106, via `xmlrpc/2/common`) e il nome del database (`<db_odoo_cliente>`, risponde senza errore "database does not exist"). Il login con le credenziali fornite (`read-only-api` + chiave) restituisce `uid=False` (credenziali non valide per quel database) — non è stato possibile completare la verifica sui modelli `ngo.donor`/`ngo.job`/`ngo.subscription` lato Donodoo. **Nessuna scrittura o cancellazione è stata tentata su nessuna delle due istanze.**

## 6. Nota sull'assunzione iniziale del brief

L'architettura REST descritta nel brief esiste realmente ed è stata confermata sia dal codice sia dal comportamento live: Metaface **non** parla col backend in altro modo (non è un'app che usa solo GraphQL, gRPC, o WebSocket per i dati applicativi — Channels è usato solo per notifiche realtime, non per il modello dati principale). Nessuna smentita dell'assunzione da segnalare.
