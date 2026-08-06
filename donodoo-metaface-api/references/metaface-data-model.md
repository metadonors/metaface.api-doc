# Metaface — modello dati denso (entità, enum, relazioni)

Fonte: ricognizione codice `metadonors/metaface`, app `sheet`, `team`, `campaigns`, `hr`, `widgets`, `stats`, `integrations/*`. Per campo→endpoint vedi `metaface-api.md`.

## Sheet / DefaultSheet — l'adesione (entità centrale)

Campi chiave: `author`(dialogatore che ha raccolto), `leader/team_leader/supervisor`(denormalizzati dal team al save), `team`, `company`, `campaign/campaign_product`, `outcome`(esito verifica/donor care, non stato workflow), `reject`(se popolato = **annullata/rifiutata** con causale), `outcome_date`, `tracking_code`, `donor/beneficiary`(Person), `uuid`(idempotenza), `donation`, `payment`, `checkpoint_date`(prima volta raggiunto uno stato checkpoint = dati validati = **"firmata"**), `deleted`(soft-delete, manager di default filtra `deleted=False`), `stripe_intent_id/stripe_subscription_id/paypal_subscription_id/paypal_token`, `widget`(se da form online), `state`(FK workflow.State), `communicated_states`(JSON, anti-duplicazione verso Donodoo).

### Firmata vs Attivata vs Annullata — NON è un campo enum unico, va calcolato

- **Firmata**: `state.checkpoint == True` e `checkpoint_date` non nulla. Significa "dati completi e validati" (importo>0, IBAN/carta compilati, mandate_date valida, ecc.), non necessariamente pagamento incassato.
- **Attivata**: nessun flag diretto. Inferita da `have_a_valid_transaction`(esiste `CreditCardTransaction` con `transaction_result=='OK'`) e/o `stripe_subscription_id`/`paypal_subscription_id` popolati, oppure lo stato coincide col "success_state" configurato per il progetto sul `PaymentTrigger`.
- **Annullata**: `sheet.reject is not None` (causale di rifiuto) — segnale canonico, usato anche nel calcolo statistico ufficiale.

Formula di classificazione usata dal sistema di reportistica (`stats/models.py compute_stats`):
```
if sheet.reject:                          -> rejected (annullata)
elif state.outcome == POSITIVE:           -> completed (attivata/firmata con successo)
elif not state or state.outcome == GROSS: -> incomplete
else:                                      -> rejected
```
**Prima di calcolare un numero su "adesioni firmate/attivate" per un cliente specifico, verificare quali sono le `state.label` reali configurate per quel progetto** — sono dati per-cliente, non fissi. Se non è chiaro, chiedere all'utente invece di assumere.

## Donation

`frequency` (0=oneoff/una-tantum, 1=annuale, 2=semestrale, 3=quadrimestrale, 4=trimestrale, 6=bimestrale, 12=mensile — il numero è "rate/anno"). `amount`, `mandate_date`(data firma/adesione), `first_payment`, `destination`(FK, la causa/progetto scelto), `topic`(FK, sotto-tema), `sad_code`(Sostegno a Distanza). Proprietà: `is_oneoff = frequency==0`, `annualized_amount = amount*frequency` (o `amount` se oneoff).

## PaymentMethod

`method`: `BW`=SEPA SDD (bankwire nel nome, ma è mandato SDD non bonifico), `DD`=direct debit, `CC`=carta, `TTL`=SDD via TTL, `POS`=pagamento fisico, `PP`=PayPal. Solo il ramo corrispondente (`creditcard`/`bankwire`/`pos`/`ttl`/`directdebit`) è popolato.

`CreditCardTransaction`: `transaction_result` è stringa libera con valore chiave `'OK'`/`'KO'` (non enum Django). Non esiste un modello "SheetTransaction" generico, solo questo specifico per carta.

## Person (donor/beneficiary/holder)

