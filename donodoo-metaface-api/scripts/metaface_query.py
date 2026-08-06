#!/usr/bin/env python3
"""Client di sola lettura per l'API Metaface (v3).

Nessun comando di scrittura e' implementato in questo script, per scelta:
la skill donodoo-metaface-api e' read-only e deve restare tale.

Variabili d'ambiente richieste:
  METAFACE_URL       es. https://<cliente>.metaface.it
  METAFACE_TOKEN     token DRF (Authorization: Token <...>)
oppure, se non si ha ancora un token:
  METAFACE_USER, METAFACE_PASSWORD  (lo script fa POST /api/v3/auth/token/ per ottenerne uno)

Se METAFACE_URL manca lo script si ferma e spiega cosa impostare.
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

DEFAULT_TIMEOUT = 20
MAX_RETRIES = 3


def env_or_die(name, hint):
    value = os.environ.get(name)
    if not value:
        print(f"Errore: variabile d'ambiente {name} non impostata.\n{hint}", file=sys.stderr)
        sys.exit(2)
    return value


def get_base_url():
    url = env_or_die("METAFACE_URL", "Esempio: export METAFACE_URL=https://<cliente>.metaface.it")
    return url.rstrip("/")


def get_token():
    token = os.environ.get("METAFACE_TOKEN")
    if token:
        return token
    user = os.environ.get("METAFACE_USER")
    pwd = os.environ.get("METAFACE_PASSWORD")
    if not (user and pwd):
        print(
            "Errore: serve METAFACE_TOKEN oppure METAFACE_USER + METAFACE_PASSWORD.\n"
            "Esempio: export METAFACE_TOKEN=9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
            file=sys.stderr,
        )
        sys.exit(2)
    base = get_base_url()
    body = json.dumps({"username": user, "password": pwd}).encode()
    req = urllib.request.Request(
        f"{base}/api/v3/auth/token/", data=body, method="POST",
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=DEFAULT_TIMEOUT) as resp:
        data = json.loads(resp.read())
    return data["token"]


def request_json(method, path, params=None, retries=MAX_RETRIES):
    base = get_base_url()
    token = get_token()
    url = f"{base}{path}"
    if params:
        url += "?" + urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})

    last_error = None
    for attempt in range(1, retries + 1):
        req = urllib.request.Request(url, method=method, headers={"Authorization": f"Token {token}"})
        try:
            with urllib.request.urlopen(req, timeout=DEFAULT_TIMEOUT) as resp:
                content_type = resp.headers.get("Content-Type", "")
                raw = resp.read()
                if "application/json" not in content_type:
                    raise RuntimeError(
                        f"Risposta non JSON da {path} (Content-Type: {content_type}). "
                        "Alcuni endpoint (es. /reports/) restituiscono una pagina di errore HTML "
                        "con status 200: vedi RICOGNIZIONE.md / references/metaface-api.md."
                    )
                return json.loads(raw)
        except urllib.error.HTTPError as e:
            last_error = e
            if e.code in (429, 502, 503) and attempt < retries:
                time.sleep(2 ** attempt)
                continue
            body = e.read().decode(errors="replace")
            print(f"Errore HTTP {e.code} su {path}: {body}", file=sys.stderr)
            sys.exit(1)
        except urllib.error.URLError as e:
            last_error = e
            if attempt < retries:
                time.sleep(2 ** attempt)
                continue
            print(f"Errore di rete su {path}: {e}", file=sys.stderr)
            sys.exit(1)
    raise RuntimeError(f"Retry esauriti su {path}: {last_error}")


def paginate_all(path, params=None):
    """Segue next/previous per le risorse paginate (es. sheets). Per le risorse
    non paginate restituisce semplicemente l'array ricevuto."""
    params = dict(params or {})
    results = []
    first = request_json("GET", path, params)
    if isinstance(first, dict) and "results" in first:
        results.extend(first["results"])
        next_url = first.get("next")
        while next_url:
            parsed = urllib.parse.urlparse(next_url)
            query = dict(urllib.parse.parse_qsl(parsed.query))
            page = request_json("GET", parsed.path, query)
            results.extend(page.get("results", []))
            next_url = page.get("next")
        return results
    return first  # lista piatta, non paginata


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


COMMANDS = {
    "ping": {"path": "/api/v3/ping/", "fields": None},
    "me": {"path": "/api/v3/users/me/", "fields": None},
    "teams": {"path": "/api/v3/teams/", "fields": ["id", "name", "company_id"]},
    "locations": {"path": "/api/v3/locations/", "fields": ["id", "code", "label", "city"]},
    "campaigns": {"path": "/api/v3/campaigns/", "fields": ["id", "name"]},
    "trackings": {"path": "/api/v3/trackings/", "fields": ["id", "code", "label", "is_active"]},
    "sheets": {
        "path": "/api/v3/sheets/",
        "fields": ["id", "code", "state", "checkpoint_date", "team", "company"],
        "filters": ["mandate_date_gte", "mandate_date_lte", "created_gte", "created_lte",
                    "updated_gte", "updated_lte", "checkpoint_date_gte", "checkpoint_date_lte",
                    "state", "id_in"],
        "paginated": True,
    },
    "workedshifts": {
        "path": "/api/v3/workedshifts/",
        "fields": ["id", "uuid", "date", "team_label", "location_label", "staff_label"],
        "filters": ["from_date", "to_date", "staff"],
        "paginated": False,
    },
    "shifts": {"path": "/api/v3/shifts/", "fields": ["id", "name", "duration"]},
}


def main():
    parser = argparse.ArgumentParser(
        description="Query di sola lettura sull'API Metaface v3. "
        "Configurazione via env: METAFACE_URL, METAFACE_TOKEN (o METAFACE_USER/METAFACE_PASSWORD).",
        epilog="Esempio: METAFACE_URL=https://<cliente>.metaface.it METAFACE_TOKEN=... "
        "python3 metaface_query.py sheets --mandate_date_gte 2026-06-01 --mandate_date_lte 2026-06-30",
    )
    parser.add_argument("command", choices=sorted(COMMANDS.keys()), help="Cosa interrogare")
    parser.add_argument("--json", action="store_true", help="Stampa JSON grezzo invece della tabella")

    # Filtri passati come --nome valore, validi solo se il comando scelto li supporta
    known_filters = set()
    for cfg in COMMANDS.values():
        known_filters.update(cfg.get("filters", []))
    for f in sorted(known_filters):
        parser.add_argument(f"--{f}", default=None)

    args = parser.parse_args()
    cfg = COMMANDS[args.command]
    params = {}
    for f in cfg.get("filters", []):
        value = getattr(args, f, None)
        if value is not None:
            params[f] = value

    if cfg.get("paginated"):
        data = paginate_all(cfg["path"], params)
    else:
        data = request_json("GET", cfg["path"], params)

    if args.json or cfg["fields"] is None:
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return

    rows = data if isinstance(data, list) else [data]
    print_table(rows, cfg["fields"])


if __name__ == "__main__":
    main()
