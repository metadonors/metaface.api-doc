# Limiti noti e punti aperti

Una pagina onesta vale più di dieci pagine ottimistiche: qui è raccolto tutto ciò che non è stato possibile confermare con certezza, o che si è verificato essere fragile.

## Da verificare con priorità alta

1. **`sale.subscription` vs `ngo.subscription`**: il client Metaface (`libs/donodoo/donodoo.py`) legge le sottoscrizioni dal nome di modello Odoo `sale.subscription`; il modello Donodoo reale per le adesioni ricorrenti fundraising è `ngo.subscription`. Se confermato, è un bug silenzioso nella sincronizzazione (le eccezioni in quel punto sono solo loggate in debug). **Domanda per chi mantiene il codice**: il codice usa davvero la stringa `"sale.subscription"`? Da quanto tempo? Quale impatto ha avuto sui dati letti finora?
2. **Frequenza reale del polling Donodoo**: non deducibile dal codice (scheduler a configurazione database). **Domanda**: con quale frequenza viene eseguito `odoo_sync_jobs` in produzione, per quali clienti?
3. **Configurazione multi-server/trigger Donodoo effettiva**: quanti `DonodooServer`/`DonodooTrigger` sono configurati oggi, per quali clienti/progetti — dato di configurazione, non di codice.

## Bug applicativi noti dal codice

- `SheetViewSetV3.destroy` (v3): referenzia una variabile non definita — chiamare `DELETE` su una sheet produce un errore server, non un `403`/`204` pulito.
- `GET /api/v3/reports/`: **confermato anche in verifica live** — fallisce sia senza parametri sia con `?year=YYYY` valorizzato, restituendo una pagina HTML di errore con status `200` (non un errore JSON con status coerente). Non usare questo endpoint per integrazioni fino a correzione.
- `SheetViewSet.set_contact_state` (v2): la risposta segnala sempre esito negativo (`"KO"`) anche quando l'operazione riesce.
- I filtri ricchi dichiarati nel codice su `teams`/`locations` (v2 e v3) non sono in realtà raggiungibili via query string: un bug sovrascrive i parametri del client con un valore vuoto prima di applicarli.
- `LocationSerializerV3.get_address`: il campo `address` in v3 è hardcoded a stringa vuota — non è un problema dei dati, è il serializer.

## Rotte interne, fragili, da non usare per un'integrazione stabile

- `hooks/{apikey}/` — dipende da un header proprietario (`Metaface-Client-Version`) per decidere il formato della risposta.
- `mobilehelp/`, `backups/` — contengono dump di log/database locale dell'app tablet, non dati di business.
- `credit_card_check/` — verifica interna al flusso di raccolta, non pensata per un uso indipendente.

## Divergenze osservate tra codice e istanza live (cliente Arca)

- `GET /api/v3/reports/` è risultato **più rotto** di quanto suggerisse la sola lettura del codice: nel codice il bug sembrava limitato al caso "nessun parametro passato", ma in produzione fallisce anche passando `year` valorizzato.
- Tutto il resto verificato (paginazione di `sheets`, forma di `ping`/`users/me`, isolamento per company, versione Odoo `14.0-20231106`) corrisponde a quanto risultava dal codice — nessun'altra divergenza rilevata nella finestra di verifica eseguita.
- La verifica lato Donodoo è rimasta parziale: confermata solo la versione del server e il nome del database (`donodoo_arca`); il login con le credenziali fornite non è riuscito (credenziali non valide per quel database, non un problema di rete o di configurazione del client).

## Punti apertI sul modello dati

- Differenza semantica esatta tra `Team.leader` e `Team.team_leader`: due campi distinti, nessun commento nel codice che ne chiarisca l'uso differenziato.
- Se l'appartenenza a `TeamOfficer` implichi automaticamente il permesso Django usato per identificare i backofficer, o se i due meccanismi vadano gestiti/sincronizzati manualmente.
- Se `SheetProject.checkpoint_state`/`fail_state`/`contact_state` siano effettivamente letti a runtime da qualche vista non coperta in questa ricognizione, oltre alla loro definizione sul modello.
- Le etichette testuali esatte degli stati di workflow che ogni cliente usa per "firmata"/"attivata"/"annullata": dati di configurazione per progetto, non enumerabili dal codice.

## Cosa NON è stato ancora verificato in questo manuale

- Comportamento sotto carico / rate limiting reale (non risulta implementato throttling DRF nel codice, ma non è stato testato in produzione).
- Fuso orario esatto applicato ai timestamp (`created`, `updated`).
- L'endpoint `email_templates/`, definito in un'app esterna al perimetro di questa ricognizione (`notification.viewsets`).
