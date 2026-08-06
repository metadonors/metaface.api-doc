# Ruoli e permessi

## Chi vede cosa

Non esiste un sistema di ruoli con Django Groups. L'autorizzazione è costruita su tre meccanismi che coesistono:

1. **Appartenenza a company**: un utente (tramite il proprio profilo `Staff`) è associato a una o più company. Gli endpoint dell'API applicativa filtrano quasi sempre i dati per questa appartenenza — un'integrazione che usa un utente di test associato a nessuna company riceverà array vuoti da endpoint come `teams`, `locations`, `campaigns`, anche se esistono dati nell'istanza (comportamento confermato in verifica live).
2. **Ruoli per team**: `leader`, `team_leader` e `supervisor` sono campi diretti sul modello `Team` (non gruppi, non permessi) — assegnati singolarmente per ogni squadra. L'appartenenza come dialogatore, manager o backofficer è invece una relazione storicizzata con date di inizio/fine (`TeamUsers`, `TeamManagers`, `TeamOfficer`): un utente può essere stato manager di un team in passato e non esserlo più oggi.
3. **Permessi Django puntuali**: alcune capacità (es. modificare una scheda già "chiusa", gestire il fallimento di una scheda, gestire team/location/dialogatori) sono controllate da permessi Django assegnati direttamente all'utente, non derivati automaticamente dai ruoli di team. Un caso concreto: la funzione che determina se un utente è "backofficer" (`Staff.is_backofficer()`) controlla il permesso `sheet.add_as_another_user`, non l'appartenenza a `TeamOfficer` — i due meccanismi non risultano sincronizzati automaticamente nel codice.

Esiste anche un campo `Staff.role` (Trainer, Frontliner, Coach, City/Regional/National coordinator) che è una classificazione HR libera, utile per reportistica interna, ma **non collegata** ai meccanismi di autorizzazione sopra: un dialogatore con `role=Frontliner` non ottiene automaticamente permessi diversi da un altro con `role=Coach`.

## Cosa significa in pratica per un'integrazione

Se l'utente/token usato dall'integrazione non è correttamente associato a company, team e permessi, molte chiamate risponderanno con array vuoti (non con un errore): un problema di configurazione dell'utente, non dell'API. Prima di concludere che "l'API non restituisce dati", verificare che l'utente di servizio usato abbia effettivamente accesso ai dati che si stanno cercando.

## Ruolo → meccanismo (riepilogo)

| Ruolo | Come si determina |
|---|---|
| Dialogatore / fundraiser | Relazione attiva in `TeamUsers` (più tipicamente `Staff.role == Frontliner`, ma non è un requisito tecnico) |
| Team leader / Leader / Supervisor | Campi FK diretti su `Team` (`team_leader`, `leader`, `supervisor`) |
| Manager | Relazione attiva in `TeamManagers` |
| Backofficer | Relazione attiva in `TeamOfficer` **e** permesso Django `sheet.add_as_another_user` (meccanismi distinti) |
| Amministratore | `is_superuser`/`is_staff` sul modello utente Django |

## Un utente vede solo i propri dati o quelli di tutta l'organizzazione?

Dipende dall'endpoint, non è una regola unica:
- Le proprie statistiche personali (`/api/v3/reports/`, quando funziona — vedi capitolo sui limiti noti) e i propri turni di lavoro (`/api/v3/workedshifts/`) sono sempre filtrati sul singolo utente, indipendentemente dal ruolo.
- Team, location, campagne e adesioni sono filtrati per company: un utente vede i dati di tutte le company a cui è associato, non solo i propri.
- Alcune viewset (es. le immagini/slide di campagna) non applicano alcun filtro per company: sono visibili a chiunque sia autenticato, indipendentemente dall'organizzazione — una scelta di progetto o una lacuna, non è determinabile con certezza dal solo codice.

Se un'integrazione deve rispettare un confine di visibilità più stretto di quanto l'API applichi di default, va gestito lato client, verificando caso per caso quale filtro l'endpoint applica realmente (vedi il capitolo sul riferimento endpoint).
