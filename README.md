# Bubble Fury — Arcade Bubble Shooter

A free static website and SEO resource hub for **Bubble Fury** by **DevImpact**.

- Google Play: https://play.google.com/store/apps/details?id=com.game.bubblefury.devimpact
- Android application ID: com.game.bubblefury.devimpact
- Website: https://shelternewlife.github.io/bubblefury/

## Verified game scope

The website follows the official Google Play listing. Bubble Fury is an arcade bubble shooter: drag to aim and release to shoot, match at least three bubbles of the same color, build combo chains, use wall rebounds, collect coins, and adapt as the board becomes more crowded and additional bubble types appear. The listing identifies the game as containing ads.

The site does not promise multiplayer, ad-free play, unlimited levels, power-ups, or other features that are not confirmed by the store description.

## Published markets and languages

The primary markets are the United States and Canada. Europe is the secondary expansion region. The published locale routes are:

- English (United States): `/en-us/`
- English (Canada): `/en-ca/`
- French (Canada): `/fr-ca/`
- Spanish (Spain): `/es-es/`
- Portuguese (Portugal): `/pt-pt/`
- French (France): `/fr-fr/`
- German (Germany): `/de-de/`
- Italian (Italy): `/it-it/`

Each localized page has its own canonical URL, reciprocal hreflang links, localized metadata, navigation and country-flag selector.

## Site structure and SEO

The generated site includes About, Features, Download and FAQ pages, feature detail pages, plus localized Tips, Blog, User Guide and Gameplay resources. It publishes XML and text sitemaps, robots.txt, llms.txt, Open Graph metadata, SoftwareApplication and FAQPage JSON-LD, and GA4 Google Play click events.

Keyword seeds are based on the store-described bubble shooter gameplay. Search volume and ranking difficulty are not asserted; validate them by market in Google Keyword Planner and Google Search Console.

## Build and test

```bash
python -m unittest discover -s tests -v
python scripts/build.py
python scripts/validate.py
```

The generated website is written to `dist/` and is not committed. GitHub Actions runs the tests, builds the site, validates output and deploys GitHub Pages from `main`.

## Free-tier architecture and limitations

The project uses GitHub Pages, GitHub Actions, static JSON content and Python's standard library. It has no database, server-side API, user accounts, Firebase, Cloudflare or paid runtime dependency. Search engines decide independently when to crawl and index pages; publishing a sitemap does not guarantee indexing.

## Content maintenance

Edit `content/app.json`, `content/features.json`, `content/faq.json`, `content/locales.json`, `content/resource-locales.json`, `content/screenshots.json`, `content/seo-keywords.json` and `content/market-strategy.json`. Keep every claim aligned with the live Google Play listing.
