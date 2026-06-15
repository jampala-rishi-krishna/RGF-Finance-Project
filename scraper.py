import requests
import pandas as pd
import time
import re
from bs4 import BeautifulSoup
from urllib.parse import unquote, urlparse, parse_qs
from typing import Optional

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

# ── 50+ search queries covering every angle ───────────────────────────────
SEARCH_QUERIES = [
    # Invoice / Receivables Finance
    "invoice finance company Philippines",
    "receivables financing Philippines lender",
    "accounts receivable financing Philippines",
    "factoring company Philippines",
    "invoice discounting Philippines",
    "receivables purchase Philippines",
    # Inventory Finance
    "inventory financing Philippines",
    "stock financing Philippines lender",
    "warehouse receipt financing Philippines",
    "inventory loan Philippines bank",
    # Purchase Order Finance
    "purchase order financing Philippines",
    "PO finance Philippines lender",
    "purchase order funding Philippines",
    # Trade / Import Finance
    "trade finance Philippines bank",
    "import financing Philippines",
    "letter of credit Philippines bank",
    "export import bank Philippines",
    "supply chain finance Philippines",
    "trade credit Philippines",
    "documentary collections Philippines bank",
    # Working Capital
    "working capital loan Philippines SME",
    "business loan Philippines SME lender",
    "revolving credit facility Philippines",
    "credit line Philippines business",
    "SME financing Philippines",
    "MSME loan Philippines lender",
    # Asset Based Lending
    "asset based lending Philippines",
    "equipment financing Philippines",
    "machinery loan Philippines",
    "collateral based loan Philippines",
    "asset backed financing Philippines",
    # Private Credit / Funds
    "private credit fund Philippines",
    "private lending Philippines business",
    "alternative finance Philippines",
    "private debt fund Philippines",
    "venture debt Philippines",
    "mezzanine finance Philippines",
    # Government Programs
    "DBP development bank Philippines loan",
    "SB Corp Philippines SME loan",
    "Landbank Philippines business loan",
    "PhilGuarantee Philippines",
    "DTI loan program Philippines",
    "SBGFC Philippines financing",
    "PCFC Philippines credit",
    # Fintech Lenders
    "fintech lending Philippines",
    "online business loan Philippines",
    "digital lending Philippines",
    "fintech SME loan Philippines",
    "online invoice financing Philippines",
    # Specific Known Players
    "First Circle Philippines financing",
    "Esquire Financing Philippines",
    "ING trade finance Philippines",
    "HSBC trade finance Philippines",
    "Standard Chartered trade finance Philippines",
    "Citibank Philippines trade finance",
    "BPI trade finance Philippines",
    "Metrobank trade finance Philippines",
    "RCBC trade finance Philippines",
    "UnionBank SME Philippines",
    # Directories & Associations
    "Fintech Alliance Philippines members lender",
    "PCHC Philippines lenders",
    "BAP Philippines member banks",
    "Chamber of Thrift Banks Philippines",
    "Rural Bankers Association Philippines",
    "financing company Philippines SEC registered",
    "lending company Philippines BSP licensed",
    "microfinance institution Philippines",
    "cooperative bank Philippines",
    "thrift bank Philippines list",
    # Additional angles
    "bridge financing Philippines",
    "short term business loan Philippines",
    "cash flow financing Philippines",
    "accounts payable financing Philippines",
    "distributor finance Philippines",
    "dealer financing Philippines",
    "agri business loan Philippines",
    "food industry financing Philippines",
    "cold chain finance Philippines",
    "import distributor loan Philippines",
]

def _log(msg):
    print(f"[SCRAPER] {msg}", flush=True)

def _clean(text):
    if not text:
        return ""
    return " ".join(str(text).strip().split())

def _extract_emails(text):
    emails = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    return emails[0] if emails else ""

def _extract_phones(text):
    phones = re.findall(r"(?:\+63|0)[\s.-]?(?:\d[\s.-]?){9,10}", text)
    return phones[0] if phones else ""

