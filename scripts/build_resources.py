#!/usr/bin/env python3
"""Create the base English and Arabic Bubble Fury resource routes."""
import html
import json
import pathlib
import xml.etree.ElementTree as ET

ROOT=pathlib.Path(__file__).resolve().parents[1]
DIST=ROOT/"dist"
APP=json.loads((ROOT/"content/app.json").read_text(encoding="utf-8"))
FEATURES=json.loads((ROOT/"content/features.json").read_text(encoding="utf-8"))
BASE=APP["website_url"].rstrip("/")
NS="http://www.sitemaps.org/schemas/sitemap/0.9"
XHTML="http://www.w3.org/1999/xhtml"
DATA=[
 ("bubble-shooter-basics","How to Play Bubble Fury: Aim, Shoot and Pop","كيف تلعب Bubble Fury: صوّب وأطلق وفقّع"),
 ("match-three-strategy","Match Three or More Bubbles: Plan Your Shots","طابق ثلاث فقاعات أو أكثر: خطط لطلقاتك"),
 ("combos-and-high-scores","Build Bubble Fury Combos and Chase High Scores","اصنع سلاسل الكومبو واطارد النتائج العالية")
]
GUIDES={"tips":None,"guide":None,"comparison":None}

def esc(value):
    return html.escape(str(value),quote=True)

def route_url(lang,tail=""):
    return f'{BASE}/{lang}/'+(f'{tail}/' if tail else "")

def routes():
    tails=["","about","features","download","faq","blog"]
    tails += ["features/"+f["id"] for f in FEATURES]
    tails += ["blog/"+article[0] for article in DATA]
    tails += list(GUIDES)
    return [(lang,tail) for lang in ("en","ar") for tail in tails]

def build_extra_pages():
    (DIST/"assets").mkdir(parents=True,exist_ok=True)
    css=DIST/"assets/style.css"
    if css.exists():
        css.write_text(css.read_text(encoding="utf-8")+"\n.article{max-width:850px;margin:auto}.article-section{padding:18px 0;border-bottom:1px solid #ffffff18}.guide-list{display:grid;gap:18px;margin-top:28px}.guide-step{padding:22px;background:#111925;border:1px solid #283449;border-radius:16px}.guide-shot{margin:18px 0;padding:12px;background:#080b12;border-radius:12px}.guide-shot img{display:block;width:100%;height:auto;object-fit:contain}.resource-hub{max-width:1000px}.resource-hub .grid{margin-top:28px}\n.nav-menu{position:relative}.nav-menu>summary{list-style:none;cursor:pointer;display:flex;align-items:center;min-height:44px;padding:8px 13px;border:1px solid #34445c;border-radius:9px;background:#111925;color:#e5edf7;font-weight:700;white-space:nowrap}.nav-menu>summary::-webkit-details-marker{display:none}.nav-menu>summary::after{content:'▾';margin-inline-start:9px;color:#00c4df}.nav-menu>summary:focus-visible{outline:3px solid #00c4df;outline-offset:3px}.nav-menu[open]>summary{border-color:#00c4df}.nav-dropdown{position:absolute;top:calc(100% + 8px);inset-inline-start:0;z-index:60;display:grid;gap:3px;width:min(260px,calc(100vw - 36px));padding:8px;background:#111925;border:1px solid #34445c;border-radius:12px;box-shadow:0 16px 36px #0009}.nav-dropdown a{display:flex;align-items:center;min-height:42px;padding:8px 12px;border-radius:8px;color:#dce5f2;text-decoration:none}.nav-dropdown a:hover,.nav-dropdown a:focus-visible{background:#1c2b3e;color:#fff}.nav-dropdown a:focus-visible{outline:2px solid #00c4df;outline-offset:1px}\n",encoding="utf-8")
    for lang,tail in routes():
        if tail in ("","about","features","download","faq"):
            continue
        title="Bubble Fury" if not tail else "Bubble Fury | "+tail.replace("/"," ").replace("-"," ").title()
        url=route_url(lang,tail)
        organization={"@type":"Organization","@id":f"{BASE}/#organization","name":APP["developer"],"url":BASE+"/"}
        node={"@type":"WebPage","name":title,"url":url,"inLanguage":lang,"publisher":{"@id":f"{BASE}/#organization"}}
        schema={"@context":"https://schema.org","@graph":[organization,node]}
        canonical=f'<link rel="canonical" href="{url}">'
        alternates=f'<link rel="alternate" hreflang="en" href="{route_url("en",tail)}"><link rel="alternate" hreflang="ar" href="{route_url("ar",tail)}"><link rel="alternate" hreflang="x-default" href="{route_url("en",tail)}">'
        content=f'<section class="section"><h1>{esc(title)}</h1><p>{esc(APP["description"].get(lang,APP["description"]["en"]))}</p><a class="btn" href="{esc(APP["google_play_url"])}">Google Play</a></section>'
        page=f'<!doctype html><html lang="{lang}" dir="{"rtl" if lang=="ar" else "ltr"}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)}</title><meta name="description" content="{esc(APP["description"].get(lang,APP["description"]["en"]))}">{canonical}{alternates}<script type="application/ld+json">{json.dumps(schema,ensure_ascii=False)}</script><link rel="stylesheet" href="{BASE}/assets/style.css"></head><body><main>{content}</main></body></html>'
        target=DIST/lang/(tail or "")/"index.html"
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(page,encoding="utf-8")
    entries=[(route_url(lang,tail),lang,tail) for lang,tail in routes()]
    xml='<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">'
    for url,lang,tail in entries:
        xml+=f'<url><loc>{esc(url)}</loc><xhtml:link rel="alternate" hreflang="en" href="{esc(route_url("en",tail))}"/><xhtml:link rel="alternate" hreflang="ar" href="{esc(route_url("ar",tail))}"/><xhtml:link rel="alternate" hreflang="x-default" href="{esc(route_url("en",tail))}"/></url>'
    (DIST/"sitemap.xml").write_text(xml+"</urlset>",encoding="utf-8")
    (DIST/"sitemap.txt").write_text("\n".join(url for url,_,_ in entries)+"\n",encoding="utf-8")
    (DIST/"llms.txt").write_text(f"# {APP['name']}\n\n{APP['description']['en']}\n\n- Google Play: {APP['google_play_url']}\n- Website: {BASE}/\n",encoding="utf-8")

if __name__=="__main__":
    build_extra_pages()
