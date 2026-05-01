#!/usr/bin/env python3
"""Render Ervee product pages with the AlorAir-inspired layout.

Imports SERIES + PRODUCTS data from build.py (keeps a single source of truth)
and writes 24 distinct product pages plus an updated sitemap.xml.
"""

import json, os, re, html, sys
from pathlib import Path
from datetime import date

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "build"))

# Import product data from the existing build.py without running its main()
import importlib.util
spec = importlib.util.spec_from_file_location("build_data", ROOT / "build" / "build.py")
build_data = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build_data)  # this will run main(), but it's harmless — overwrites old DryEaz-style pages first

SITE_URL = build_data.SITE_URL
SERIES = build_data.SERIES
PRODUCTS = build_data.PRODUCTS

# ============================================================
# Series-specific benefit copy (long-form, 6 cards per series)
# ============================================================
BENEFITS = {
    "UTC": [
        ("Slim", "20 cm chassis", "Hidden ceiling install — fits in any plenum void above the false ceiling. Zero floor footprint."),
        ("Quiet", "39 to 50 dB(A)", "Inverter compressor, multiple shock-absorbing mounts, metal cast motor with Japan NSK bearing."),
        ("Smart", "WiFi App + RS485 BMS", "Adjust setpoint and monitor humidity from anywhere. RS485 Modbus integration with any BMS."),
        ("Sterile", "UV-C lamp included", "Eliminates 99.9% of bacteria and viruses in the airstream. Hospital-grade air handling."),
        ("Whole-house", "Ducted distribution", "One unit serves multiple rooms. 80–100 Pa static pressure for residential and commercial duct runs."),
        ("Reliable", "Auto pump, 1.8 m head", "Continuous drainage, water-leak sensor port, fault-indicator output, emergency stop button."),
    ],
    "GEC": [
        ("Commercial scale", "68 to 550 L/day", "Single chassis covers 800 to 5,000 sq ft with high-static-pressure ducted distribution."),
        ("Three-phase", "380V on 280+ models", "Industrial-grade electrical with multi-stage safety protection and inverter pump."),
        ("Smart control", "RS485 BMS · WiFi optional", "Modbus integration on every model. WiFi App on smaller GEC68 unit."),
        ("Sterile", "UV-C sterilisation", "Hospital-grade air sterilisation across the range. Stainless steel mesh filter."),
        ("Precision", "±1% RH control", "Tight humidity setpoint maintenance for galleries, archives, and quality-controlled environments."),
        ("Safety-first", "Multi-layer protection", "Water-leak sensor port, fault-indicator output, emergency stop, water-full alarm."),
    ],
    "GEX": [
        ("Restoration-grade", "75 to 110 L/day LGR", "Low-grain refrigerant design drives RH below 35% — the standard for water damage recovery."),
        ("Stackable", "Easy fleet transport", "Designed to stack 2-3 high in trucks. Maximises operator vehicle capacity."),
        ("Rugged", "LLDPE housing", "Impact-resistant polymer chassis. Survives years of jobsite handling and weather."),
        ("Mobile", "Fold-down handle, wheels", "Roll into any space. Retractable handle for tight transport and storage."),
        ("Smart diagnostics", "WiFi App included", "Remote monitoring of working hours, coil temperature, compressor current, total power consumption."),
        ("Eco refrigerant", "R290 low-GWP", "Natural refrigerant with global warming potential of just 3 — meets EU F-Gas regulations."),
    ],
    "GE": [
        ("Industrial-grade", "280 to 550 L/day", "Single-unit coverage of 3,000 to 5,000 sq ft for warehouses, switchgear rooms, and production floors."),
        ("Stainless steel", "Corrosion-proof tank", "316-grade stainless tank handles aggressive industrial environments."),
        ("Heavy-duty drain", "10 m pump head", "Inverter DC drain pump with 15,000-hour rated lifetime. Service-friendly access."),
        ("Three-phase", "380V industrial power", "Multi-stage protection: phase, surge, overcurrent, overheat — all standard."),
        ("Smart control", "BMS RS485 + dry contact", "Modbus integration with central building management. Real-time temperature and humidity display."),
        ("Filter-protected", "Dust filter intake", "Easily replaceable filter prevents particulate ingress in dirty industrial environments."),
    ],
    "HC": [
        ("Two-way control", "Add or remove moisture", "Holds tight RH bands across seasonal swings — single setpoint, automatic mode switching."),
        ("Wet-membrane humidify", "Isenthalpic, clean", "Evaporative humidification adds moisture without adding heat. Self-cleaning tank and membrane."),
        ("Filtered water", "Built-in filter", "Mineral and particulate filtration on inlet water — extends humidification cartridge life."),
        ("UV-C sterilisation", "Sterile output", "UV-C lamp on dehumidify circuit ensures pathogen-free air return."),
        ("Heritage-grade", "±2% RH precision", "Suitable for galleries, museums, archives, wine cellars, and data centre humidity envelopes."),
        ("BMS integrated", "RS485 + dry contact", "Modbus protocol for centralised setpoint, alarming, and runtime telemetry."),
    ],
    "DD": [
        ("Below-freezing", "Operates from −20°C", "Silica honeycomb desiccant rotor adsorbs water vapour where compressor systems frost over."),
        ("Ultra-low RH", "1 to 90% range", "Drives spaces below 1% RH for lithium battery production and pharmaceutical packing."),
        ("ProFlute rotor", "Long-life desiccant", "Patented honeycomb rotor with high water-vapour adsorption capacity. Field-replaceable."),
        ("PTC heater", "Ceramic reactivation", "Self-regulating positive-temperature-coefficient heater for stable rotor regeneration."),
        ("Data logging", "On-board RH log", "7-inch LCD displays current RH, setpoint, and historical log. Exportable via RS485."),
        ("Multi-stage safety", "Phase + surge + overcurrent", "Industrial-grade protection rated for 24/7 critical-environment operation."),
    ],
    "DH": [
        ("Compact", "Mobile chassis", "Caster wheels for easy room-to-room repositioning. Small footprint."),
        ("HEPA + Plasma", "Air purification", "True HEPA filter removes PM2.5; plasma purifier eliminates bacteria. Dehumidify and clean simultaneously."),
        ("WiFi App", "Phone control", "Remote start/stop, schedule, and humidity monitoring from a mobile device."),
        ("Continuous drain", "Pump or hose", "Auto pump drainage or continuous drain hose for unattended operation."),
        ("Auto defrost", "Always running", "Continuous operation in cool conditions without ice buildup."),
        ("Child lock", "Family-safe", "Locks the control panel against accidental adjustments — ideal for family homes."),
    ],
}

