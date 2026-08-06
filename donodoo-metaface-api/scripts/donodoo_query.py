#!/usr/bin/env python3
"""Client di sola lettura per l'API esterna di Donodoo (Odoo 14, XML-RPC).

Nessun comando di scrittura e' implementato in questo script, per scelta:
la skill donodoo-metaface-api e' read-only e deve restare tale. Non aggiungere
create/write/unlink qui senza una richiesta esplicita e separata dell'utente.

Variabili d'ambiente richieste:
  DONODOO_URL       es. https://arca.donodoo.it
  DONODOO_DB        nome del database Odoo (es. donodoo_arca) - non e' deducibile
                     per convenzione, va richiesto a chi ha fatto il provisioning
  DONODOO_USER      login Odoo (es. read-only-api)
  DONODOO_API_KEY   password o API key Odoo (intercambiabili per l'autenticazione)

Modelli custom fundraising rilevanti: ngo.donor, ngo.job, ngo.campaign, ngo.outcome,
ngo.subscription (NON sale.subscription, vedi references/donodoo-api.md).
"""
import argparse
import json
import os
import sys
import time
import xmlrpc.client

DEFAULT_TIMEOUT = 20
MAX_RETRIES = 3

KNOWN_MODELS = {
    "donor": "ngo.donor",
    "job": "ngo.job",
    "campaign": "ngo.campaign",
    "outcome": "ngo.outcome",
    "subscription": "ngo.subscription",
}

DEFAULT_FIELDS = {
    "ngo.donor": ["id", "donor_ref", "name", "email", "state"],
    "ngo.job": ["id", "name", "state", "donor_id", "subscription_id", "campaign_id", "outcome_id"],
    "ngo.campaign": ["id", "code", "name", "start_date", "end_date"],
    "ngo.outcome": ["id", "name", "outcome_type", "outcome_category"],
    "ngo.subscription": ["id", "code", "state", "donor_id", "amount", "mandate_date"],
}


def env_or_die(name, hint):
    value = os.environ.get(name)
    if not value:
        print(f"Errore: variabile d'ambiente {name} non impostata.\n{hint}", file=sys.stderr)
        sys.exit(2)
    return value


def get_config():
    url = env_or_die("DONODOO_URL", "Esempio: export DONODOO_URL=https://arca.donodoo.it").rstrip("/")
    db = env_or_die("DONODOO_DB", "Esempio: export DONODOO_DB=donodoo_arca (richiedilo a chi ha fatto il provisioning)")
    user = env_or_die("DONODOO_USER", "Esempio: export DONODOO_USER=read-only-api")
    key = env_or_die("DONODOO_API_KEY", "Esempio: export DONODOO_API_KEY=<api key o password>")
    return url, db, user, key


def authenticate():
    url, db, user, key = get_config()
    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
    uid = common.authenticate(db, user, key, {})
    if not uid:
        print(
            f"Errore: autenticazione Odoo fallita per db={db!r} user={user!r} "
            "(uid=False). Credenziali non valide per questo database, non un problema "
            "di rete: verifica login/API key con chi le ha fornite.",
            file=sys.stderr,
        )
        sys.exit(1)
    return url, db, uid, key


def execute(model, method, args, kwargs=None, retries=MAX_RETRIES):
    url, db, uid, key = authenticate()
    models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            return models.execute_kw(db, uid, key, model, method, args, kwargs or {})
        except xmlrpc.client.Fault as e:
            last_error = e
            print(f"Errore Odoo su {model}.{method}: {e.faultString}", file=sys.stderr)
            sys.exit(1)
        except OSError as e:
            last_error = e
            if attempt < retries:
                time.sleep(2 ** attempt)
                continue
            print(f"Errore di rete su {model}.{method}: {e}", file=sys.stderr)
            sys.exit(1)
    raise RuntimeError(f"Retry esauriti su {model}.{method}: {last_error}")


def print_table(rows, fields):
    if not rows:
        print("(nessun risultato)")
        return
    widths = {f: max(len(f), max((len(str(r.get(f, ""))) for r in rows), default=0)) for f in fields}
    header = " | ".join(f.ljust(widths[f]) for f in fields)
    print(header)
    print("-+-".join("-" * widths[f] for f in fields))
    for r in rows:
        print(" | ".join(str(r.get(f, "")).ljust(widths[f]) for f in fields))


def main():
    parser = argparse.ArgumentParser(
        description="Query di sola lettura sui modelli fundraising di Donodoo (Odoo 14, XML-RPC). "
        "Configurazione via env: DONODOO_URL, DONODOO_DB, DONODOO_USER, DONODOO_API_KEY.",
        epilog="Esempi:\n"
        "  python3 donodoo_query.py donor --domain \"[('donor_ref','=','D00123')]\"\n"
        "  python3 donodoo_query.py campaign --domain \"[('code','=','19XXXXXX1')]\"\n"
        "  python3 donodoo_query.py job --domain \"[('state','=','completed')]\" --limit 5",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("resource", choices=sorted(KNOWN_MODELS.keys()), help="Modello da interrogare")
    parser.add_argument("--domain", default="[]", help="Domain Odoo in sintassi Python, es. \"[('state','=','open')]\"")
    parser.add_argument("--fields", default=None, help="Lista campi separata da virgola (default: campi principali)")
    parser.add_argument("--limit", type=int, default=50, help="Numero massimo di record (default 50)")
    parser.add_argument("--count", action="store_true", help="Restituisce solo il conteggio (search_count)")
    parser.add_argument("--json", action="store_true", help="Stampa JSON grezzo invece della tabella")
    args = parser.parse_args()

    model = KNOWN_MODELS[args.resource]
    try:
        domain = eval(args.domain, {"__builtins__": {}}, {})  # noqa: S307 - input locale, sintassi domain Odoo
    except Exception as e:
        print(f"Errore nel parsing di --domain: {e}", file=sys.stderr)
        sys.exit(2)

    if args.count:
        total = execute(model, "search_count", [domain])
        print(total)
        return

    fields = args.fields.split(",") if args.fields else DEFAULT_FIELDS.get(model, ["id", "name"])
    rows = execute(model, "search_read", [domain], {"fields": fields, "limit": args.limit})

    if args.json:
        print(json.dumps(rows, indent=2, ensure_ascii=False))
        return
    print_table(rows, fields)


if __name__ == "__main__":
    main()
