# Mews Booking Widget Fix

**Goal:** Fix de Mews widget — `Mews.D(id, callback)` gebruikt callback als dataBaseUrl. Fix: `Mews.Distributor({configurationIds:[id]}, callback)`.

**Root cause bewijs:**
- `Mews.D(t, r)`: r = dataBaseUrl, geen callback
- Wrong URL: `/function(api){window.mewsApi=api...}/distributor/configuration`
- `Mews.Distributor({configurationIds:[id]}, callback)` werkt wél (getest via Playwright)

Tasks:
1. Fix wellness-arr-c.html (NL) — Mews.D → Mews.Distributor
2. Fix template — snippet + launchMews toevoegen, window.open vervangen
3. Rebuild (python3 build.py)
4. Push + deploy
5. Verify live
