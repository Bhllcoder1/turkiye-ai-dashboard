#!/usr/bin/env python3
"""Generate dashboard JSON. Uses direct data definitions instead of fragile markdown parsing."""

import json, re, os

BASE = "/home/behlul/research/turkiye-tum-ai-sirketleri"

# ═══════════════════════════════════════════════════════════════════
# UTILS
# ═══════════════════════════════════════════════════════════════════

def parse_funding(text):
    if not text or text in ("-", "", "Bilinmiyor", "Seed"):
        return None, None
    text = str(text).replace("$", "").replace("€", "").replace(",", "").replace("+", "").strip()
    mult = 1
    currency_eur = "€" in str(text)
    if "M" in text: mult, text = 1_000_000, text.replace("M", "").strip()
    elif "K" in text: mult, text = 1_000, text.replace("K", "").strip()
    elif "B" in text: mult, text = 1_000_000_000, text.replace("B", "").strip()
    try:
        val = float(text) * mult
        if currency_eur: val *= 1.12
        return int(val), fmt_funding(int(val))
    except (ValueError, TypeError):
        return None, None

def fmt_funding(v):
    if v is None: return None
    if v >= 1_000_000_000: return f"${v/1_000_000_000:.1f}B"
    if v >= 1_000_000: return f"${v/1_000_000:.0f}M"
    if v >= 1_000: return f"${v/1_000:.0f}K"
    return f"${v}"

def slugify(name):
    return re.sub(r'[^a-z0-9-]', '', name.lower()
        .replace(' ','-').replace('ı','i').replace('ğ','g')
        .replace('ü','u').replace('ş','s').replace('ö','o').replace('ç','c'))

# ═══════════════════════════════════════════════════════════════════
# PARSE TRAI COMPANIES (name + slug only, from master_database.md)
# ═══════════════════════════════════════════════════════════════════

with open(f"{BASE}/master_database.md") as f:
    md = f.read()

trai_raw = re.findall(r'\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*([a-z0-9][a-z0-9-]+[a-z0-9])\s*\|', md)
trai_names = {}
for num, name, slug in trai_raw:
    trai_names[name.strip()] = slug.strip()
print(f"TRAI companies: {len(trai_names)}")

# ═══════════════════════════════════════════════════════════════════
# ENRICHED COMPANY DATA (directly defined, from all our research)
# ═══════════════════════════════════════════════════════════════════

