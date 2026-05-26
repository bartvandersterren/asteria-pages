# Weer–Verkoop Correlatie Analyse — Implementatieplan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Eenmalig onderzoeken of weersomstandigheden (temperatuur, neerslag, zonneschijn) correleren met de dagelijkse gross profit van Scentech over de afgelopen 12 maanden.

**Architecture:** Python-script dat Shopify Admin GraphQL aanroept voor orders + Open-Meteo Historical API voor weerdata (De Bilt, gratis, geen API key). Data wordt samengevoegd per dag, geanalyseerd via pandas/scipy, en weggeschreven naar een zelfstandig HTML-rapport met Plotly-charts.

**Tech Stack:** Python 3, requests, pandas, scipy, plotly (standalone HTML output), Shopify Admin GraphQL API, Open-Meteo Archive API

---

## Bestandsstructuur

```
scentech-weather-analyse/
├── analyse.py          # Alles in één script (fetch + merge + analyse + rapport)
├── requirements.txt    # requests, pandas, scipy, plotly
└── rapport.html        # Output — gegenereerd door script
```

---

### Task 1: Project opzetten

**Files:**
- Create: `scentech-weather-analyse/requirements.txt`
- Create: `scentech-weather-analyse/analyse.py` (skeleton)

- [ ] **Stap 1: Map aanmaken en requirements schrijven**

```bash
mkdir scentech-weather-analyse
```

Schrijf `scentech-weather-analyse/requirements.txt`:
```
requests==2.31.0
pandas==2.2.2
scipy==1.13.0
plotly==5.22.0
```

- [ ] **Stap 2: Dependencies installeren**

```bash
cd scentech-weather-analyse && pip install -r requirements.txt
```

Verwacht: `Successfully installed ...` zonder errors.

- [ ] **Stap 3: Skeleton van analyse.py schrijven**

```python
"""
Scentech — Weer vs. Gross Profit analyse
Periode: afgelopen 365 dagen
Weerlocatie: De Bilt (KNMI referentiestation, lat=52.1093, lon=5.1810)
"""

import os
import requests
import pandas as pd
from datetime import date, timedelta
from scipy import stats
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# ── Configuratie ────────────────────────────────────────────────────────────
SHOPIFY_STORE = "d80787-b7.myshopify.com"
SHOPIFY_TOKEN = os.environ["SHOPIFY_ADMIN_TOKEN"]   # export vóór draaien
WEATHER_LAT   = 52.1093
WEATHER_LON   = 5.1810
PERIOD_DAYS   = 365

END_DATE   = date.today()
START_DATE = END_DATE - timedelta(days=PERIOD_DAYS)
# ────────────────────────────────────────────────────────────────────────────


if __name__ == "__main__":
    print("Stap 1: Shopify orders ophalen...")
    print("Stap 2: Weerdata ophalen...")
    print("Stap 3: Data samenvoegen en correlaties berekenen...")
    print("Stap 4: Rapport genereren → rapport.html")
```

- [ ] **Stap 4: Controleer dat script zonder errors start**

```bash
export SHOPIFY_ADMIN_TOKEN="placeholder"
cd scentech-weather-analyse && python analyse.py
```

Verwacht:
```
Stap 1: Shopify orders ophalen...
Stap 2: Weerdata ophalen...
...
```

- [ ] **Stap 5: Commit**

```bash
cd scentech-weather-analyse
git init
git add requirements.txt analyse.py
git commit -m "feat: project skeleton voor weer-verkoop analyse"
```

---

### Task 2: Shopify orders ophalen

**Files:**
- Modify: `scentech-weather-analyse/analyse.py` — voeg `fetch_shopify_orders()` toe

Shopify Admin GraphQL endpoint: `https://d80787-b7.myshopify.com/admin/api/2024-01/graphql.json`

Gross profit per order = som van (verkoopprijs − inkoopprijs) × aantal per line item.
Inkoopprijs staat op `variant.inventoryItem.unitCost.amount`. Als die `null` is, wordt `0` gebruikt (dan is het effectief omzet).

- [ ] **Stap 1: GraphQL query definiëren**

Voeg toe boven `if __name__ == "__main__":`:

```python
ORDERS_QUERY = """
query getOrders($cursor: String, $query: String!) {
  orders(first: 250, after: $cursor, query: $query) {
    pageInfo {
      hasNextPage
      endCursor
    }
    edges {
      node {
        id
        createdAt
        lineItems(first: 100) {
          edges {
            node {
              quantity
              originalUnitPriceSet {
                shopMoney { amount }
              }
              variant {
                inventoryItem {
                  unitCost { amount }
                }
              }
            }
          }
        }
      }
    }
  }
}
"""
```

