# Donodoo (Odoo 14) — API esterna e modelli fundraising rilevanti

Donodoo è Odoo 14.0 standard (build confermata live: `14.0-20231106`). L'API esterna è quella nativa di Odoo, non un'API REST custom. Due protocolli disponibili, stessa semantica:

- **XML-RPC**: `POST /xmlrpc/2/common` (auth) e `/xmlrpc/2/object` (chiamate ai modelli).
- **JSON-RPC**: `POST /jsonrpc`.

Nessuna delle due richiede header speciali oltre al body della chiamata RPC. Non confondere con l'API v2/v3 di Metaface: sono due sistemi completamente diversi.

## Autenticazione

```python
import xmlrpc.client
common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
uid = common.authenticate(db, login, password_or_apikey, {})
```
`uid` è un intero (id utente) se le credenziali sono valide, `False` se non valide (nessuna eccezione, controllare sempre il valore). `password_or_apikey` può essere la password utente oppure una API key generata da Odoo (Impostazioni utente → Sicurezza account → Chiavi API) — sono intercambiabili nella chiamata `authenticate`.

Poi le chiamate ai modelli:
```python
models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")
models.execute_kw(db, uid, password_or_apikey, "ngo.donor", "search_read",
                   [[("donor_ref", "=", "D00123")]], {"fields": ["id", "name", "donor_ref"]})
```
Metodi principali: `search`, `search_count`, `search_read`, `read`, `create`, `write`, `unlink`. **La skill usa solo `search`/`search_read`/`search_count`/`read` — nessuna scrittura.**

## Nome del database

Non è deducibile a priori dal sottodominio: per il cliente Arca il database confermato (risponde senza errore "database does not exist") è `donodoo_arca`. Se si aggiunge un nuovo cliente, il nome del database va richiesto a chi ha fatto il provisioning, non assunto per convenzione.

## Modelli fundraising rilevanti (moduli custom `ngo_*`, non standard Odoo)

### ngo.donor — donatore
`_inherits = {'res.partner': 'partner_id'}`: quasi tutti i campi persona (nome, contatti, indirizzo) sono su `res.partner` ma leggibili direttamente su `ngo.donor`.

Campi propri: `donor_ref`(riferimento univoco, generato da sequenza), `is_prospect`, `state`(available, inprocess, blacklisted, privacy, canceled, dead), `source_campaign_id`. Da `res.partner`: `ssn, gender(male/female/family/company/other), birthdate_date, firstname/lastname, vat, phone, email, city, ...`.

### ngo.campaign — campagna
Campo chiave: `code` (cercato da Metaface con `search([('code','=', campaign_name)])`). Altri: `name, description, start_date/end_date, campaign_type_id, job_ids(O2M ngo.job)`.

### ngo.outcome — esito
Campo chiave: `name` (cercato da Metaface con `search([('name','=', outcome_name)])`). Altri: `outcome_type(useful/useless), outcome_category(positive/negative), workflow_id`.

### ngo.job — coda di lavorazione (il "buffer" tra Metaface e i dati reali)
Non è un donatore né una donazione: è un record temporaneo che Odoo elabora in modo asincrono. Campi principali: `state(new, sent, processing, verification, completed, canceled)`, `donor_id`, `subscription_id`(**FK verso `ngo.subscription`, non `sale.subscription`** — vedi nota critica sotto), `campaign_id`, `outcome_id`, tutti i campi anagrafici/pagamento del donatore (`donor_firstname`, `donor_ssn`, `bank_account`, `creditcard_*`, ecc.), campi F2F (`fundraiser_name/code`, `team_name/code`, `location_name/code`, `batch`).

Quando `state == "completed"`, `job.donor_id` e `job.subscription_id` sono popolati con id reali.

### ngo.subscription — l'adesione ricorrente reale (NON sale.subscription)
Campo chiave: `code` (letto da Metaface dopo il completamento del job). Altri: `state(draft/check/open/pending/cancel/revoked/close — stessi valori di ngo.job.subscription_state)`, `donor_id`, `amount`, `mandate_date`, `template_id`(frequenza), `external_id`(corrisponde a `subscription_external_ref` sul job). Arricchito da `ngo_face2face` con `fundraiser_id/team_id/location_id`.

> **Nota critica**: `sale.subscription` esiste in questo Odoo solo come modulo Enterprise standard, scollegato dal flusso fundraising. Se un client (incluso il codice Metaface attuale) usa `"sale.subscription"` come nome modello per leggere i dati di un `ngo.job.subscription_id`, sta interrogando il modello sbagliato. Usare sempre `ngo.subscription`.

## Esempio di lettura corretta

```python
donor = models.execute_kw(db, uid, key, "ngo.donor", "search_read",
    [[("donor_ref", "=", ref)]], {"fields": ["id", "name", "email", "state"]})

sub = models.execute_kw(db, uid, key, "ngo.subscription", "search_read",   # NON sale.subscription
    [[("id", "=", subscription_id)]], {"fields": ["id", "code", "state", "amount", "mandate_date"]})
```

## DA VERIFICARE

- Quali `ngo.job.workflow`/`ngo.job.activity` sono configurati per le campagne Face2Face in uso (dato applicativo nel DB, non nel codice).
- Se il campo `subscription_state`/`state` esposto da Odoo usa esattamente le label indicate qui per la versione live del cliente specifico — verificare con una `search_read` di prova quando le credenziali saranno valide.
