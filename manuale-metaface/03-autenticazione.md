# Autenticazione

La pagina più importante di questo manuale: se la salti, la tua integrazione non funzionerà. Copre solo l'API applicativa (`/api/v2/`, `/api/v3/`); per l'API widget pubblica vedi il capitolo sul riferimento endpoint dedicato — non richiede login utente.

## Schema di autenticazione

Django REST Framework `TokenAuthentication` + `SessionAuthentication` (quest'ultima usata dall'interfaccia web, non da un client esterno). Permesso richiesto di default: `IsAuthenticated`. Non esiste JWT, non esiste OAuth, non esiste una API key custom per questa parte dell'API.

## Ottenere una credenziale, da zero, in una chiamata

```bash
curl -X POST https://<cliente>.metaface.it/api/v3/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "mario.rossi", "password": "la-tua-password"}'
```

Risposta:

```json
{"token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"}
```

## Usare il token

```bash
curl https://<cliente>.metaface.it/api/v3/teams/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

Header esatto: `Authorization: Token <token>`. Non è uno schema Bearer, non aggiungere altre parole.

## Verificare che tutto funzioni: dalla richiesta del token a una risposta autenticata

Sequenza completa, eseguibile da zero:

```bash
# 1. Ottieni il token
TOKEN=$(curl -s -X POST https://<cliente>.metaface.it/api/v3/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "mario.rossi", "password": "la-tua-password"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")

# 2. Verifica che sia valido, senza rischiare un 401 su un endpoint di business
curl -s https://<cliente>.metaface.it/api/v3/ping/ \
  -H "Authorization: Token $TOKEN"
# {"status":"OK","customer":"<nome cliente>","localization":"it","currency":"€","valid_token":true}

# 3. Prima chiamata autenticata "vera"
curl -s https://<cliente>.metaface.it/api/v3/users/me/ \
  -H "Authorization: Token $TOKEN"
# {"id":123,"last_login":"...","username":"mario.rossi","first_name":"Mario","is_staff":false,"is_superuser":false,"last_name":"Rossi","email":"..."}
```

## Durata e rinnovo

Il token DRF standard **non ha una scadenza codificata**: resta valido finché non viene rigenerato manualmente o l'utente disattivato. Non esiste un meccanismo di refresh automatico (non è JWT): se il token viene compromesso o va revocato, l'unica via è la rigenerazione tramite azione amministrativa sull'utente (interfaccia web, non API).

## Un endpoint utile per non sbagliare integrazione

`GET /api/v3/ping/` non richiede autenticazione, ma se viene passato comunque un token nell'header, la risposta include `valid_token: true|false`. È il modo più economico per un client di controllare se una credenziale salvata è ancora valida, senza rischiare un errore su un endpoint di business che magari ha anche effetti collaterali di logging.

`GET /api/v2/ping/` esiste anch'esso ma è più povero: risponde solo `{"status":"OK"}`, senza informazioni sul cliente né sulla validità del token.

## Cosa succede senza autenticazione

`GET /api/v3/` (la vista radice del router, senza specificare una risorsa) risponde `401` — confermato anche contro l'istanza live. `GET /api/` e `GET /api/v1/` non esistono affatto (`404`): la premessa comune a chi integra per la prima volta — "le rotte di scoperta standard sono tutte 404" — è corretta, ma non significa che l'API non esista: significa solo che va indirizzata direttamente al prefisso versionato giusto.