- [ ] **Stap 2: `fetch_shopify_orders()` implementeren met paginatie**

```python
def fetch_shopify_orders() -> pd.DataFrame:
    """
    Haalt alle betaalde orders op voor de gedefinieerde periode.
    Retourneert DataFrame met kolommen: date (date), gross_profit (float).
    """
    url = f"https://{SHOPIFY_STORE}/admin/api/2024-01/graphql.json"
    headers = {
        "X-Shopify-Access-Token": SHOPIFY_TOKEN,
        "Content-Type": "application/json",
    }
    date_filter = (
        f"created_at:>={START_DATE.isoformat()} "
        f"created_at:<={END_DATE.isoformat()} "
        f"financial_status:paid"
    )

    rows = []
    cursor = None
    page = 0

    while True:
        page += 1
        variables = {"query": date_filter, "cursor": cursor}

        for attempt in range(3):
            resp = requests.post(
                url,
                headers=headers,
                json={"query": ORDERS_QUERY, "variables": variables},
            )
            if resp.status_code == 429:
                import time; time.sleep(2)
                continue
            break
        resp.raise_for_status()
        data = resp.json()

        if "errors" in data:
            raise RuntimeError(f"Shopify GraphQL errors: {data['errors']}")

        orders_data = data["data"]["orders"]
        edges = orders_data["edges"]
        print(f"  Pagina {page}: {len(edges)} orders")

        for edge in edges:
            order = edge["node"]
            order_date = date.fromisoformat(order["createdAt"][:10])
            gp = 0.0
            for li_edge in order["lineItems"]["edges"]:
                li = li_edge["node"]
                qty = li["quantity"]
                revenue = float(li["originalUnitPriceSet"]["shopMoney"]["amount"])
                cost_node = (li.get("variant") or {}).get("inventoryItem") or {}
                cost_amount = cost_node.get("unitCost") or {}
                cost = float(cost_amount.get("amount", 0) or 0)
                gp += (revenue - cost) * qty
            rows.append({"date": order_date, "gross_profit": gp})

        if not orders_data["pageInfo"]["hasNextPage"]:
            break
        cursor = orders_data["pageInfo"]["endCursor"]

    df = pd.DataFrame(rows)
    if df.empty:
        raise RuntimeError("Geen orders gevonden voor deze periode.")

    daily = df.groupby("date")["gross_profit"].sum().reset_index()
    daily = daily.sort_values("date").reset_index(drop=True)
    print(f"  Totaal: {len(df)} orders over {len(daily)} dagen")
    print("  Let op: als gross_profit gelijk is aan omzet, zijn kostprijzen niet ingevuld in Shopify.")
    return daily
```

- [ ] **Stap 3: Aanroepen in `main`**

Vervang de print-regel voor stap 1 door:

```python
    print("Stap 1: Shopify orders ophalen...")
    orders_df = fetch_shopify_orders()
    print(orders_df.head())
```

- [ ] **Stap 4: API token instellen en testen**

Token aanmaken: Shopify admin > Apps > App and sales channel settings > Develop apps > Create an app > Configure Admin API scopes: vink `read_orders` aan > Install app > kopieer de access token (begint met `shpat_`).

```bash
export SHOPIFY_ADMIN_TOKEN="shpat_xxxxxxxxxxxx"
python analyse.py
```

Verwachte output:
```
Stap 1: Shopify orders ophalen...
  Pagina 1: 250 orders
  Pagina 2: 187 orders
  Totaal: 437 orders over 203 dagen
         date  gross_profit
0  2025-05-26        342.50
...
```

- [ ] **Stap 5: Commit**

```bash
git add analyse.py
git commit -m "feat: shopify orders fetch met gross profit berekening"
```

---

### Task 3: Weerdata ophalen via Open-Meteo

**Files:**
- Modify: `scentech-weather-analyse/analyse.py` — voeg `fetch_weather()` toe

Open-Meteo Archive API, geen key nodig: `https://archive-api.open-meteo.com/v1/archive`

Variabelen:
- `temperature_2m_mean` — gemiddelde dagtemperatuur (°C)
- `precipitation_sum` — totale neerslag (mm)
- `sunshine_duration` — zonneschijnduur (seconden, omzetten naar uren)

- [ ] **Stap 1: `fetch_weather()` implementeren**

