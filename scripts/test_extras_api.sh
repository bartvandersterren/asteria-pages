#!/usr/bin/env bash
#
# API-proef voor /api/extras/* (functions/api/extras/[[path]].js). Port van parkhotel-site scripts/test_extras_api.sh.
#
#   bash scripts/test_extras_api.sh               # start zelf `wrangler pages dev . --port PORT` (standaard 8788)
#   PORT=8831 bash scripts/test_extras_api.sh
#
# Vereist .dev.vars in de repo-root (niet in git): EXTRAS_DRY_RUN=1, MAIL_DRY_RUN=1, EXTRAS_SHARED_SECRET=test.
# Niets verlaat de machine behalve het ophalen van de catalogus bij Mews (netwerk nodig): geen Zapier (dry-run,
# payload in het dev-log) en geen mail (MAIL_DRY_RUN). Blok 4 start een tweede server zonder dry-run en zonder hook
# (fallback-pad, [HANDMATIG]) en met een nep-RESEND_API_KEY (gastmail via de Resend-route, in dry-run).
# Er is geen ratelimit-binding op het Pages-project, dus geen 429-test (rateOk laat alles door).

set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PORT="${PORT:-8788}"
WRANGLER="${WRANGLER:-npx --yes wrangler@4}"
TMP="$(mktemp -d)"
PASS=0
FAIL=0
DEV_PID=""
BASE="http://127.0.0.1:$PORT"
RUN=0
LOG=""
MARK=0

DINER="75fce6f2-6339-41c2-9e48-b3b60095d412"
ONTBIJT="a80b1abc-7079-44f7-be63-af2e00bb4d9f"
WELLNESS="bd06307a-e86f-434c-a799-b43400d93806"
FIETS="a3a062b9-3854-449c-b74f-b05300c1a15e"
EBIKE="527b5916-5451-4db7-9839-b0b2008e6dd3"
KRUIDENOLIE="a2871461-233c-4aac-a2b9-b43400854b25"
BADJAS="8a5468e9-1aa8-4a2f-818a-af810098ec66"
HANDDOEK="c558563b-c217-4b66-ac99-b43300d08641"
EARLY="325c73ef-09f9-4596-81d9-b0970067bd55"
LATE="196e6fe4-f15a-4384-a7e0-b097006801ee"
SERVICE="755424cc-3077-4320-b069-af1d00ffbe47"
GUID="0c90a9f6-2e2e-4214-88c8-b4b900b4f047"
VERBLIJF="\"r\":\"$GUID\",\"n\":\"123456\",\"a\":\"2026-10-20\",\"d\":\"2026-10-22\",\"p\":\"2\",\"v\":\"Test\""

[ -f "$ROOT/.dev.vars" ] || { echo "!! .dev.vars ontbreekt (EXTRAS_DRY_RUN=1, MAIL_DRY_RUN=1, EXTRAS_SHARED_SECRET=test)"; exit 1; }

stop_dev() {
  if [ -n "$DEV_PID" ]; then kill "$DEV_PID" 2>/dev/null; wait "$DEV_PID" 2>/dev/null; DEV_PID=""; fi
  local i pids
  for i in $(seq 1 20); do
    pids="$(lsof -ti "tcp:$PORT" -sTCP:LISTEN 2>/dev/null)"
    [ -z "$pids" ] && return 0
    echo "$pids" | xargs kill 2>/dev/null
    sleep 1
  done
}
cleanup() { stop_dev; rm -rf "$TMP"; }
trap cleanup EXIT

# start_dev [--binding K=V ...]
start_dev() {
  stop_dev
  RUN=$((RUN + 1))
  LOG="$TMP/dev-$RUN.log"
  echo "== wrangler pages dev op $BASE  (${*:-.dev.vars})"
  ( cd "$ROOT" && $WRANGLER pages dev . --port "$PORT" --compatibility-date 2026-10-06 \
      --persist-to "$TMP/state-$RUN" "$@" ) >"$LOG" 2>&1 &
  DEV_PID=$!
  local i
  for i in $(seq 1 90); do
    if curl -s -o /dev/null --max-time 2 "$BASE/api/extras/sessie" 2>/dev/null; then return 0; fi
    sleep 1
  done
  echo "!! wrangler pages dev kwam niet op. Log:"; tail -30 "$LOG"; exit 1
}

check() { # check <naam> <verwacht> <werkelijk>
  if [ "$2" = "$3" ]; then
    PASS=$((PASS + 1)); printf '  OK    %-62s %s\n' "$1" "$3"
  else
    FAIL=$((FAIL + 1)); printf '  FOUT  %-62s kreeg %s, verwacht %s  body: %s\n' "$1" "$3" "$2" "$(head -c 300 "$TMP/body")"
  fi
}

