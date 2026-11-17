#!/usr/bin/env python3
"""Replace template career content with Bubble Fury game-specific pages."""
import html
import json
import pathlib
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
APP = json.loads((ROOT / "content/app.json").read_text(encoding="utf-8"))
FEATURES = json.loads((ROOT / "content/features.json").read_text(encoding="utf-8"))
SHOTS = json.loads((ROOT / "content/screenshots.json").read_text(encoding="utf-8"))
LOCALES = json.loads((ROOT / "content/locales.json").read_text(encoding="utf-8"))
RESOURCE = json.loads((ROOT / "content/resource-locales.json").read_text(encoding="utf-8"))
STRATEGY = json.loads((ROOT / "content/market-strategy.json").read_text(encoding="utf-8"))
BASE = APP["website_url"].rstrip("/")
PLAY = APP["google_play_url"]
PUBLISHED = STRATEGY["published_locales"]
ARTICLES = {
 "bubble-shooter-basics": {
  "en": ("How to Play Bubble Fury: Aim, Shoot and Pop", "Learn the basic Bubble Fury controls and the simple loop behind each arcade run.", [
   ("Drag to aim", "Move your aim carefully to line up a shot with bubbles of the same color."),
   ("Release to shoot", "Release your aim to launch the bubble. Each shot changes the space and options on the board."),
   ("Match three or more", "Connect at least three bubbles of the same color to pop them and clear room for the next shot.")]),
  "ar": ("كيف تلعب Bubble Fury: صوّب وأطلق وفقّع", "تعرّف على أدوات التحكم الأساسية وطريقة اللعب في جولات Bubble Fury السريعة.", [
   ("اسحب للتصويب", "حرّك اتجاه التصويب بعناية لمحاذاة الطلقة مع فقاعات من اللون نفسه."),
   ("اترك للإطلاق", "اترك التصويب لإطلاق الفقاعة. تغيّر كل طلقة المساحة والخيارات المتاحة على اللوحة."),
   ("طابق ثلاث فقاعات أو أكثر", "اجمع ثلاث فقاعات على الأقل من اللون نفسه لتفجيرها وإخلاء مساحة للطلقة التالية.")])},
 "match-three-strategy": {
  "en": ("Match Three or More Bubbles: Plan Your Shots", "Use color matching and careful positioning to make more of each Bubble Fury shot.", [
   ("Look for matching groups", "Before shooting, scan the board for groups that already contain the same color."),
   ("Think about the angle", "A direct shot is not the only option. The game description highlights wall rebounds for reaching difficult angles."),
   ("Make space deliberately", "Matching three or more bubbles clears space. As the board becomes more crowded, shot selection matters even more.")]),
  "ar": ("طابق ثلاث فقاعات أو أكثر: خطط لطلقاتك", "استخدم مطابقة الألوان والتصويب المدروس للاستفادة من كل طلقة في Bubble Fury.", [
   ("ابحث عن مجموعات متطابقة", "قبل الإطلاق، افحص اللوحة وابحث عن مجموعات تحتوي بالفعل على فقاعات من اللون نفسه."),
   ("فكر في زاوية التصويب", "الطلقة المباشرة ليست الخيار الوحيد؛ يوضح وصف اللعبة إمكانية الاستفادة من ارتداد الجدران للوصول إلى زوايا صعبة."),
   ("افتح مساحة بذكاء", "تؤدي مطابقة ثلاث فقاعات أو أكثر إلى إخلاء مساحة. ومع ازدياد ازدحام اللوحة تصبح دقة اختيار الطلقة أكثر أهمية.")])},
 "combos-and-high-scores": {
  "en": ("Build Bubble Fury Combos and Chase High Scores", "Understand combo chains, score rewards and coin collection in Bubble Fury.", [
   ("Keep successful matches flowing", "The Google Play description explains that successful matches help build combo chains."),
   ("Aim for a personal best", "Clear bubbles efficiently and keep your momentum to pursue a higher score."),
   ("Collect coins as you play", "Bubble Fury awards coins through gameplay as you pop bubbles and score points.")]),
  "ar": ("اصنع سلاسل الكومبو واطارد النتائج العالية", "تعرّف على سلاسل الكومبو ومكافآت النقاط وجمع العملات في Bubble Fury.", [
   ("واصل المطابقات الناجحة", "يوضح وصف Google Play أن المطابقات الناجحة تساعد على بناء سلاسل الكومبو."),
   ("اسعَ إلى أفضل نتيجة شخصية", "أزل الفقاعات بكفاءة وحافظ على زخم اللعب للوصول إلى نتيجة أعلى."),
   ("اجمع العملات أثناء اللعب", "تمنحك Bubble Fury عملات أثناء اللعب عندما تفجّر الفقاعات وتحقق النقاط.")])}
}
ARTICLE_SLUGS = tuple(ARTICLES)