enriched = {
    "Insider": {"founded": "2012", "city": "İstanbul", "funding": "$777M", "fundingRaw": 777_000_000, "category": "Pazarlama / E-ticaret", "website": "insiderone.com", "description": "AI destekli omnichannel müşteri etkileşim platformu; Agent One™ otonom AI agent'lar; CDP, journey orchestration, kişiselleştirme", "isUnicorn": True},
    "Grand Games": {"founded": "2024", "city": "İstanbul", "funding": "$103M", "fundingRaw": 103_000_000, "category": "Oyun / Gaming", "description": "AI destekli mobil oyun geliştirme; $103M yatırım"},
    "Fal.ai": {"founded": "2021", "city": "Diaspora", "funding": "$72M", "fundingRaw": 72_000_000, "category": "Üretken AI / GenAI", "website": "fal.ai", "description": "Generative media AI platformu; ses, video, görüntü üretimi; Quora, Canva, Perplexity müşterisi", "isUnicorn": True, "isDiaspora": True},
    "HockeyStack": {"founded": "2021", "city": "İstanbul", "funding": "$23M", "fundingRaw": 23_000_000, "category": "Veri Analitiği / Tahminleme", "website": "hockeystack.com", "description": "Enterprise revenue platform; ML ile satış verilerinden Blueprint modeli, otonom AI Revenue Agent'lar"},
    "Fuse Games": {"founded": "2023", "city": "İstanbul", "funding": "$11M", "fundingRaw": 11_000_000, "category": "Oyun / Gaming", "description": "AI mobil oyun geliştirme"},
    "Dataroid": {"founded": "2021", "city": "İstanbul", "funding": "$9M", "fundingRaw": 9_000_000, "category": "Veri Analitiği / Tahminleme", "website": "dataroid.com", "description": "Davranışsal analitik ve müşteri etkileşim platformu; AI Agent D ile anlık analitik, churn tahmini"},
    "Vispera": {"founded": "2014", "city": "İstanbul", "funding": "$8M", "fundingRaw": 8_000_000, "category": "Görüntü İşleme / Computer Vision", "website": "vispera.co", "description": "Perakende için görüntü tanıma tabanlı raf yönetimi; stok takibi, planogram uyumu"},
    "Novus": {"founded": "2020", "city": "İstanbul", "funding": "$5M", "fundingRaw": 5_000_000, "category": "Agentic AI", "website": "novusasi.com", "description": "Agentic AI sistemleri; Nano (orchestration) ve Dot (enterprise agentic AI framework)"},
    "FERASET": {"founded": "2023", "city": "İstanbul", "funding": "$4.5M", "fundingRaw": 4_500_000, "category": "Pazarlama / E-ticaret", "description": "AI tüketici uygulamaları"},
    "Mindsite": {"founded": "2019", "city": "İstanbul", "funding": "$4.7M", "fundingRaw": 4_700_000, "category": "Pazarlama / E-ticaret", "description": "AI E-commerce Analytics"},
    "Uniti AI": {"founded": "2022", "city": "Diaspora", "funding": "$4M", "fundingRaw": 4_000_000, "category": "Pazarlama / E-ticaret", "isDiaspora": True},
    "Intryc": {"founded": "2021", "city": "Diaspora", "funding": "$3.1M", "fundingRaw": 3_100_000, "category": "Veri Analitiği / Tahminleme", "isDiaspora": True},
    "Saha Robotics": {"founded": "2020", "city": "İstanbul", "funding": "$3M", "fundingRaw": 3_000_000, "category": "Otonom Sistemler / Robotik", "website": "saharobotik.com", "description": "Otonom servis robotları; Saha OS navigasyon sistemi, HeyHolo!, HORECA 4.0"},
    "Archmir": {"founded": "", "city": "İstanbul", "funding": "$2.4M", "fundingRaw": 2_400_000, "category": "Görüntü İşleme / Computer Vision"},
    "ThingsHappen": {"founded": "2024", "city": "İstanbul", "funding": "$2M", "fundingRaw": 2_000_000, "category": "Finans / Sigorta / Bankacılık"},
    "Eachlabs": {"founded": "", "city": "Diaspora", "funding": "$2M", "fundingRaw": 2_000_000, "category": "Üretken AI / GenAI", "isDiaspora": True},
    "Musixen": {"founded": "", "city": "İstanbul", "funding": "$2M", "fundingRaw": 2_000_000, "category": "Üretken AI / GenAI"},
    "Mindtail": {"founded": "2026", "city": "İstanbul", "funding": "$2M", "fundingRaw": 2_000_000, "category": "Oyun / Gaming", "description": "AI-native hibrit casual puzzle oyunları; Dream Games/King deneyimli kurucular", "isNew": True},
    "DIGINAK.COM": {"founded": "", "city": "İstanbul", "funding": "$1.5M", "fundingRaw": 1_500_000, "category": "Akıllı Platformlar"},
    "Pera Labs": {"founded": "", "city": "İstanbul", "funding": "$1.3M", "fundingRaw": 1_300_000, "category": "Sağlık / HealthTech"},
    "Boby AI": {"founded": "2023", "city": "İstanbul", "funding": "$1.25M", "fundingRaw": 1_250_000, "category": "Pazarlama / E-ticaret"},
    "Rierino": {"founded": "2020", "city": "İstanbul", "funding": "$1.25M", "fundingRaw": 1_250_000, "category": "Pazarlama / E-ticaret"},
    "Mindra": {"founded": "2025", "city": "İstanbul", "funding": "$1.2M", "fundingRaw": 1_200_000, "category": "Agentic AI"},
    "VenueX": {"founded": "2022", "city": "İstanbul", "funding": "$1.2M", "fundingRaw": 1_200_000, "category": "Pazarlama / E-ticaret"},
    "Kavaken": {"founded": "2022", "city": "İstanbul", "funding": "$1.1M", "fundingRaw": 1_100_000, "category": "Enerji / Çevre", "website": "kavaken.com", "description": "Yenilenebilir enerji varlıkları için AI destekli yönetim ve optimizasyon"},
    "Finedine": {"founded": "2016", "city": "İstanbul", "funding": "$1M", "fundingRaw": 1_000_000, "category": "Akıllı Platformlar"},
    "GameByte": {"founded": "2025", "city": "İstanbul", "funding": "$1M", "fundingRaw": 1_000_000, "category": "Oyun / Gaming", "isNew": True},
    "Hop Health": {"founded": "2022", "city": "İstanbul", "funding": "$1M", "fundingRaw": 1_000_000, "category": "Sağlık / HealthTech"},
    "Flyway Health": {"founded": "2024", "city": "Diaspora", "funding": "$1M", "fundingRaw": 1_000_000, "category": "Sağlık / HealthTech", "isDiaspora": True},
    "Replenit": {"founded": "2025", "city": "Diaspora", "funding": "$2.4M", "fundingRaw": 2_400_000, "category": "Pazarlama / E-ticaret", "description": "AI perakende karar motoru; ElevenLabs CEO'su yatırımcı; %235 gelir artışı", "isNew": True, "isDiaspora": True},
    "Syntonym": {"founded": "", "city": "İstanbul", "funding": "$824K", "fundingRaw": 824_000, "category": "Görüntü İşleme / Computer Vision"},
    "Yuppo": {"founded": "", "city": "İstanbul", "funding": "$840K", "fundingRaw": 840_000, "category": "Eğitim / EdTech"},
    "Reprai": {"founded": "", "city": "İstanbul", "funding": "$500K", "fundingRaw": 500_000, "category": "Sağlık / HealthTech"},
    "Sertifier": {"founded": "", "city": "İstanbul", "funding": "$350K", "fundingRaw": 350_000, "category": "Eğitim / EdTech"},
    "Skymod Technology": {"founded": "2023", "city": "İzmir", "funding": "$200K", "fundingRaw": 200_000, "category": "Üretken AI / GenAI", "description": "Enterprise AI + Türkçe LLM ('Goat' modeli)"},
    "Mamosis": {"founded": "2024", "city": "İstanbul", "funding": "$118K", "fundingRaw": 118_000, "category": "Sağlık / HealthTech"},
    "Albert Health": {"founded": "", "city": "İstanbul", "funding": "$1.5M", "fundingRaw": 1_500_000, "category": "Sağlık / HealthTech", "website": "albert.health", "description": "Kronik hastalık yönetimi için AI destekli dijital platform; sesli asistan ve condition-specific language model"},
    "Intenseye": {"founded": "", "city": "İstanbul", "funding": "", "category": "Görüntü İşleme / Computer Vision", "website": "intenseye.com", "description": "AI tabanlı iş yeri güvenliği; mevcut CCTV ile gerçek zamanlı SIF risk tespiti, Sentinel edge cihazları"},
    "Sestek": {"founded": "", "city": "İstanbul", "funding": "", "category": "NLP / Doğal Dil İşleme", "website": "sestek.com", "description": "Conversational automation; >%97 speech recognition, TTS, NLP, voice biometrics; hibrit NLP+LLM AI Agent"},
    "Buluttan": {"founded": "", "city": "İstanbul", "funding": "", "category": "Enerji / Çevre", "website": "buluttan.com", "description": "AI tabanlı hiper-lokal hava durumu istihbaratı; Weather Intelligence API; enerji, havacılık, lojistik"},
    "Kimola": {"founded": "", "city": "İstanbul", "funding": "", "category": "NLP / Doğal Dil İşleme", "website": "kimola.com", "description": "Müşteri geri bildirim analizi; AI ile tema, duygu ve pattern tespiti; sektöre özel AI modelleri"},
    "Khenda": {"founded": "", "city": "İstanbul", "funding": "", "category": "RPA / AI Otomasyon", "website": "khenda.com", "description": "Üretim süreç analizi; telefondan AI ile otomatik zaman etüdü, iş talimatı üretimi"},
    "JetScoring": {"founded": "", "city": "İstanbul", "funding": "", "category": "Finans / Sigorta / Bankacılık", "website": "jetscoring.com", "description": "Finansal analiz; OCR + ML ile dokümanlardan otomatik veri çıkarma, likidite/iflas riski tahmini"},
    "B2Metric": {"founded": "", "city": "İstanbul", "funding": "", "category": "Makine Öğrenmesi / ML", "website": "b2metric.com", "description": "AI Customer Data Platform; churn tahmini, CLTV, AutoML Studio, segmentasyon"},
    "Enhencer": {"founded": "", "city": "İstanbul", "funding": "", "category": "Pazarlama / E-ticaret", "website": "enhencer.com", "description": "E-ticaret için AI reklam platformu; Meta/Google Ads'te otomatik kampanya optimizasyonu"},
    "Stockimg AI": {"founded": "", "city": "İstanbul", "funding": "", "category": "Üretken AI / GenAI", "website": "stockimg.ai", "description": "AI ile logo, illüstrasyon, sosyal medya içeriği ve video üretimi"},
    "Decktopus": {"founded": "", "city": "İstanbul", "funding": "", "category": "Üretken AI / GenAI", "website": "decktopus.com", "description": "Prompt'tan otomatik sunum oluşturma; AI araştırma, metin, görsel, markalı slaytlar"},
    "Lifemote": {"founded": "", "city": "İstanbul", "funding": "", "category": "IoT / Nesnelerin İnterneti", "website": "lifemote.com", "description": "ISP'ler için AI Wi-Fi analitiği; kanal yoğunluğu, kapsama sorunlarını ML ile tespit"},
    "AIATUS": {"founded": "", "city": "İstanbul", "funding": "", "category": "Görüntü İşleme / Computer Vision", "website": "aiatus.com", "description": "AI platformu; yüz tanıma, imza doğrulama, duygu/sentiment analizi, GenAI churn tahmini"},
    "Ambeent": {"founded": "", "city": "İstanbul", "funding": "", "category": "IoT / Nesnelerin İnterneti", "website": "ambeent.ai", "description": "AIOps genişbant ağ izleme ve optimizasyonu; cihaz-merkezli sıfır kurulum AI"},
    "Adsbot": {"founded": "", "city": "İstanbul", "funding": "", "category": "Otonom Sistemler / Robotik", "website": "adsbot.co"},
    "Agrovisio": {"founded": "", "city": "İstanbul", "funding": "", "category": "Tarım / AgriTech", "website": "agrovisio.com.tr"},
    "Aidea": {"founded": "2026", "city": "İstanbul", "funding": "", "category": "Üretken AI / GenAI", "description": "AI içerik üretim platformu; tüm içerik sürecini tek ekranda yönetme", "isNew": True},
    "Vimesoft": {"founded": "", "city": "İstanbul", "funding": "$1.5M", "fundingRaw": 1_500_000, "category": "Siber Güvenlik", "isNew": True},
    "DOF Robotics": {"founded": "", "city": "İstanbul", "funding": "$40M+", "fundingRaw": 40_000_000, "category": "Otonom Sistemler / Robotik", "description": "AI immersive teknolojiler; 56 ülkede faaliyet; BIST halka arz", "isNew": True},
    "KazAI": {"founded": "2025", "city": "İstanbul", "funding": "", "category": "Finans / Sigorta / Bankacılık", "description": "AI araç hasar analizi; İTÜ Çekirdek", "isNew": True},
    "Solustiq": {"founded": "2025", "city": "Edirne", "funding": "", "category": "Akıllı Platformlar", "description": "Türkiye'nin ilk dikey AI şirketi; DataGreat (38+ modül), SkilledAgents, VibePy", "isNew": True},
    "HaloScape": {"founded": "", "city": "İstanbul", "funding": "", "category": "Sağlık / HealthTech", "description": "AI tabanlı giyilebilir sağlık cihazı; NYAS programına kabul edilen ilk teknoloji şirketi", "isNew": True},
    "RaceData AI": {"founded": "2023", "city": "Ankara", "funding": "", "category": "Veri Analitiği / Tahminleme", "description": "Motorsporları için AI tabanlı telemetri veri analitiği; 35 ülkede 8.000+ kullanıcı", "isNew": True},
    "Viseur AI": {"founded": "", "city": "İstanbul", "funding": "$350K", "fundingRaw": 350_000, "category": "Sağlık / HealthTech", "description": "Dijital patoloji ve tanı süreçlerinde AI; GEN Türkiye mikro unicorn adayı", "isNew": True},
    "Workybe": {"founded": "", "city": "İstanbul", "funding": "", "category": "Enerji / Çevre", "description": "Endüstriyel tesisler için AI ile enerji optimizasyonu; karbon ayak izi azaltma", "isNew": True},
    "Megatek": {"founded": "", "city": "İstanbul", "funding": "", "category": "Akıllı Platformlar", "description": "Global AI ekosistem kaynaklarını tek çatı altında toplayan platform", "isNew": True},
    "Danex AI": {"founded": "", "city": "İzmir", "funding": "", "category": "Akıllı Platformlar", "isNew": True},
    "Onysoft AI": {"founded": "", "city": "İzmir", "funding": "", "category": "Akıllı Platformlar", "isNew": True},
    "Lucida AI": {"founded": "", "city": "İstanbul", "funding": "", "category": "Akıllı Platformlar"},
    "NeuroVision AI": {"founded": "", "city": "İstanbul", "funding": "", "category": "Görüntü İşleme / Computer Vision"},
    "Myth Technologies": {"founded": "", "city": "İstanbul", "funding": "", "category": "Akıllı Platformlar"},
    "Reminisce": {"founded": "", "city": "İstanbul", "funding": "", "category": "Akıllı Platformlar"},
    "Periodic Labs": {"founded": "", "city": "Diaspora", "isUnicorn": True, "isDiaspora": True, "category": "Akıllı Platformlar"},
    "Voiser": {"founded": "2019", "city": "İstanbul", "funding": "", "category": "NLP / Doğal Dil İşleme"},
    "Visea": {"founded": "", "city": "İstanbul", "funding": "", "category": "Görüntü İşleme / Computer Vision"},
    "From Your Eyes": {"founded": "", "city": "İstanbul", "funding": "", "category": "Görüntü İşleme / Computer Vision"},
}