json_check() { # json_check <naam> <python-expressie over B>
  if python3 - "$TMP/body" "$2" <<'PY'
import json, sys
B = json.load(open(sys.argv[1]))
sys.exit(0 if eval(sys.argv[2]) else 1)
PY
  then PASS=$((PASS + 1)); printf '  OK    %-62s\n' "$1"
  else FAIL=$((FAIL + 1)); printf '  FOUT  %-62s %s  body: %s\n' "$1" "$2" "$(head -c 400 "$TMP/body")"
  fi
}

log_mark() { sleep 0.3; MARK=$(wc -l <"$LOG" | tr -d ' '); }

log_check() { # log_check <naam> <python-expressie over P (payloads ná log_mark)>
  sleep 0.8
  if python3 - "$LOG" "$MARK" "$2" <<'PY'
import json, sys
regels = open(sys.argv[1], encoding="utf-8", errors="replace").read().splitlines()[int(sys.argv[2]):]
P = []
for r in regels:
    i = r.find("payload=")
    if i >= 0:
        P.append(json.loads(r[i + 8:]))
try:
    ok = eval(sys.argv[3])
except Exception as e:
    print("     (fout in expressie: %s; %d payloads)" % (e, len(P))); ok = False
if not ok:
    print("     payloads: " + json.dumps([{k: p.get(k) for k in ("product_name","count","persons","units","evenings","billing","mews_total","line_total","deviation","task","task_name")} for p in P], ensure_ascii=False))
sys.exit(0 if ok else 1)
PY
  then PASS=$((PASS + 1)); printf '  OK    %-62s\n' "$1"
  else FAIL=$((FAIL + 1)); printf '  FOUT  %-62s %s\n' "$1" "$2"
  fi
}

log_grep() { # log_grep <naam> <fragment>
  sleep 0.3
  if tail -n +"$((MARK + 1))" "$LOG" | grep -q -- "$2"; then
    PASS=$((PASS + 1)); printf '  OK    %-62s\n' "$1"
  else
    FAIL=$((FAIL + 1)); printf '  FOUT  %-62s mist "%s" in het dev-log\n' "$1" "$2"
  fi
}

post() { curl -s -o "$TMP/body" -w '%{http_code}' -X POST "$BASE/api/extras/bestel" -H 'Content-Type: application/json' -d "$1"; }
get() { curl -s -o "$TMP/body" -w '%{http_code}' "$BASE/api/extras/sessie?$1"; }

OUD=$(( $(date +%s) * 1000 - 60000 ))

start_dev

echo
echo "== 1. sessie"
S=$(get "r=$GUID&n=123456&a=2026-10-20&d=2026-10-22&p=2&v=Test&k=diner&taal=nl&client=extras-v2")
check "sessie 200" 200 "$S"
json_check "sessie: tien producten in Mews-volgorde" \
  "B['ok'] and [p['key'] for p in B['products']]==['diner','ontbijt','wellness','fiets','ebike','kruidenolie','badjas','handdoek','early','late']"
json_check "sessie: echte Mews-prijzen (centen)" \
  "{p['key']:p['price_cents'] for p in B['products']}=={'diner':3750,'ontbijt':1750,'wellness':1250,'fiets':950,'ebike':2500,'kruidenolie':495,'badjas':700,'handdoek':450,'early':2500,'late':2500}"
json_check "sessie: Mews-chargingmodes" \
  "{p['key']:p['mews_charging'] for p in B['products']}=={'diner':'PerPersonPerTimeUnit','ontbijt':'PerPersonPerTimeUnit','wellness':'PerPerson','fiets':'PerPerson','ebike':'PerPerson','kruidenolie':'Once','badjas':'PerPerson','handdoek':'PerPerson','early':'Once','late':'Once'}"
json_check "sessie: groep, type, dagLabel, eenheid" \
  "{p['key']:(p['groep'],p['type'],p['dagLabel'],p['eenheid']) for p in B['products']}=={'diner':('verblijf','perdag','avond','persoon'),'ontbijt':('verblijf','pernacht','','persoon'),'wellness':('verblijf','perdag','dag','persoon'),'fiets':('verblijf','personen','','fiets'),'ebike':('verblijf','personen','','fiets'),'kruidenolie':('verblijf','eenmalig','',''),'badjas':('aankomst','personen','','persoon'),'handdoek':('aankomst','personen','','persoon'),'early':('aankomst','eenmalig','',''),'late':('vertrek','eenmalig','','')}"
