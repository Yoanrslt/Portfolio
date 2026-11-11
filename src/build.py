# -*- coding: utf-8 -*-
"""Générateur du site statique.

Usage (depuis la racine du dépôt) :
    python src/build.py

Lit src/content.py et écrit les pages HTML :
    index.html, experiences/, projects/, education/   -> français
    en/index.html, en/experiences/, ...               -> anglais
"""
import html
import os
import posixpath
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from content import (BEYOND, EXTRA_TIMELINE, LETTERS, PAGES, PERSON, PROJECTS,  # noqa: E402
                     SKILLS, TIMELINE_ORDER, UI)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE_BY_SLUG = {p["slug"]: p for p in PAGES}
# Images "photo" (recadrées) ; les autres (diapositives, schémas) sont affichées en entier
PHOTO_PREFIXES = ("gend-", "armee", "blockout", "hti-plasma", "hti-ceramiques", "hti-implants", "hti-usinage",
                  "hti-production", "mobilis-prototype", "voyage", "parachut", "profil")


def is_portrait(img):
    """Vrai si l'image est plus haute que large (lecture via Pillow si disponible)."""
    try:
        from PIL import Image
        with Image.open(os.path.join(ROOT, "assets", "img", img)) as im:
            return im.height > im.width
    except Exception:
        return False
FONTS = ("https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700"
         "&family=Playfair+Display:ital,wght@0,500;0,600;0,700;1,500&display=swap")

# ---------------------------------------------------------------- icônes
ICONS = {
    "shield": '<path d="M12 3l7 3v5c0 4.5-3 8.4-7 10-4-1.6-7-5.5-7-10V6l7-3z"/><path d="M9 12l2 2 4-4"/>',
    "flask": '<path d="M9 3h6"/><path d="M10 3v6L4.5 18.5A2 2 0 006.2 21h11.6a2 2 0 001.7-2.5L14 9V3"/><path d="M7 15h10"/>',
    "check": '<rect x="4" y="3" width="16" height="18" rx="2"/><path d="M8 8h8M8 12h5"/><path d="M9 16.5l2 2 4-4"/>',
    "wave": '<path d="M2 12h3l2-6 3 12 3-9 2 5 2-2h5"/>',
    "swim": '<circle cx="16" cy="6" r="2"/><path d="M3 18c1.5 0 1.5-1 3-1s1.5 1 3 1 1.5-1 3-1 1.5 1 3 1 1.5-1 3-1 1.5 1 3 1"/><path d="M6 14l4-4 3 2 3-3"/>',
    "chart": '<path d="M4 20V4"/><path d="M4 20h16"/><path d="M7 15l4-5 3 3 5-6"/>',
    "cap": '<path d="M2 9l10-5 10 5-10 5L2 9z"/><path d="M6 11v5c3 2 9 2 12 0v-5"/><path d="M22 9v6"/>',
    "spark": '<path d="M12 3v4M12 17v4M3 12h4M17 12h4M5.6 5.6l2.8 2.8M15.6 15.6l2.8 2.8M18.4 5.6l-2.8 2.8M8.4 15.6l-2.8 2.8"/>',
    "phone": '<path d="M5 4h4l2 5-2.5 1.5a11 11 0 005 5L15 13l5 2v4a2 2 0 01-2 2A16 16 0 013 6a2 2 0 012-2"/>',
    "sms": '<path d="M21 15a2 2 0 01-2 2H8l-5 4V5a2 2 0 012-2h14a2 2 0 012 2z"/><path d="M8 9h8M8 13h5"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/>',
    "linkedin": '<rect x="3" y="3" width="18" height="18" rx="3"/><path d="M8 10v7M8 7v.01M12 17v-4a2 2 0 014 0v4M12 10v7"/>',
    "pin": '<path d="M12 21s-7-6.2-7-11a7 7 0 0114 0c0 4.8-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/>',
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "back": '<path d="M19 12H5M11 6l-6 6 6 6"/>',
    "pdf": '<path d="M14 3H7a2 2 0 00-2 2v14a2 2 0 002 2h10a2 2 0 002-2V8z"/><path d="M14 3v5h5"/><path d="M9 14h6M9 17h4"/>',
    "quote": '<path d="M7 7h4v4c0 3-1.5 5-4 6M14 7h4v4c0 3-1.5 5-4 6"/>',
    "menu": '<path d="M4 7h16M4 12h16M4 17h16"/>',
    "close": '<path d="M6 6l12 12M18 6L6 18"/>',
    "briefcase": '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M9 7V5a2 2 0 012-2h2a2 2 0 012 2v2M3 13h18"/>',
    "lab": '<path d="M12 3v3M8 21h8M12 18a6 6 0 100-12 6 6 0 000 12z"/><path d="M12 10v2l1.5 1.5"/>',
}