# Companies with known jobs/internships
JOB_COMPANIES = {
    "Insider": 50, "Grand Games": 15, "Sestek": 15, "Intenseye": 10, "HockeyStack": 12,
    "Novus": 8, "Vispera": 5, "Fuse Games": 8, "Mindtail": 5, "Dataroid": 4,
    "Enhencer": 4, "Albert Health": 3, "Kimola": 3, "Lifemote": 3, "AIATUS": 3,
    "Buluttan": 2, "From Your Eyes": 2,
}
INTERNSHIP_COMPANIES = {
    "Insider", "Sestek", "Grand Games", "Intenseye", "Vispera",
    "Lifemote", "Albert Health", "Novus", "Mindtail", "Solustiq",
}

print(f"Enriched companies: {len(enriched)}")

# ═══════════════════════════════════════════════════════════════════
# MERGE: TRAI names + enriched data
# ═══════════════════════════════════════════════════════════════════

all_companies = []
seen = set()

def strip_parens(name):
    """Remove parenthetical text like 'Adsbot (Atlas Robotics)' -> 'Adsbot'"""
    return re.sub(r'\s*\([^)]*\)\s*', '', name).strip()

# Build reverse lookup: enriched key -> TRAI name (for parenthetical TRAI names)
enriched_to_trai = {}
for name in trai_names:
    base = strip_parens(name)
    if base != name and base in enriched:
        enriched_to_trai[base] = name