json_check "sessie: eigen foto's, default_count, max, wellness tijd_overleg" \
  "all(p['image_url']=='/fotos/extras-'+p['key']+'.webp' for p in B['products']) and {p['key']:p['default_count'] for p in B['products']}['badjas']==2 and {p['key']:p['max'] for p in B['products']}['kruidenolie']==3 and [p['tijd_overleg'] for p in B['products'] if p['key']=='wellness']==[True]"
json_check "sessie: labels, nights_list, recommended" \
  "B['reservation']['arrival_label']=='di 20 okt 2026' and [n['short'] for n in B['reservation']['nights_list']]==['di 20 okt','wo 21 okt'] and B['recommended']=='diner'"
H=$(curl -s -D - -o /dev/null "$BASE/api/extras/sessie?r=$GUID" | tr -d '\r' | grep -i '^cache-control' | cut -d' ' -f2-)
check "sessie Cache-Control" "private, max-age=60" "$H"
S=$(get "r=$GUID")
json_check "sessie zonder client: zelfde tien producten" "len(B['products'])==10"
S=$(get "r=nope")
check "sessie ongeldige link -> 400" 400 "$S"
S=$(get "r=$GUID&a=2026-10-22&d=2026-10-20")
json_check "sessie vertrek vóór aankomst -> datums leeg, 1 nacht" \
  "B['reservation']['arrival']=='' and B['reservation']['nights']==1 and B['reservation']['nights_list']==[]"

echo
echo "== 2. bestellen (dry-run)"
log_mark
S=$(post "{$VERBLIJF,\"client\":\"extras-v2\",\"e\":\"test@example.com\",\"t0\":$OUD,\"k\":\"kruidenolie\",
  \"regels\":[{\"product_id\":\"$KRUIDENOLIE\",\"count\":2},{\"product_id\":\"$BADJAS\",\"count\":2},{\"product_id\":\"$EARLY\"}]}")
check "exact (kruidenolie 2 + badjas 2 + early) -> 200" 200 "$S"
json_check "exact: total 990+1400+2500, fallback false, mail_sent false (geen Resend)" \
  "B['ok'] and B['total_cents']==4890 and B['fallback'] is False and B['mail_sent'] is False and [(r['key'],r['count']) for r in B['regels']]==[('kruidenolie',2),('badjas',2),('early',1)]"
log_check "exact: 3 payloads, geen afwijking, service Asteria, secret, client" \
  "len(P)==3 and all(p['deviation']=='' and p['service_id']=='$SERVICE' and p['secret']=='test' and p['client']=='extras-v2' and p['recommended_key']=='kruidenolie' for p in P)"
log_check "exact: badjas count 1 (Mews × 2 pers.), billing B, € 14,00" \
  "[(p['count'],p['billing'],p['mews_total'],p['line_total']) for p in P if p['product_id']=='$BADJAS']==[(1,'B','€ 14,00','€ 14,00')]"
log_check "exact: taak alleen op regel 1, bronregel visit.asteria.nl" \
  "[p['task'] for p in P]==['ja','nee','nee'] and P[0]['task_description'].startswith('Besteld via visit.asteria.nl/extras (pre-arrival mail).') and P[1]['task_name']==''"
log_check "exact: negen Zap-velden aanwezig, count integer, deadline aankomst" \
  "all(all(k in p for k in ('secret','reservation_id','service_id','product_id','count','task','task_name','task_description','task_deadline')) and isinstance(p['count'],int) and p['task_deadline']=='2026-10-20T12:00:00' for p in P)"
log_grep "exact: receptiemail via FormSubmit (dry-run)" "MAIL_DRY_RUN (formsubmit), niet verstuurd. to=info@asteria.nl subject=Extra's besteld · reservering 123456 (Test)"

log_mark
S=$(post "{$VERBLIJF,\"client\":\"extras-v2\",\"e\":\"test@example.com\",\"t0\":$OUD,
  \"regels\":[{\"product_id\":\"$WELLNESS\",\"count\":2},{\"product_id\":\"$DINER\",\"count\":2,\"avonden\":[\"2026-10-21\"],\"tijd\":\"19.00\"}]}")
check "diner 1 van 2 avonden + wellness 2 x 2 -> 200" 200 "$S"
json_check "diner+wellness: gasttotaal 75 + 50" "B['total_cents']==12500"
log_check "diner: eerst (afwijking), count 1, billing B, Mews € 150 ≠ € 75" \
  "(P[0]['product_id'],P[0]['count'],P[0]['billing'],P[0]['mews_total'],P[0]['line_total'])==('$DINER',1,'B','€ 150,00','€ 75,00') and P[0]['deviation']!=''"
