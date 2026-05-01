#!/usr/bin/env python3
"""Generate per-product pages, sitemap, and updated homepage product links."""

import json, os, re, html
from pathlib import Path
from datetime import date

ROOT = Path(__file__).resolve().parent.parent
SITE_URL = "https://ervee-com.onrender.com"  # update when custom domain is live

# ============================================================
# SHARED SERIES DATA
# ============================================================
SERIES = {
    "UTC": {
        "name": "Ultra-Slim Ceiling",
        "slug": "utc",
        "tagline": "Hidden in the ceiling. Felt everywhere.",
        "lead": "A 20cm slim profile that disappears into the ceiling void. WiFi App, RS485 BMS, and UV-C sterilisation standard across the range.",
        "catalog": "catalogs/dba-utc-ultra-thin-ceiling.pdf",
        "config": [
            "Auto pump drainage · 1.8 m head",
            "UV-C sterilisation lamp",
            "Stainless steel mesh filter",
            "Cold-rolled steel casing",
            "Emergency stop button",
            "5 m humidity sensor cable",
            "8 m LCD control panel cable",
            "Remote controller included",
        ],
        "control": [
            "Set humidity range 20–95%",
            "Low / High fan speed",
            "Fan and dehumidifying modes",
            "Scheduled on/off timer",
            "Power-off memory function",
            "WiFi App control",
            "BMS RS485 (Modbus)",
            "Dry contact + water-leak port",
        ],
        "highlights": [
            ("⌖", "20cm Ultra-Slim", "Hidden ceiling install"),
            ("🌬", "Whole-House Coverage", "Ducted distribution"),
            ("🔇", "Whisper Quiet", "39–50 dB(A)"),
            ("🦠", "UV-C Sterilisation", "99.9% pathogen kill"),
            ("📱", "WiFi + BMS", "App and Modbus"),
            ("⚡", "Energy Saving", "Inverter compressor"),
        ],
    },
    "GEC": {
        "name": "Commercial Ceiling",
        "slug": "gec",
        "tagline": "Commercial-scale humidity, ducted.",
        "lead": "Higher static pressure and capacity for large floors and multi-room ducted systems. RS485 BMS standard; WiFi App on smaller models.",
        "catalog": "catalogs/dba-gec-commercial-ceiling.pdf",
        "config": [
            "Drain pump (68 / 145 models)",
            "UV-C sterilisation lamp",
            "Stainless steel mesh filter",
            "Cold-rolled steel casing",
            "Emergency stop button",
            "LCD control panel + remote",
            "5 m humidity sensor cable",
            "8 m control panel cable",
        ],
        "control": [
            "Set humidity range 20–95%",
            "Fan and dehumidifying modes",
            "Scheduled on/off timer",
            "Fault detection &amp; diagnosis",
            "Power-off memory function",
            "BMS RS485 (Modbus)",
            "Water-leak sensor port",
            "Fault indicator output 220V 6A",
        ],
        "highlights": [
            ("⌧", "High Static Pressure", "Long ducted runs"),
            ("⌬", "BMS Integrated", "RS485 Modbus"),
            ("◉", "Precision ±1% RH", "Rock-stable control"),
            ("⌗", "Multi-Zone", "One unit, many rooms"),
            ("🦠", "UV-C Lamp", "Pathogen sterilisation"),
            ("⚙", "Auto Defrost", "Continuous operation"),
        ],
    },
    "GEX": {
        "name": "Portable LGR",
        "slug": "gex",
        "tagline": "Roll in. Dry out. Move on.",
        "lead": "LGR restoration dehumidifiers built for water damage, flood recovery, and construction site dry-out. Stackable, ruggedised, WiFi-controlled.",
        "catalog": "catalogs/dba-gex-portable-restoration.pdf",
        "config": [
            "Pump drainage · 5 m head",
            "Dust filter · washable / replaceable",
            "LLDPE rugged housing",
            "Rubber wheels + metal handle",
            "5 m drain hose included",
            "5 m Type G power cable",
            "External ducting flange",
            "Stackable for transport",
        ],
        "control": [
            "Set humidity range 30–90%",
            "Manual purge button",
            "Display: working hours",
            "Display: air in/out + coil temp",
            "Display: compressor current",
            "Display: total power consumption",
            "°C / °F selection",
            "WiFi App + power-off memory",
        ],
        "highlights": [
            ("⌬", "LGR Technology", "Drives RH below 35%"),
            ("⌥", "No Install Needed", "5 m cable + 5 m hose"),
            ("⌘", "Wheels + Handle", "Roll into any space"),
            ("⌭", "Stackable", "Easy fleet transport"),
            ("📱", "WiFi App", "Full diagnostics on phone"),
            ("⌹", "Pump Drain 5 m", "Continuous operation"),
        ],
    },
    "GE": {
        "name": "Industrial Floor",
        "slug": "ge",
        "tagline": "Industrial workhorse. Stainless steel.",
        "lead": "Heavy-duty floor-standing dehumidifiers for warehouses, factories, and large facilities. 10 m drain head, three-phase power, BMS-integrated.",
        "catalog": "catalogs/dba-ge-hc-dd-commercial.pdf",
        "config": [
            "Drain pump · 10 m head",
            "Dust filter",
            "Cold-rolled steel casing",
            "Emergency stop button",
            "LCD control panel",
            "3 m drain hose",
            "5 m power cable",
            "Operating range 1–40°C",
        ],
        "control": [
            "Set humidity range 20–95%",
            "Manual purge button",
            "Low / High fan speed",
            "Fan and dehumidifying modes",
            "Scheduled on/off timer",
            "Fault detection",
            "Power-off memory function",
            "BMS RS485 + dry contact",
        ],
        "highlights": [
            ("⌧", "Stainless Tank", "Corrosion-proof"),
            ("⌬", "10 m Drain Head", "15,000-hr pump life"),
            ("◉", "Three-Phase 380V", "Industrial power"),
            ("⌗", "5,000–6,000 sq ft", "Single-unit coverage"),
            ("⚙", "BMS RS485", "Modbus integration"),
            ("⌹", "LCD + Diagnostics", "Real-time T/RH"),
        ],
    },
    "HC": {
        "name": "Humidity Control Unit",
        "slug": "hc",
        "tagline": "Add. Remove. Hold.",
        "lead": "Two-way humidity control units. Wet-membrane evaporative humidification combined with refrigerant dehumidification — hold a precise RH band for galleries, archives, wine cellars, data centres, and labs.",
        "catalog": "catalogs/dba-ge-hc-dd-commercial.pdf",
        "config": [
            "Drain pump",
            "UV-C sterilisation lamp",
            "Dust filter",
            "Emergency stop button",
            "LCD control panel",
            "5 m power cable",
            "Self-cleaning water tank",
            "Filtered water input",
        ],
        "control": [
            "Set humidity range 20–95%",
            "Manual purge button",
            "Auto / Humidify / Dehumidify modes",
            "Scheduled on/off timer",
            "Fault detection",
            "Power-off memory function",
            "BMS RS485 + dry contact",
            "Water-leak sensor port",
        ],
        "highlights": [
            ("◉", "Two-Way Control", "Add or remove moisture"),
            ("⌬", "±2% RH Stability", "Gallery-grade precision"),
            ("⌧", "Wet-Membrane Humidify", "Isenthalpic, clean"),
            ("⌥", "UV-C + Filter", "Sterile output air"),
            ("⌹", "BMS RS485", "Centralised control"),
            ("⌭", "Self-Cleaning Tank", "Low maintenance"),
        ],
    },
    "DD": {
        "name": "Desiccant Rotary",
        "slug": "dd",
        "tagline": "Performance below freezing.",
        "lead": "'ProFlute' desiccant rotor with PTC ceramic reactivation heater. Operates from −20°C to 40°C, holds 1–90% RH — the choice for cold rooms, lithium battery production, and pharmaceuticals.",
        "catalog": "catalogs/dba-ge-hc-dd-commercial.pdf",
        "config": [
            "'ProFlute' desiccant rotor",
            "PTC ceramic heater",
            "7-inch LCD display panel",
            "Dust filter",
            "5 m power cable",
            "Operating range −20 to 40°C",
            "Process &amp; reactivation airflows",
            "Robust steel construction",
        ],
        "control": [
            "Set humidity range 1–90%",
            "Fault detection",
            "Humidity data log",
            "Power-off memory function",
            "BMS RS485 (Modbus)",
            "Multi-stage safety protection",
            "Phase &amp; surge protection",
            "Centralised remote control",
        ],
        "highlights": [
            ("❄", "−20°C Operation", "Below-freezing dehumidify"),
            ("◉", "1–90% RH Range", "Ultra-low humidity"),
            ("⌬", "ProFlute Rotor", "Silica honeycomb"),
            ("⌥", "PTC Heater", "Ceramic reactivation"),
            ("⌹", "7\" LCD Panel", "Data logging"),
            ("⌭", "BMS RS485", "Modbus integration"),
        ],
    },
    "DH": {
        "name": "Mobile Compressor",
        "slug": "dh",
        "tagline": "The everyday performer.",
        "lead": "Compact mobile units for residential and small commercial spaces. HEPA filtration, plasma purification, WiFi App control.",
        "catalog": None,
        "config": [
            "HEPA high-efficiency filter",
            "Plasma air purifier",
            "Auto pump drainage",
            "Anti-drip valve",
            "Caster wheels",
            "Continuous drainage hose",
            "LED display",
            "Child lock",
        ],
        "control": [
            "Set humidity range 30–80%",
            "Low / High fan speed",
            "WiFi App control",
            "24-hr scheduled timer",
            "Auto defrost",
            "Drainage fault protection",
            "LED status indicator",
            "Anti-bacterial filter",
        ],
        "highlights": [
            ("🌬", "HEPA Filtration", "Removes PM2.5"),
            ("⚡", "Plasma Purifier", "Eliminates pathogens"),
            ("📱", "WiFi App", "Remote control"),
            ("⌥", "Auto Defrost", "Continuous operation"),
            ("⌭", "Roll-Anywhere", "Caster wheels"),
            ("⌹", "Child Lock", "Safe for households"),
        ],
    },
}