for name, slug in sorted(trai_names.items()):
    seen.add(name.lower())
    # Also mark the base name (without parenthetical) as seen for dedup
    base = strip_parens(name)
    if base != name:
        seen.add(base.lower())

    # Try direct match first, then try base name (without parenthetical)
    ext = enriched.get(name)
    if not ext and base != name:
        ext = enriched.get(base)
        if ext:
            enriched_to_trai[base] = name

    if ext:
        tier = "verified" if ext.get("website") and ext.get("description") else "enriched"
        c = {
            "id": slug, "name": name, "slug": slug, "tier": tier,
            "founded": ext.get("founded") or None,
            "city": ext.get("city") or None,
            "funding": ext.get("funding") or None,
            "fundingRaw": ext.get("fundingRaw") or None,
            "category": ext.get("category") or None,
            "website": ext.get("website") or None,
            "description": ext.get("description") or None,
            "isUnicorn": ext.get("isUnicorn", False),
            "isDiaspora": ext.get("isDiaspora", False),
            "isNew": ext.get("isNew", False),
            "verified": tier == "verified",
            "hasJobs": name in JOB_COMPANIES,
            "hasInternship": name in INTERNSHIP_COMPANIES,
            "source": "TRAI+Enriched",
        }
    else:
        c = {
            "id": slug, "name": name, "slug": slug, "tier": "basic",
            "category": None, "city": None, "founded": None,
            "funding": None, "fundingRaw": None, "website": None,
            "description": None, "verified": False,
            "isUnicorn": False, "isDiaspora": False, "isNew": False,
            "hasJobs": name in JOB_COMPANIES,
            "hasInternship": name in INTERNSHIP_COMPANIES,
            "source": "TRAI",
        }
    all_companies.append(c)