```python
def fetch_weather() -> pd.DataFrame:
    """
    Haalt dagelijkse weerdata op voor De Bilt via Open-Meteo Archive API.
    Retourneert DataFrame met kolommen:
      date (date), temp_mean (float), precipitation_mm (float), sunshine_hours (float)
    """
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": WEATHER_LAT,
        "longitude": WEATHER_LON,
        "start_date": START_DATE.isoformat(),
        "end_date": END_DATE.isoformat(),
        "daily": "temperature_2m_mean,precipitation_sum,sunshine_duration",
        "timezone": "Europe/Amsterdam",
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()

    daily = data["daily"]
    df = pd.DataFrame({
        "date": pd.to_datetime(daily["time"]).dt.date,
        "temp_mean": daily["temperature_2m_mean"],
        "precipitation_mm": daily["precipitation_sum"],
        "sunshine_hours": [s / 3600 if s is not None else None
                           for s in daily["sunshine_duration"]],
    })
    print(f"  Weerdata: {len(df)} dagen, {df['temp_mean'].min():.1f}–{df['temp_mean'].max():.1f}°C")
    return df
```

- [ ] **Stap 2: Aanroepen in `main`**

```python
    print("Stap 2: Weerdata ophalen...")
    weather_df = fetch_weather()
    print(weather_df.head())
```

- [ ] **Stap 3: Test**

```bash
python analyse.py
```

Verwachte output:
```
Stap 2: Weerdata ophalen...
  Weerdata: 365 dagen, -3.2–29.1°C
         date  temp_mean  precipitation_mm  sunshine_hours
0  2025-05-26       14.2               0.0            8.32
...
```

- [ ] **Stap 4: Commit**

```bash
git add analyse.py
git commit -m "feat: weer fetch via open-meteo (de bilt)"
```

---

### Task 4: Data samenvoegen en correlaties berekenen

**Files:**
- Modify: `scentech-weather-analyse/analyse.py` — voeg `merge_and_analyse()` toe

Correlatiemethode: Pearson r (lineair) + Spearman rho (niet-lineair / outlier-robuust).
Alleen dagen met minstens één order tellen mee (inner join).

- [ ] **Stap 1: `merge_and_analyse()` implementeren**

```python
def merge_and_analyse(orders_df: pd.DataFrame, weather_df: pd.DataFrame) -> dict:
    """
    Samenvoegen en correlaties berekenen.
    Retourneert dict met keys 'df' (merged DataFrame) en 'correlations' (dict per variabele).
    """
    df = pd.merge(orders_df, weather_df, on="date", how="inner")
    df["weekday"] = pd.to_datetime(df["date"]).dt.dayofweek  # 0=ma, 6=zo
    df["month"] = pd.to_datetime(df["date"]).dt.month

    weather_vars = ["temp_mean", "precipitation_mm", "sunshine_hours"]
    results = {}

    for var in weather_vars:
        sub = df[["gross_profit", var]].dropna()
        pearson_r, pearson_p = stats.pearsonr(sub[var], sub["gross_profit"])
        spearman_r, spearman_p = stats.spearmanr(sub[var], sub["gross_profit"])
        significant = pearson_p < 0.05 or spearman_p < 0.05
        results[var] = {
            "pearson_r": round(pearson_r, 3),
            "pearson_p": round(pearson_p, 4),
            "spearman_r": round(spearman_r, 3),
            "spearman_p": round(spearman_p, 4),
            "n": len(sub),
            "significant": significant,
        }
        sig = "✓ significant" if significant else "✗ niet significant"
        print(f"  {var:25s} Pearson r={pearson_r:+.3f} (p={pearson_p:.4f})  {sig}")

    return {"df": df, "correlations": results}
```

- [ ] **Stap 2: Aanroepen in `main`**

```python
    print("Stap 3: Data samenvoegen en correlaties berekenen...")
    analysis = merge_and_analyse(orders_df, weather_df)
    df = analysis["df"]
    correlations = analysis["correlations"]
    print(f"  Overlap: {len(df)} dagen")
```

- [ ] **Stap 3: Test**

```bash
python analyse.py
```

Verwacht (getallen variëren):
```
Stap 3: Data samenvoegen en correlaties berekenen...
  temp_mean                 Pearson r=+0.112 (p=0.1234)  ✗ niet significant
  precipitation_mm          Pearson r=-0.089 (p=0.2341)  ✗ niet significant
  sunshine_hours            Pearson r=+0.203 (p=0.0312)  ✓ significant
  Overlap: 198 dagen
```

- [ ] **Stap 4: Commit**

```bash
git add analyse.py
git commit -m "feat: correlatie berekening (pearson + spearman)"
```

---