def icon(name, cls="ico"):
    return (f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>')


def esc(s):
    return html.escape(s, quote=True)


# ---------------------------------------------------------------- chemins
def out_path(lang, rel):
    return rel if lang == "fr" else "en/" + rel


def page_rel(p):
    return f"{p['section']}/{p['slug']}.html"


def link(from_file, to_file):
    """Lien relatif entre deux fichiers du site (chemins depuis la racine)."""
    r = posixpath.relpath(to_file, posixpath.dirname(from_file) or ".")
    return r


def asset(from_file, a):
    return link(from_file, "assets/" + a)


def versioned(from_file, a):
    """Lien vers un fichier CSS/JS avec ?v=<empreinte> pour forcer le rafraîchissement du cache."""
    import hashlib
    with open(os.path.join(ROOT, "assets", *a.split("/")), "rb") as fh:
        v = hashlib.md5(fh.read()).hexdigest()[:8]
    return f"{asset(from_file, a)}?v={v}"


# ---------------------------------------------------------------- gabarit
def head(lang, from_file, title, desc, other_file):
    u = UI[lang]
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="author" content="{esc(PERSON['name'])}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:type" content="website">
<meta property="og:image" content="{asset(from_file, 'img/profil.jpg')}">
<meta name="theme-color" content="#0b0b0d">
<link rel="alternate" hreflang="{u['other_lang']}" href="{link(from_file, other_file)}">
<link rel="icon" href="{asset(from_file, 'img/favicon.svg')}" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="{versioned(from_file, 'css/style.css')}">
</head>
"""


def header(lang, from_file, home_file, other_file, is_home):
    u = UI[lang]
    anchor = "" if is_home else link(from_file, home_file)
    items = "".join(f'<li><a href="{anchor}#{a}" data-nav="{a}">{esc(label)}</a></li>' for a, label in u["nav"])
    return f"""<body class="{'home' if is_home else 'detail'}">
<a class="skip" href="#main">{'Aller au contenu' if lang == 'fr' else 'Skip to content'}</a>
<header class="site-header" id="top">
  <div class="wrap header-inner">
    <a class="brand" href="{anchor or '#'}{'' if anchor else 'top'}" aria-label="{esc(PERSON['name'])}">
      <span class="monogram">YR</span><span class="brand-name">Yoan Rousselot</span>
    </a>
    <nav class="main-nav" aria-label="Navigation">
      <ul id="nav-list">{items}</ul>
    </nav>
    <div class="header-actions">
      <div class="lang-switch" role="group" aria-label="Langue / Language">
        <span class="current" aria-current="true">{u['this_lang_label']}</span>
        <a href="{link(from_file, other_file)}" hreflang="{u['other_lang']}" lang="{u['other_lang']}" title="{esc(u['switch_title'])}">{u['other_lang_label']}</a>
      </div>
      <button class="nav-toggle" aria-expanded="false" aria-controls="nav-list" aria-label="{u['menu']}">
        {icon('menu', 'ico open')}{icon('close', 'ico shut')}
      </button>
    </div>
  </div>
</header>
"""


def footer(lang, from_file):
    u = UI[lang]
    return f"""<footer class="site-footer">
  <div class="wrap footer-inner">
    <div class="footer-brand"><span class="monogram">YR</span>
      <div><strong>Yoan Rousselot</strong><span>{esc(u['footer'])}</span></div>
    </div>
    <div class="footer-links">
      <a href="sms:{PERSON['phone_intl']}">{icon('sms')}<span>{PERSON['phone_display']}</span></a>
      <a href="mailto:{PERSON['email']}">{icon('mail')}<span>{PERSON['email']}</span></a>
      <a href="{PERSON['linkedin']}" target="_blank" rel="noopener">{icon('linkedin')}<span>LinkedIn</span></a>
    </div>
    <p class="copy">© 2026 Yoan Rousselot</p>
  </div>
</footer>
<div class="lightbox" id="lightbox" hidden role="dialog" aria-modal="true">
  <button class="lb-close" aria-label="{u['close']}">{icon('close')}</button>
  <button class="lb-nav lb-prev" aria-label="{u['prev']}">{icon('back')}</button>
  <figure><img alt=""><figcaption></figcaption></figure>
  <button class="lb-nav lb-next" aria-label="{u['next']}">{icon('arrow')}</button>
</div>
<script src="{versioned(from_file, 'js/main.js')}" defer></script>
</body>
</html>
"""


def section_head(kicker, title, intro=None):
    s = f'<p class="kicker">{esc(kicker)}</p><h2 class="section-title">{esc(title)}</h2>'
    if intro:
        s += f'<p class="section-intro">{esc(intro)}</p>'
    return f'<div class="section-head reveal">{s}</div>'


# ---------------------------------------------------------------- accueil
def build_home(lang):
    u = UI[lang]
    f = out_path(lang, "index.html")
    other = out_path(u["other_lang"], "index.html")
    sk = SKILLS[lang]
    P = PERSON

    stats = "".join(f'<div class="stat"><span class="stat-value">{esc(v)}</span><span class="stat-label">{esc(l)}</span></div>'
                    for v, l in u["stats"])
    about = "".join(f"<p>{p}</p>" for p in u["about"])
    pillars = "".join(f'<div class="pillar reveal">{icon(i)}<h3>{esc(t)}</h3><p>{esc(d)}</p></div>'
                      for i, t, d in u["pillars"])

    tech = ""
    for title, sub, chips in sk["tech"]:
        tech += (f'<article class="card skill-card reveal"><h4>{esc(title)}</h4><p class="muted small">{esc(sub)}</p>'
                 f'<ul class="chips">{"".join(f"<li>{esc(c)}</li>" for c in chips)}</ul></article>')
    soft = "".join(f"<li>{esc(s)}</li>" for s in sk["soft"])
    quals = "".join(f'<div class="quality"><h4>{esc(q)}</h4><p>{esc(d)}</p></div>' for q, d in sk["qualities"])
    langs = "".join(f'<div class="lang-row"><div class="lang-top"><strong>{esc(n)}</strong><span>{esc(l)}</span></div>'
                    f'<div class="bar"><span style="--w:{w}%"></span></div></div>' for n, l, w in sk["languages"])
    certs = "".join(f"<li>{esc(c)}</li>" for c in sk["certs"])

    # parcours
    tl = ""
    for item in TIMELINE_ORDER:
        if isinstance(item, int):
            e = EXTRA_TIMELINE[item]
            d, kind, href = e[lang], e["kind"], None
        else:
            p = PAGE_BY_SLUG[item]
            d, kind, href = p[lang], p["kind"], link(f, out_path(lang, page_rel(p)))
        filt = "edu" if kind == "edu" else "exp"
        btn = (f'<a class="btn btn-ghost btn-sm" href="{href}">{esc(u["see_detail"])}{icon("arrow")}</a>' if href else "")
        tag = u["type_labels"][kind]
        tl += f"""<li class="tl-item reveal" data-kind="{filt}">
  <span class="tl-dot" aria-hidden="true"></span>
  <article class="card tl-card{' is-link' if href else ''}">
    <div class="tl-meta"><span class="tl-date">{esc(d['period'])}</span><span class="tag tag-{kind}">{esc(tag)}</span></div>
    <h3>{esc(d['title'])}</h3>
    <p class="tl-org">{esc(d['org'])}</p>
    <p>{esc(d['timeline'])}</p>
    {btn}
  </article>
</li>"""
    filters = "".join(f'<button class="filter{" active" if k == "all" else ""}" data-filter="{k}" aria-pressed="{"true" if k == "all" else "false"}">{esc(l)}</button>'
                      for k, l in u["filters"])

    beyond = ""
    for b in BEYOND:
        t, txt = b[lang]
        media = (f'<img src="{asset(f, "img/" + b["image"])}" alt="{esc(t)}" loading="lazy">' if b["image"]
                 else f'<div class="media-icon">{icon(b["icon"])}</div>')
        beyond += f'<article class="card beyond-card reveal"><div class="beyond-media">{media}</div><div class="beyond-body"><h4>{esc(t)}</h4><p>{esc(txt)}</p></div></article>'

    # projets
    projects = ""
    for pr in PROJECTS:
        p = PAGE_BY_SLUG[pr["slug"]]
        d = pr[lang]
        href = link(f, out_path(lang, page_rel(p)))
        media = (f'<img src="{asset(f, "img/" + pr["image"])}" alt="{esc(d["title"])}" loading="lazy">' if pr.get("image")
                 else f'<div class="media-icon">{icon(pr["icon"])}</div>')
        tags = "".join(f"<li>{esc(t)}</li>" for t in d["tags"])
        projects += f"""<a class="card project-card reveal{' featured' if pr.get('featured') else ''}" href="{href}">
  <div class="project-media">{media}</div>
  <div class="project-body">
    <p class="project-period">{esc(p[lang]['period'])}</p>
    <h3>{esc(d['title'])}</h3>
    <p>{esc(d['text'])}</p>
    <ul class="chips">{tags}</ul>
    <span class="btn-link">{esc(u['see_project'])}{icon('arrow')}</span>
  </div>
</a>"""

    # recommandations
    recos = ""
    for key in ("hti", "laval", "usmb"):
        L = LETTERS[key]
        d = L[lang]
        tr = f'<span class="translated">{esc(u["translated"])}</span>' if u["translated"] else ""
        recos += f"""<figure class="card reco-card reveal">
  {icon('quote', 'ico quote-ico')}
  <blockquote>« {esc(d['quote'])} »</blockquote>{tr}
  <figcaption>
    <strong>{esc(L['name'])}</strong>
    <span>{esc(d['role'])}</span>
    <span class="muted small">{esc(d['context'])} · {esc(d['date'])}</span>
  </figcaption>
  <a class="btn btn-ghost btn-sm" href="{asset(f, 'docs/' + L['pdf'])}" target="_blank" rel="noopener">{icon('pdf')}{esc(u['read_letter'])}</a>
</figure>"""

    import urllib.parse as up
    mail_href = f"mailto:{P['email']}?subject={up.quote(u['mail_subject'])}"
    sms_href = f"sms:{P['phone_intl']}?&body={up.quote(u['sms_body'])}"

    body = f"""<main id="main">
<section class="hero" id="profil">
  <div class="wrap hero-grid">
    <div class="hero-text">
      <p class="eyebrow reveal">{esc(u['eyebrow'])}</p>
      <h1 class="reveal">{u['hero_title']}</h1>
      <p class="lead reveal">{esc(u['hero_lead'])}</p>
      <div class="hero-cta reveal">
        <a class="btn btn-gold" href="#projets">{esc(u['cta_projects'])}{icon('arrow')}</a>
        <a class="btn btn-ghost" href="#contact">{esc(u['cta_contact'])}</a>
      </div>
      <p class="availability reveal"><span class="pulse" aria-hidden="true"></span>{esc(u['availability'])}</p>
    </div>
    <div class="hero-photo reveal">
      <div class="photo-ring"><img src="{asset(f, 'img/profil.jpg')}" alt="{esc(u['photo_alt'])}" width="900" height="1080"></div>
    </div>
  </div>
  <div class="wrap"><div class="stats reveal">{stats}</div></div>
</section>

<section class="section" id="about">
  <div class="wrap about-grid">
    <div>{section_head(u['about_kicker'], u['about_title'])}<div class="prose reveal">{about}</div></div>
    <div class="pillars">{pillars}</div>
  </div>
</section>

<section class="section alt" id="competences">
  <div class="wrap">
    {section_head(u['skills_kicker'], u['skills_title'])}
    <h3 class="sub-title reveal">{esc(u['skills_tech'])}</h3>
    <div class="grid grid-2">{tech}</div>
    <article class="card soft-card reveal"><h4>{esc(u['skills_soft'])}</h4><ul class="list-check list-2col">{soft}</ul></article>
    <div class="grid grid-2 skills-bottom">
      <article class="card reveal"><h4>{esc(u['languages'])}</h4>{langs}</article>
      <article class="card reveal"><h4>{esc(u['certs'])}</h4><ul class="list-check">{certs}</ul></article>
    </div>
    <h3 class="sub-title reveal">{esc(u['qualities'])}</h3>
    <div class="qualities reveal">{quals}</div>
  </div>
</section>

<section class="section" id="parcours">
  <div class="wrap">
    {section_head(u['path_kicker'], u['path_title'], u['path_intro'])}
    <div class="filters reveal" role="group">{filters}</div>
    <ol class="timeline">{tl}</ol>
    <h3 class="sub-title reveal">{esc(u['beyond_title'])}</h3>
    <p class="section-intro reveal">{esc(u['beyond_intro'])}</p>
    <div class="grid grid-4">{beyond}</div>
  </div>
</section>

<section class="section alt" id="projets">
  <div class="wrap">
    {section_head(u['projects_kicker'], u['projects_title'], u['projects_intro'])}
    <div class="projects">{projects}</div>
  </div>
</section>

<section class="section" id="recommandations">
  <div class="wrap">
    {section_head(u['reco_kicker'], u['reco_title'], u['reco_intro'])}
    <div class="grid grid-3">{recos}</div>
  </div>
</section>

<section class="section alt" id="contact">
  <div class="wrap">
    {section_head(u['contact_kicker'], u['contact_title'], u['contact_intro'])}
    <div class="contact-grid">
      <article class="card contact-card reveal">{icon('phone')}<h4>{esc(u['c_phone'])}</h4><p>{P['phone_display']}</p>
        <div class="contact-actions"><a class="btn btn-gold btn-sm" href="{esc(sms_href)}">{icon('sms')}{esc(u['c_sms'])}</a><a class="btn btn-ghost btn-sm" href="tel:{P['phone_intl']}">{esc(u['c_call'])}</a></div></article>
      <article class="card contact-card reveal">{icon('mail')}<h4>{esc(u['c_email'])}</h4><p class="break">{P['email'].replace('@', '@<wbr>')}</p>
        <div class="contact-actions"><a class="btn btn-gold btn-sm" href="{esc(mail_href)}">{esc(u['c_write'])}</a></div></article>
      <article class="card contact-card reveal">{icon('linkedin')}<h4>{esc(u['c_linkedin'])}</h4><p>yoan-rousselot</p>
        <div class="contact-actions"><a class="btn btn-gold btn-sm" href="{P['linkedin']}" target="_blank" rel="noopener">{esc(u['c_profile'])}{icon('arrow')}</a></div></article>
      <article class="card contact-card reveal">{icon('pin')}<h4>{esc(u['c_city'])}</h4><p>{esc(P['city'][lang])}</p>
        <p class="muted small">{esc(u['c_mobile'])}</p></article>
    </div>
  </div>
</section>
</main>
"""
    return f, (head(lang, f, u["site_title"], u["site_desc"], other)
               + header(lang, f, f, other, True) + body + footer(lang, f))


# ---------------------------------------------------------------- pages détaillées
def build_detail(lang, p, prev_p, next_p):
    u = UI[lang]
    d = p[lang]
    rel = page_rel(p)
    f = out_path(lang, rel)
    other = out_path(u["other_lang"], rel)
    home = out_path(lang, "index.html")
    back_anchor = "projets" if p["kind"] == "project" else "parcours"
    back_label = u["back_projects"] if p["kind"] == "project" else u["back_path"]

    cover = ""
    if p.get("cover"):
        fit = "" if p["cover"].startswith(PHOTO_PREFIXES) else " fit"
        cover = f'<div class="detail-cover{fit} reveal"><img src="{asset(f, "img/" + p["cover"])}" alt="{esc(d["title"])}"></div>'
    else:
        cover = f'<div class="detail-cover detail-cover-icon reveal">{icon(p.get("icon", "briefcase"))}</div>'

    highlights = ""
    if d.get("highlights"):
        highlights = '<div class="highlights reveal">' + "".join(
            f'<div class="highlight"><span class="stat-value">{esc(v)}</span><span class="stat-label">{esc(l)}</span></div>'
            for v, l in d["highlights"]) + "</div>"

    sections = "".join(f'<section class="detail-block reveal"><h2>{esc(h)}</h2>{body}</section>' for h, body in d["sections"])

    gallery = ""
    if p.get("gallery"):
        items = ""
        for img, cfr, cen in p["gallery"]:
            cap = cfr if lang == "fr" else cen
            src = asset(f, "img/" + img)
            fit = (" tall" if is_portrait(img) else "") if img.startswith(PHOTO_PREFIXES) else " fit"
            items += (f'<figure class="g-item reveal"><button class="g-open{fit}"data-src="{src}" data-caption="{esc(cap)}" aria-label="{esc(cap)}">'
                      f'<img src="{src}" alt="{esc(cap)}" loading="lazy"></button><figcaption>{esc(cap)}</figcaption></figure>')
        gallery = f'<section class="detail-gallery"><h2 class="reveal">{esc(u["gallery"])}</h2><div class="gallery">{items}</div></section>'

    reco = ""
    if p.get("letter"):
        L = LETTERS[p["letter"]]
        ld = L[lang]
        reco = f"""<div class="card aside-reco">
  <p class="kicker">{esc(u['reco_short'])}</p>
  <blockquote>« {esc(ld['quote'])} »</blockquote>
  <p class="aside-author"><strong>{esc(L['name'])}</strong><span>{esc(ld['role'])}</span></p>
  <a class="btn btn-ghost btn-sm" href="{asset(f, 'docs/' + L['pdf'])}" target="_blank" rel="noopener">{icon('pdf')}{esc(u['read_letter'])}</a>
</div>"""

    chips = "".join(f"<li>{esc(s)}</li>" for s in d["skills"])
    tag = u["type_labels"][p["kind"]]

    def nav_link(q, label, cls):
        if not q:
            return "<span></span>"
        return (f'<a class="pn {cls}" href="{link(f, out_path(lang, page_rel(q)))}"><span class="muted small">{esc(label)}</span>'
                f'<strong>{esc(q[lang]["short"])}</strong></a>')

    body = f"""<main id="main" class="detail-main">
<section class="detail-hero">
  <div class="wrap">
    <a class="back" href="{link(f, home)}#{back_anchor}">{icon('back')}{esc(back_label)}</a>
    <div class="detail-hero-grid">
      <div>
        <p class="eyebrow reveal"><span class="tag tag-{p['kind']}">{esc(tag)}</span> {esc(d['period'])}</p>
        <h1 class="reveal">{esc(d['title'])}</h1>
        <p class="detail-org reveal">{esc(d['org'])}</p>
        <p class="lead reveal">{esc(d['summary'])}</p>
      </div>
      {cover}
    </div>
    {highlights}
  </div>
</section>
<div class="wrap detail-grid">
  <article class="detail-content">{sections}</article>
  <aside class="detail-aside">
    <div class="card facts reveal">
      <p class="kicker">{esc(u['facts'])}</p>
      <dl>
        <dt>{esc(u['period'])}</dt><dd>{esc(d['period'])}</dd>
        <dt>{esc(u['place'])}</dt><dd>{esc(d['place'])}</dd>
        <dt>{esc(u['role'])}</dt><dd>{esc(d['role'])}</dd>
      </dl>
      <p class="kicker">{esc(u['skills_dev'])}</p>
      <ul class="chips">{chips}</ul>
    </div>
    {reco}
  </aside>
</div>
<div class="wrap">{gallery}
  <nav class="prev-next" aria-label="{esc(u['prev'])} / {esc(u['next'])}">
    {nav_link(prev_p, u['prev'], 'pn-prev')}
    {nav_link(next_p, u['next'], 'pn-next')}
  </nav>
</div>
</main>
"""
    title = f"{d['title']} · {d['short']} · Yoan Rousselot"
    return f, (head(lang, f, title, d["summary"], other)
               + header(lang, f, home, other, False) + body + footer(lang, f))


def write(rel, content):
    path = os.path.join(ROOT, *rel.split("/"))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(content)
    print("écrit :", rel)


def main():
    ordered = [PAGE_BY_SLUG[s] for s in TIMELINE_ORDER if isinstance(s, str)]
    for lang in ("fr", "en"):
        write(*build_home(lang))
        for i, p in enumerate(ordered):
            prev_p = ordered[i - 1] if i > 0 else None
            next_p = ordered[i + 1] if i + 1 < len(ordered) else None
            write(*build_detail(lang, p, prev_p, next_p))


if __name__ == "__main__":
    main()