# ============================================================
# Helpers (re-implemented for the new template)
# ============================================================
def find_related(current_slug, current_series, n=3):
    return [p for p in PRODUCTS if p["series"] == current_series and p["slug"] != current_slug][:n]

def slug_to_path(slug):
    return f"products/{slug}.html"

def jsonld(product):
    series = SERIES[product["series"]]
    data = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": product["model"],
        "description": product["intro"],
        "brand": {"@type": "Brand", "name": "DBA"},
        "manufacturer": {
            "@type": "Organization",
            "name": "DBA Electric Pte. Ltd.",
            "url": "https://dba.sg"
        },
        "category": series["name"] + " Dehumidifier",
        "image": f"{SITE_URL}/images/{product['image']}",
        "url": f"{SITE_URL}/{slug_to_path(product['slug'])}",
        "sku": product["model"],
    }
    if product.get("price_usd"):
        data["offers"] = {
            "@type": "Offer",
            "priceCurrency": "USD",
            "price": str(product["price_usd"]),
            "availability": "https://schema.org/InStock",
            "seller": {"@type": "Organization", "name": "DBA Electric Pte. Ltd."}
        }
    return json.dumps(data, indent=2)

def breadcrumb_jsonld(product):
    series = SERIES[product["series"]]
    items = [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE_URL + "/"},
        {"@type": "ListItem", "position": 2, "name": "Products", "item": SITE_URL + "/#products"},
        {"@type": "ListItem", "position": 3, "name": series["name"], "item": SITE_URL + f"/#products"},
        {"@type": "ListItem", "position": 4, "name": product["model"], "item": SITE_URL + "/" + slug_to_path(product["slug"])},
    ]
    return json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items}, indent=2)