# Add enriched companies not in TRAI
for name, ext in enriched.items():
    if name.lower() not in seen:
        seen.add(name.lower())
        tier = "verified" if ext.get("website") and ext.get("description") else "enriched"
        c = {
            "id": slugify(name), "name": name, "slug": None, "tier": tier,
            "founded": ext.get("founded") or None,
            "city": ext.get("city") or None,
            "funding": ext.get("funding") or None,
            "fundingRaw": ext.get("fundingRaw") or None,
            "category": ext.get("category") or None,
            "website": ext.get("website") or None,
            "description": ext.get("description") or None,
            "isUnicorn": ext.get("isUnicorn", False),
            "isDiaspora": ext.get("isDiaspora", False),
            "isNew": ext.get("isNew", False),
            "verified": tier == "verified",
            "hasJobs": name in JOB_COMPANIES,
            "hasInternship": name in INTERNSHIP_COMPANIES,
            "source": "Ek Kaynak" if not ext.get("isNew") else "Yeni Kesif",
        }
        all_companies.append(c)

# ═══════════════════════════════════════════════════════════════════
# STATISTICS
# ═══════════════════════════════════════════════════════════════════

# TRAI official technical category distribution (from Calisma-Alanlari-Dagilimi.md)
TRAI_CATEGORIES = {
    "Görüntü İşleme / Computer Vision": 89,
    "Üretken AI / GenAI": 68,
    "Öngörü ve Veri Analitiği": 68,
    "Makine Öğrenmesi / ML": 55,
    "NLP / Doğal Dil İşleme": 21,
    "Chatbot / Diyalogsal AI": 21,
    "Optimizasyon": 16,
    "Otonom Sistemler / Robotik": 15,
    "RPA / AI Otomasyon": 15,
    "Akıllı Platformlar": 10,
    "IoT / Nesnelerin İnterneti": 10,
    "Diğer (AR/VR, Sağlık, Enerji vb.)": 17,
}
# Map our enriched sector categories to TRAI technical categories for per-company assignment
SECTOR_TO_TRAI = {
    "Görüntü İşleme / Computer Vision": "Görüntü İşleme / Computer Vision",
    "Üretken AI / GenAI": "Üretken AI / GenAI",
    "Veri Analitiği / Tahminleme": "Öngörü ve Veri Analitiği",
    "Makine Öğrenmesi / ML": "Makine Öğrenmesi / ML",
    "NLP / Doğal Dil İşleme": "NLP / Doğal Dil İşleme",
    "Chatbot / Diyalogsal AI": "Chatbot / Diyalogsal AI",
    "Otonom Sistemler / Robotik": "Otonom Sistemler / Robotik",
    "RPA / AI Otomasyon": "RPA / AI Otomasyon",
    "Akıllı Platformlar": "Akıllı Platformlar",
    "IoT / Nesnelerin İnterneti": "IoT / Nesnelerin İnterneti",
    "Agentic AI": "Üretken AI / GenAI",
    "Pazarlama / E-ticaret": "Öngörü ve Veri Analitiği",
    "Oyun / Gaming": "Üretken AI / GenAI",
    "Finans / Sigorta / Bankacılık": "Öngörü ve Veri Analitiği",
    "Enerji / Çevre": "Diğer (AR/VR, Sağlık, Enerji vb.)",
    "Sağlık / HealthTech": "Diğer (AR/VR, Sağlık, Enerji vb.)",
    "Eğitim / EdTech": "Diğer (AR/VR, Sağlık, Enerji vb.)",
    "Tarım / AgriTech": "Diğer (AR/VR, Sağlık, Enerji vb.)",
    "Siber Güvenlik": "Diğer (AR/VR, Sağlık, Enerji vb.)",
    "Optimizasyon": "Optimizasyon",
}