def esc(value):
    return html.escape(str(value), quote=True)

def route(locale, tail=""):
    return f"{BASE}/{locale.lower()}/" + (f"{tail}/" if tail else "")

def alternates(locale, tail):
    if locale in PUBLISHED:
        pairs = [(code, route(code, tail)) for code in PUBLISHED]
        default = route("en-US", tail)
    else:
        pairs = [("en", route("en", tail)), ("ar", route("ar", tail))]
        default = route("en", tail)
    markup = "".join(f'<link rel="alternate" hreflang="{code}" href="{url}">\\n' for code, url in pairs)
    return markup + f'<link rel="alternate" hreflang="x-default" href="{default}">'

def header(locale, tail):
    import build
    import build_locales
    is_market = locale in PUBLISHED
    is_ar = locale == "ar"
    if is_market:
        data = RESOURCE[locale]
        primary = LOCALES[locale]["text"]
        nav_labels = data["nav"]
        group1, group2 = {
            "en-US": ("Explore", "Resources"), "en-CA": ("Explore", "Resources"),
            "fr-CA": ("Explorer", "Ressources"), "es-ES": ("Explorar", "Recursos"),
            "pt-PT": ("Explorar", "Recursos"), "fr-FR": ("Explorer", "Ressources"),
            "de-DE": ("Entdecken", "Ressourcen"), "it-IT": ("Esplora", "Risorse")
        }[locale]
        primary_items = [("about", primary["about"]), ("features", primary["features"]),
                         ("download", primary["download_nav"]), ("faq", primary["faq"])]
        flags = build_locales.render_locale_flags(PUBLISHED, tail + ("/" if tail else ""), locale)
    else:
        nav_labels = {"tips":"Tips","blog":"Blog","guide":"User guide","comparison":"Gameplay"} if not is_ar else {"tips":"نصائح","blog":"المدونة","guide":"دليل اللعب","comparison":"أسلوب اللعب"}
        group1, group2 = ("Explore", "Resources") if not is_ar else ("استكشف", "الموارد")
        primary_items = ([("about","About"),("features","Features"),("download","Download"),("faq","FAQ")] if not is_ar
                         else [("about","عن اللعبة"),("features","المزايا"),("download","التنزيل"),("faq","الأسئلة الشائعة")])
        flags = build_locales.render_locale_flags(PUBLISHED, tail + ("/" if tail else ""))
    primary_links = "".join(f'<a data-nav-item="{key}" href="{route(locale,key)}">{esc(label)}</a>' for key,label in primary_items)
    resource_links = "".join(f'<a data-nav-item="{key}" href="{route(locale,key)}">{esc(nav_labels[key])}</a>' for key in ("tips","blog","guide","comparison"))
    return (
      '<header class="standard-header"><div class="header-main">'
      f'<div class="locale-switch" aria-label="Country and region">{flags}{build.render_social_links()}</div>'
      f'<a class="brand" href="{BASE}/">BUBBLE <b>FURY</b></a>'
      '<nav aria-label="Primary navigation">'
      f'<details class="nav-menu" data-nav-group="primary"><summary>{esc(group1)}</summary><div class="nav-dropdown">{primary_links}</div></details>'
      f'<details class="nav-menu" data-nav-group="resources"><summary>{esc(group2)}</summary><div class="nav-dropdown">{resource_links}</div></details>'
      '</nav></div></header>'
    )