# ============================================================
# Page builder — using string concatenation to avoid f-string nesting issues
# ============================================================
def build_page(product):
    s = SERIES[product["series"]]
    related = find_related(product["slug"], product["series"], 3)
    series_models = [p for p in PRODUCTS if p["series"] == product["series"]]

    title = f"{product['model']} · {s['name']} Dehumidifier | Ervee"
    desc = f"{product['model']} {s['name']} dehumidifier — {product['tagline']} {product['key_stats'][0][1]} capacity. Manufactured by DBA Electric Pte. Ltd. International distribution by Ervee."
    desc = re.sub(r"\s+", " ", desc).strip()[:160]

    # Stats strip
    stats_html = "".join(
        f'<div class="ph-stat"><span class="ps-val">{html.escape(v)}</span><span class="ps-label">{html.escape(l)}</span></div>'
        for l, v in product["key_stats"]
    )

    # Hero bullets
    bullets_html = "".join(
        f'<li><strong>{html.escape(l)}:</strong> {html.escape(v)}</li>'
        for l, v in product["key_stats"]
    )

    # Benefits
    benefits = BENEFITS.get(product["series"], [])
    benefits_html = "".join(
        '<div class="ph-benefit reveal">'
        f'<div class="pb-tag">{html.escape(b[0])}</div>'
        f'<h3>{html.escape(b[1])}</h3>'
        f'<p>{html.escape(b[2])}</p>'
        '</div>'
        for b in benefits
    )

    # Specs
    specs_html = "".join(
        f'<tr><td>{html.escape(l)}</td><td>{v}</td></tr>'
        for l, v in product["specs"]
    )

    # In-the-box (config + control)
    config_html = "".join(f'<li>{x}</li>' for x in s["config"])
    control_html = "".join(f'<li>{x}</li>' for x in s["control"])

    # Use case pills
    cases_html = "".join(f'<span class="case-pill">{html.escape(c)}</span>' for c in product["use_cases"])

    # Comparison table within series
    compare_section = ""
    if len(series_models) > 1:
        cmp_header = "<tr><th></th>"
        for p in series_models:
            cls = " class=\"current\"" if p["slug"] == product["slug"] else ""
            cmp_header += f'<th{cls}>{p["model"]}</th>'
        cmp_header += "</tr>"

        cmp_rows = ""
        labels = [l for l, _ in product["key_stats"]]
        for label in labels:
            cmp_rows += f'<tr><td class="cmp-label">{html.escape(label)}</td>'
            for p in series_models:
                v = next((vv for ll, vv in p["key_stats"] if ll == label), "—")
                cls = " class=\"current\"" if p["slug"] == product["slug"] else ""
                cmp_rows += f'<td{cls}>{html.escape(v)}</td>'
            cmp_rows += "</tr>"

        compare_section = f"""
  <section id="compare" class="ph-compare">
    <div class="container">
      <div class="section-head reveal">
        <p class="eyebrow">Compare in series</p>
        <h2>{product['model']} vs the rest of the {s['name']} range.</h2>
      </div>
      <div class="cmp-wrap reveal">
        <table class="cmp-table">{cmp_header}{cmp_rows}</table>
      </div>
    </div>
  </section>"""

    # Related cards
    related_section = ""
    if related:
        rel_html = ""
        for r in related:
            r_stat = r["key_stats"][0]
            rel_html += (
                f'<a href="{r["slug"]}.html" class="related-card">'
                f'<div class="rc-img"><img src="../images/{r["image"]}" alt="{r["model"]}" loading="lazy" /></div>'
                f'<div class="rc-body">'
                f'<p class="rc-meta">{s["name"]}</p>'
                f'<h4>{r["model"]}</h4>'
                f'<p class="rc-stat">{r_stat[1]} {r_stat[0].lower()}</p>'
                f'<span class="rc-link">View →</span>'
                f'</div></a>'
            )
        related_section = f"""
  <section class="ph-related">
    <div class="container">
      <div class="section-head reveal">
        <p class="eyebrow">Other models</p>
        <h2>The rest of the {s['name']} range.</h2>
      </div>
      <div class="ph-related-grid reveal">{rel_html}</div>
    </div>
  </section>"""

    # Catalogue link
    cat_link = ""
    if s.get("catalog"):
        cat_link = f'<a href="../{s["catalog"]}" download class="catalog-link">↓ Download {s["name"]} catalogue (PDF)</a>'
    else:
        cat_link = '<p class="ph-no-catalog">Catalogue available on request via the <a href="../index.html#contact">contact form</a>.</p>'

    # Price pill
    price_pill = ""
    if product.get("price_label"):
        price_pill = f'<span class="ph-price-pill">{product["price_label"]}</span>'

    # Product FAQ
    range_low = series_models[0]["key_stats"][0][1]
    range_hi = series_models[-1]["key_stats"][0][1]
    energy_label = "Selected models also carry Hong Kong Grade 1 Energy Label." if product["series"] == "UTC" else ""
    pfaq_html = f"""
        <details class="pfaq-item"><summary>How does {product['model']} compare to other models in the {s['name']} range?</summary>
          <p>{product['model']} is positioned at {product['key_stats'][0][1]} capacity within the {s['name']} family that spans {range_low} to {range_hi}. Use the comparison table above to evaluate against the other models in the same series.</p>
        </details>
        <details class="pfaq-item"><summary>What is included in the standard package?</summary>
          <p>Standard packaging includes the {product['model']} unit, mounting hardware, drainage hose, power cable, control panel with cable, remote controller (where applicable), and operating manual. Specific in-the-box contents are listed in the configuration table on this page.</p>
        </details>
        <details class="pfaq-item"><summary>What certifications does {product['model']} carry?</summary>
          <p>All DBA dehumidifiers carry CE marking for European market access, the CB scheme for international electrical-safety reciprocity, ISO 9001 quality certification, and RoHS compliance. {energy_label}</p>
        </details>
        <details class="pfaq-item"><summary>What warranty applies?</summary>
          <p>Standard manufacturer warranty is 12 months from invoice date for parts and labour. Extended warranty options are available through dealer networks. Spare parts are stocked in Singapore for 7+ years from model phase-out.</p>
        </details>
        <details class="pfaq-item"><summary>Is {product['model']} available for OEM/ODM programmes?</summary>
          <p>Yes. Available customisations include voltage variants (110V 60Hz, 220-240V 50Hz, 380V 3-phase), plug types, label and packaging changes, custom enclosure colours, and (for sufficient volumes) bespoke control firmware. Submit project details via the <a href="../index.html#contact">contact form</a>.</p>
        </details>
        <details class="pfaq-item"><summary>How does shipping work for international orders?</summary>
          <p>Ervee handles FCL container loads and LCL part-shipments from Singapore and Hong Kong worldwide. Standard models in stock typically ship within 5-10 business days; made-to-order configurations take 4-6 weeks; bespoke OEM/ODM with custom firmware takes 8-12 weeks for first runs.</p>
        </details>"""

    # ============== ASSEMBLE PAGE ==============
    out = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{html.escape(title)}</title>
  <meta name="description" content="{html.escape(desc)}" />
  <meta name="keywords" content="{product['model']}, DBA dehumidifier, {s['name']}, dehumidifier supplier, OEM dehumidifier, dealer, wholesale, international shipping" />
  <link rel="canonical" href="{SITE_URL}/{slug_to_path(product['slug'])}" />

  <meta property="og:type" content="product" />
  <meta property="og:title" content="{html.escape(product['model'])} — {html.escape(product['tagline'])}" />
  <meta property="og:description" content="{html.escape(desc)}" />
  <meta property="og:url" content="{SITE_URL}/{slug_to_path(product['slug'])}" />
  <meta property="og:image" content="{SITE_URL}/images/{product['image']}" />
  <meta property="og:site_name" content="Ervee" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{html.escape(product['model'])} — Ervee" />
  <meta name="twitter:description" content="{html.escape(desc)}" />
  <meta name="twitter:image" content="{SITE_URL}/images/{product['image']}" />

  <script type="application/ld+json">{jsonld(product)}</script>
  <script type="application/ld+json">{breadcrumb_jsonld(product)}</script>

  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="../style.css" />
  <link rel="stylesheet" href="../product.css" />