# Map individual company categories to TRAI technical categories for graph connectivity
for c in all_companies:
    if c.get("category"):
        c["category"] = SECTOR_TO_TRAI.get(c["category"], c["category"])

cats = {}
cities = {}
for c in all_companies:
    if c.get("category"):
        # Map to TRAI technical category for distribution counts
        trai_cat = SECTOR_TO_TRAI.get(c["category"], c["category"])
        cats[trai_cat] = cats.get(trai_cat, 0) + 1
    if c.get("city"):
        ct = c["city"]
        if "diaspora" in ct.lower(): ct = "Diaspora"
        cities[ct] = cities.get(ct, 0) + 1

# Override categories with TRAI's published distribution for accurate display
cats = dict(sorted(TRAI_CATEGORIES.items(), key=lambda x: x[1], reverse=True))

funded = sorted([c for c in all_companies if c.get("fundingRaw")], key=lambda c: c["fundingRaw"], reverse=True)
total_inv = sum(c["fundingRaw"] for c in funded)

tiers_count = {"verified": 0, "enriched": 0, "basic": 0}
for c in all_companies: tiers_count[c["tier"]] += 1

print(f"Total companies: {len(all_companies)}")
print(f"  Verified: {tiers_count['verified']} | Enriched: {tiers_count['enriched']} | Basic: {tiers_count['basic']}")
print(f"  Funded: {len(funded)} | Total investment: {fmt_funding(total_inv)}")