# ============================================================
# PRODUCT DATA
# ============================================================
PRODUCTS = [
    # ===== UTC SERIES =====
    {
        "slug": "dba-utc20", "model": "DBA-UTC20", "series": "UTC",
        "image": "ceiling-dba-utc20-1.jpg",
        "image_alt": "ceiling-dba-utc20-2.jpg",
        "tagline": "20 L/day in 20 cm of plenum.",
        "intro": "The smallest of the Ultra-Slim Ceiling range. Designed for studio apartments, single bedrooms, and small offices where ceiling height is at a premium.",
        "key_stats": [
            ("Capacity", "20 L/day"),
            ("Coverage", "200 – 400 sq ft"),
            ("Noise", "39 dB(A)"),
            ("Weight", "28 kg"),
        ],
        "specs": [
            ("Dehumidifying Capacity (30°C 80% RH)", "20 L/day"),
            ("Dehumidifying Capacity (26.7°C 60% RH)", "9.9 L/day"),
            ("Cover Area", "200 – 400 sq ft"),
            ("Airflow", "220 CMH"),
            ("Sound Pressure Level (3 m)", "39 dB(A)"),
            ("Static Pressure", "80 Pa"),
            ("Rated Power", "196 W"),
            ("Max. Power", "300 W"),
            ("Voltage", "220–240V 50Hz"),
            ("Drain Height", "1.8 m"),
            ("Air Outlet/Inlet Flange", "⌀146 mm"),
            ("Refrigerant", "R134a / 0.23 kg"),
            ("Operating Temperature", "5 – 40°C"),
            ("Weight", "28 kg"),
            ("Dimensions (L × W × H)", "865 × 376 × 200 mm"),
        ],
        "use_cases": ["Studio apartments", "Walk-in closets", "Wine fridges", "Server cabinets", "Cigar humidors"],
    },
    {
        "slug": "dba-utc68", "model": "DBA-UTC68", "series": "UTC",
        "image": "ceiling-dba-utc68-1.jpg",
        "image_alt": "ceiling-dba-utc68-2.jpg",
        "tagline": "Whole-floor humidity from one ceiling unit.",
        "intro": "Mid-capacity Ultra-Slim ceiling unit. Sized for 2 to 3-bedroom apartments and small offices. Ducts dry air to multiple rooms quietly.",
        "key_stats": [
            ("Capacity", "68 L/day"),
            ("Coverage", "800 – 1,000 sq ft"),
            ("Noise", "48 dB(A)"),
            ("Weight", "42 kg"),
        ],
        "specs": [
            ("Dehumidifying Capacity (30°C 80% RH)", "68 L/day"),
            ("Dehumidifying Capacity (26.7°C 60% RH)", "42 L/day"),
            ("Cover Area", "800 – 1,000 sq ft"),
            ("Airflow", "500 CMH"),
            ("Sound Pressure Level (3 m)", "48 dB(A)"),
            ("Static Pressure", "100 Pa"),
            ("Rated Power", "880 W"),
            ("Max. Power", "1,250 W"),
            ("Voltage", "220–240V 50Hz"),
            ("Drain Height", "1.8 m"),
            ("Air Outlet/Inlet Flange", "⌀146 mm"),
            ("Refrigerant", "R410A / 0.6 kg"),
            ("Operating Temperature", "5 – 40°C"),
            ("Weight", "42 kg"),
            ("Dimensions (L × W × H)", "1,010 × 500 × 240 mm"),
        ],
        "use_cases": ["3-bedroom apartments", "Boutique retail", "Showrooms", "Pilates studios", "Yoga rooms"],
    },
    {
        "slug": "dba-utc120", "model": "DBA-UTC120", "series": "UTC",
        "image": "ceiling-dba-utc120-1.jpg",
        "image_alt": "ceiling-dba-utc120-2.jpg",
        "tagline": "120 L/day. Still under 32 cm tall.",
        "intro": "Largest of the Ultra-Slim range. Twin-intake design for higher airflow, sized for whole-house ducted systems and large open-plan offices.",
        "key_stats": [
            ("Capacity", "120 L/day"),
            ("Coverage", "1,300 – 1,500 sq ft"),
            ("Noise", "50 dB(A)"),
            ("Weight", "64 kg"),
        ],
        "specs": [
            ("Dehumidifying Capacity (30°C 80% RH)", "120 L/day"),
            ("Dehumidifying Capacity (26.7°C 60% RH)", "53 L/day"),
            ("Cover Area", "1,300 – 1,500 sq ft"),
            ("Airflow", "890 CMH"),
            ("Sound Pressure Level (3 m)", "50 dB(A)"),
            ("Static Pressure", "100 Pa"),
            ("Rated Power", "1,010 W"),
            ("Max. Power", "1,600 W"),
            ("Voltage", "220–240V 50Hz"),
            ("Drain Height", "1.8 m"),
            ("Air Outlet/Inlet Flange", "⌀196 mm × 2"),
            ("Refrigerant", "R410A / 0.9 kg"),
            ("Operating Temperature", "5 – 40°C"),
            ("Weight", "64 kg"),
            ("Dimensions (L × W × H)", "1,075 × 746 × 310 mm"),
        ],
        "use_cases": ["Whole-house systems", "Penthouses", "Open-plan offices", "Restaurants", "Hotel suites"],
    },
    # ===== GEC SERIES =====
    {
        "slug": "dba-gec68ld-hp", "model": "DBA-GEC68LD-HP", "series": "GEC",
        "image": "ceiling-dba-gec68ld-1.jpg",
        "image_alt": "ceiling-dba-gec68ld-2.jpg",
        "tagline": "Commercial-grade in a compact frame.",
        "intro": "Entry into the Commercial Ceiling range. Wi-Fi App control plus RS485 BMS. Ideal where you need commercial reliability in a residential footprint.",
        "key_stats": [
            ("Capacity", "68 L/day"),
            ("Coverage", "800 – 1,000 sq ft"),
            ("Noise", "49 dB(A)"),
            ("Weight", "44 kg"),
        ],
        "specs": [
            ("Dehumidifying Capacity (30°C 80% RH)", "68 L/day"),
            ("Dehumidifying Capacity (26.7°C 60% RH)", "33 L/day"),
            ("Cover Area", "800 – 1,000 sq ft"),
            ("Airflow", "500 CMH"),
            ("Sound Pressure Level (3 m)", "49 dB(A)"),
            ("Static Pressure", "100 Pa"),
            ("Rated Power", "730 W"),
            ("Max. Power", "940 W"),
            ("Voltage", "220–240V 50Hz"),
            ("Drain Height", "1.8 m"),
            ("Air Outlet/Inlet Flange", "⌀146 mm"),
            ("Refrigerant", "R410A / 0.4 kg"),
            ("Operating Temperature", "5 – 40°C"),
            ("Weight", "44 kg"),
            ("Dimensions (L × W × H)", "970 × 525 × 345 mm"),
            ("Connectivity", "WiFi App + RS485 Modbus"),
        ],
        "use_cases": ["Small offices", "Server rooms", "Studios", "Boutiques", "Specialty stores"],
    },
    {
        "slug": "dba-gec145ld-hp", "model": "DBA-GEC145LD-HP", "series": "GEC",
        "image": "ceiling-dba-gec145ld-1.jpg",
        "image_alt": "ceiling-dba-gec145ld-2.jpg",
        "tagline": "1,200 CMH for serious throughput.",
        "intro": "Mid-range commercial ceiling unit. RS485 BMS-ready with high static pressure for ducted distribution across larger floors.",
        "key_stats": [
            ("Capacity", "145 L/day"),
            ("Coverage", "1,500 – 1,700 sq ft"),
            ("Noise", "50 dB(A)"),
            ("Weight", "70 kg"),
        ],
        "specs": [
            ("Dehumidifying Capacity (30°C 80% RH)", "145 L/day"),
            ("Dehumidifying Capacity (26.7°C 60% RH)", "85 L/day"),
            ("Cover Area", "1,500 – 1,700 sq ft"),
            ("Airflow", "1,200 CMH"),
            ("Sound Pressure Level (3 m)", "50 dB(A)"),
            ("Static Pressure", "100 Pa"),
            ("Rated Power", "1,520 W"),
            ("Max. Power", "2,220 W"),
            ("Voltage", "220–240V 50Hz"),
            ("Drain Height", "1.8 m"),
            ("Air Outlet/Inlet Flange", "⌀196 mm"),
            ("Refrigerant", "R410A / 1.2 kg"),
            ("Operating Temperature", "5 – 40°C"),
            ("Weight", "70 kg"),
            ("Dimensions (L × W × H)", "1,005 × 695 × 440 mm"),
            ("Connectivity", "RS485 Modbus"),
        ],
        "use_cases": ["Mid-size offices", "Showrooms", "Yacht clubs", "Galleries", "Restaurants"],
    },
    {
        "slug": "dba-gec280ld", "model": "DBA-GEC280LD", "series": "GEC",
        "image": "ceiling-dba-gec280ld-1.jpg",
        "image_alt": "ceiling-dba-gec280ld-2.jpg",
        "tagline": "Three-phase ceiling power.",
        "intro": "Step into three-phase 380V territory. 1,700 CMH airflow drives dry air through extended duct runs to multi-room commercial floors.",
        "key_stats": [
            ("Capacity", "280 L/day"),
            ("Coverage", "2,500 – 3,000 sq ft"),
            ("Noise", "58 dB(A)"),
            ("Weight", "108 kg"),
        ],
        "specs": [
            ("Dehumidifying Capacity (30°C 80% RH)", "280 L/day"),
            ("Dehumidifying Capacity (26.7°C 60% RH)", "132 L/day"),
            ("Cover Area", "2,500 – 3,000 sq ft"),
            ("Airflow", "1,700 CMH"),
            ("Sound Pressure Level (3 m)", "58 dB(A)"),
            ("Static Pressure", "80 Pa"),
            ("Rated Power", "2,580 W"),
            ("Max. Power", "3,510 W"),
            ("Voltage", "380V 3N 50Hz"),
            ("Refrigerant", "R410A / 1.9 kg"),
            ("Operating Temperature", "5 – 40°C"),
            ("Weight", "108 kg"),
            ("Dimensions (L × W × H)", "1,137 × 900 × 540 mm"),
            ("Connectivity", "RS485 Modbus"),
        ],
        "use_cases": ["F&amp;B kitchens", "Hotel back-of-house", "Indoor pools", "Gym floors", "Function halls"],
    },
    {
        "slug": "dba-gec400ld", "model": "DBA-GEC400LD", "series": "GEC",
        "image": "ceiling-dba-gec400ld-1.jpg",
        "image_alt": "ceiling-dba-gec400ld-2.jpg",
        "tagline": "Twin-circuit performance.",
        "intro": "Dual refrigerant circuits deliver 400 L/day with redundancy. 3,250 CMH airflow makes this the default for large commercial floors and event venues.",
        "key_stats": [
            ("Capacity", "400 L/day"),
            ("Coverage", "3,000 – 4,000 sq ft"),
            ("Noise", "65 dB(A)"),
            ("Weight", "210 kg"),
        ],
        "specs": [
            ("Dehumidifying Capacity (30°C 80% RH)", "400 L/day"),
            ("Dehumidifying Capacity (26.7°C 60% RH)", "240 L/day"),
            ("Cover Area", "3,000 – 4,000 sq ft"),
            ("Airflow", "3,250 CMH"),
            ("Sound Pressure Level (3 m)", "65 dB(A)"),
            ("Static Pressure", "80 Pa"),
            ("Rated Power", "4,600 W"),
            ("Max. Power", "6,250 W"),
            ("Voltage", "380V 3N 50Hz"),
            ("Refrigerant", "R410A / 1.9 kg × 2"),
            ("Operating Temperature", "5 – 40°C"),
            ("Weight", "210 kg"),
            ("Dimensions (L × W × H)", "1,270 × 1,200 × 605 mm"),
            ("Connectivity", "RS485 Modbus"),
        ],
        "use_cases": ["Indoor pool halls", "Banquet venues", "Manufacturing floors", "Cold rooms", "Storage warehouses"],
    },
    {
        "slug": "dba-gec550ld", "model": "DBA-GEC550LD", "series": "GEC",
        "image": "ceiling-dba-gec550ld-1.jpg",
        "image_alt": "ceiling-dba-gec550ld-1.jpg",
        "tagline": "Top of the ceiling line.",
        "intro": "550 L/day from a single ceiling unit. Maximum capacity in the GEC range — for the largest ducted commercial systems.",
        "key_stats": [
            ("Capacity", "550 L/day"),
            ("Coverage", "4,000 – 5,000 sq ft"),
            ("Noise", "65 dB(A)"),
            ("Weight", "240 kg"),
        ],
        "specs": [
            ("Dehumidifying Capacity (30°C 80% RH)", "550 L/day"),
            ("Dehumidifying Capacity (26.7°C 60% RH)", "276 L/day"),
            ("Cover Area", "4,000 – 5,000 sq ft"),
            ("Airflow", "3,250 CMH"),
            ("Sound Pressure Level (3 m)", "65 dB(A)"),
            ("Static Pressure", "80 Pa"),
            ("Rated Power", "4,900 W"),
            ("Max. Power", "6,550 W"),
            ("Voltage", "380V 3N 50Hz"),
            ("Refrigerant", "R410A / 2.2 kg × 2"),
            ("Operating Temperature", "5 – 40°C"),
            ("Weight", "240 kg"),
            ("Dimensions (L × W × H)", "1,270 × 1,200 × 605 mm"),
            ("Connectivity", "RS485 Modbus"),
        ],
        "use_cases": ["Mega event halls", "Indoor sports facilities", "Large warehouses", "Aquatic centres", "Industrial drying"],
    },
    # ===== GEX SERIES =====
    {
        "slug": "dba-gex75", "model": "DBA-GEX75", "series": "GEX",
        "image": "mobile-dba-gex75-1.jpg",
        "image_alt": "mobile-dba-gex75-2.jpg",
        "tagline": "75 L/day. Wheels included.",
        "intro": "Compact LGR portable for restoration crews and small flood jobs. R290 refrigerant for low-GWP operation.",
        "key_stats": [
            ("Capacity", "75 L/day"),
            ("Coverage", "1,000 sq ft"),
            ("Noise", "55 dB(A)"),
            ("Weight", "29.2 kg"),
        ],
        "specs": [
            ("Dehumidifying Capacity (30°C 80% RH)", "75 L/day"),
            ("Dehumidifying Capacity (26.7°C 60% RH)", "35 L/day"),
            ("Cover Area", "1,000 sq ft"),
            ("Airflow", "420 CMH"),
            ("Sound Pressure Level (3 m)", "55 dB(A)"),
            ("Rated Power", "580 W"),
            ("Voltage", "220–240V 50Hz"),
            ("Drain Height", "5 m"),
            ("Air Outlet Flange", "⌀160 mm"),
            ("Refrigerant", "R290 / 0.2 kg"),
            ("Operating Temperature", "1 – 38°C"),
            ("Weight", "29.2 kg"),
            ("Dimensions (L × W × H)", "560 × 345 × 450 mm"),
        ],
        "use_cases": ["Flood recovery", "Post-leak drying", "Construction site dry-out", "Painting / drywall jobs", "Basement cleanup"],
    },
    {
        "slug": "dba-gex110", "model": "DBA-GEX110", "series": "GEX",
        "image": "mobile-dba-gex110-1.jpg",
        "image_alt": "mobile-dba-gex110-1.jpg",
        "tagline": "110 L/day. Big jobs, fast.",
        "intro": "Higher-capacity LGR for larger restoration scenes. 1,000 CMH airflow with full WiFi diagnostics.",
        "key_stats": [
            ("Capacity", "110 L/day"),
            ("Coverage", "1,500 sq ft"),
            ("Noise", "60 dB(A)"),
            ("Weight", "45 kg"),
        ],
        "specs": [
            ("Dehumidifying Capacity (30°C 80% RH)", "110 L/day"),
            ("Dehumidifying Capacity (26.7°C 60% RH)", "55 L/day"),
            ("Cover Area", "1,500 sq ft"),
            ("Airflow", "1,000 CMH"),
            ("Sound Pressure Level (3 m)", "60 dB(A)"),
            ("Rated Power", "950 W"),
            ("Voltage", "220–240V 50Hz"),
            ("Drain Height", "5 m"),
            ("Air Outlet Flange", "⌀220 mm"),
            ("Refrigerant", "R290 / 0.235 kg"),
            ("Operating Temperature", "1 – 38°C"),
            ("Weight", "45 kg"),
            ("Dimensions (L × W × H)", "705 × 445 × 530 mm"),
        ],
        "use_cases": ["Major flood recovery", "Whole-house water damage", "Commercial roof leaks", "Industrial spills", "Emergency drying"],
    },
    # ===== GE SERIES =====
    {
        "slug": "dba-ge280ld-hp", "model": "DBA-GE280LD-HP", "series": "GE",
        "image": "industrial-dba-ge280ld-1.jpg",
        "image_alt": "industrial-dba-ge280ld-2.jpg",
        "tagline": "Industrial floor power.",
        "intro": "Floor-standing industrial dehumidifier with stainless steel water tank and 10 m drain head. Single-circuit design for 3,000 sq ft spaces.",
        "key_stats": [
            ("Capacity", "280 L/day"),
            ("Coverage", "3,000 sq ft"),
            ("Drain Head", "10 m"),
            ("Weight", "160 kg"),
        ],
        "specs": [
            ("Dehumidifying Capacity (30°C 80% RH)", "280 L/day"),
            ("Dehumidifying Capacity (26.7°C 60% RH)", "144 L/day"),
            ("Cover Area", "3,000 sq ft"),
            ("Rated Power", "3,400 W"),
            ("Max. Power", "4,100 W"),
            ("Voltage", "380V 3N 50Hz"),
            ("Drain Height", "10 m"),
            ("Refrigerant", "R410A / 1.7 kg"),
            ("Operating Temperature", "1 – 40°C"),
            ("Weight", "160 kg"),
            ("Dimensions (L × W × H)", "820 × 465 × 1,775 mm"),
        ],
        "use_cases": ["Warehouses", "Switchgear rooms", "Manufacturing floors", "Storage facilities", "Logistics hubs"],
    },
    {
        "slug": "dba-ge400ld-hp", "model": "DBA-GE400LD-HP", "series": "GE",
        "image": "industrial-dba-ge400ld-1.jpg",
        "image_alt": "industrial-dba-ge400ld-1.jpg",
        "tagline": "Twin-circuit industrial muscle.",
        "intro": "Dual refrigerant circuits for redundancy and capacity. 4,000 sq ft coverage with industrial-grade reliability.",
        "key_stats": [
            ("Capacity", "400 L/day"),
            ("Coverage", "4,000 sq ft"),
            ("Drain Head", "10 m"),
            ("Weight", "230 kg"),
        ],
        "specs": [
            ("Dehumidifying Capacity (30°C 80% RH)", "400 L/day"),
            ("Dehumidifying Capacity (26.7°C 60% RH)", "228 L/day"),
            ("Cover Area", "4,000 sq ft"),
            ("Rated Power", "4,780 W"),
            ("Max. Power", "7,800 W"),
            ("Voltage", "380V 3N 50Hz"),
            ("Drain Height", "10 m"),
            ("Refrigerant", "R410A / 1.45 kg × 2"),
            ("Operating Temperature", "1 – 40°C"),
            ("Weight", "230 kg"),
            ("Dimensions (L × W × H)", "1,200 × 540 × 1,740 mm"),
        ],
        "use_cases": ["Large warehouses", "Cold storage", "Pharmaceutical packing", "Industrial drying", "Plant rooms"],
    },
    {
        "slug": "dba-ge550ld-hp", "model": "DBA-GE550LD-HP", "series": "GE",
        "image": "industrial-dba-ge550ld-1.jpg",
        "image_alt": "industrial-dba-ge550ld-2.jpg",
        "tagline": "550 L/day. Industrial flagship.",
        "intro": "The largest GE-series unit. Twin-circuit, 5,000 sq ft coverage, industrial-grade construction throughout.",
        "key_stats": [
            ("Capacity", "550 L/day"),
            ("Coverage", "5,000 sq ft"),
            ("Drain Head", "10 m"),
            ("Weight", "240 kg"),
        ],
        "specs": [
            ("Dehumidifying Capacity (30°C 80% RH)", "550 L/day"),
            ("Dehumidifying Capacity (26.7°C 60% RH)", "276 L/day"),
            ("Cover Area", "5,000 sq ft"),
            ("Rated Power", "5,450 W"),
            ("Max. Power", "8,300 W"),
            ("Voltage", "380V 3N 50Hz"),
            ("Drain Height", "10 m"),
            ("Refrigerant", "R410A / 1.65 kg × 2"),
            ("Operating Temperature", "1 – 40°C"),
            ("Weight", "240 kg"),
            ("Dimensions (L × W × H)", "1,200 × 540 × 1,740 mm"),
        ],
        "use_cases": ["Mega warehouses", "Cold storage chains", "Aquatic facilities", "Heavy manufacturing", "Distribution centres"],
    },
    # ===== HC SERIES =====
    {
        "slug": "dba-hc68", "model": "DBA-HC68", "series": "HC",
        "image": "humidistat-dba-hc68-1.png",
        "image_alt": "humidistat-dba-hc68-1.png",
        "tagline": "Two-way precision humidity, compact.",
        "intro": "Smallest of the Humidity Control range. Dehumidify 68 L/day or humidify 3 kg/hr — single unit, single setpoint.",
        "key_stats": [
            ("Dehumidify", "68 L/day"),
            ("Humidify", "3 kg/hr"),
            ("Coverage", "1,000 sq ft"),
            ("Weight", "150 kg"),
        ],
        "specs": [
            ("Dehumidifying Capacity (30°C 80% RH)", "68 L/day"),
            ("Humidifying Capacity", "3 kg/hr"),
            ("Cover Area", "1,000 sq ft"),
            ("Rated Power (Dehumidify)", "780 W"),
            ("Rated Power (Humidify)", "300 W"),
            ("Max. Power", "950 W"),
            ("Voltage", "220–240V 50Hz"),
            ("Refrigerant", "R410A / 500 g"),
            ("Operating Temperature", "5 – 40°C"),
            ("Weight", "150 kg"),
            ("Dimensions (L × W × H)", "800 × 500 × 1,650 mm"),
        ],
        "use_cases": ["Wine cellars", "Cigar lounges", "Music studios", "Specialty galleries", "Server cabinets"],
    },
    {
        "slug": "dba-hc145", "model": "DBA-HC145", "series": "HC",
        "image": "humidistat-dba-hc145-1.png",
        "image_alt": "humidistat-dba-hc145-1.png",
        "tagline": "Precision RH for collections.",
        "intro": "Mid-range Humidity Control unit for galleries, archives, and wine cellars. Holds tight RH bands across seasons.",
        "key_stats": [
            ("Dehumidify", "145 L/day"),
            ("Humidify", "5 kg/hr"),
            ("Coverage", "1,500 sq ft"),
            ("Weight", "150 kg"),
        ],
        "specs": [
            ("Dehumidifying Capacity (30°C 80% RH)", "145 L/day"),
            ("Humidifying Capacity", "5 kg/hr"),
            ("Cover Area", "1,500 sq ft"),
            ("Rated Power (Dehumidify)", "1,600 W"),
            ("Rated Power (Humidify)", "430 W"),
            ("Max. Power", "2,750 W"),
            ("Voltage", "220–240V 50Hz"),
            ("Refrigerant", "R410A / 1.1 kg"),
            ("Operating Temperature", "5 – 40°C"),
            ("Weight", "150 kg"),
            ("Dimensions (L × W × H)", "800 × 500 × 1,850 mm"),
        ],
        "use_cases": ["Art galleries", "Heritage archives", "Wine cellars", "Musical instrument storage", "Rare book libraries"],
    },
    {
        "slug": "dba-hc280", "model": "DBA-HC280", "series": "HC",
        "image": "humidistat-dba-hc280-1.png",
        "image_alt": "humidistat-dba-hc280-1.png",
        "tagline": "Three-phase humidity precision.",
        "intro": "Step up to three-phase 380V power and 280 L/day capacity. Built for larger galleries, museums, and data centres.",
        "key_stats": [
            ("Dehumidify", "280 L/day"),
            ("Humidify", "10 kg/hr"),
            ("Coverage", "3,000 sq ft"),
            ("Weight", "290 kg"),
        ],
        "specs": [
            ("Dehumidifying Capacity (30°C 80% RH)", "280 L/day"),
            ("Humidifying Capacity", "10 kg/hr"),
            ("Cover Area", "3,000 sq ft"),
            ("Rated Power (Dehumidify)", "2,450 W"),
            ("Rated Power (Humidify)", "1,350 W"),
            ("Max. Power", "4,500 W"),
            ("Voltage", "380V 3N 50Hz"),
            ("Refrigerant", "R410A / 1.8 kg"),
            ("Operating Temperature", "5 – 40°C"),
            ("Weight", "290 kg"),
            ("Dimensions (L × W × H)", "1,200 × 600 × 2,200 mm"),
        ],
        "use_cases": ["Museums", "Data centres", "Hospital labs", "Climate-controlled archives", "Pharmaceutical storage"],
    },
    {
        "slug": "dba-hc400", "model": "DBA-HC400", "series": "HC",
        "image": "humidistat-dba-hc400-1.png",
        "image_alt": "humidistat-dba-hc400-1.png",
        "tagline": "Large-format precision humidity.",
        "intro": "400 L/day dehumidify, 15 kg/hr humidify. Engineered for the largest precision-RH environments.",
        "key_stats": [
            ("Dehumidify", "400 L/day"),
            ("Humidify", "15 kg/hr"),
            ("Coverage", "4,000 sq ft"),
            ("Weight", "360 kg"),
        ],
        "specs": [
            ("Dehumidifying Capacity (30°C 80% RH)", "400 L/day"),
            ("Humidifying Capacity", "15 kg/hr"),
            ("Cover Area", "4,000 sq ft"),
            ("Rated Power (Dehumidify)", "4,500 W"),
            ("Rated Power (Humidify)", "1,450 W"),
            ("Max. Power", "6,500 W"),
            ("Voltage", "380V 3N 50Hz"),
            ("Refrigerant", "R410A / 1.45 kg × 2"),
            ("Operating Temperature", "5 – 40°C"),
            ("Weight", "360 kg"),
            ("Dimensions (L × W × H)", "1,400 × 750 × 2,200 mm"),
        ],
        "use_cases": ["Large museums", "Climate test chambers", "Tier-3 data centres", "Pharmaceutical clean rooms", "Aerospace storage"],
    },
    {
        "slug": "dba-hc550", "model": "DBA-HC550", "series": "HC",
        "image": "humidistat-dba-hc550-1.png",
        "image_alt": "humidistat-dba-hc550-1.png",
        "tagline": "Top of the HC line.",
        "intro": "Maximum HC-series capacity. 550 L/day dehumidify, 20 kg/hr humidify. The choice for the most demanding RH-stable environments.",
        "key_stats": [
            ("Dehumidify", "550 L/day"),
            ("Humidify", "20 kg/hr"),
            ("Coverage", "5,000 sq ft"),
            ("Weight", "380 kg"),
        ],
        "specs": [
            ("Dehumidifying Capacity (30°C 80% RH)", "550 L/day"),
            ("Humidifying Capacity", "20 kg/hr"),
            ("Cover Area", "5,000 sq ft"),
            ("Rated Power (Dehumidify)", "6,500 W"),
            ("Rated Power (Humidify)", "1,530 W"),
            ("Max. Power", "8,500 W"),
            ("Voltage", "380V 3N 50Hz"),
            ("Refrigerant", "R410A / 1.8 kg × 2"),
            ("Operating Temperature", "5 – 40°C"),
            ("Weight", "380 kg"),
            ("Dimensions (L × W × H)", "1,400 × 750 × 2,200 mm"),
        ],
        "use_cases": ["National museums", "Hyperscale data centres", "Industrial labs", "Aerospace test facilities", "Precision manufacturing"],
    },
    # ===== DD SERIES =====
    {
        "slug": "dba-dd210", "model": "DBA-DD210", "series": "DD",
        "image": "rotary-dba-dd210-1.jpg",
        "image_alt": "rotary-dba-dd210-1.jpg",
        "tagline": "1 kg/hr at −20°C.",
        "intro": "Compact desiccant rotary dehumidifier. Operates from −20°C to 40°C, holds 1–90% RH — ideal for cold storage and small low-temp applications.",
        "key_stats": [
            ("Capacity", "1 kg/hr"),
            ("Process Airflow", "350 CMH"),
            ("Operating Temp", "−20 – 40°C"),
            ("Weight", "20 kg"),
        ],
        "specs": [
            ("Dehumidifying Capacity (20°C 60% RH)", "1 kg/hr"),
            ("Process Airflow", "350 CMH"),
            ("Reactivation Airflow", "35 CMH"),
            ("Max. Power", "935 W"),
            ("Rated Current", "4.3 A"),
            ("Voltage", "220–240V 50Hz"),
            ("Operating Temperature", "−20 – 40°C"),
            ("Set Humidity Range", "1 – 90% RH"),
            ("Weight", "20 kg"),
            ("Dimensions (L × W × H)", "491 × 430 × 346 mm"),
        ],
        "use_cases": ["Lithium battery rooms", "Small cold storage", "Pharmaceutical packing", "Chocolate finishing", "Electronics test labs"],
    },
    {
        "slug": "dba-dd550", "model": "DBA-DD550", "series": "DD",
        "image": "rotary-dba-dd550-1.jpg",
        "image_alt": "rotary-dba-dd550-1.jpg",
        "tagline": "2.5 kg/hr cold-room workhorse.",
        "intro": "Mid-range desiccant rotary. 550 CMH process airflow for medium-scale low-temperature dehumidification.",
        "key_stats": [
            ("Capacity", "2.5 kg/hr"),
            ("Process Airflow", "550 CMH"),
            ("Operating Temp", "−20 – 40°C"),
            ("Weight", "52 kg"),
        ],
        "specs": [
            ("Dehumidifying Capacity (20°C 60% RH)", "2.5 kg/hr"),
            ("Process Airflow", "550 CMH"),
            ("Reactivation Airflow", "180 CMH"),
            ("Max. Power", "3,700 W"),
            ("Rated Current", "17 A"),
            ("Voltage", "220–240V 50Hz"),
            ("Operating Temperature", "−20 – 40°C"),
            ("Set Humidity Range", "1 – 90% RH"),
            ("Weight", "52 kg"),
            ("Dimensions (L × W × H)", "802 × 615 × 567 mm"),
        ],
        "use_cases": ["Cold storage rooms", "Pharmaceutical labs", "Lyophilisation", "Battery production", "Specialty food processing"],
    },
    {
        "slug": "dba-dd850", "model": "DBA-DD850", "series": "DD",
        "image": "rotary-dba-dd850-1.jpg",
        "image_alt": "rotary-dba-dd850-1.jpg",
        "tagline": "7.5 kg/hr industrial desiccant.",
        "intro": "Largest of the DD range. 850 CMH process airflow with three-phase power for industrial low-temperature operations.",
        "key_stats": [
            ("Capacity", "7.5 kg/hr"),
            ("Process Airflow", "850 CMH"),
            ("Operating Temp", "−20 – 40°C"),
            ("Weight", "120 kg"),
        ],
        "specs": [
            ("Dehumidifying Capacity (20°C 60% RH)", "7.5 kg/hr"),
            ("Process Airflow", "850 CMH"),
            ("Reactivation Airflow", "340 CMH"),
            ("Max. Power", "9,770 W"),
            ("Rated Current", "20 A"),
            ("Voltage", "380V 3N 50Hz"),
            ("Operating Temperature", "−20 – 40°C"),
            ("Set Humidity Range", "1 – 90% RH"),
            ("Weight", "120 kg"),
            ("Dimensions (L × W × H)", "750 × 750 × 1,700 mm"),
        ],
        "use_cases": ["Industrial cold storage", "Pharma manufacturing", "Lithium battery factories", "Aerospace chambers", "Frozen food production"],
    },
    # ===== DH / FEATURED MOBILE =====
    {
        "slug": "dba-dh65", "model": "DBA-DH65", "series": "DH",
        "image": "mobile-dba-dh65-1.jpg",
        "image_alt": "mobile-dba-dh65-1.jpg",
        "tagline": "The everyday best-seller.",
        "intro": "Compact mobile dehumidifier with HEPA filtration and plasma purification. The most popular DBA unit for residential use.",
        "price_usd": 700,
        "price_label": "From US$700",
        "key_stats": [
            ("Capacity", "65 L/day"),
            ("Coverage", "700 – 1,000 sq ft"),
            ("Filtration", "HEPA + Plasma"),
            ("Control", "WiFi App"),
        ],
        "specs": [
            ("Dehumidifying Capacity", "65 L/day"),
            ("Cover Area", "700 – 1,000 sq ft"),
            ("Filtration", "HEPA high-efficiency + Plasma purifier"),
            ("Control", "WiFi App + LED display"),
            ("Drainage", "Auto pump + continuous hose"),
            ("Fan Speed", "Low / High"),
            ("Timer", "24-hour scheduled"),
            ("Defrost", "Auto"),
            ("Voltage", "220–240V 50Hz"),
            ("Mobility", "Caster wheels"),
            ("Safety", "Child lock, drainage fault protection"),
        ],
        "use_cases": ["Apartments", "Bedrooms", "Living rooms", "Home offices", "Studios"],
    },
    {
        "slug": "dba-x65", "model": "DBA-X65", "series": "DH",
        "image": "mobile-dba-x65-1.jpg",
        "image_alt": "mobile-dba-x65-2.png",
        "tagline": "Compact. Versatile. Wall-ready.",
        "intro": "Portable 65 L/day unit that doubles as a wall-mount or ceiling-suspended dehumidifier. The narrowest chassis in the range.",
        "price_usd": 1000,
        "price_label": "From US$1,000",
        "key_stats": [
            ("Capacity", "65 L/day"),
            ("Coverage", "700 – 1,000 sq ft"),
            ("Footprint", "488 × 310 × 340 mm"),
            ("Mounting", "Floor / Wall / Ceiling"),
        ],
        "specs": [
            ("Dehumidifying Capacity", "65 L/day"),
            ("Cover Area", "700 – 1,000 sq ft"),
            ("Dimensions (L × W × H)", "488 × 310 × 340 mm"),
            ("Mounting", "Freestanding / wall-mount / ceiling-hung"),
            ("Drainage", "Auto pump"),
            ("Voltage", "220–240V 50Hz"),
            ("Control", "Direct panel"),
            ("Display", "Real-time humidity readout"),
        ],
        "use_cases": ["Utility rooms", "Narrow corridors", "Server cabinets", "Walk-in closets", "Pantry / storage"],
    },
    {
        "slug": "dba-c150", "model": "DBA-C150", "series": "DH",
        "image": "mobile-dba-c150-1.jpg",
        "image_alt": "mobile-dba-c150-1.jpg",
        "tagline": "150 L/day. ±1% RH.",
        "intro": "Heavy-duty commercial mobile dehumidifier. 1,500–2,000 sq ft coverage, choose tank or pump drainage. Precision RH control across the full range.",
        "price_usd": 1650,
        "price_label": "From US$1,650",
        "key_stats": [
            ("Capacity", "150 L/day"),
            ("Coverage", "1,500 – 2,000 sq ft"),
            ("RH Precision", "±1%"),
            ("Drainage", "Tank or pump"),
        ],
        "specs": [
            ("Dehumidifying Capacity", "150 L/day"),
            ("Cover Area", "1,500 – 2,000 sq ft"),
            ("RH Range", "10 – 98%"),
            ("RH Precision", "±1%"),
            ("Drainage Options", "8L tank / pump (6 m head)"),
            ("Power Cord", "5 m, weatherproof"),
            ("Defrost", "Auto"),
            ("Display", "Real-time T &amp; RH"),
            ("Voltage", "220–240V 50Hz"),
        ],
        "use_cases": ["Commercial kitchens", "Mid-size showrooms", "Restoration jobs", "Indoor riding arenas", "Whole-house drying"],
    },
]