`sex`: `M`=maschio, `F`=femmina, `N`=nucleo familiare, `C`=azienda. Campi: `business_name, first_name, last_name, dob, pob, job, ssn(codice fiscale), vat`. `contacts`: `phone, mobile, fax, email` + 7 flag privacy granulari per canale (`privacy, sms_privacy, phone_privacy, mail_privacy, paper_privacy, profilation_privacy, profilation_third_party_privacy, social_privacy`) + preferenze.

## Team / Location / Company / Staff

`Team`: `area, leader(FK User), team_leader(FK User, differenza esatta con leader DA VERIFICARE), supervisor(FK User), company, locations(M2M)`. Ruoli denormalizzati su ogni sheet al momento del salvataggio.

Composizione membri (storicizzata con `date_start/date_end`): `TeamUsers`=dialogatore/fundraiser, `TeamManagers`=manager, `TeamOfficer`=backofficer.

`Location`: `code(unique), label, category, typology, status(confirmed/negative_outcome/in_progress/no_outcome/not_yet), level(1=Hot,0=Normal,-1=Cold), region, active`.

`Staff`: O2O User. `role`(Trainer, Frontliner, Coach, City coordinator, Regional coordinator, National coordinator) — classificazione HR libera, NON collegata ai ruoli di team sopra. `is_backofficer()` si basa sul permesso Django `sheet.add_as_another_user`, non su `TeamOfficer` — i due meccanismi non risultano sincronizzati (DA VERIFICARE).

**Riepilogo ruoli per la skill**: "dialogatore"→membro attivo `TeamUsers`; "team leader"/"leader"/"supervisor"→FK diretti su `Team`; "manager"→membro attivo `TeamManagers`; "backofficer"→membro attivo `TeamOfficer` + permesso Django.

## Workflow (state machine)

`Workflow` è per-progetto (O2O con `SheetProject`); alla creazione ha solo 2 stati generici ("Created","Closed"). **Tutti gli altri stati sono configurati manualmente per progetto/cliente — non è un enum fisso, va interrogato via API (`state.label` sulle sheet) o chiesto all'utente.**

`State`: `label`(libero), `editable`, `checkpoint`(se True, raggiungerlo forza validazione stringente), `closed`, `entry`, `outcome`(-1=Negative, 0=Gross, 1=Positive default).

## Campaign

`name, active, version(incrementa ad ogni save), checkpoint_state/fail_state(FK State)`. `Product`: collega una Campaign a una `Destination` di donazione. `ContractClause`: clausole privacy/contrattuali mostrate in campagna.

## SheetProject

`name, sheet_type(quale classe Sheet), companies(M2M, chi può usarlo), beneficiary_enabled, checkpoint_state/fail_state/contact_state(FK State — uso a runtime da confermare)`.

## hr — contratti e presenze dialogatori (NON contratti commerciali con clienti ETS)

`Contract`(valid_from/until, contract_type, company), `TimeUsage`/`Rounds`(turni), `Expense`(extra/logistic/employee).

## jobs — job asincroni Metaface locali (NON confondere con "ngo.job" di Odoo!)

`BackgroundJob`(state: pending/running/completed/failed). Sottoclassi: `SheetMoveJob`(sposta massivamente sheet a un nuovo stato), `ImportJob`(import CSV massivo).

## widgets — configurazione widget donazione online

`Widget`: `company/staff/team/location/destination/checkpoint_state, apikey(generato al save, NO vincolo unicità DB), embed_code`.

## Collegamento a Donodoo — riassunto (dettaglio in donodoo-api.md)

Nessun export CSV, nessun webhook: Metaface crea un record `ngo.job` su Donodoo via RPC (libreria `odoorpc`) quando una sheet cambia stato e un `DonodooTrigger` è configurato per quello stato/progetto/esito. Donodoo elabora il job in modo asincrono e lo trasforma in `ngo.donor` + (se ricorrente) `ngo.subscription`. Metaface fa polling sullo stato del job (`odoo_sync_jobs`) per recuperare gli id creati. **Attenzione**: il client Metaface legge le subscription dal nome modello `sale.subscription`, che potrebbe essere sbagliato (il modello reale è `ngo.subscription`) — vedi RICOGNIZIONE.md punto 1.