# ═══════════════════════════════════════════════════════════════════
# JOB MARKET DATA
# ═══════════════════════════════════════════════════════════════════

job_companies_list = [
    {"name": "Insider", "positions": 50, "roles": "ML Engineer, Data Scientist, Backend, Frontend, PM"},
    {"name": "Grand Games", "positions": 15, "roles": "AI Game Developer, AI Engineer, Artist"},
    {"name": "Sestek", "positions": 15, "roles": "NLP Engineer, Voice AI Developer, QA"},
    {"name": "HockeyStack", "positions": 12, "roles": "Senior SWE, Data Engineer, DevOps"},
    {"name": "Intenseye", "positions": 10, "roles": "Computer Vision, MLOps, Backend Engineer"},
    {"name": "Novus", "positions": 8, "roles": "AI Engineer, Full Stack Developer"},
    {"name": "Fuse Games", "positions": 8, "roles": "Unity Developer, AI Game Designer"},
    {"name": "Vispera", "positions": 5, "roles": "Computer Vision Engineer, Data Scientist"},
    {"name": "Mindtail", "positions": 5, "roles": "AI Game Developer, ML Engineer"},
    {"name": "Dataroid", "positions": 4, "roles": "Data Engineer, Analytics Consultant"},
    {"name": "Enhencer", "positions": 4, "roles": "ML Engineer, Frontend Developer"},
    {"name": "Albert Health", "positions": 3, "roles": "ML Engineer, Mobile Developer"},
    {"name": "Kimola", "positions": 3, "roles": "Data Analyst, Software Developer"},
    {"name": "Lifemote", "positions": 3, "roles": "Data Scientist, Embedded SWE"},
    {"name": "AIATUS", "positions": 3, "roles": "Computer Vision, AI Engineer"},
    {"name": "Buluttan", "positions": 2, "roles": "AI Engineer, Full Stack"},
    {"name": "From Your Eyes", "positions": 2, "roles": "Computer Vision, Mobile Developer"},
]
total_positions = sum(j["positions"] for j in job_companies_list)

internships = [
    {"company": "THY", "program": "Turkish Technology Talent Bridge", "type": "Yaz 2026", "location": "İstanbul", "focus": "AI dahil tüm teknoloji"},
    {"company": "HAVELSAN", "program": "SUIT", "type": "2025-2026", "location": "Ankara", "focus": "Savunma AI projeleri"},
    {"company": "SAYZEK", "program": "ATP", "type": "2025-2026", "location": "Ankara", "focus": "AI odaklı tez/staj"},
    {"company": "Insider", "program": "Yaz Stajı", "type": "3 ay, ücretli", "location": "İstanbul", "focus": "ML, Data Science, PM"},
    {"company": "Sestek", "program": "Dönem Stajı", "type": "Dönem", "location": "İstanbul (hibrit)", "focus": "NLP, Voice AI"},
    {"company": "Grand Games", "program": "Yaz Stajı", "type": "Yaz", "location": "İstanbul", "focus": "AI Oyun Geliştirme"},
    {"company": "Intenseye", "program": "Yaz Stajı", "type": "Yaz", "location": "İstanbul", "focus": "Computer Vision, MLOps"},
    {"company": "Albert Health", "program": "Yaz Stajı", "type": "Yaz", "location": "İstanbul", "focus": "Sağlık AI"},
    {"company": "Novus", "program": "Dönem Stajı", "type": "Dönem", "location": "İstanbul/Remote", "focus": "Agentic AI"},
    {"company": "Mindtail", "program": "Yaz Stajı", "type": "Yaz (yeni)", "location": "İstanbul", "focus": "AI Oyun"},
    {"company": "Solustiq", "program": "Dönem Stajı", "type": "Dönem (yeni)", "location": "Edirne/Remote", "focus": "Dikey AI, Turizm"},
    {"company": "Çizgi Technology", "program": "Yapay Zeka Stajyeri", "type": "Dönem", "location": "İstanbul", "focus": "Python, TensorFlow"},
]