def footer(locale):
    fr = locale.startswith("fr")
    de = locale.startswith("de")
    it = locale.startswith("it")
    es = locale.startswith("es")
    pt = locale.startswith("pt")
    privacy = ("Politique de confidentialité" if fr else "Datenschutzerklärung" if de else "Informativa sulla privacy" if it else "Política de privacidad" if es else "Política de privacidade" if pt else "Privacy policy")
    support = ("Soutien" if locale=="fr-CA" else "Assistance" if fr else "Support" if de else "Assistenza" if it else "Ayuda" if es else "Apoio" if pt else "Support")
    return f'<footer><span>© DevImpact · BUBBLE FURY</span><span><a href="{esc(APP["privacy_policy_url"])}">{privacy}</a> · <a href="mailto:{esc(APP["support_email"])}">{support}</a></span></footer>'

def page(locale, tail, title, description, content, schema_type="WebPage"):
    url = route(locale, tail)
    lang = locale.split("-")[0]
    org = {"@type":"Organization","@id":f"{BASE}/#organization","name":APP["developer"],"url":BASE+"/","email":APP["support_email"]}
    node = {"@type":schema_type,"name":title,"description":description,"inLanguage":locale,"url":url,"publisher":{"@id":f"{BASE}/#organization"}}
    if schema_type == "Article":
        node.update({"headline":title,"mainEntityOfPage":url,"author":{"@id":f"{BASE}/#organization"}})
    schema = {"@context":"https://schema.org","@graph":[org,node]}
    og_locale = locale.replace("-","_")
    skip_label = LOCALES[locale]["text"]["skip_to_content"] if locale in PUBLISHED else ("تجاوز إلى المحتوى الرئيسي" if locale == "ar" else "Skip to main content")
    return f'''<!doctype html>
<html lang="{esc(locale)}" dir="{"rtl" if locale == "ar" else "ltr"}">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title><meta name="description" content="{esc(description)}">
<meta name="robots" content="index,follow,max-image-preview:large">
<link rel="canonical" href="{url}">
{alternates(locale,tail)}
<meta property="og:locale" content="{og_locale}"><meta property="og:type" content="website">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{url}"><meta property="og:image" content="{esc(SHOTS[0]["src"])}">
<meta property="og:image:alt" content="{esc(SHOTS[0]["alt"].get(lang,"Bubble Fury gameplay screenshot"))}">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(description)}"><meta name="twitter:image" content="{esc(SHOTS[0]["src"])}">
<link rel="preconnect" href="https://play-lh.googleusercontent.com" crossorigin>
<link rel="stylesheet" href="{BASE}/assets/style.css">
<script type="application/ld+json">{json.dumps(schema,ensure_ascii=False)}</script>
</head>
<body data-page-section="{esc(tail.split('/')[0] if tail else 'home')}">
<a class="skip-link" href="#main-content">{esc(skip_label)}</a>
{header(locale,tail)}
<main id="main-content">{content}</main>
{footer(locale)}
</body></html>'''

def cta(locale):
 label = "Get it on Google Play" if locale.split("-")[0] == "en" else "Obtenir sur Google Play" if locale.startswith("fr") else "Obtener en Google Play" if locale.startswith("es") else "Obter no Google Play" if locale.startswith("pt") else "Bei Google Play herunterladen" if locale.startswith("de") else "Scarica da Google Play" if locale.startswith("it") else "احصل عليها من Google Play"
 return f'<a class="btn" href="{PLAY}" target="_blank" rel="noopener noreferrer" data-analytics-event="google_play_click" data-cta-location="resource_page">{label}</a>'

