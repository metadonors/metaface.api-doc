# Panoramica

Metaface è la piattaforma Face2Face di Metadonors: l'app tablet e il backend usati dai dialogatori che raccolgono adesioni e donazioni regolari sul campo — strada, ospedali, eventi, porta a porta. Un dialogatore compila una "scheda" (sheet) con i dati del donatore, l'importo e la frequenza della donazione, il metodo di pagamento; la scheda passa attraverso un flusso di validazione (workflow a stati configurabile per cliente) e, quando è pronta, viene inviata al CRM Donodoo per diventare un donatore e un'adesione ricorrente vere e proprie.

Questo manuale documenta l'API REST del backend Metaface per chi deve integrarsi da fuori: script di estrazione dati, riconciliazione con Donodoo, dashboard custom, automazioni. Non copre l'interfaccia web di amministrazione di Metaface (accessibile solo da browser, non ha un'API dedicata per la configurazione).

## Cosa copre questo manuale

Ricostruito dal codice sorgente dei repository `metadonors/metaface` (backend), `metadonors/metaface-mobile` (app tablet realmente in uso) e `metadonors/donodoo` (per la parte di modello dati Odoo coinvolta dall'integrazione), verificato per quanto possibile contro l'istanza live di un cliente reale (Arca). Data di ricognizione: 6 agosto 2026.

Nota su `metadonors/metaface-app`: esiste anche questo repository, ma al momento della ricognizione contiene solo lo scheletro predefinito di un progetto Expo mai avviato (nessuna logica applicativa). Non è l'app usata sul campo — l'app reale è `metaface-mobile`, React Native puro. Questo manuale ignora `metaface-app`.

## Versione del software coperta

Backend Metaface: stack Django/Django REST Framework, versione ricostruita dal branch principale del repository alla data sopra indicata (non esiste un numero di versione unico esposto dall'applicazione). Donodoo collegato: Odoo 14.0, build confermata live `14.0-20231106`.

## Cosa l'API permette

- Leggere e scrivere adesioni (sheet): dati donatore, importo/frequenza, metodo di pagamento, avanzamento di stato nel workflow.
- Leggere anagrafiche: team, location, campagne, codici di tracciamento, progetti.
- Gestire turni di lavoro dei dialogatori (creazione, modifica, cancellazione, lettura per periodo).
- Configurare e ricevere dati da widget di donazione pubblici embeddabili su siti terzi (con gateway Stripe, PayPal, SEPA Direct Debit).
- Consultare statistiche personali del singolo dialogatore.

## Cosa l'API non permette (o permette solo in modo fragile)

- Non esiste un'API per la configurazione applicativa (workflow, stati, trigger di integrazione, widget): tutto questo si gestisce solo dall'interfaccia web/Django admin.
- Non esiste un endpoint per enumerare i clienti/istanze Metaface disponibili: il tenant è determinato dal sottodominio con cui si effettua la chiamata.
- Alcuni endpoint (backup offline dell'app, richieste di supporto tecnico) sono pensati esclusivamente per l'app tablet e non hanno senso in un'integrazione esterna.
- Un endpoint di reportistica (`/api/v3/reports/`) risulta rotto anche nell'uso "documentato" — non affidabile per estrazioni automatiche, vedi il capitolo sui limiti noti.

## Come è organizzato il resto del manuale

Architettura e multi-tenant, poi autenticazione (la pagina da leggere per primi dieci minuti), ruoli e permessi, convenzioni trasversali dell'API, il catalogo degli endpoint (diviso per area funzionale), il modello dati completo con la legenda degli enum, l'integrazione con Donodoo, alcune ricette pratiche end-to-end, i limiti noti e i punti ancora aperti, e infine il changelog di questo manuale.