# ============================================================
# HELPERS
# ============================================================
def find_related(current_slug, current_series, n=3):
    related = [p for p in PRODUCTS if p["series"] == current_series and p["slug"] != current_slug]
    return related[:n]

def slug_to_path(slug):
    return f"products/{slug}.html"

def jsonld(product):
    """Generate Product JSON-LD structured data."""
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
    return json.dumps({
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": items
    }, indent=2)

# ============================================================
# PAGE TEMPLATE
# ============================================================
def render_product_page(product):
    series = SERIES[product["series"]]
    related = find_related(product["slug"], product["series"], 3)
    meta_desc = f"{product['model']} — {product['tagline']} {series['name']} dehumidifier by DBA. {product['key_stats'][0][1]} capacity, {product['key_stats'][1][1] if len(product['key_stats']) > 1 else ''}. International showcase by Ervee."
    meta_desc = re.sub(r"\s+", " ", meta_desc).strip()[:160]
    title = f"{product['model']} · {series['name']} Dehumidifier | Ervee — DBA Worldwide"

    # Hero stats
    stats_html = "".join(
        f'<div class="ph-stat"><span class="ps-val">{html.escape(v)}</span><span class="ps-label">{html.escape(l)}</span></div>'
        for l, v in product["key_stats"]
    )
    # Highlights
    highlights_html = "".join(
        f'''<div class="ph-card reveal">
              <div class="ph-icon">{icon}</div>
              <h3>{title}</h3>
              <p>{desc}</p>
            </div>'''
        for icon, title, desc in series["highlights"]
    )
    # Specs table
    specs_html = "".join(
        f'<tr><td>{html.escape(l)}</td><td>{v}</td></tr>'
        for l, v in product["specs"]
    )
    # Config / control
    config_html = "".join(f'<li>{x}</li>' for x in series["config"])
    control_html = "".join(f'<li>{x}</li>' for x in series["control"])
    # Use cases
    cases_html = "".join(f'<span class="case-pill">{html.escape(c)}</span>' for c in product["use_cases"])
    # Related
    related_html = ""
    for r in related:
        r_stat = r["key_stats"][0]
        related_html += f'''<a href="{r['slug']}.html" class="related-card">
            <div class="rc-img"><img src="../images/{r['image']}" alt="{r['model']}" loading="lazy" /></div>
            <div class="rc-body">
              <p class="rc-meta">{series['name']}</p>
              <h4>{r['model']}</h4>
              <p class="rc-stat">{r_stat[1]} {r_stat[0].lower()}</p>
              <span class="rc-link">View →</span>
            </div>
          </a>'''
    # Catalog link
    cat_link_html = f'<a href="../{series["catalog"]}" download class="catalog-link">↓ Download {series["name"]} catalog (PDF)</a>' if series.get("catalog") else ''
    price_pill = f'<span class="ph-price-pill">{product["price_label"]}</span>' if product.get("price_label") else ''

    related_section = ""
    if related:
        related_section = f'''<section class="ph-related">
    <div class="container">
      <div class="section-head reveal">
        <p class="eyebrow">Other models</p>
        <h2>The rest of the {series['name']} range.</h2>
      </div>
      <div class="ph-related-grid reveal">
        {related_html}
      </div>
    </div>
  </section>'''

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{html.escape(title)}</title>
  <meta name="description" content="{html.escape(meta_desc)}" />
  <meta name="keywords" content="{product['model']}, DBA dehumidifier, {series['name']}, dehumidifier Singapore, humidity control" />
  <link rel="canonical" href="{SITE_URL}/{slug_to_path(product['slug'])}" />

  <meta property="og:type" content="product" />
  <meta property="og:title" content="{html.escape(product['model'])} — {html.escape(product['tagline'])}" />
  <meta property="og:description" content="{html.escape(meta_desc)}" />
  <meta property="og:url" content="{SITE_URL}/{slug_to_path(product['slug'])}" />
  <meta property="og:image" content="{SITE_URL}/images/{product['image']}" />
  <meta property="og:site_name" content="Ervee" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{html.escape(product['model'])} — Ervee" />
  <meta name="twitter:description" content="{html.escape(meta_desc)}" />
  <meta name="twitter:image" content="{SITE_URL}/images/{product['image']}" />

  <script type="application/ld+json">{jsonld(product)}</script>
  <script type="application/ld+json">{breadcrumb_jsonld(product)}</script>

  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="../style.css" />
  <link rel="stylesheet" href="../product.css" />