def render_hub(locale, tail, data):
    title, description, heading, intro, cards = data
    cards_html = "".join(
      f'<article class="item"><h2><a href="{route(locale,target)}">{esc(card_title)}</a></h2><p>{esc(card_text)}</p><a href="{route(locale,target)}">{esc(RESOURCE.get(locale,{}).get("labels",{}).get("more","Explore this resource"))}</a></article>'
      for card_title,card_text,target in cards
    )
    gallery = ""
    if tail == "guide":
      gallery = f'<section class="section"><h2>{esc(LOCALES[locale]["text"]["gallery"])}</h2><div class="gallery">' + "".join(
       f'<figure class="shot"><img src="{esc(shot["src"])}" width="526" height="296" alt="{esc(LOCALES[locale]["screenshots"][i][0] if locale in PUBLISHED else shot["alt"].get(locale,shot["alt"]["en"]))}" loading="lazy" decoding="async"><figcaption>{esc(LOCALES[locale]["screenshots"][i][1] if locale in PUBLISHED else shot["caption"].get(locale,shot["caption"]["en"]))}</figcaption></figure>'
       for i,shot in enumerate(SHOTS)) + '</div></section>'
    note = '<p class="muted">This is a gameplay overview based on the published description, not an independent performance study.</p>' if tail=="comparison" and locale.split("-")[0]=="en" else ""
    content = (
      f'<section class="section resource-hub"><div class="tag">BUBBLE FURY · {esc(RESOURCE.get(locale,{}).get("labels",{}).get("resource","GAME RESOURCES"))}</div>'
      f'<h1>{esc(heading)}</h1><p class="lead">{esc(intro)}</p><div class="grid">{cards_html}</div>{note}{gallery}<div class="end"><h2>Bubble Fury</h2><p>{esc(LOCALES[locale]["tagline"] if locale in PUBLISHED else APP["tagline"].get(locale,APP["tagline"]["en"]))}</p>{cta(locale)}</div></section>'
    )
    return page(locale,tail,title,description,content,"CollectionPage")

def render_feature(locale, feature, index):
    lang = locale.split("-")[0]
    if locale in PUBLISHED:
        bundle = LOCALES[locale]
        title, description = bundle["features"][index]
    else:
        title = feature["title"][lang]
        description = feature["description"][lang]
    shot = SHOTS[index]
    if locale in PUBLISHED:
        shot_alt, shot_caption = LOCALES[locale]["screenshots"][index]
    else:
        shot_alt, shot_caption = shot["alt"].get(lang,shot["alt"]["en"]), shot["caption"].get(lang,shot["caption"]["en"])
    intro = description
    bullets = {
      "en":[("Aim with precision","Drag to aim and release to shoot."),("Read the board","Look for matching colors and angles that can reach them."),("Keep adapting","The board becomes more crowded as the run continues.")],
      "ar":[("صوّب بدقة","اسحب للتصويب واترك للإطلاق."),("راقب اللوحة","ابحث عن الألوان المتطابقة والزوايا التي تساعدك على الوصول إليها."),("تكيف باستمرار","تصبح اللوحة أكثر ازدحاماً مع استمرار الجولة.")]
    }
    items = bullets["ar" if lang=="ar" else "en"] if locale in ("en","ar") else []
    sections = "".join(f'<section class="article-section"><h2>{esc(h)}</h2><p>{esc(p)}</p></section>' for h,p in items)
    content = (
      f'<article class="section article"><div class="tag">BUBBLE FURY · {esc(RESOURCE[locale]["labels"]["resource"] if locale in PUBLISHED else ("GAME RESOURCES" if lang=="en" else "موارد اللعبة"))}</div><h1>{esc(title)}</h1><p class="lead">{esc(intro)}</p>'
      f'<figure class="guide-shot"><img src="{esc(shot["src"])}" width="526" height="296" alt="{esc(shot_alt)}" loading="lazy" decoding="async"><figcaption>{esc(shot_caption)}</figcaption></figure>'
      f'{sections}<p><a href="{route(locale,"features")}">{esc(LOCALES[locale]["text"]["features"] if locale in PUBLISHED else ("Explore all features" if lang=="en" else "استكشف جميع المزايا"))}</a></p>{cta(locale)}</article>'
    )
    return page(locale,f"features/{feature['id']}",title+" | Bubble Fury",description,content)

def render_article(locale, slug, data):
    title, description, sections = data[locale]
    body = "".join(f'<section class="article-section"><h2>{esc(h)}</h2><p>{esc(p)}</p></section>' for h,p in sections)
    lang = locale
    back = "← All Bubble Fury articles" if lang=="en" else "← جميع مقالات Bubble Fury"
    content = f'<article class="section article"><div class="tag">BUBBLE FURY · ARCADE GUIDE</div><h1>{esc(title)}</h1><p class="lead">{esc(description)}</p>{body}<p><a href="{route(locale,"blog")}">{back}</a></p><div class="end"><h2>Bubble Fury</h2><p>{esc(APP["tagline"][lang])}</p>{cta(locale)}</div></article>'
    return page(locale,f"blog/{slug}",title,description,content,"Article")