### Task 5: HTML-rapport genereren

**Files:**
- Modify: `scentech-weather-analyse/analyse.py` — voeg `generate_report()` toe
- Create: `scentech-weather-analyse/rapport.html` (output van script)

Het rapport bevat:
1. Samenvatting-tabel met correlaties per weervariabele
2. Tijdlijnplot: dagelijkse gross profit + temperatuur op dubbele y-as
3. Scatterplot: gross profit vs. temperatuur (punten gekleurd per seizoen)
4. Scatterplot: gross profit vs. neerslag
5. Scatterplot: gross profit vs. zonneschijn

- [ ] **Stap 1: `generate_report()` implementeren**

```python
def generate_report(df: pd.DataFrame, correlations: dict) -> None:
    """Genereert rapport.html met interactieve Plotly-charts."""

    season_map = {12: "Winter", 1: "Winter", 2: "Winter",
                  3: "Lente",  4: "Lente",  5: "Lente",
                  6: "Zomer",  7: "Zomer",  8: "Zomer",
                  9: "Herfst", 10: "Herfst", 11: "Herfst"}
    df = df.copy()
    df["seizoen"] = df["month"].map(season_map)

    season_colors = {"Lente": "#4CAF50", "Zomer": "#FF9800",
                     "Herfst": "#795548", "Winter": "#2196F3"}

    figs_html = []

    # ── Tijdlijn: gross profit + temperatuur ────────────────────────────
    fig1 = make_subplots(specs=[[{"secondary_y": True}]])
    fig1.add_trace(
        go.Scatter(x=df["date"], y=df["gross_profit"],
                   name="Gross Profit (EUR)", line=dict(color="#1976D2", width=1.5)),
        secondary_y=False,
    )
    fig1.add_trace(
        go.Scatter(x=df["date"], y=df["temp_mean"],
                   name="Temperatuur (C)", line=dict(color="#F44336", width=1.5, dash="dot")),
        secondary_y=True,
    )
    fig1.update_layout(title="Gross Profit & Temperatuur over tijd",
                       height=400, template="plotly_white")
    fig1.update_yaxes(title_text="Gross Profit (EUR)", secondary_y=False)
    fig1.update_yaxes(title_text="Temperatuur (C)", secondary_y=True)
    figs_html.append(fig1.to_html(full_html=False, include_plotlyjs=False))

    # ── Scatterplots per weervariabele ──────────────────────────────────
    scatter_config = [
        ("temp_mean",        "Gemiddelde temperatuur (C)",  "Gross Profit vs. Temperatuur"),
        ("precipitation_mm", "Neerslag (mm)",                "Gross Profit vs. Neerslag"),
        ("sunshine_hours",   "Zonneschijn (uur)",            "Gross Profit vs. Zonneschijn"),
    ]

    for var, xlabel, title in scatter_config:
        sub = df.dropna(subset=[var, "gross_profit"])
        corr = correlations[var]
        sig_label = "significant" if corr["significant"] else "niet significant"
        subtitle = (
            f"Pearson r={corr['pearson_r']:+.3f} (p={corr['pearson_p']:.4f}) | "
            f"Spearman rho={corr['spearman_r']:+.3f} (p={corr['spearman_p']:.4f}) | "
            f"n={corr['n']} — {sig_label}"
        )
        fig = px.scatter(
            sub, x=var, y="gross_profit",
            color="seizoen", color_discrete_map=season_colors,
            hover_data=["date"],
            labels={var: xlabel, "gross_profit": "Gross Profit (EUR)", "seizoen": "Seizoen"},
            title=f"{title}<br><sup>{subtitle}</sup>",
            template="plotly_white",
            height=420,
        )
        m, b, *_ = stats.linregress(sub[var], sub["gross_profit"])
        x_range = [sub[var].min(), sub[var].max()]
        fig.add_trace(go.Scatter(
            x=x_range, y=[m * x + b for x in x_range],
            mode="lines", line=dict(color="black", dash="dash", width=1),
            name="Trendlijn",
        ))
        figs_html.append(fig.to_html(full_html=False, include_plotlyjs=False))

    # ── Samenvatting tabel ────────────────────────────────────────────────
    var_labels = {
        "temp_mean":        "Gemiddelde temperatuur",
        "precipitation_mm": "Neerslag",
        "sunshine_hours":   "Zonneschijn",
    }
    table_rows = ""
    for var, label in var_labels.items():
        c = correlations[var]
        sig_badge = ('<span style="color:green;font-weight:bold">ja</span>'
                     if c["significant"]
                     else '<span style="color:#999">nee</span>')
        table_rows += (
            f"<tr><td>{label}</td>"
            f"<td>{c['pearson_r']:+.3f}</td><td>{c['pearson_p']:.4f}</td>"
            f"<td>{c['spearman_r']:+.3f}</td><td>{c['spearman_p']:.4f}</td>"
            f"<td>{c['n']}</td><td>{sig_badge}</td></tr>"
        )

    html = f"""<!DOCTYPE html>
<html lang="nl">
<head>
  <meta charset="utf-8">
  <title>Scentech — Weer vs. Verkoop</title>
  <script src="https://cdn.plot.ly/plotly-2.32.0.min.js"></script>
  <style>
    body {{ font-family: system-ui, sans-serif; max-width: 1200px; margin: 0 auto; padding: 24px; background: #f9f9f9; }}
    h1 {{ color: #1a1a1a; }}
    .meta {{ color: #666; font-size: 14px; margin-bottom: 32px; }}
    table {{ border-collapse: collapse; width: 100%; margin-bottom: 40px; background: white;
             border-radius: 8px; overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,.1); }}
    th {{ background: #1976D2; color: white; padding: 10px 14px; text-align: left; font-size: 14px; }}
    td {{ padding: 9px 14px; border-bottom: 1px solid #eee; font-size: 14px; }}
    tr:last-child td {{ border-bottom: none; }}
    .chart {{ background: white; border-radius: 8px; box-shadow: 0 1px 4px rgba(0,0,0,.1);
              margin-bottom: 24px; padding: 8px; }}
    .note {{ background: #fff8e1; border-left: 4px solid #FFC107; padding: 12px 16px;
             border-radius: 4px; font-size: 13px; margin-bottom: 32px; }}
  </style>
</head>
<body>
  <h1>Scentech — Weer vs. Gross Profit</h1>
  <p class="meta">
    Periode: {START_DATE.isoformat()} t/m {END_DATE.isoformat()} &nbsp;|&nbsp;
    Weerlocatie: De Bilt (KNMI referentiestation) &nbsp;|&nbsp;
    Gegenereerd: {date.today().isoformat()}
  </p>
  <div class="note">
    <strong>Interpretatie:</strong> r &gt; 0.3 of r &lt; -0.3 wijst op een matig verband.
    p &lt; 0.05 = statistisch significant (5% kans op toeval). Correlatie is geen causaliteit.
  </div>
  <h2>Samenvatting correlaties</h2>
  <table>
    <thead>
      <tr>
        <th>Weervariabele</th><th>Pearson r</th><th>Pearson p</th>
        <th>Spearman rho</th><th>Spearman p</th><th>n (dagen)</th><th>Significant?</th>
      </tr>
    </thead>
    <tbody>{table_rows}</tbody>
  </table>
  {"".join(f'<div class="chart">{f}</div>' for f in figs_html)}
</body>
</html>"""

    with open("rapport.html", "w", encoding="utf-8") as fh:
        fh.write(html)
    print("  rapport.html geschreven")
```

