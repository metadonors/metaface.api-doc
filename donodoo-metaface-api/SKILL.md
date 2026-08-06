---
name: donodoo-metaface-api
description: >
  Interroga i dati di un cliente Metadonors su Metaface (piattaforma Face2Face:
  dialogatori, adesioni raccolte sul campo, mandati SEPA, campagne, team, turni
  di lavoro) e su Donodoo (CRM donor management: donatori, campagne, esiti)
  tramite le rispettive API, e traduce in italiano semplice le risposte per
  personale non tecnico. Trigger: domande su "adesioni", "donatori", "dialogatori",
  "F2F", "mandati", "campagne", "team di [città/cliente]", "quante donazioni",
  "turni di lavoro", "quanto ha raccolto [team/dialogatore]", o qualsiasi domanda
  sui dati di un cliente che usa Metaface e/o Donodoo. NON è Riseact (altro CRM
  fundraising), NON è DonationBox/Tap2Pay (donazioni fisiche self-service), NON è
  Diabolocom (motore di fonia per il contact center telefonico) e non gestisce
  telefonate o campagne telemarketing. Solo lettura: non crea, modifica o
  cancella mai dati su Metaface o Donodoo.
---

# Skill: dati Donodoo + Metaface

Questa skill risponde in italiano a domande di staff non tecnico sui dati di un cliente Metadonors che usa Metaface (raccolta fondi Face2Face) e/o Donodoo (CRM donor management). Interroga le API reali via gli script in `scripts/`, non inventa numeri.

## Regola non negoziabile: solo lettura

Questa skill **non scrive mai** su Metaface o Donodoo. Gli script in `scripts/` non implementano nessun comando di creazione, modifica o cancellazione — per scelta esplicita, non per limite tecnico temporaneo. Se un utente chiede di "correggere", "aggiornare" o "cancellare" un dato, spiega che questa skill non lo fa e indirizzalo al canale corretto (backoffice/supporto).

## Configurazione (variabili d'ambiente)

Nessuna credenziale è scritta in questi file. Prima di usare la skill, servono:

```
METAFACE_URL=https://<cliente>.metaface.it
METAFACE_TOKEN=<token DRF>            # oppure METAFACE_USER + METAFACE_PASSWORD
DONODOO_URL=https://<cliente>.donodoo.it
DONODOO_DB=<nome database Odoo>       # non deducibile per convenzione, richiedilo a chi ha fatto il provisioning
DONODOO_USER=<login Odoo>
DONODOO_API_KEY=<api key o password>
```

Se una variabile manca, gli script si fermano con un messaggio che spiega cosa impostare — non tentano di indovinare o proseguire con valori finti. Se l'utente chiede di lavorare su un cliente e le variabili non sono impostate, dillo chiaramente e chiedi le credenziali (o di impostarle) prima di procedere.

## Multi-cliente per costruzione