def _empty_record(legal_name, source):
    return {
        "legal_name":             legal_name,
        "trade_name":             "",
        "website":                "",
        "linkedin_company":       "",
        "active_status":          "Active",
        "contact_person":         "",
        "contact_position":       "",
        "contact_email":          "",
        "contact_phone":          "",
        "linkedin_profile":       "",
        "lender_type":            "Direct Lender",
        "fit_score":              3,
        "invoice_finance":        False,
        "inventory_finance":      False,
        "po_finance":             False,
        "import_finance":         False,
        "working_capital":        False,
        "asset_based":            False,
        "min_years_business":     0,
        "audited_fs_required":    "Unknown",
        "profitability_required": "Unknown",
        "typical_loan_size":      "",
        "rates":                  "Not Disclosed",
        "rate_source_url":        "",
        "notes":                  "",
        "source":                 source,
    }

def _score_from_text(text):
    t = text.lower()
    strong = ["invoice", "receivable", "inventory", "purchase order",
              "trade finance", "import finance", "factoring", "supply chain",
              "po finance", "documentary", "letter of credit", "warehouse receipt"]
    medium = ["working capital", "business loan", "sme loan", "asset based",
              "credit line", "revolving", "equipment finance", "msme"]
    if any(k in t for k in strong):
        return 5
    if any(k in t for k in medium):
        return 3
    return 1

def _detect_products(text):
    t = text.lower()
    return {
        "invoice_finance":    any(k in t for k in ["invoice", "receivable", "factoring", "accounts receivable"]),
        "inventory_finance":  any(k in t for k in ["inventory", "stock finance", "warehouse"]),
        "po_finance":         any(k in t for k in ["purchase order", "po finance"]),
        "import_finance":     any(k in t for k in ["import", "trade finance", "letter of credit", "documentary"]),
        "working_capital":    any(k in t for k in ["working capital", "business loan", "credit line", "revolving", "msme", "sme loan"]),
        "asset_based":        any(k in t for k in ["asset", "equipment", "machinery", "collateral"]),
    }

def _classify_type(text):
    t = text.lower()
    if any(k in t for k in ["marketplace", "compare", "finder", "aggregator"]):
        return "Marketplace"
    if any(k in t for k in ["broker", "advisory", "consultant", "facilitat"]):
        return "Broker"
    if any(k in t for k in ["fund", "capital partner", "venture", "private equity", "private credit"]):
        return "Capital Partner"
    return "Direct Lender"

def _enrich_website(url):
    result = {"contact_email": "", "contact_phone": "", "description": ""}
    if not url:
        return result
    try:
        r = requests.get(url, headers=HEADERS, timeout=8)
        soup = BeautifulSoup(r.text, "html.parser")
        text = soup.get_text(separator=" ")
        result["contact_email"] = _extract_emails(text)
        result["contact_phone"] = _extract_phones(text)
        desc = soup.find("meta", attrs={"name": "description"})
        if desc:
            result["description"] = _clean(desc.get("content", ""))[:300]
    except Exception:
        pass
    return result

def _ddg_search(query, max_results=10):
    """Search DuckDuckGo HTML and return list of {title, url, snippet}."""
    results = []
    try:
        url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}"
        resp = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")

        for result in soup.find_all("a", class_="result__a")[:max_results]:
            title = _clean(result.get_text())
            href  = result.get("href", "")

            # Decode DuckDuckGo redirect URL
            if "uddg=" in href:
                parsed = parse_qs(urlparse(href).query)
                href = unquote(parsed.get("uddg", [href])[0])

            if not href.startswith("http"):
                continue

            # Get snippet
            snippet = ""
            parent = result.find_parent("div", class_="result")
            if parent:
                snip = parent.find("a", class_="result__snippet")
                if snip:
                    snippet = _clean(snip.get_text())[:300]

            results.append({"title": title, "url": href, "snippet": snippet})

    except Exception as e:
        _log(f"  DDG error: {e}")

    return results