roles_data = [
    {"role": "Machine Learning Engineer", "count": 25, "areas": "Tüm alanlarda (temel rol)"},
    {"role": "AI Game Developer", "count": 20, "areas": "AI Oyun sektörü (yeni trend)"},
    {"role": "Data Scientist", "count": 18, "areas": "Finans, Pazarlama, E-ticaret"},
    {"role": "AI Full Stack Developer", "count": 15, "areas": "Startup'lar, GenAI"},
    {"role": "Computer Vision Engineer", "count": 12, "areas": "Görüntü İşleme, Savunma, Perakende"},
    {"role": "NLP Engineer", "count": 8, "areas": "Chatbot, Ses Teknolojileri"},
    {"role": "MLOps Engineer", "count": 5, "areas": "Büyük ölçekli ML deploy"},
    {"role": "Prompt/GenAI Specialist", "count": 5, "areas": "Üretken AI (en yeni rol)"},
]

# ═══════════════════════════════════════════════════════════════════
# BUILD OUTPUT
# ═══════════════════════════════════════════════════════════════════

output = {
    "meta": {
        "date": "2026-05-23",
        "totalCompanies": len(all_companies),
        "verifiedCompanies": tiers_count["verified"],
        "enrichedCompanies": tiers_count["enriched"],
        "totalInvestment": total_inv,
        "totalInvestmentFmt": fmt_funding(total_inv),
        "unicorns": 3,
        "activeJobs": total_positions,
        "activeInternships": len(internships),
        "jobCompanies": len(job_companies_list),
    },
    "companies": all_companies,
    "categories": dict(sorted(cats.items(), key=lambda x: x[1], reverse=True)),
    "cities": dict(sorted(cities.items(), key=lambda x: x[1], reverse=True)),
    "fundedTop15": [
        {"name": c["name"], "funding": c["funding"], "fundingRaw": c["fundingRaw"],
         "category": c.get("category"), "isUnicorn": c.get("isUnicorn", False),
         "city": c.get("city"), "founded": c.get("founded")}
        for c in funded[:15]
    ],
    "unicornList": [
        {"name": "Insider", "funding": "$777M", "description": "Omnichannel AI, İstanbul"},
        {"name": "Fal.ai", "funding": "$72M", "description": "Generative Media AI, NY/Körfez"},
        {"name": "Periodic Labs", "funding": "Bilinmiyor", "description": "AI, US (diaspora)"},
    ],
    "jobs": {
        "totalPositions": total_positions,
        "companies": job_companies_list,
        "internships": internships,
        "roles": roles_data,
    },
    "trends": [
        {"area": "AI Oyun", "growth": "Çok hızlı", "indicator": "4 şirket $117M yatırım (2024-2026)"},
        {"area": "Agentic AI", "growth": "Çok hızlı", "indicator": "Novus, Mindra, Insider Agent One"},
        {"area": "Üretken AI / GenAI", "growth": "Hızlı", "indicator": "68 şirket, en büyük 2. kategori"},
        {"area": "Sağlık AI", "growth": "Hızlı", "indicator": "5+ yeni girişim, $7M+ yatırım"},
        {"area": "Dikey AI", "growth": "Yeni", "indicator": "Solustiq — turizmde ilk dikey AI"},
        {"area": "Görüntü İşleme / CV", "growth": "İstikrarlı", "indicator": "89 şirket, en büyük kategori"},
        {"area": "NLP / Chatbot", "growth": "Olgun", "indicator": "42 şirket, rekabetçi pazar"},
    ],
}

out_path = f"{BASE}/dashboard/data.json"
with open(out_path, "w") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)
print(f"\nWritten: {out_path} ({os.path.getsize(out_path)/1024:.0f}KB)")
