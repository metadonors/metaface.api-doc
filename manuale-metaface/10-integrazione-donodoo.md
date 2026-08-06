# Integrazione con Donodoo

## Il meccanismo reale (nessun export, nessun webhook: è RPC)

Non esiste un file di export, un CSV programmato o un webhook che collega Metaface a Donodoo: il collegamento avviene interamente via chiamate RPC dirette, innescate da un evento applicativo.

1. **Trigger**: quando un'adesione (sheet) cambia stato nel workflow di Metaface, un segnale controlla se esiste un `DonodooTrigger` configurato per quella combinazione di stato/progetto/esito. Questa configurazione vive nel database di Metaface (tabella amministrabile solo da Django admin), non nel codice: un cliente può avere più server Donodoo configurati, tipicamente uno per progetto/campagna.
2. **Creazione del job**: Metaface si connette a Donodoo via **XML-RPC/JSON-RPC** (libreria Python `odoorpc`, non un endpoint REST) e crea un record `ngo.job` con tutti i dati dell'adesione: dialogatore, team, location, dati del donatore, importo, frequenza, metodo di pagamento, consensi privacy raccolti.
3. **Elaborazione asincrona lato Odoo**: il job viene accodato e processato da un workflow Odoo configurabile per tipo di campagna/esito, che crea o aggancia un `ngo.donor` esistente e, se l'adesione è ricorrente, crea un `ngo.subscription` (arricchito con i dati fundraiser/team/location specifici del modulo Face2Face).
4. **Polling**: Metaface interroga periodicamente lo stato del job (`new → processing → completed`, oppure `verification`/`canceled` in caso di problemi, tramite il comando `odoo_sync_jobs`). Quando il job è `completed`, Metaface legge `donor_id` e `subscription_id` per popolare i propri riferimenti locali (visibili come dati storici sulla sheet, non tramite l'API pubblica).

## Frequenza

Non determinabile dal codice sorgente: il task che effettua il polling non è nello scheduler statico, e Metaface usa uno scheduler con configurazione salvata a database (`django_celery_beat`). La frequenza reale per un cliente specifico va verificata direttamente con chi gestisce l'infrastruttura, o interrogando la tabella di scheduling sul database di produzione — non è un dato che l'API espone.

## Un comportamento da conoscere: la creazione del job è sincrona

Il codice prevede anche un task in background dedicato a questo scopo, ma non risulta più invocato nel percorso attivo: oggi la creazione del job Donodoo avviene **sincronamente**, nello stesso momento in cui l'adesione cambia stato in Metaface. Se Donodoo è lento o temporaneamente irraggiungibile in quel momento, l'operazione sul lato Metaface rischia di richiedere più tempo del previsto o di fallire in modo visibile per chi sta lavorando sull'app in quel momento.

## Dove può fallire

- **Nome del modello sottoscrizione** (punto critico, non ancora confermato in produzione): il client Metaface legge le adesioni ricorrenti dal nome di modello Odoo `sale.subscription`. Nel Donodoo reale, il modello usato dal modulo fundraising per questo scopo è `ngo.subscription` — un modello diverso, custom, non collegato a `sale.subscription` (che è invece il modulo Enterprise standard di Odoo, estraneo al flusso di raccolta fondi). Se il codice punta davvero al nome sbagliato, la lettura di ritorno dopo il completamento del job può restituire dati vuoti o incoerenti — e il problema passerebbe inosservato perché le eccezioni in quel punto sono solo loggate in modalità debug, non sollevate come errore.
- **Connessione a Donodoo non disponibile**: essendo sincrona, un'interruzione di rete o un'istanza Donodoo sovraccarica blocca visibilmente il flusso di lavoro Metaface nel momento del cambio di stato.
- **Campagna o esito non trovati su Donodoo**: se il codice della campagna (cercato per `tracking_code` dell'adesione, o per un valore fisso configurato sul trigger) o l'esito non esistono sul lato Donodoo, la creazione del job fallisce con un errore registrato ma il flusso può restare bloccato in attesa di intervento manuale.

## Personalizzazioni per cliente

Esiste un meccanismo di estensione per singolo cliente: alcuni clienti hanno una classe Python dedicata che arricchisce i dati inviati a Donodoo con campi aggiuntivi specifici (un esempio riscontrato nel codice riguarda un cliente che aggiunge settimana, modulo e tipo di sottoscrizione ai dati standard). Questo confirma che l'integrazione è pensata per essere personalizzata, non è un flusso identico e rigido per tutti i clienti.

## Se il collegamento non esistesse (per chiarezza)

Non è il caso di Metaface/Donodoo: il collegamento esiste ed è descritto sopra. Se in futuro si dovesse valutare un cliente Metaface senza integrazione Donodoo attiva, servirebbe: un `DonodooServer` configurato (credenziali di accesso all'istanza Odoo del cliente) e almeno un `DonodooTrigger` collegato a uno stato del workflow del progetto — senza questi due elementi configurati via Django admin, nessun dato passa automaticamente da Metaface a Donodoo, e l'unica via diventerebbe un export manuale.