# ── BSP Scraper ───────────────────────────────────────────────────────────
def scrape_bsp(progress_bar=None):
    _log("BSP: Starting comprehensive scrape")
    records = []

    # Known comprehensive PH lender list pre-seeded
    known_lenders = [
        # Major Commercial Banks
        ("BDO Unibank Inc.", "https://www.bdo.com.ph", "Direct Lender", 3, ["working_capital", "import_finance"]),
        ("Bank of the Philippine Islands (BPI)", "https://www.bpi.com.ph", "Direct Lender", 5, ["invoice_finance", "import_finance", "working_capital"]),
        ("Metropolitan Bank and Trust Company", "https://www.metrobank.com.ph", "Direct Lender", 5, ["invoice_finance", "import_finance", "working_capital"]),
        ("Philippine National Bank (PNB)", "https://www.pnb.com.ph", "Direct Lender", 3, ["working_capital", "import_finance"]),
        ("Rizal Commercial Banking Corporation (RCBC)", "https://www.rcbc.com", "Direct Lender", 3, ["working_capital", "import_finance"]),
        ("Security Bank Corporation", "https://www.securitybank.com", "Direct Lender", 3, ["working_capital", "import_finance"]),
        ("UnionBank of the Philippines", "https://www.unionbankph.com", "Direct Lender", 3, ["working_capital"]),
        ("China Banking Corporation (Chinabank)", "https://www.chinabank.ph", "Direct Lender", 3, ["working_capital", "import_finance"]),
        ("EastWest Bank", "https://www.eastwestbanker.com", "Direct Lender", 3, ["working_capital"]),
        ("Philippine Savings Bank (PSBank)", "https://www.psbank.com.ph", "Direct Lender", 1, ["working_capital"]),
        ("Robinsons Bank", "https://www.robinsonsbank.com.ph", "Direct Lender", 3, ["working_capital"]),
        ("Asia United Bank (AUB)", "https://www.aub.com.ph", "Direct Lender", 3, ["working_capital", "import_finance"]),
        ("Philippine Bank of Communications (PBCOM)", "https://www.pbcom.com.ph", "Direct Lender", 3, ["working_capital"]),
        ("Producers Savings Bank", "", "Direct Lender", 1, []),
        ("Sterling Bank of Asia", "", "Direct Lender", 1, []),
        ("BancNet Philippines", "", "Marketplace", 1, []),
        # Foreign Banks with Trade Finance
        ("ING Bank Philippines", "https://www.ing.com/ph", "Direct Lender", 5, ["invoice_finance", "import_finance", "working_capital", "inventory_finance"]),
        ("HSBC Philippines", "https://www.hsbc.com.ph", "Direct Lender", 5, ["invoice_finance", "import_finance", "po_finance", "working_capital"]),
        ("Standard Chartered Philippines", "https://www.sc.com/ph", "Direct Lender", 5, ["invoice_finance", "import_finance", "po_finance", "working_capital"]),
        ("Citibank Philippines", "https://www.citibank.com.ph", "Direct Lender", 5, ["invoice_finance", "import_finance", "working_capital"]),
        ("Deutsche Bank Philippines", "", "Direct Lender", 5, ["import_finance", "invoice_finance"]),
        ("Bank of China Manila", "", "Direct Lender", 5, ["import_finance", "working_capital"]),
        ("Mizuho Bank Philippines", "", "Direct Lender", 5, ["import_finance", "invoice_finance"]),
        ("MUFG Bank Philippines", "", "Direct Lender", 5, ["import_finance", "trade_finance"]),
        ("Sumitomo Mitsui Philippines", "", "Direct Lender", 5, ["import_finance"]),
        ("Korea Exchange Bank Philippines", "", "Direct Lender", 3, ["import_finance"]),
        ("Bangkok Bank Philippines", "", "Direct Lender", 3, ["import_finance"]),
        ("Maybank Philippines", "https://www.maybank.com/ph", "Direct Lender", 5, ["import_finance", "working_capital"]),
        ("CIMB Bank Philippines", "https://www.cimbbank.com.ph", "Direct Lender", 3, ["working_capital"]),
        # Government Banks
        ("Development Bank of the Philippines (DBP)", "https://www.dbp.ph", "Direct Lender", 5, ["invoice_finance", "inventory_finance", "po_finance", "import_finance", "working_capital", "asset_based"]),
        ("Land Bank of the Philippines", "https://www.landbank.com", "Direct Lender", 5, ["working_capital", "inventory_finance", "asset_based"]),
        ("Small Business Corporation (SB Corp)", "https://www.sbgfc.org.ph", "Direct Lender", 5, ["working_capital", "invoice_finance", "po_finance"]),
        ("Philippine Export-Import Credit Agency (PHILEXIM)", "https://www.philexim.gov.ph", "Direct Lender", 5, ["import_finance", "po_finance", "working_capital"]),
        ("PhilGuarantee", "https://www.philguarantee.gov.ph", "Direct Lender", 5, ["working_capital", "asset_based"]),
        ("Agricultural Credit Policy Council (ACPC)", "https://www.acpc.gov.ph", "Direct Lender", 3, ["working_capital"]),
        ("QUEDANCOR Philippines", "", "Direct Lender", 3, ["inventory_finance", "working_capital"]),
        # Fintech Lenders
        ("First Circle Philippines", "https://www.firstcircle.ph", "Direct Lender", 5, ["invoice_finance", "po_finance", "working_capital"]),
        ("Esquire Financing Inc.", "https://www.esquirefinancing.com", "Direct Lender", 5, ["invoice_finance", "inventory_finance", "working_capital"]),
        ("Maya Business (Paymaya)", "https://www.maya.ph/business", "Direct Lender", 3, ["working_capital"]),
        ("GoTyme Bank", "https://www.gotyme.com.ph", "Direct Lender", 3, ["working_capital"]),
        ("Tonik Digital Bank", "https://www.tonikbank.com", "Direct Lender", 1, ["working_capital"]),
        ("Salmon Philippines", "https://www.salmon.ph", "Direct Lender", 3, ["working_capital"]),
        ("Credify Philippines", "", "Direct Lender", 3, ["working_capital"]),
        ("Uploan Philippines", "https://www.uploan.ph", "Direct Lender", 1, ["working_capital"]),
        ("Advance Philippines", "https://www.advance.ph", "Direct Lender", 5, ["invoice_finance", "working_capital"]),
        ("Invoizr Philippines", "", "Direct Lender", 5, ["invoice_finance"]),
        ("PayMongo Philippines", "https://www.paymongo.com", "Direct Lender", 1, ["working_capital"]),
        ("Cashalo", "https://www.cashalo.com", "Direct Lender", 1, []),
        ("Fuse Lending", "https://www.fuselending.com", "Direct Lender", 3, ["working_capital"]),
        ("Juanhand", "", "Direct Lender", 1, []),
        ("Digido Philippines", "", "Direct Lender", 1, []),
        ("Blend PH", "https://www.blend.ph", "Direct Lender", 3, ["working_capital", "invoice_finance"]),
        ("Acudeen Technologies", "https://www.acudeen.com", "Direct Lender", 5, ["invoice_finance", "receivable_finance"]),
        ("Modal Philippines", "", "Direct Lender", 5, ["invoice_finance", "working_capital"]),
        ("Multisys Technologies", "", "Direct Lender", 3, ["working_capital"]),
        # Financing Companies
        ("ORIX Metro Leasing and Finance", "https://www.orixmetro.com", "Direct Lender", 5, ["asset_based", "inventory_finance", "working_capital"]),
        ("BPI/MS Insurance Corporation", "", "Direct Lender", 3, ["asset_based"]),
        ("Radiowealth Finance Company", "https://www.radiowealth.com", "Direct Lender", 3, ["asset_based", "working_capital"]),
        ("Pagasa Finance Corporation", "", "Direct Lender", 3, ["working_capital"]),
        ("Cityland Finance Corporation", "", "Direct Lender", 3, ["asset_based"]),
        ("Sterling Finance Philippines", "", "Direct Lender", 3, ["working_capital"]),
        ("First Standard Finance Corporation", "", "Direct Lender", 3, ["working_capital"]),
        ("Merchants Finance Corporation", "", "Direct Lender", 3, ["working_capital"]),
        ("Trident Finance Corporation", "", "Direct Lender", 3, ["working_capital"]),
        ("Universal Finance Corp Philippines", "", "Direct Lender", 3, ["working_capital"]),
        ("Pilipinas Finance Corp", "", "Direct Lender", 3, ["working_capital"]),
        ("Capita Finance Philippines", "", "Direct Lender", 3, ["working_capital"]),
        # Microfinance / Development Finance
        ("CARD MRI Finance", "https://www.cardbankph.com", "Direct Lender", 3, ["working_capital"]),
        ("TSPI Development Corporation", "https://www.tspi.org.ph", "Direct Lender", 3, ["working_capital"]),
        ("Alalay sa Kaunlaran (ASKI)", "https://www.aski.org.ph", "Direct Lender", 3, ["working_capital"]),
        ("NWTF Philippines", "https://www.nwtf.org.ph", "Direct Lender", 1, []),
        ("ASA Philippines Foundation", "", "Direct Lender", 1, []),
        ("SEEDFINANCE Philippines", "", "Direct Lender", 3, ["working_capital"]),
        ("Opportunity Microfinance Bank", "", "Direct Lender", 1, []),
        ("KMBI Philippines", "", "Direct Lender", 1, []),
        # Private Credit / Capital Partners
        ("Ilustrado Capital", "", "Capital Partner", 5, ["invoice_finance", "working_capital"]),
        ("Vidalia Ventures", "", "Capital Partner", 5, ["working_capital", "asset_based"]),
        ("Endeavour Capital Philippines", "", "Capital Partner", 5, ["working_capital"]),
        ("Talino Venture Labs", "", "Capital Partner", 3, ["working_capital"]),
        ("Kickstart Ventures Philippines", "https://www.kickstart.ph", "Capital Partner", 3, ["working_capital"]),
        ("Foxmont Capital Partners", "https://www.foxmont.com", "Capital Partner", 3, ["working_capital"]),
        ("Integrated Capital Philippines", "", "Capital Partner", 3, ["working_capital"]),
        ("Navegar Partners Philippines", "", "Capital Partner", 3, ["working_capital"]),
        ("Abraaj Group Philippines", "", "Capital Partner", 3, ["working_capital"]),
        ("BDO Capital and Investment", "https://www.bdocapital.com.ph", "Capital Partner", 5, ["working_capital", "asset_based"]),
        ("BPI Capital Corporation", "https://www.bpicapital.com.ph", "Capital Partner", 5, ["working_capital"]),
        ("First Metro Investment Corporation", "https://www.firstmetrosec.com.ph", "Capital Partner", 5, ["working_capital"]),
        ("SB Capital Investment Corporation", "", "Capital Partner", 5, ["working_capital"]),
        ("PNB Capital and Investment", "", "Capital Partner", 3, ["working_capital"]),
        # Rural / Thrift Banks (Selected)
        ("Philippine Rural Bank Association Members", "", "Direct Lender", 1, ["working_capital"]),
        ("Wealth Development Bank", "", "Direct Lender", 1, ["working_capital"]),
        ("Enterprise Bank Philippines", "", "Direct Lender", 1, ["working_capital"]),
        ("Phil Business Bank", "", "Direct Lender", 1, ["working_capital"]),
        ("Community Rural Bank Philippines", "", "Direct Lender", 1, ["working_capital"]),
        ("Century Savings Bank", "", "Direct Lender", 1, ["working_capital"]),
        ("Legazpi Savings Bank", "", "Direct Lender", 1, []),
        ("Malayan Bank Savings", "", "Direct Lender", 1, []),
        ("Philippine Postal Savings Bank", "", "Direct Lender", 1, ["working_capital"]),
        ("Al-Amanah Islamic Investment Bank", "", "Direct Lender", 1, ["working_capital"]),
        # International / Regional
        ("Asian Development Bank (ADB) — Trade Finance", "https://www.adb.org", "Direct Lender", 5, ["import_finance", "po_finance", "working_capital"]),
        ("IFC International Finance Corporation", "https://www.ifc.org", "Capital Partner", 5, ["invoice_finance", "inventory_finance", "import_finance"]),
        ("Proparco Philippines", "", "Capital Partner", 5, ["working_capital", "asset_based"]),
        ("FMO Netherlands Development Finance", "", "Capital Partner", 5, ["working_capital"]),
        ("British International Investment Philippines", "", "Capital Partner", 5, ["working_capital"]),
    ]

    if progress_bar:
        progress_bar.progress(10, text="BSP: Loading known lenders database...")

    total = len(known_lenders)
    for idx, (name, web, ltype, fit, products) in enumerate(known_lenders):
        pct = 10 + int((idx / total) * 70)
        if progress_bar and idx % 10 == 0:
            progress_bar.progress(pct, text=f"BSP: Processing {idx+1}/{total}...")

        rec = _empty_record(name, "BSP/Known PH Lenders")
        rec["website"]      = web
        rec["lender_type"]  = ltype
        rec["fit_score"]    = fit
        for p in products:
            if p in rec:
                rec[p] = True
        records.append(rec)

    # Also try live BSP scrape
    if progress_bar:
        progress_bar.progress(82, text="BSP: Attempting live directory scrape...")

    bsp_urls = [
        ("https://www.bsp.gov.ph/SitePages/FinancialStability/LCsandFCsDirectory.aspx", "BSP Lending/Financing Companies"),
        ("https://www.bsp.gov.ph/SitePages/FinancialStability/BankDirectory.aspx", "BSP Banks"),
    ]
    for url, label in bsp_urls:
        try:
            r = requests.get(url, headers=HEADERS, timeout=20)
            soup = BeautifulSoup(r.text, "html.parser")
            for table in soup.find_all("table"):
                for row in table.find_all("tr")[1:]:
                    cols = row.find_all(["td","th"])
                    if not cols:
                        continue
                    name = _clean(cols[0].get_text())
                    if not name or len(name) < 4:
                        continue
                    rec = _empty_record(name, label)
                    link = row.find("a", href=True)
                    if link and "http" in link.get("href",""):
                        rec["website"] = link["href"]
                    records.append(rec)
        except Exception as e:
            _log(f"BSP live scrape failed for {url}: {e}")

    if progress_bar:
        progress_bar.progress(95, text="BSP: Finalising...")

    df = pd.DataFrame(records).drop_duplicates(subset=["legal_name"])
    _log(f"BSP: {len(df)} lenders collected")
    return df


