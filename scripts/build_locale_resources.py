#!/usr/bin/env python3
"""Generate the localized Bubble Fury resource hubs for published locales."""
import html
import json
import pathlib
import xml.etree.ElementTree as ET

ROOT=pathlib.Path(__file__).resolve().parents[1]
DIST=ROOT/"dist"
APP=json.loads((ROOT/"content/app.json").read_text(encoding="utf-8"))
STRATEGY=json.loads((ROOT/"content/market-strategy.json").read_text(encoding="utf-8"))
CONTENT=json.loads((ROOT/"content/resource-locales.json").read_text(encoding="utf-8"))
LOCALES=json.loads((ROOT/"content/locales.json").read_text(encoding="utf-8"))
BASE=APP["website_url"].rstrip("/")
HUBS=("tips","blog","guide","comparison")
NS="http://www.sitemaps.org/schemas/sitemap/0.9"
XHTML="http://www.w3.org/1999/xhtml"
SHOTS=json.loads((ROOT/"content/screenshots.json").read_text(encoding="utf-8"))

FLAG_DATA={
 "en-US":("us","United States","United States · English"),
 "en-CA":("ca","Canada","Canada · English"),
 "fr-CA":("ca","Canada","Canada · Français"),
 "es-ES":("es","Spain","España · Español"),
 "pt-PT":("pt","Portugal","Portugal · Português"),
 "fr-FR":("fr","France","France · Français"),
 "de-DE":("de","Germany","Deutschland · Deutsch"),
 "it-IT":("it","Italy","Italia · Italiano")
}

def esc(value):
    return html.escape(str(value),quote=True)

def route(locale,tail=""):
    return f"{BASE}/{locale.lower()}/"+(f"{tail}/" if tail else "")

def render_page(locale,tail,data):
    title,description,heading,intro,cards=data
    links="".join(f'<article class="item"><h2><a href="{route(locale,target)}">{esc(label)}</a></h2><p>{esc(text)}</p></article>' for label,text,target in cards)
    locale_links=[]
    for code in STRATEGY["published_locales"]:
        country,country_name,label=FLAG_DATA[code]
        locale_links.append(f'<a class="locale-flag" lang="{code}" href="{route(code,tail)}" title="{esc(label)}" aria-label="{esc(label)}"><img src="https://flagcdn.com/w80/{country}.png" alt="{country_name} flag" width="40" height="30" loading="eager" decoding="async"></a>')
    labels=CONTENT[locale]["labels"]
    nav=CONTENT[locale]["nav"]
    text=LOCALES[locale]["text"]
    primary=[("about",text["about"]),("features",text["features"]),("download",text["download_nav"]),("faq",text["faq"])]
    primary_html="".join(f'<a data-nav-item="{key}" href="{route(locale,key)}">{esc(value)}</a>' for key,value in primary)
    resources="".join(f'<a data-nav-item="{key}" href="{route(locale,key)}">{esc(nav[key])}</a>' for key in HUBS)
    group1,group2={
      "en-US":("Explore","Resources"),"en-CA":("Explore","Resources"),
      "fr-CA":("Explorer","Ressources"),"es-ES":("Explorar","Recursos"),
      "pt-PT":("Explorar","Recursos"),"fr-FR":("Explorer","Ressources"),
      "de-DE":("Entdecken","Ressourcen"),"it-IT":("Esplora","Risorse")
    }[locale]
    url=route(locale,tail)
    alternates="".join(f'<link rel="alternate" hreflang="{code}" href="{route(code,tail)}">' for code in STRATEGY["published_locales"])
    alternates+=f'<link rel="alternate" hreflang="x-default" href="{route("en-US",tail)}">'
    organization={"@type":"Organization","@id":f"{BASE}/#organization","name":APP["developer"],"url":BASE+"/"}
    schema={"@context":"https://schema.org","@graph":[organization,{"@type":"CollectionPage","name":title,"description":description,"inLanguage":locale,"url":url,"publisher":{"@id":f"{BASE}/#organization"}}]}
    content=f'<section class="section resource-hub"><div class="tag">BUBBLE FURY · {esc(labels["resource"])}</div><h1>{esc(heading)}</h1><p class="lead">{esc(intro)}</p><div class="grid">{links}</div></section>'
    return f'''<!doctype html><html lang="{locale}" dir="ltr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)}</title><meta name="description" content="{esc(description)}"><meta name="robots" content="index,follow,max-image-preview:large"><link rel="canonical" href="{url}">{alternates}<meta property="og:locale" content="{locale.replace("-","_")}"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{esc(SHOTS[0]["src"])}"><link rel="stylesheet" href="{BASE}/assets/style.css"><script type="application/ld+json">{json.dumps(schema,ensure_ascii=False)}</script></head><body><header class="standard-header"><div class="header-main"><div class="locale-switch" aria-label="Country and region">{"".join(locale_links)}</div><a class="brand" href="{BASE}/">BUBBLE <b>FURY</b></a><nav aria-label="{esc(labels["nav_aria"])}"><details class="nav-menu" data-nav-group="primary"><summary>{esc(group1)}</summary><div class="nav-dropdown">{primary_html}</div></details><details class="nav-menu" data-nav-group="resources"><summary>{esc(group2)}</summary><div class="nav-dropdown">{resources}</div></details></nav></div></header><main id="main-content">{content}</main><footer>© DevImpact · BUBBLE FURY · <a href="{esc(APP["privacy_policy_url"])}">{esc(labels["privacy"])}</a> · <a href="mailto:{esc(APP["support_email"])}">{esc(labels["support"])}</a></footer></body></html>'''

def build_localized_resource_pages():
    published=STRATEGY.get("published_locales",[])
    if set(published)!=set(CONTENT):
        raise ValueError("Bubble Fury resource translations must cover every published locale")
    for locale in published:
        for tail in HUBS:
            target=DIST/locale.lower()/tail/"index.html"
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_text(render_page(locale,tail,CONTENT[locale]["pages"][tail]),encoding="utf-8")
    xml_path=DIST/"sitemap.xml"
    tree=ET.parse(xml_path);root=tree.getroot()
    ET.register_namespace("",NS);ET.register_namespace("xhtml",XHTML)
    existing={node.findtext(f"{{{NS}}}loc") for node in root.findall(f"{{{NS}}}url")}
    for locale in published:
        for tail in HUBS:
            loc=route(locale,tail)
            if loc in existing:continue
            node=ET.SubElement(root,f"{{{NS}}}url")
            ET.SubElement(node,f"{{{NS}}}loc").text=loc
            for code in published:
                ET.SubElement(node,f"{{{XHTML}}}link",{"rel":"alternate","hreflang":code,"href":route(code,tail)})
            ET.SubElement(node,f"{{{XHTML}}}link",{"rel":"alternate","hreflang":"x-default","href":route("en-US",tail)})
    tree.write(xml_path,encoding="utf-8",xml_declaration=True)
    txt=DIST/"sitemap.txt"
    urls=[x.strip() for x in txt.read_text(encoding="utf-8").splitlines() if x.strip()]
    for locale in published:
        for tail in HUBS:
            loc=route(locale,tail)
            if loc not in urls:urls.append(loc)
    txt.write_text("\n".join(urls)+"\n",encoding="utf-8")

if __name__=="__main__":
    build_localized_resource_pages()
