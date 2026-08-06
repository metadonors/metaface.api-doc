# Architettura e modello multi-tenant

## Componenti del sistema

- **Backend Metaface**: Django + Django REST Framework. Espone sia le pagine web dell'interfaccia amministrativa/operativa, sia l'API REST oggetto di questo manuale. Usa Celery per i task asincroni (es. sincronizzazione con Donodoo) e `django_celery_beat` come scheduler, con le schedulazioni periodiche salvate a database, non nel codice.
- **App tablet (`metaface-mobile`)**: React Native, è il client "vero" usato dai dialogatori sul campo. Parla esclusivamente con `/api/v3/`, mai con v2 né con rotte non documentate in questo manuale — verificato leggendo il codice del client HTTP dell'app.
- **API widget pubblica**: un secondo livello di API, separato da quello applicativo, pensato per form di donazione online embeddabili su siti terzi (donazioni via widget, non raccolte da un dialogatore). Non richiede login utente.
- **Donodoo**: CRM esterno (Odoo 14) che riceve i dati delle adesioni completate. Il collegamento è realizzato via RPC (XML-RPC/JSON-RPC nativo di Odoo), non via un'API REST dedicata — vedi il capitolo sull'integrazione con Donodoo.

## Due API distinte, non confonderle

| | API applicativa | API widget |
|---|---|---|
| Prefisso | `/api/v2/`, `/api/v3/` | `/api/widget/`, `/api/widget/v2/` |
| Chi la usa | App tablet, back office, integrazioni interne | Form di donazione pubblici su siti terzi |
| Autenticazione | Token DRF (utente/password) | Nessuna autenticazione DRF: identificazione tramite `apikey` del widget |
| Isolamento dati | Per company/staff dell'utente loggato | Per singolo widget configurato |

Preferire sempre `/api/v3/` per l'API applicativa: è la versione usata realmente dall'app tablet, generalmente più completa (paginazione corretta su `sheets`, filtri più ricchi, isolamento multi-tenant più solido) rispetto a `/api/v2/`, che resta per compatibilità con integrazioni storiche.

## Come si identifica l'istanza di un cliente

Il tenant è determinato **dall'host**, non da un campo utente né da un header applicativo: ogni cliente Metadonors ha un proprio sottodominio (`<cliente>.metaface.it`, es. `arca.metaface.it`) che corrisponde a un'istanza e a un database separati. Non esiste alcun endpoint che elenchi i clienti disponibili o permetta di cambiare tenant a runtime: un client software che deve lavorare su più clienti tratta l'host come parametro di configurazione esterno (variabile d'ambiente, file di configurazione), non come un dato scopribile dall'API.

Lo stesso principio vale per Donodoo, con una differenza pratica: lì il tenant è determinato dalla combinazione di host (`<cliente>.donodoo.it`) **e** nome del database Odoo, che non segue una convenzione automatica dedotta dal sottodominio — va richiesto a chi ha eseguito il provisioning dell'istanza.

## Dove sta il confine dei dati fra un cliente e l'altro

A livello di infrastruttura, ogni cliente ha probabilmente un database Metaface separato (il codice conferma un solo record "Customer" per installazione, letto da `customer.utils.get_customer()`). All'interno della stessa installazione, l'isolamento più fine è per **company**: un utente vede solo i dati (team, location, campagne, adesioni) delle company a cui è associato tramite il proprio profilo `Staff`. Questo isolamento è implementato in modo non uniforme fra le versioni dell'API: `/api/v3/sheets/` filtra sempre per `company__in=<company dell'utente>`, mentre l'equivalente `/api/v2/sheets/{project_slug}/` con `project_slug` uguale al valore letterale `all` può restituire schede di tutte le company senza questo filtro — un comportamento da trattare con cautela se si costruisce un'integrazione nuova (preferire v3, che non ha questa lacuna).
