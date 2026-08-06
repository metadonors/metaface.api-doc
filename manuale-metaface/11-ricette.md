# Ricette

Casi d'uso concreti risolti end-to-end, con codice eseguibile. Usano gli script della skill `donodoo-metaface-api` (vedi il repository della skill), ma sono scritti anche in `curl` puro dove è più semplice seguirli. Valori di esempio fittizi.

## 1. Estrarre le adesioni di un periodo per un team

Obiettivo: tutte le adesioni con data mandato in un intervallo, per un team specifico. Il filtro per team non è raggiungibile server-side su `/sheets/` (non esiste un parametro `team`): si estrae per periodo e si filtra lato client sul campo `team` restituito.

```bash
TOKEN="9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
BASE="https://arca.metaface.it/api/v3"

# 1. Trova l'id del team (nome esatto o via ricerca manuale sull'elenco)
curl -s "$BASE/teams/" -H "Authorization: Token $TOKEN" | python3 -c "
import json,sys
teams = json.load(sys.stdin)
for t in teams:
    if 'Milano' in t['name']:
        print(t['id'], t['name'])
"

# 2. Estrai le adesioni del periodo (segue automaticamente la paginazione)
curl -s "$BASE/sheets/?mandate_date_gte=2026-06-01&mandate_date_lte=2026-06-30&limit=100" \
  -H "Authorization: Token $TOKEN" | python3 -c "
import json,sys
data = json.load(sys.stdin)
milano = [s for s in data['results'] if s['team'] == 4]  # id trovato al passo 1
print(f\"{len(milano)} adesioni per il team Milano nel periodo\")
"
```

Con lo script della skill, lo stesso risultato in una riga (il filtro per team va comunque fatto lato client, lo script non lo fa per te):

```bash
METAFACE_URL=https://arca.metaface.it METAFACE_TOKEN=$TOKEN \
  python3 scripts/metaface_query.py sheets --mandate_date_gte 2026-06-01 --mandate_date_lte 2026-06-30 --json \
  | python3 -c "import json,sys; print(len([s for s in json.load(sys.stdin) if s['team']==4]))"
```

## 2. Riconciliare un dialogatore fra Metaface e Donodoo

Non esiste un endpoint diretto "dammi il record Donodoo di questo dialogatore": la riconciliazione passa per l'adesione che il dialogatore ha raccolto.

```bash
# 1. Su Metaface: trova le adesioni raccolte da un dialogatore (per username noto)
curl -s "$BASE/sheets/?limit=200" -H "Authorization: Token $TOKEN" | python3 -c "
import json,sys
data = json.load(sys.stdin)
mie = [s for s in data['results'] if s.get('author') == 42]  # id utente del dialogatore
print(f\"{len(mie)} adesioni raccolte\")
for s in mie[:5]:
    print(s['id'], s['code'], s['donor']['last_name'])
"

# 2. Su Donodoo: per ogni adesione completata, cerca il donatore per riferimento esterno
python3 scripts/donodoo_query.py job --domain "[('external_ref','=','SC00501')]" --fields "id,state,donor_id,subscription_id"

# 3. Se il job e' completed, leggi il donatore e l'adesione ricorrente reali
python3 scripts/donodoo_query.py donor --domain "[('id','=','<donor_id trovato al passo 2>')]"
python3 scripts/donodoo_query.py subscription --domain "[('id','=','<subscription_id trovato al passo 2>')]"
```

Attenzione: se il job risulta ancora in `processing` o `verification`, la riconciliazione non è ancora completa — è normale, l'elaborazione lato Donodoo è asincrona (vedi il capitolo sull'integrazione).

## 3. Costruire un report per campagna

Obiettivo: importo totale raccolto per campagna in un periodo, con distinzione fra adesioni "firmate" (checkpoint raggiunto) e non.

```bash
curl -s "$BASE/sheets/?mandate_date_gte=2026-01-01&mandate_date_lte=2026-06-30&limit=500" \
  -H "Authorization: Token $TOKEN" | python3 -c "
import json,sys
from collections import defaultdict

data = json.load(sys.stdin)
totali = defaultdict(lambda: {'firmate': 0.0, 'non_firmate': 0.0, 'n_firmate': 0, 'n_totali': 0})

for s in data['results']:
    campagna = s.get('campaign') or 'senza campagna'
    importo = s['donation']['amount'] if s.get('donation') else 0
    totali[campagna]['n_totali'] += 1
    if s.get('checkpoint_date'):
        totali[campagna]['firmate'] += importo
        totali[campagna]['n_firmate'] += 1
    else:
        totali[campagna]['non_firmate'] += importo

for campagna, dati in totali.items():
    print(f\"Campagna {campagna}: {dati['n_firmate']}/{dati['n_totali']} firmate, €{dati['firmate']:.2f} raccolti (firmate)\")
"
```

Nota: 'firmata' qui è definita come `checkpoint_date` presente — verificare con l'utente se è il criterio corretto per il proprio caso (vedi il capitolo sul modello dati, sezione firmata/attivata/annullata) prima di presentare il numero come definitivo.

## 4. Verificare la configurazione di un widget pubblico prima di pubblicarlo

```bash
curl -s https://arca.metaface.it/api/widget/v2/ping/abc123token | python3 -m json.tool
```

Controlla che `options.payment.methods` contenga i metodi di pagamento attesi e che `options.currency` sia quella corretta, prima di dare l'ok alla pubblicazione del widget su un sito cliente.