</head>
<body class="product-page">

  <nav id="nav">
    <div class="nav-inner">
      <a href="../index.html" class="logo"><img src="../images/logo-ervee.svg" alt="Ervee" /></a>
      <ul class="nav-links">
        <li><a href="../index.html#products">Products</a></li>
        <li><a href="../index.html#industries">Industries</a></li>
        <li><a href="../index.html#why-dba">Why DBA</a></li>
        <li><a href="../index.html#partner">Partnership</a></li>
        <li><a href="../index.html#contact" class="nav-cta">Contact</a></li>
      </ul>
      <button class="nav-mobile-btn" onclick="toggleNav()" aria-label="Menu"><span></span><span></span><span></span></button>
    </div>
    <ul class="mobile-nav" id="mobileNav">
      <li><a href="../index.html#products" onclick="toggleNav()">Products</a></li>
      <li><a href="../index.html#industries" onclick="toggleNav()">Industries</a></li>
      <li><a href="../index.html#why-dba" onclick="toggleNav()">Why DBA</a></li>
      <li><a href="../index.html#partner" onclick="toggleNav()">Partnership</a></li>
      <li><a href="../index.html#contact" onclick="toggleNav()">Contact</a></li>
    </ul>
  </nav>

  <div class="breadcrumb">
    <div class="container">
      <a href="../index.html">Home</a><span>›</span><a href="../index.html#products">Products</a><span>›</span><a href="../index.html#products">{html.escape(s['name'])}</a><span>›</span><span class="bc-current">{html.escape(product['model'])}</span>
    </div>
  </div>

  <div class="sub-nav">
    <div class="container">
      <a href="#overview">Overview</a>
      <a href="#features">Features</a>
      <a href="#specs">Specs</a>
      <a href="#compare">Compare</a>
      <a href="#downloads">Downloads</a>
      <a href="#faq">FAQ</a>
      <a href="../index.html#contact" class="sn-cta">Get a quote</a>
    </div>
  </div>

  <section class="ph-hero" id="overview">
    <div class="container">
      <div class="ph-grid">
        <div class="ph-img reveal-img">
          <img src="../images/{product['image']}" alt="{product['model']} {s['name']} dehumidifier" />
        </div>
        <div class="ph-text">
          <p class="series-eyebrow reveal">{html.escape(s['name'])} · {product['series']} Series</p>
          <h1 class="reveal">{html.escape(product['model'])}</h1>
          <p class="ph-tagline reveal">{html.escape(product['tagline'])}</p>
          <ul class="ph-bullets reveal">{bullets_html}</ul>
          {price_pill}
          <div class="ph-actions reveal">
            <a href="../index.html#contact" class="btn-pill">Request a quote</a>
            <a href="https://wa.me/6589859886" target="_blank" rel="noopener" class="btn-text">WhatsApp Singapore →</a>
          </div>
          <p class="ph-trust reveal">Manufactured by DBA Electric Pte. Ltd. · CE · CB · ISO 9001 · RoHS</p>
        </div>
      </div>
    </div>
  </section>

  <section class="ph-stats-bar">
    <div class="container">
      <div class="ph-stats reveal">{stats_html}</div>
    </div>
  </section>

  <section class="ph-overview">
    <div class="container">
      <div class="po-grid reveal">
        <div class="po-left">
          <p class="eyebrow">Overview</p>
          <h2>{html.escape(product['intro'])}</h2>
        </div>
        <div class="po-body">
          <p>The {product['model']} is part of the {s['name']} family — {s['lead']}</p>
          <p>It is engineered, tested, and manufactured at DBA Electric Pte. Ltd., a Singapore-headquartered humidity-control specialist with over twenty years of design and production experience. Every unit ships with international certifications (CE, CB, ISO 9001, RoHS) and is supported by a 12-month manufacturer warranty.</p>
          <p>Ervee handles international distribution: dealer agreements, OEM/ODM partnerships, container-load shipping, and direct enterprise inquiries from outside the Singapore and Hong Kong domestic markets.</p>
        </div>
      </div>
    </div>
  </section>

  <section class="ph-benefits" id="features">
    <div class="container">
      <div class="section-head reveal">
        <p class="eyebrow">Why specify {product['model']}</p>
        <h2>Six reasons it ships internationally.</h2>
      </div>
      <div class="ph-benefit-grid">{benefits_html}</div>
    </div>
  </section>

  <section class="ph-banner">
    <div class="container">
      <div class="ph-banner-inner reveal">
        <img src="../images/{product['image_alt']}" alt="{product['model']} detail" />
        <div class="ph-banner-text">
          <p class="ph-banner-eyebrow">DBA Electric Pte. Ltd.</p>
          <h2>Engineered in Singapore.<br />Distributed worldwide.</h2>
          <p>Every {product['model']} is built to international standards by DBA — a humidity-control specialist with two decades of manufacturing experience. Ervee distributes the full range to dealers, OEM partners, and direct buyers worldwide.</p>
          <a href="https://dba.sg" target="_blank" rel="noopener" class="btn-pill outline">Visit dba.sg ↗</a>
        </div>
      </div>
    </div>
  </section>

  <section class="ph-box">
    <div class="container">
      <div class="section-head reveal">
        <p class="eyebrow">In the box</p>
        <h2>What ships with {product['model']}.</h2>
        <p class="lead">Standard configuration across the {s['name']} series.</p>
      </div>
      <div class="ph-box-grid reveal">
        <div class="ph-box-col">
          <h3>Configuration</h3>
          <ul>{config_html}</ul>
        </div>
        <div class="ph-box-col">
          <h3>Control matrix</h3>
          <ul>{control_html}</ul>
        </div>
      </div>
    </div>
  </section>

  <section class="ph-specs" id="specs">
    <div class="container">
      <div class="section-head reveal">
        <p class="eyebrow">Technical data</p>
        <h2>Full specifications.</h2>
      </div>
      <div class="ph-spec-wrap reveal">
        <table class="ph-spec-table">{specs_html}</table>
      </div>
    </div>
  </section>
{compare_section}

  <section class="ph-cases">
    <div class="container">
      <div class="section-head reveal">
        <p class="eyebrow">Where it ships</p>
        <h2>Built for these spaces.</h2>
      </div>
      <div class="ph-case-pills reveal">{cases_html}</div>
    </div>
  </section>

  <section class="ph-downloads" id="downloads">
    <div class="container">
      <div class="section-head reveal">
        <p class="eyebrow">Resources</p>
        <h2>Downloads.</h2>
      </div>
      <div class="ph-dl-row reveal">{cat_link}</div>
    </div>
  </section>

  <section class="ph-faq" id="faq">
    <div class="container narrow">
      <div class="section-head reveal">
        <p class="eyebrow">Common questions</p>
        <h2>About {product['model']}.</h2>
      </div>
      <div class="pfaq-list reveal">{pfaq_html}</div>
    </div>
  </section>

  <section class="ph-warranty">
    <div class="container">
      <div class="ph-warranty-grid reveal">
        <div class="ph-w-card">
          <div class="phw-icon">⌬</div>
          <h3>12-month warranty</h3>
          <p>Standard manufacturer warranty from invoice date — parts and labour. Extended options through dealer networks.</p>
        </div>
        <div class="ph-w-card">
          <div class="phw-icon">⌹</div>
          <h3>7+ year spares</h3>
          <p>Spare parts stocked in Singapore for at least 7 years from model phase-out date. Long product lifecycle support.</p>
        </div>
        <div class="ph-w-card">
          <div class="phw-icon">⌗</div>
          <h3>Technical support</h3>
          <p>Engineering support direct from the factory. Sizing tools, training, and marketing assets for dealer partners.</p>
        </div>
        <div class="ph-w-card">
          <div class="phw-icon">⌭</div>
          <h3>OEM/ODM ready</h3>
          <p>Custom voltage, plug types, labels, packaging, enclosure colours, and (for volumes) bespoke firmware.</p>
        </div>
      </div>
    </div>
  </section>
{related_section}

  <section class="ph-cta">
    <div class="container narrow center">
      <h2 class="reveal">Specify {product['model']} for your project.</h2>
      <p class="lead reveal">Tell us about your market, project, or distribution interest. A specialist colleague replies within one business day.</p>
      <div class="ph-cta-actions reveal">
        <a href="../index.html#contact" class="btn-pill primary">Request a quote</a>
        <a href="https://wa.me/6589859886" target="_blank" rel="noopener" class="btn-pill outline">WhatsApp · +65 8985 9886</a>
      </div>
      <p class="ph-cta-foot reveal">Or reach the Hong Kong office: <a href="tel:+85225411611">+852 2541 1611</a> · <a href="mailto:dba@dba.hk">dba@dba.hk</a></p>
    </div>
  </section>

  <footer>
    <div class="container">
      <div class="footer-top">
        <div class="footer-brand">
          <img src="../images/logo-ervee.svg" alt="Ervee" class="footer-logo-img" />
          <p>The international showcase for DBA dehumidifier technology.</p>
          <div class="footer-network">
            <a href="https://dba.sg" target="_blank" rel="noopener">dba.sg</a>
            <a href="https://www.dba.hk" target="_blank" rel="noopener">dba.hk</a>
            <a href="https://www.dryeaz.hk" target="_blank" rel="noopener">dryeaz.hk</a>
            <a href="https://www.dryeaz.sg" target="_blank" rel="noopener">dryeaz.sg</a>
          </div>
        </div>
        <div class="footer-cols">
          <div class="fcol">
            <h4>Range</h4>
            <ul>
              <li><a href="../index.html#products">UTC · Ultra-slim ceiling</a></li>
              <li><a href="../index.html#products">GEC · Commercial ceiling</a></li>
              <li><a href="../index.html#products">GEX · Portable LGR</a></li>
              <li><a href="../index.html#products">GE · Industrial floor</a></li>
              <li><a href="../index.html#products">HC · Humidity control</a></li>
              <li><a href="../index.html#products">DD · Desiccant rotary</a></li>
            </ul>
          </div>
          <div class="fcol">
            <h4>Singapore HQ</h4>
            <ul>
              <li><a href="https://dba.sg" target="_blank" rel="noopener">dba.sg</a></li>
              <li><a href="mailto:dba@dba.sg">dba@dba.sg</a></li>
              <li><a href="tel:+6567729962">+65 6772 9962</a></li>
              <li><a href="https://wa.me/6589859886" target="_blank" rel="noopener">WhatsApp +65 8985 9886</a></li>
            </ul>
          </div>
          <div class="fcol">
            <h4>Hong Kong Office</h4>
            <ul>
              <li><a href="https://www.dba.hk" target="_blank" rel="noopener">dba.hk</a></li>
              <li><a href="mailto:dba@dba.hk">dba@dba.hk</a></li>
              <li><a href="tel:+85225411611">+852 2541 1611</a></li>
              <li><a href="https://wa.me/85254880850" target="_blank" rel="noopener">WhatsApp +852 5488 0850</a></li>
            </ul>
          </div>
        </div>
      </div>
      <div class="footer-bottom">© 2026 Ervee. International showcase for DBA Electric Pte. Ltd. dehumidifier technology.</div>
    </div>
  </footer>

  <script src="../script.js"></script>