log_check "diner: CORRIGEER-blok en (CORRIGEER) in de taak" \
  "P[0]['task_description'].startswith('!! CORRIGEER IN MEWS') and P[0]['task_name'].endswith('(CORRIGEER)')"
log_check "diner: avond, tijd en restaurant-taak" \
  "(P[0]['evenings'],P[0]['preferred_time'])==('2026-10-21','19:00') and 'tafel in ons restaurant reserveren voor 2 pers. op wo 21 okt 2026 rond 19:00' in P[0]['task_description']"
log_check "wellness: count 2 (2 pers. x 2 dagen), exact € 50,00, receptie reserveert" \
  "[(p['count'],p['units'],p['mews_total'],p['deviation']) for p in P if p['product_id']=='$WELLNESS']==[(2,'4','€ 50,00','')] and 'wellness reserveren voor 2 pers. op di 20 okt 2026 en wo 21 okt 2026' in P[0]['task_description']"
log_grep "diner: receptiemail met [CORRIGEER]" "subject=\[CORRIGEER\] Extra's besteld"

log_mark
S=$(post "{$VERBLIJF,\"client\":\"extras-v2\",\"e\":\"test@example.com\",\"t0\":$OUD,
  \"regels\":[{\"product_id\":\"$FIETS\",\"count\":2},{\"product_id\":\"$EBIKE\",\"count\":1},{\"product_id\":\"$ONTBIJT\",\"count\":2},{\"product_id\":\"$HANDDOEK\",\"count\":2},{\"product_id\":\"$LATE\"}]}")
check "fiets 2 + e-bike 1 + ontbijt 2 + handdoek 2 + late -> 200" 200 "$S"
json_check "gasttotaal 19 + 25 + 70 + 9 + 25" "B['total_cents']==14800"
log_check "e-bike 1 fiets bij 2 gasten: afwijking (Mews € 50 ≠ € 25), vooraan" \
  "(P[0]['product_id'],P[0]['mews_total'],P[0]['line_total'])==('$EBIKE','€ 50,00','€ 25,00') and '1 fiets, eenmalig' in P[0]['deviation']"
log_check "fiets 2: count 1, exact € 19,00; ontbijt count 1, exact € 70,00" \
  "[(p['count'],p['line_total'],p['deviation']) for p in P if p['product_id']=='$FIETS']==[(1,'€ 19,00','')] and [(p['count'],p['line_total'],p['deviation']) for p in P if p['product_id']=='$ONTBIJT']==[(1,'€ 70,00','')]"
log_check "taak: fietsen klaarzetten, ontbijtcontrole, handdoeken op de kamer, late" \
  "'Fietshuur · 2 fietsen · € 19,00' in P[0]['task_description'] and 'fietsen klaarzetten bij de receptie: 2 fietsen (fietshuur)' in P[0]['task_description'] and 'Controleer of het tarief al ontbijt bevat' in P[0]['task_description'] and 'handdoekpakketten op de kamer klaarleggen' in P[0]['task_description'] and 'early check-in/late check-out noteren' in P[0]['task_description']"

log_mark
S=$(post "{$VERBLIJF,\"t0\":$OUD,\"regels\":[{\"product_id\":\"$KRUIDENOLIE\"}]}")
check "zonder client en zonder e -> 200 (telt als v2)" 200 "$S"
json_check "zonder e: mail_sent false, count 1" "B['mail_sent'] is False and B['regels'][0]['count']==1"
log_check "zonder e: taak meldt e-mail onbekend, client extras-v2" "'e-mail onbekend' in P[0]['task_description'] and P[0]['client']=='extras-v2'"