- [ ] **Stap 2: Aanroepen in `main`**

```python
    print("Stap 4: Rapport genereren → rapport.html")
    generate_report(df, correlations)
    print("Klaar. Open rapport.html in je browser.")
```

- [ ] **Stap 3: Volledig draaien**

```bash
python analyse.py && open rapport.html
```

Verwacht: browser opent rapport met tijdlijn + 3 scatterplots en samenvatting-tabel.

- [ ] **Stap 4: Final commit**

```bash
git add analyse.py
git commit -m "feat: html rapport met plotly charts en correlatie tabel"
```

---

## Shopify Admin Token aanmaken

1. Shopify admin > **Apps** > App and sales channel settings
2. Klik **Develop apps** > Create an app (naam: "Weer analyse")
3. Configure Admin API scopes: vink `read_orders` aan
4. Install app > kopieer de access token (begint met `shpat_`)
5. `export SHOPIFY_ADMIN_TOKEN="shpat_..."`

---

## Na de analyse — interpretatie

| Bevinding | Implicatie |
|-----------|-----------|
| Positieve correlatie met temperatuur | Meer verkopen bij warm weer — campagnes in zomer ophogen |
| Negatieve correlatie met neerslag | Slechte weerdagen = minder verkoop — niet ads uitdunnen op regenachtige periodes |
| Geen significante correlatie | Weer speelt geen rol — budget constant houden |
| Sterke seizoenseffecten zichtbaar in scatterplots | Maandelijkse patronen domineren — overweeg seizoens-bid-adjustments |