`arca` è il primo cliente configurato, non l'unico supportato. L'istanza (host Metaface, host+database Donodoo) arriva sempre dalla configurazione (variabili d'ambiente), non è scritta nel codice degli script né in questi file. **Per aggiungere un cliente nuovo**: basta impostare le stesse variabili d'ambiente puntando all'host/database del nuovo cliente — nessuna modifica agli script o ai file di riferimento è necessaria.

## Come rispondere a una domanda

1. **Capisci cosa serve davvero**. Una domanda come "quante adesioni ha raccolto il team di Milano a giugno" richiede: risolvere il team per nome (`metaface_query.py teams`, poi filtrare per nome lato client — i filtri server-side su `teams` non sono attendibili, vedi `references/metaface-api.md`), poi interrogare `sheets` con `mandate_date_gte`/`mandate_date_lte` del mese richiesto.
2. **Se un termine è ambiguo, chiedi — non indovinare**. "Adesioni firmate" può significare `checkpoint_date` non nulla, oppure un esito specifico registrato: sono concetti diversi e l'etichetta esatta degli stati cambia per cliente (vedi `references/metaface-data-model.md`, sezione "Firmata vs Attivata vs Annullata"). Se non è ovvio dal contesto della domanda, chiedi all'utente cosa intende prima di calcolare un numero.
3. **Dichiara sempre il periodo considerato** nella risposta, anche se l'utente non lo ha specificato esplicitamente (es. "ho considerato il mese di giugno 2026, dal 1° al 30").
4. **Esegui la query** con gli script (vedi sotto), non costruire richieste HTTP/RPC a mano nella conversazione.
5. **Traduci in italiano leggibile**: numeri, una tabella breve se ci sono più righe, niente JSON grezzo salvo richiesta esplicita ("fammi vedere il dato grezzo"/"il JSON").
6. **Se un endpoint restituisce un errore o una forma inattesa** (es. `/api/v3/reports/` è noto per essere rotto anche con parametri validi, vedi `references/metaface-api.md`), dillo esplicitamente invece di presentare un numero incerto come certo.

## Script disponibili

### `scripts/metaface_query.py` — dati Metaface (adesioni, team, location, campagne, turni)

```bash
python3 scripts/metaface_query.py --help
python3 scripts/metaface_query.py sheets --mandate_date_gte 2026-06-01 --mandate_date_lte 2026-06-30
python3 scripts/metaface_query.py teams
python3 scripts/metaface_query.py workedshifts --from_date 2026-06-01 --to_date 2026-06-30 --staff 42
```

Gestisce internamente: ottenimento token (se non fornito direttamente), paginazione (segue `next` automaticamente per le risorse paginate), retry con backoff su errori di rete/5xx, stampa a tabella o `--json` per il dato grezzo.

### `scripts/donodoo_query.py` — dati Donodoo (donatori, campagne, esiti, adesioni ricorrenti)

```bash
python3 scripts/donodoo_query.py --help
python3 scripts/donodoo_query.py donor --domain "[('donor_ref','=','D00123')]"
python3 scripts/donodoo_query.py campaign --domain "[('code','=','19XXXXXX1')]"
python3 scripts/donodoo_query.py subscription --domain "[('state','=','open')]" --limit 20 --count
```

Usa XML-RPC (l'API esterna nativa di Odoo 14). Interroga sempre `ngo.subscription` per le adesioni ricorrenti, **non** `sale.subscription` (modello diverso, scollegato dal fundraising — vedi `references/donodoo-api.md`, nota critica). Il nome del modello si passa come parola semplice (`donor`, `job`, `campaign`, `outcome`, `subscription`), lo script lo traduce nel nome tecnico Odoo.

## Riconciliare un dialogatore o un'adesione fra i due sistemi

Non esiste un export/webhook automatico che collega i due sistemi in modo documentabile a priori: Metaface crea un record `ngo.job` su Donodoo via RPC quando un'adesione cambia stato, Donodoo lo elabora in background e lo trasforma in `ngo.donor` + `ngo.subscription`. Per riconciliare un'adesione specifica:
1. Su Metaface, trova la sheet (`metaface_query.py sheets --id_in <id>` o per `code`).
2. Se la sheet ha superato la fase di sincronizzazione, il codice Donodoo della sottoscrizione è normalmente riportato come riferimento esterno — se non è visibile nei campi restituiti dall'API Metaface, serve accedere all'interfaccia admin di Metaface (fuori scope di questa skill, che è read-only via API).
3. Su Donodoo, cerca per `external_id`/`code` su `ngo.subscription`, o per `donor_ref` su `ngo.donor` una volta noto il riferimento.

Leggi `references/metaface-data-model.md` (sezione integrazione) prima di dare per scontato che il collegamento sia immediato: c'è un ritardo di elaborazione asincrona lato Donodoo, e una discrepanza nota (non confermata in produzione) sul nome del modello sottoscrizione.

## Quando leggere i file in `references/`

Non servono per rispondere a domande generiche ("cos'è Metaface"): sono catalogo tecnico denso, da consultare quando serve il dettaglio esatto di un campo, un filtro o un modello.

- **`references/metaface-api.md`**: quale endpoint chiamare, quali filtri funzionano davvero (alcuni dichiarati nel codice non sono raggiungibili via query string — è documentato quali), forma esatta delle risposte, endpoint da non usare per integrazioni stabili.
- **`references/metaface-data-model.md`**: cosa significano i campi (enum, stati, ruoli), e soprattutto la sezione su "firmata/attivata/annullata" — leggila prima di calcolare qualsiasi numero su esiti di adesioni.
- **`references/donodoo-api.md`**: come autenticarsi via XML-RPC, quali modelli Odoo custom interrogare, la nota critica su `ngo.subscription` vs `sale.subscription`.

## Esempi di domande gestibili

- "Quante adesioni ha raccolto il team di Milano a giugno?" → `sheets` filtrato per team (lato client) e `mandate_date_gte/lte`, conteggio.
- "Chi ha lavorato più ore la settimana scorsa?" → `workedshifts` filtrato per data, aggregazione per `staff_label`.
- "Mi trovi il donatore con codice fiscale XYZ su Donodoo?" → `donodoo_query.py donor --domain "[('ssn','=','XYZ')]"`.
- "Quante campagne attive abbiamo su Metaface?" → `campaigns`, filtro `active` lato client se il campo non è filtrabile server-side (verifica in `references/metaface-api.md`).

## Cosa NON fare

- Non inventare un numero quando un endpoint fallisce o restituisce una forma inattesa: dillo.
- Non presumere l'etichetta di uno stato di workflow: è configurazione per cliente, non un enum fisso.
- Non tentare mai scritture, nemmeno "solo per provare" o dietro richiesta esplicita dell'utente: questa skill non lo fa, punto.
- Non mostrare token o credenziali nelle risposte, anche se compaiono per errore nell'output di un comando.
