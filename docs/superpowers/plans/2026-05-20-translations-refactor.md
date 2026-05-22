# Translations Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Vervang de 3 aparte HTML-bestanden door één template + 3 JSON-bestanden zodat content-wijzigingen maar op één plek hoeven.

**Architecture:** `wellness-arr-c.template.html` bevat `{{key}}` markers op alle vertaalbare tekst. `build.py` vervangt alle markers met waarden uit `translations/{nl,en,de}.json` en schrijft 3 HTML-outputbestanden. Commit zowel template/JSON als gegenereerde HTML naar git — Cloudflare krijgt geen aparte build-stap.

**Tech Stack:** Python 3 (stdlib only: json, re, sys), vanilla HTML/JS

---

## Bestandsstructuur

```
translations/
  nl.json                        ← NL waarden voor alle ~120 keys
  en.json                        ← EN waarden voor alle ~120 keys
  de.json                        ← DE waarden voor alle ~120 keys
wellness-arr-c.template.html    ← bronbestand (afleiden van NL HTML)
build.py                         ← genereert 3 HTML-bestanden
wellness-arr-c.html             ← gegenereerd (NL, gecommit)
wellness-arr-c-en.html          ← gegenereerd (EN, gecommit)
wellness-arr-c-de.html          ← gegenereerd (DE, gecommit)
```

