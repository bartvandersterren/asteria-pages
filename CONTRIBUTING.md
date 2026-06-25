# Bijdragen aan Asteria Pages

## Eerste keer opzetten

```bash
git clone https://github.com/bartvandersterren/asteria-pages.git
cd asteria-pages
```

## Werkwijze

`main` is beschermd — je kunt er niet direct naar pushen. Alle wijzigingen gaan via een Pull Request.

### Stappen

1. **Start vanaf up-to-date main:**
   ```bash
   git checkout main && git pull
   ```

2. **Maak een feature branch:**
   ```bash
   git checkout -b feature/beschrijving-van-je-wijziging
   ```

3. **Maak je wijzigingen en commit:**
   ```bash
   git add <bestanden>
   git commit -m "Korte beschrijving van wat je deed"
   ```

4. **Push en maak een PR:**
   ```bash
   git push -u origin feature/beschrijving-van-je-wijziging
   ```
   Ga daarna naar https://github.com/bartvandersterren/asteria-pages en maak een Pull Request aan.

5. **Na merge** deployt Cloudflare automatisch naar visit.asteria.nl.

## Translations

Als je teksten wijzigt in de wellness- of feedbackpagina's:

```bash
# Pas de juiste JSON aan in translations/
# Bouw de HTML's opnieuw:
python3 build.py

# Commit zowel de JSON als de gegenereerde HTML's
```

## Belangrijk

- Lees `CLAUDE.md` voor alle technische context en conventies
- Lees `docs/` voor kennisdocumenten (tone of voice, CRO, design)
- Foto's staan in `fotos/` (WebP, quality=72)
- Test je pagina lokaal voor je pusht (open het HTML-bestand in je browser)