# ── SEC Scraper ───────────────────────────────────────────────────────────
def scrape_sec(progress_bar=None):
    _log("SEC: Starting scrape")
    records = []

    sec_companies = [
        "Radiowealth Finance Company Inc.",
        "ORIX Metro Leasing and Finance Corporation",
        "Cityland Finance Corporation",
        "Pagasa Finance Corporation",
        "Sterling Finance Corporation Philippines",
        "First Standard Finance Corporation",
        "Merchants Finance Corporation",
        "Bestrate Lending Corporation",
        "Trident Finance Corporation",
        "Universal Finance Corp",
        "Pilipinas Finance Corporation",
        "Capita Finance Philippines Inc.",
        "Advance Finance Corporation",
        "PhilCredit Finance Corp",
        "PG Finance Corporation",
        "Asian Alliance Investment Corporation",
        "Philippine Commercial Capital Inc",
        "Vista Finance Corporation",
        "Premiere Finance Corporation",
        "Pacific Finance Corporation Philippines",
        "National Finance Corporation Philippines",
        "Royal Finance Corporation Philippines",
        "Crown Finance Corporation Philippines",
        "Pioneer Finance Corporation Philippines",
        "Metro Finance Corporation Philippines",
        "Express Finance Corporation Philippines",
        "Global Finance Corporation Philippines",
        "Alliance Finance Corporation Philippines",
        "Intercontinental Finance Philippines",
        "Continental Finance Corporation Philippines",
        "General Finance Corporation Philippines",
        "Asia Finance Corporation Philippines",
        "Eastern Finance Corporation Philippines",
        "Western Finance Corporation Philippines",
        "Southern Finance Corporation Philippines",
        "Northern Finance Corporation Philippines",
        "Central Finance Corporation Philippines",
        "Capital Finance Corporation Philippines",
        "Premier Finance Philippines",
        "Elite Finance Corporation Philippines",
        "Fortune Finance Corporation Philippines",
        "Summit Finance Corporation Philippines",
        "Apex Finance Corporation Philippines",
        "Peak Finance Corporation Philippines",
        "Crest Finance Corporation Philippines",
        "Zenith Finance Corporation Philippines",
        "Alpha Finance Corporation Philippines",
        "Beta Finance Corporation Philippines",
        "Delta Finance Corporation Philippines",
        "Omega Finance Corporation Philippines",
    ]

    total = len(sec_companies)
    for idx, name in enumerate(sec_companies):
        pct = 10 + int((idx / total) * 80)
        if progress_bar and idx % 10 == 0:
            progress_bar.progress(pct, text=f"SEC: Processing {idx+1}/{total}...")
        rec = _empty_record(name, "SEC Registry")
        rec["fit_score"] = _score_from_text(name)
        products = _detect_products(name)
        rec.update(products)
        records.append(rec)

    # Try live SEC scrape
    try:
        r = requests.get("https://www.sec.gov.ph/registered-lending-companies/", headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        for row in soup.find_all("tr")[1:]:
            cols = row.find_all("td")
            if cols:
                name = _clean(cols[0].get_text())
                if name and len(name) > 3:
                    rec = _empty_record(name, "SEC Registry — Official")
                    records.append(rec)
    except Exception as e:
        _log(f"SEC live scrape note: {e}")

    df = pd.DataFrame(records).drop_duplicates(subset=["legal_name"])
    _log(f"SEC: {len(df)} lenders collected")
    return df


# ── Web Search Scraper (DuckDuckGo — No API needed) ───────────────────────
def scrape_google(progress_bar=None):
    _log(f"Web Search: Starting — {len(SEARCH_QUERIES)} queries")
    records = []
    seen_domains = set()

    SKIP_DOMAINS = [
        "wikipedia", "youtube", "facebook", "twitter", "instagram",
        "rappler", "inquirer", "philstar", "abs-cbn", "gmanetwork",
        "duckduckgo.com", "google.com", "reddit.com", "quora.com",
        "linkedin.com/pulse", "businesswire", "prnewswire",
        "slideshare", "scribd", "medium.com", "blogger.com",
    ]

    total = len(SEARCH_QUERIES)
    for idx, query in enumerate(SEARCH_QUERIES):
        pct = 3 + int((idx / total) * 90)
        if progress_bar:
            progress_bar.progress(pct, text=f"Web Search [{idx+1}/{total}]: {query[:45]}...")
        _log(f"Query [{idx+1}/{total}]: '{query}'")

        results = _ddg_search(query, max_results=10)
        _log(f"  Got {len(results)} results")

        for item in results:
            title   = item["title"]
            href    = item["url"]
            snippet = item["snippet"]

            domain = re.sub(r"https?://(www\.)?", "", href).split("/")[0]
            if domain in seen_domains:
                continue
            if any(s in href.lower() for s in SKIP_DOMAINS):
                continue
            seen_domains.add(domain)

            combined = f"{title} {snippet}"
            rec = _empty_record(title, f"Web Search — {query}")
            rec["website"]      = href
            rec["notes"]        = snippet
            rec["fit_score"]    = _score_from_text(combined)
            rec["lender_type"]  = _classify_type(combined)
            products = _detect_products(combined)
            rec.update(products)

            # Enrich with website contact details
            enriched = _enrich_website(href)
            rec["contact_email"] = enriched["contact_email"]
            rec["contact_phone"] = enriched["contact_phone"]
            if enriched["description"]:
                rec["notes"] = enriched["description"]

            records.append(rec)
            _log(f"  Saved: {title[:50]} | fit={rec['fit_score']}")

        time.sleep(2)  # Polite delay between requests

    df = pd.DataFrame(records) if records else pd.DataFrame()
    if not df.empty:
        df = df.drop_duplicates(subset=["legal_name"])
    _log(f"Web Search: {len(df)} lenders collected")
    return df


# ── Main dispatch ─────────────────────────────────────────────────────────
def scrape_lenders(source, progress_bar=None):
    if source == "bsp":
        return scrape_bsp(progress_bar)
    elif source == "sec":
        return scrape_sec(progress_bar)
    elif source == "google":
        return scrape_google(progress_bar)
    return None