echo
echo "== 3. fouten en spam"
S=$(post "{$VERBLIJF,\"t0\":$OUD,\"regels\":[{\"product_id\":\"$DINER\",\"count\":2,\"avonden\":[\"2026-10-22\"]}]}")
check "ongeldige avond -> 400" 400 "$S"
json_check "ongeldige avond: fields [avonden], product_id" "B['fields']==['avonden'] and B['product_id']=='$DINER'"
S=$(post "{$VERBLIJF,\"t0\":$OUD,\"regels\":[{\"product_id\":\"$KRUIDENOLIE\",\"count\":4}]}")
check "count boven max -> 400" 400 "$S"
json_check "count boven max: fields [count]" "B['fields']==['count'] and B['ok'] is False"
S=$(post "{$VERBLIJF,\"t0\":$OUD,\"regels\":[{\"product_id\":\"$DINER\",\"count\":2,\"tijd\":\"zeven uur\"}]}")
check "ongeldige tijd -> 400" 400 "$S"
S=$(post "{$VERBLIJF,\"t0\":$OUD,\"regels\":[{\"product_id\":\"$FIETS\",\"avonden\":[\"2026-10-20\"]}]}")
check "dagen bij fiets (geen perdag) -> 400" 400 "$S"
S=$(post "{\"r\":\"$GUID\",\"a\":\"2026-10-20\",\"d\":\"2026-10-29\",\"p\":\"8\",\"t0\":$OUD,\"regels\":[{\"product_id\":\"$DINER\",\"count\":8}]}")
check "plafond € 2.500 (diner 8 pers. x 9 avonden) -> 400" 400 "$S"
json_check "plafond: melding met belnummer" "'0478 511 466' in B['message'] and B['fields']==['regels']"
S=$(post "{$VERBLIJF,\"t0\":$OUD,\"regels\":[{\"product_id\":\"00000000-0000-4000-8000-000000000000\"}]}")
check "onbekend product -> 400" 400 "$S"
S=$(post "{$VERBLIJF,\"t0\":$OUD,\"regels\":[]}")
check "geen regels -> 400" 400 "$S"
S=$(post "{\"r\":\"nope\",\"t0\":$OUD}")
check "ongeldige link -> 400" 400 "$S"
S=$(post "{$VERBLIJF,\"e\":\"geen-mail\",\"t0\":$OUD,\"regels\":[{\"product_id\":\"$KRUIDENOLIE\"}]}")
check "ongeldig e-mailadres -> 400" 400 "$S"
json_check "ongeldig e-mailadres: fields [e]" "B['fields']==['e']"
S=$(curl -s -o "$TMP/body" -w '%{http_code}' -X POST "$BASE/api/extras/bestel" -H 'Content-Type: application/json' -d 'geen json')
check "ongeldige JSON -> 400" 400 "$S"
log_mark
S=$(post "{$VERBLIJF,\"website\":\"ik ben een bot\",\"t0\":$OUD,\"regels\":[{\"product_id\":\"$KRUIDENOLIE\"}]}")
check "honeypot -> stil 200" 200 "$S"
log_check "honeypot: niets naar Zapier" "len(P)==0"
log_mark
S=$(post "{$VERBLIJF,\"t0\":$(( $(date +%s) * 1000 )),\"regels\":[{\"product_id\":\"$KRUIDENOLIE\"}]}")
check "t0 < 3 s -> stil 200" 200 "$S"
log_check "t0: niets naar Zapier" "len(P)==0"
S=$(curl -s -o "$TMP/body" -w '%{http_code}' "$BASE/api/extras/bestel")
check "GET bestel -> 405" 405 "$S"
S=$(curl -s -o "$TMP/body" -w '%{http_code}' -X POST "$BASE/api/extras/sessie" -d '{}')
check "POST sessie -> 405" 405 "$S"
S=$(curl -s -o "$TMP/body" -w '%{http_code}' -X OPTIONS "$BASE/api/extras/bestel")
check "OPTIONS bestel -> 204" 204 "$S"
S=$(curl -s -o "$TMP/body" -w '%{http_code}' "$BASE/api/extras/iets")
check "onbekend eindpunt -> 404" 404 "$S"

echo
echo "== 4. zonder dry-run en zonder ZAPIER_EXTRAS_HOOK (fallback) + nep-Resend (gastmail in MAIL_DRY_RUN)"
start_dev --binding EXTRAS_DRY_RUN=0 --binding RESEND_API_KEY=test-key
log_mark
S=$(post "{$VERBLIJF,\"e\":\"test@example.com\",\"t0\":$OUD,\"regels\":[{\"product_id\":\"$LATE\"}]}")
check "geen hook -> 200 met fallback" 200 "$S"
json_check "fallback true, mail_sent true (Resend-route)" "B['ok'] and B['fallback'] is True and B['mail_sent'] is True"
log_grep "receptiemail [HANDMATIG] via Resend" "MAIL_DRY_RUN (resend), niet verstuurd. to=info@asteria.nl subject=\[HANDMATIG\] Extra's besteld"
log_grep "gastmail met Asteria-onderwerp" "to=test@example.com subject=Je extra's voor Hotel Asteria staan genoteerd"
log_grep "hookfout gelogd" "geen ZAPIER_EXTRAS_HOOK ingesteld"

echo
echo "== resultaat: $PASS OK, $FAIL FOUT"
[ "$FAIL" = "0" ]