</head>
<body class="product-page">

  <nav id="nav">
    <div class="nav-inner">
      <a href="../index.html" class="logo"><img src="../images/logo-ervee.svg" alt="Ervee" /></a>
      <ul class="nav-links">
        <li><a href="../index.html#technology">Technology</a></li>
        <li><a href="../index.html#applications">Applications</a></li>
        <li><a href="../index.html#products">Products</a></li>
        <li><a href="../index.html#catalogs">Catalogs</a></li>
        
        <li><a href="https://dba.sg" target="_blank" rel="noopener" class="external">DBA.sg ↗</a></li>
        <li><a href="../index.html#contact" class="nav-cta">Get a Quote</a></li>
      </ul>
      <button class="nav-mobile-btn" onclick="toggleNav()" aria-label="Menu"><span></span><span></span><span></span></button>
    </div>
    <ul class="mobile-nav" id="mobileNav">
      <li><a href="../index.html#technology" onclick="toggleNav()">Technology</a></li>
      <li><a href="../index.html#applications" onclick="toggleNav()">Applications</a></li>
      <li><a href="../index.html#products" onclick="toggleNav()">Products</a></li>
      <li><a href="../index.html#catalogs" onclick="toggleNav()">Catalogs</a></li>
      <li><a href="../index.html#partner" onclick="toggleNav()">Become a Dealer</a></li>
      <li><a href="https://dba.sg" target="_blank" rel="noopener">DBA.sg ↗</a></li>
      <li><a href="../index.html#contact" onclick="toggleNav()">Get a Quote</a></li>
    </ul>
  </nav>

  <!-- Breadcrumb -->
  <div class="breadcrumb">
    <div class="container">
      <a href="../index.html">Home</a><span>›</span><a href="../index.html#products">Products</a><span>›</span><a href="../index.html#products">{html.escape(series['name'])}</a><span>›</span><span class="bc-current">{html.escape(product['model'])}</span>
    </div>
  </div>

  <!-- HERO -->
  <section class="ph-hero">
    <div class="container">
      <div class="ph-grid">
        <div class="ph-text">
          <p class="series-eyebrow reveal">{html.escape(series['name'])} · {product['series']} Series</p>
          <h1 class="reveal">{html.escape(product['model'])}</h1>
          <p class="ph-tagline reveal">{html.escape(product['tagline'])}</p>
          <p class="ph-intro reveal">{html.escape(product['intro'])}</p>
          {price_pill}
          <div class="ph-actions reveal">
            <a href="../index.html#contact" class="btn-pill">Request a quote</a>
            <a href="https://dba.sg" target="_blank" rel="noopener" class="btn-text">View on DBA.sg ↗</a>
          </div>
        </div>
        <div class="ph-img reveal-img">
          <img src="../images/{product['image']}" alt="{product['model']} {series['name']} dehumidifier" />
        </div>
      </div>
      <div class="ph-stats reveal">
        {stats_html}
      </div>
    </div>
  </section>

  <!-- AT A GLANCE -->
  <section class="ph-glance">
    <div class="container">
      <p class="eyebrow center reveal">At a glance</p>
      <h2 class="center reveal">{html.escape(series['tagline'])}</h2>
      <div class="ph-cards">
        {highlights_html}
      </div>
    </div>
  </section>

  <!-- BIG IMAGE BANNER (parallax) -->
  <section class="ph-banner">
    <div class="container">
      <div class="ph-banner-inner reveal">
        <img src="../images/{product['image_alt']}" alt="{product['model']} detail" />
        <div class="ph-banner-text">
          <h2>Engineered in Asia.<br />Distributed by Ervee.</h2>
          <p>Every {product['model']} is built to international standards by DBA Electric Pte. Ltd. Ervee distributes the full range to dealers, OEM partners, and direct buyers worldwide.</p>
          <a href="https://dba.sg" target="_blank" rel="noopener" class="btn-pill outline">Visit dba.sg ↗</a>
        </div>
      </div>
    </div>
  </section>

  <!-- SPECS -->
  <section class="ph-specs">
    <div class="container">
      <div class="section-head reveal">
        <p class="eyebrow">Technical data</p>
        <h2>Full specifications.</h2>
      </div>
      <div class="ph-spec-wrap reveal">
        <table class="ph-spec-table">
          {specs_html}
        </table>
      </div>
    </div>
  </section>

  <!-- CONFIG &amp; CONTROL -->
  <section class="ph-config">
    <div class="container">
      <div class="section-head reveal">
        <p class="eyebrow">Inside the unit</p>
        <h2>Configuration &amp; Control.</h2>
        <p class="lead">Standard across the {series['name']} series.</p>
      </div>
      <div class="ph-config-grid reveal">
        <div class="ph-config-col">
          <h3>Configuration</h3>
          <ul>{config_html}</ul>
        </div>
        <div class="ph-config-col">
          <h3>Control</h3>
          <ul>{control_html}</ul>
        </div>
      </div>
      {cat_link_html}
    </div>
  </section>

  <!-- USE CASES -->
  <section class="ph-cases">
    <div class="container">
      <div class="section-head reveal">
        <p class="eyebrow">Where it shines</p>
        <h2>Built for these spaces.</h2>
      </div>
      <div class="ph-case-pills reveal">
        {cases_html}
      </div>
    </div>
  </section>

  <!-- RELATED -->
  {related_section}

  <!-- CTA -->
  <section class="ph-cta">
    <div class="container narrow center">
      <h2 class="reveal">Interested in {product['model']}?</h2>
      <p class="lead reveal">Tell us about your market, project, or distribution interest. A specialist colleague replies within one business day.</p>
      <div class="ph-cta-actions reveal">
        <a href="../index.html#contact" class="btn-pill primary">Request a quote</a>
        <a href="https://wa.me/6589859886" target="_blank" rel="noopener" class="btn-pill outline">WhatsApp · +65 8985 9886</a>
      </div>
      <p class="ph-cta-foot reveal">Or browse the full DBA catalog at <a href="https://dba.sg" target="_blank" rel="noopener">dba.sg</a></p>
    </div>
  </section>

  <footer>
    <div class="container">
      <div class="footer-top">
        <div class="footer-brand">
          <img src="../images/logo-ervee.svg" alt="Ervee" class="footer-logo-img" />
          <p>The international showcase for DBA dehumidifier technology. For dealers, OEM partners, and direct buyers worldwide.</p>
          <a href="https://dba.sg" target="_blank" rel="noopener" class="footer-dba">↗ Visit dba.sg</a>
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
            <h4>Resources</h4>
            <ul>
              <li><a href="../index.html#technology">Technology</a></li>
              <li><a href="../index.html#applications">Applications</a></li>
              <li><a href="../index.html#catalogs">Product catalogs</a></li>
              
              <li><a href="../index.html#contact">Get a quote</a></li>
            </ul>
          </div>
          <div class="fcol">
            <h4>DBA Electric Pte. Ltd.</h4>
            <ul>
              <li><a href="https://wa.me/6589859886" target="_blank" rel="noopener">WhatsApp · +65 8985 9886</a></li>
              <li><a href="tel:+6567729962">Hotline · +65 6772 9962</a></li>
              <li><a href="mailto:dba@dba.sg">dba@dba.sg</a></li>
              <li>Block B, Cititech Industrial Building,<br />629 Aljunied Road, #07-08,<br />Singapore 389838</li>
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
'''

# ============================================================
# SITEMAP & ROBOTS
# ============================================================
def render_sitemap():
    today = date.today().isoformat()
    urls = [
        (SITE_URL + "/", "1.0", today),
        (SITE_URL + "/#products", "0.9", today),
        (SITE_URL + "/#technology", "0.8", today),
        (SITE_URL + "/#applications", "0.8", today),
        (SITE_URL + "/#catalogs", "0.8", today),
        (SITE_URL + "/#faq", "0.7", today),
        (SITE_URL + "/#quote", "0.7", today),
    ]
    for p in PRODUCTS:
        urls.append((f"{SITE_URL}/{slug_to_path(p['slug'])}", "0.9", today))
    body = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/0.9/sitemap.xsd">\n'
    for u, p, d in urls:
        body += f"  <url><loc>{u}</loc><lastmod>{d}</lastmod><priority>{p}</priority></url>\n"
    body += "</urlset>\n"
    return body

def render_robots():
    return f"""User-agent: *
Allow: /

Sitemap: {SITE_URL}/sitemap.xml
"""

# ============================================================
# MAIN
# ============================================================
def main():
    out = ROOT / "products"
    out.mkdir(exist_ok=True)
    for p in PRODUCTS:
        path = out / f"{p['slug']}.html"
        path.write_text(render_product_page(p))
    (ROOT / "sitemap.xml").write_text(render_sitemap())
    (ROOT / "robots.txt").write_text(render_robots())

    # Also write a JSON map of products for the homepage to know the URLs
    with open(ROOT / "build" / "products.json", "w") as f:
        json.dump([{"slug": p["slug"], "model": p["model"], "series": p["series"]} for p in PRODUCTS], f, indent=2)

    print(f"Generated {len(PRODUCTS)} product pages, sitemap.xml, robots.txt")

if __name__ == "__main__":
    main()