def build_bubble_pages():
    import build
    import build_locales
    # Replace all generated resource hubs and feature-detail pages for published locales.
    for locale in PUBLISHED:
        for tail in ("tips","blog","guide","comparison"):
            target = DIST / locale.lower() / tail / "index.html"
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_text(render_hub(locale,tail,RESOURCE[locale]["pages"][tail]),encoding="utf-8")
        for index,feature in enumerate(FEATURES):
            target = DIST / locale.lower() / "features" / feature["id"] / "index.html"
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_text(render_feature(locale,feature,index),encoding="utf-8")
    # Keep the legacy English/Arabic routes working, but replace their template copy too.
    base_hubs = {
      "en":{
       "tips":("Bubble Shooter Tips | Bubble Fury","Practical tips for aiming, matching colors, using wall rebounds and building combos.","Bubble shooter tips","Learn precise aiming, match-three bubbles and combo basics.",[("Aim with a plan","Drag to aim and release to shoot.","guide"),("Match three or more","Pop groups of at least three same-color bubbles.","blog"),("Use wall rebounds","Reach difficult angles with wall rebounds.","comparison")]),
       "blog":("Bubble Fury Blog | Bubble Shooter Guides","Guides to Bubble Fury arcade gameplay, color matching, combos and high scores.","Bubble Fury gameplay articles","Explore practical guides to the mechanics described on Google Play.",[("How to play Bubble Fury","Learn the basic aim, shoot and match loop.","guide"),("Match bubbles with purpose","Plan shots around groups of the same color.","tips"),("Build combos and scores","Understand combo chains and score rewards.","comparison")]),
       "guide":("Bubble Fury User Guide | How to Play","Learn to aim, shoot, match bubbles and adapt as the board becomes more crowded.","How to play Bubble Fury","Follow the core gameplay loop using the controls described on Google Play.",[("Aim and shoot","Drag to aim and release to shoot.","tips"),("Match the same color","Match at least three same-color bubbles.","blog"),("Adapt as you play","Use rebounds and combos as the challenge grows.","comparison")]),
       "comparison":("Bubble Fury Arcade Gameplay Overview","A factual overview of Bubble Fury’s arcade bubble shooter mechanics.","The Bubble Fury arcade approach","This is a gameplay overview based on the published description, not an independent performance study.",[("Arcade rounds","Quick bubble-shooting runs focused on improving your score.","guide"),("Color matching","Pop groups of at least three bubbles of the same color.","tips"),("Skill and progression","Precision and combo management matter as the board gets crowded.","blog")])},
      "ar":{
       "tips":("نصائح لعبة الفقاعات | Bubble Fury","نصائح للتصويب ومطابقة الألوان واستخدام ارتداد الجدران وبناء سلاسل الكومبو.","نصائح لإطلاق الفقاعات","تعرّف على أساسيات التصويب الدقيق ومطابقة ثلاث فقاعات والكومبو.",""),
       "blog":("مدونة Bubble Fury | أدلة اللعب","مقالات عن أسلوب أركيد وإطلاق الفقاعات ومطابقة الألوان والكومبو والنتائج العالية.","مقالات Bubble Fury","استكشف أدلة عملية للآليات المذكورة في صفحة Google Play.",""),
       "guide":("دليل Bubble Fury | طريقة اللعب","تعلّم التصويب والإطلاق ومطابقة الفقاعات والتكيف مع ازدياد ازدحام اللوحة.","كيف تلعب Bubble Fury","اتبع طريقة اللعب الأساسية باستخدام أدوات التحكم الموضحة في Google Play.",""),
       "comparison":("نظرة على أسلوب Bubble Fury","نظرة واقعية على آليات إطلاق الفقاعات بنمط أركيد في Bubble Fury.","أسلوب أركيد في Bubble Fury","هذه مقارنة وصفية لأسلوب اللعب اعتماداً على الوصف المنشور، وليست دراسة أداء مستقلة.","")}
    }
    for locale in ("en","ar"):
        for tail,data in base_hubs[locale].items():
            if locale=="ar":
                title,desc,heading,intro,_=data
                cards=[("صوّب بدقة","اسحب للتصويب واترك للإطلاق.","guide"),("طابق ثلاث فقاعات أو أكثر","فجّر مجموعات من ثلاث فقاعات أو أكثر من اللون نفسه.","blog"),("استفد من ارتداد الجدران","استخدم الزوايا المرتدة للوصول إلى الفقاعات الصعبة.","comparison")]
                if tail=="blog":cards=[("كيف تلعب Bubble Fury","تعرّف على التصويب والإطلاق والمطابقة.","guide"),("خطط لمطابقة الفقاعات","اختر الطلقات حول مجموعات الألوان المتشابهة.","tips"),("ابنِ سلاسل الكومبو","تعرّف على سلاسل الكومبو ومكافآت النقاط.","comparison")]
                if tail=="guide":cards=[("صوّب وأطلق","اسحب للتصويب واترك لإطلاق الفقاعة.","tips"),("طابق اللون نفسه","طابق ثلاث فقاعات أو أكثر من اللون نفسه.","blog"),("تكيف أثناء اللعب","استخدم الارتداد والكومبو مع ازدياد التحدي.","comparison")]
                if tail=="comparison":cards=[("جولات أركيد","جولات سريعة تركز على تحسين نتيجتك.","guide"),("مطابقة الألوان","فجّر مجموعات من ثلاث فقاعات أو أكثر من اللون نفسه.","tips"),("المهارة والتقدم","تزداد أهمية الدقة وإدارة الكومبو مع ازدحام اللوحة.","blog")]
            else:
                title,desc,heading,intro,cards=data
            cards_html = "".join(f'<article class="item"><h2><a href="{route(locale,t)}">{esc(h)}</a></h2><p>{esc(p)}</p></article>' for h,p,t in cards)
            gallery = ""
            if tail == "guide":
                gallery = '<section class="section"><h2>{esc(gallery_title)}</h2><div class="gallery">' + "".join(f'<figure class="shot"><img src="{esc(shot["src"])}" width="526" height="296" alt="{esc(shot["alt"][locale])}" loading="lazy" decoding="async"><figcaption>{esc(shot["caption"][locale])}</figcaption></figure>' for shot in SHOTS) + '</div></section>'
            target=DIST/locale/tail/"index.html";target.parent.mkdir(parents=True,exist_ok=True)
            gallery_title = "Bubble Fury screenshots" if locale == "en" else "لقطات شاشة Bubble Fury"
            content = (
                f'<section class="section resource-hub"><div class="tag">BUBBLE FURY · GAME RESOURCES</div>'
                f'<h1>{esc(heading)}</h1><p class="lead">{esc(intro)}</p><div class="grid">{cards_html}</div>{gallery}'
                f'<div class="end"><h2>Bubble Fury</h2><p>{esc(APP["tagline"][locale])}</p>{cta(locale)}</div></section>'
            )
            target.write_text(page(locale,tail,title,desc,content,"CollectionPage"),encoding="utf-8")
        for slug,data in ARTICLES.items():
            target=DIST/locale/"blog"/slug/"index.html";target.parent.mkdir(parents=True,exist_ok=True)
            target.write_text(render_article(locale,slug,data),encoding="utf-8")
        for index,feature in enumerate(FEATURES):
            target=DIST/locale/"features"/feature["id"]/"index.html";target.parent.mkdir(parents=True,exist_ok=True)
            target.write_text(render_feature(locale,feature,index),encoding="utf-8")
    # Keep the public crawler guide focused on the current game and its real routes.
    lines=[f"# {APP['name']}","",APP["description"]["en"],"",f"- Google Play: {PLAY}",f"- Website: {BASE}/"]
    for locale in PUBLISHED:
        lines.append(f"- {locale}: {route(locale)}")
        for tail in ("about","features","download","faq","tips","blog","guide","comparison"):
            lines.append(f"- {locale} {tail}: {route(locale,tail)}")
        for feature in FEATURES:
            lines.append(f"- {locale} {feature['id']}: {route(locale,'features/'+feature['id'])}")
    (DIST/"llms.txt").write_text("\n".join(lines)+"\n",encoding="utf-8")

if __name__ == "__main__":
    build_bubble_pages()