</body>
</html>
"""
    return out

# ============================================================
# Sitemap
# ============================================================
def render_sitemap():
    today = date.today().isoformat()
    urls = [
        (SITE_URL + "/", "1.0"),
        (SITE_URL + "/#products", "0.9"),
        (SITE_URL + "/#industries", "0.8"),
        (SITE_URL + "/#why-dba", "0.8"),
        (SITE_URL + "/#partner", "0.8"),
        (SITE_URL + "/#guide", "0.8"),
        (SITE_URL + "/#catalogs", "0.7"),
        (SITE_URL + "/#faq", "0.7"),
        (SITE_URL + "/#contact", "0.7"),
    ]
    for p in PRODUCTS:
        urls.append((f"{SITE_URL}/{slug_to_path(p['slug'])}", "0.9"))
    body = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/0.9/sitemap.xsd">\n'
    for u, prio in urls:
        body += f"  <url><loc>{u}</loc><lastmod>{today}</lastmod><priority>{prio}</priority></url>\n"
    body += "</urlset>\n"
    return body

# ============================================================
# Main
# ============================================================
def main():
    out = ROOT / "products"
    out.mkdir(exist_ok=True)
    for p in PRODUCTS:
        path = out / f"{p['slug']}.html"
        path.write_text(build_page(p))
    (ROOT / "sitemap.xml").write_text(render_sitemap())
    print(f"Generated {len(PRODUCTS)} Ervee product pages + sitemap.xml")

if __name__ == "__main__":
    main()
