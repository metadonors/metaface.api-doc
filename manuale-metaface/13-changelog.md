# Changelog del manuale

Serve a capire, fra sei mesi, se quello che si sta leggendo è ancora vero.

| Data | Versione software documentata | Cosa è cambiato |
|---|---|---|
| 2026-08-06 | Backend Metaface: branch principale del repository `metadonors/metaface` alla data indicata. Donodoo collegato: Odoo 14.0, build `14.0-20231106` (confermata live su un cliente reale). | Prima versione del manuale. Ricostruito interamente dal codice sorgente (`metadonors/metaface`, `metadonors/metaface-mobile`, `metadonors/donodoo`) e verificato parzialmente contro l'istanza live di un cliente reale: confermata l'autenticazione, la forma di più endpoint di lettura, e trovata una divergenza (endpoint `/api/v3/reports/` più fragile del previsto). Verifica lato Donodoo rimasta parziale per credenziali di test non valide. |

## Come aggiornare questo manuale

Se il codice del backend Metaface cambia in modo rilevante per l'API (nuovi endpoint, cambio di autenticazione, correzione dei bug elencati nel capitolo sui limiti noti), aggiornare prima il capitolo pertinente e poi aggiungere una riga qui con data e sintesi del cambiamento — non limitarsi a cambiare il contenuto senza lasciare traccia di cosa è cambiato e quando.
