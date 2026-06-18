import requests
import pandas as pd
import time
import re
from bs4 import BeautifulSoup
from urllib.parse import quote
from config import SERPAPI_KEY

def _log(msg):
    print(f"[LINKEDIN] {msg}", flush=True)

def _clean(text):
    if not text:
        return ""
    return " ".join(str(text).strip().split())

# ── Pre-built LinkedIn map for known PH lenders ───────────────────────────
KNOWN_LINKEDIN = {
    "bpi":                                    "https://www.linkedin.com/company/bpi-bank-of-the-philippine-islands",
    "bank of the philippine islands":         "https://www.linkedin.com/company/bpi-bank-of-the-philippine-islands",
    "bpi trade finance":                      "https://www.linkedin.com/company/bpi-bank-of-the-philippine-islands",
    "metrobank":                              "https://www.linkedin.com/company/metropolitan-bank-and-trust-company",
    "metrobank trade finance":                "https://www.linkedin.com/company/metropolitan-bank-and-trust-company",
    "metropolitan bank and trust company":    "https://www.linkedin.com/company/metropolitan-bank-and-trust-company",
    "bdo unibank":                            "https://www.linkedin.com/company/bdo-unibank-inc-",
    "bdo unibank inc.":                       "https://www.linkedin.com/company/bdo-unibank-inc-",
    "dbp":                                    "https://www.linkedin.com/company/development-bank-of-the-philippines",
    "dbp development bank":                   "https://www.linkedin.com/company/development-bank-of-the-philippines",
    "development bank of the philippines (dbp)": "https://www.linkedin.com/company/development-bank-of-the-philippines",
    "sb corp":                                "https://www.linkedin.com/company/small-business-corporation",
    "small business corporation (sb corp)":   "https://www.linkedin.com/company/small-business-corporation",
    "ing philippines":                        "https://www.linkedin.com/company/ing-hubs-philippines",
    "ing bank philippines":                   "https://www.linkedin.com/company/ing-hubs-philippines",
    "hsbc philippines":                       "https://www.linkedin.com/company/hsbc",
    "standard chartered philippines":         "https://www.linkedin.com/company/standard-chartered-bank",
    "citibank philippines":                   "https://www.linkedin.com/company/citi",
    "pnb":                                    "https://www.linkedin.com/company/philippine-national-bank",
    "philippine national bank (pnb)":         "https://www.linkedin.com/company/philippine-national-bank",
    "rcbc":                                   "https://www.linkedin.com/company/rcbc",
    "rizal commercial banking corporation (rcbc)": "https://www.linkedin.com/company/rcbc",
    "security bank corporation":              "https://www.linkedin.com/company/security-bank-corporation",
    "unionbank of the philippines":           "https://www.linkedin.com/company/unionbank-of-the-philippines",
    "china banking corporation (chinabank)":  "https://www.linkedin.com/company/china-banking-corporation",
    "eastwest bank":                          "https://www.linkedin.com/company/eastwest-bank",
    "land bank of the philippines":           "https://www.linkedin.com/company/land-bank-of-the-philippines",
    "philexim":                               "https://www.linkedin.com/company/philexim",
    "philippine export-import credit agency (philexim)": "https://www.linkedin.com/company/philexim",
    "philguarantee":                          "https://www.linkedin.com/company/philguarantee",
    "first circle philippines":               "https://www.linkedin.com/company/first-circle",
    "esquire financing inc.":                 "https://www.linkedin.com/company/esquire-financing-inc-",
    "maya business (paymaya)":                "https://www.linkedin.com/company/maya-philippines",
    "gotyme bank":                            "https://www.linkedin.com/company/gotyme-bank",
    "tonik digital bank":                     "https://www.linkedin.com/company/tonikbank",
    "acudeen technologies":                   "https://www.linkedin.com/company/acudeen-technologies",
    "orix metro leasing and finance corporation": "https://www.linkedin.com/company/orix-metro-leasing-and-finance-corporation",
    "advance philippines":                    "https://www.linkedin.com/company/advance-ph",
    "fuse lending":                           "https://www.linkedin.com/company/fuse-lending",
    "blend ph":                               "https://www.linkedin.com/company/blend-ph",
    "salmon philippines":                     "https://www.linkedin.com/company/salmon-ph",
    "maybank philippines":                    "https://www.linkedin.com/company/maybank",
    "cimb bank philippines":                  "https://www.linkedin.com/company/cimb-bank",
    "asian development bank (adb) — trade finance": "https://www.linkedin.com/company/asian-development-bank",
    "ifc international finance corporation":  "https://www.linkedin.com/company/international-finance-corporation",
    "bdo capital and investment":             "https://www.linkedin.com/company/bdo-capital-and-investment-corporation",
    "bpi capital corporation":                "https://www.linkedin.com/company/bpi-capital-corporation",
    "first metro investment corporation":     "https://www.linkedin.com/company/first-metro-investment-corporation",
    "asia united bank (aub)":                 "https://www.linkedin.com/company/asia-united-bank",
    "philippine bank of communications (pbcom)": "https://www.linkedin.com/company/pbcom",
    "robinsons bank":                         "https://www.linkedin.com/company/robinsons-bank-corporation",
    "psbank":                                 "https://www.linkedin.com/company/psbank",
    "deutsche bank philippines":              "https://www.linkedin.com/company/deutsche-bank",
    "mizuho bank philippines":                "https://www.linkedin.com/company/mizuho-bank",
    "mufg bank philippines":                  "https://www.linkedin.com/company/mufg-bank-ltd-",
    "kickstart ventures philippines":         "https://www.linkedin.com/company/kickstart-ventures",
    "foxmont capital partners":               "https://www.linkedin.com/company/foxmont-capital-partners",
    "card mri finance":                       "https://www.linkedin.com/company/card-mri",
    "tspi development corporation":           "https://www.linkedin.com/company/tspi-development-corporation",
    "paymongo":                               "https://www.linkedin.com/company/paymongo",
    "uploan philippines":                     "https://www.linkedin.com/company/uploan",
    "cashalo":                                "https://www.linkedin.com/company/cashalo",
    "salmon ph":                              "https://www.linkedin.com/company/salmon-ph",
    "bank of commerce":                       "https://www.linkedin.com/company/bank-of-commerce-philippines",
    "radiowealth finance company":            "https://www.linkedin.com/company/radiowealth-finance-company",
    "modal philippines":                      "https://www.linkedin.com/company/modal-philippines",
    "credify philippines":                    "https://www.linkedin.com/company/credify",
    "juanhand":                               "https://www.linkedin.com/company/juanhand",
    "psbank":                                 "https://www.linkedin.com/company/psbank",
    "maybank":                                "https://www.linkedin.com/company/maybank",
    "bangkok bank philippines":               "https://www.linkedin.com/company/bangkok-bank",
    "sumitomo mitsui philippines":            "https://www.linkedin.com/company/smbc-group",
    "proparco philippines":                   "https://www.linkedin.com/company/proparco",
    "british international investment philippines": "https://www.linkedin.com/company/british-international-investment",
    "fmo netherlands development finance":    "https://www.linkedin.com/company/fmo-entrepreneurial-development-bank",
}

GARBAGE_PATTERNS = [
    r"^top \d+", r"^how ", r"^why ", r"^what ", r"^best ",
    r"\| ensun$", r"metapress", r"spelling bee", r"goodfirms",
    r"market size", r"market forecast", r" - results - page",
    r"everything you need to know", r"game.changer", r"outsourcing",
]

def _is_real_company(name: str) -> bool:
    n = name.lower().strip()
    for pattern in GARBAGE_PATTERNS:
        if re.search(pattern, n):
            return False
    if len(name) > 80:
        return False
    if " | " in name and len(name) > 50:
        return False
    if " - " in name and len(name) > 60:
        return False
    return True

def _lookup_known(company_name: str) -> str:
    """Check hardcoded map — exact then partial match."""
    key = company_name.lower().strip()
    if key in KNOWN_LINKEDIN:
        return KNOWN_LINKEDIN[key]
    for known_key, url in KNOWN_LINKEDIN.items():
        if known_key in key or key in known_key:
            return url
    return ""

# ── SerpApi — Real Google Results ─────────────────────────────────────────

def _serpapi_company(company_name: str, website: str = "") -> str:
    """Search Google via SerpApi for LinkedIn company page."""
    try:
        resp = requests.get(
            "https://serpapi.com/search",
            params={
                "q":       f'site:linkedin.com/company "{company_name}" Philippines',
                "api_key": SERPAPI_KEY,
                "num":     5,
                "engine":  "google",
                "gl":      "ph",
                "hl":      "en",
            },
            timeout=20
        )
        data = resp.json()

        # Check API errors
        if "error" in data:
            _log(f"  SerpApi error: {data['error']}")
            return ""

        import difflib
        from urllib.parse import urlparse

        best_link = ""
        best_score = 0

        # derive domain from website if provided
        site_domain = ""
        if website:
            try:
                site_domain = urlparse(website).netloc.lower().lstrip("www.")
            except Exception:
                site_domain = ""

        def _slug_tokens(link_url: str):
            try:
                parts = urlparse(link_url).path.split("/")
                # take last non-empty part
                for p in reversed(parts):
                    if p:
                        slug = p.lower()
                        return re.sub(r"[^a-z0-9]+", " ", slug).split()
            except Exception:
                pass
            return []

        name_tokens = re.sub(r"[^a-z0-9]+", " ", company_name.lower()).split()

        for result in data.get("organic_results", []):
            link = result.get("link", "")
            title = result.get("title", "") or ""
            snippet = result.get("snippet", "") or ""
            if "linkedin.com/company/" not in link:
                continue

            match = re.search(r"(https?://(?:www\.)?linkedin\.com/company/[^/?#&\s]+)", link)
            if not match:
                continue

            candidate = match.group(1)
            combined = f"{title} {snippet}".lower()

            # scoring components
            country_boost = 50 if any(k in combined for k in ["philippin", "manila", "philippines"]) else 0
            domain_boost = 0
            slug_boost = 0
            try:
                ratio = difflib.SequenceMatcher(None, company_name.lower(), title.lower()).ratio()
            except Exception:
                ratio = 0.0

            # slug token match
            slug_tokens = _slug_tokens(candidate)
            shared = sum(1 for t in name_tokens if t in slug_tokens)
            if shared > 0:
                slug_boost = 30 if shared >= 1 else 10

            # domain match in result text (title/snippet/link)
            domain_text = (link + " " + title + " " + snippet).lower()
            domain_match = False
            if site_domain:
                if site_domain in domain_text:
                    domain_match = True
                    domain_boost = 40
                else:
                    # attempt to fetch candidate LinkedIn page and look for the website/domain
                    try:
                        r = requests.get(candidate, headers={"User-Agent": "Mozilla/5.0"}, timeout=6)
                        if site_domain in (r.text or "").lower():
                            domain_match = True
                            domain_boost = 50
                    except Exception:
                        pass

            name_score = int(ratio * 30)

            score = 1 + country_boost + domain_boost + slug_boost + name_score

            # build debug string
            debug = f"country={country_boost}|domain={domain_boost}|slug={slug_boost}|name={name_score}|total={score}"

            # acceptance rules
            # - If domain matched, accept candidate if score reasonably high
            # - If no domain match, require name similarity >= 0.45 to accept even if country match exists
            accept = False
            if domain_match and score >= 30:
                accept = True
            elif not domain_match:
                if ratio >= 0.45 and score >= 20:
                    accept = True

            # prefer higher score
            if score > best_score:
                best_score = score
                best_link = candidate
                best_debug = debug

            if accept:
                _log(f"  SerpApi company found: {candidate} | {debug}")
                # attach debug to the returned value via a tuple-style string
                return candidate + "|" + debug

        if best_link:
            _log(f"  SerpApi company best candidate: {best_link} | {best_debug}")
            return best_link + "|" + best_debug

    except Exception as e:
        _log(f"  SerpApi company search error: {e}")

    return ""


def _serpapi_employees(company_name: str) -> list:
    """Search Google via SerpApi for employee LinkedIn profiles."""
    people    = []
    seen_urls = set()

    queries = [
        f'site:linkedin.com/in "{company_name}" Philippines "relationship manager" OR "trade finance" OR "SME lending"',
        f'site:linkedin.com/in "{company_name}" Philippines "director" OR "head" OR "vice president" finance',
        f'site:linkedin.com/in "{company_name}" Philippines "account manager" OR "business development"',
    ]

    for query in queries:
        try:
            resp = requests.get(
                "https://serpapi.com/search",
                params={
                    "q":       query,
                    "api_key": SERPAPI_KEY,
                    "num":     8,
                    "engine":  "google",
                    "gl":      "ph",
                    "hl":      "en",
                },
                timeout=20
            )
            data = resp.json()

            if "error" in data:
                _log(f"  SerpApi error: {data['error']}")
                break

            for result in data.get("organic_results", []):
                link    = result.get("link", "")
                title   = result.get("title", "")
                snippet = result.get("snippet", "")

                if "linkedin.com/in/" not in link:
                    continue

                match = re.search(
                    r"(https?://(?:www\.)?linkedin\.com/in/[^/?#&\s]+)",
                    link
                )
                if not match:
                    continue

                profile_url = match.group(1)
                if profile_url in seen_urls:
                    continue
                seen_urls.add(profile_url)

                # Parse name and position from Google title
                name     = ""
                position = ""

                if " - " in title:
                    parts    = title.split(" - ")
                    name     = parts[0].strip()
                    pos_part = parts[1] if len(parts) > 1 else ""
                    position = pos_part.split(" at ")[0].strip() if " at " in pos_part else pos_part.split("|")[0].strip()
                elif " | " in title:
                    name = title.split(" | ")[0].strip()
                else:
                    name = title.strip()

                # Clean up
                name     = re.sub(r"\s*\|\s*LinkedIn.*$", "", name).strip()
                position = re.sub(r"\s*\|\s*LinkedIn.*$", "", position).strip()

                combined = f"{title} {snippet}".lower()

                # keep PH and general candidates separately
                if name and 2 < len(name) < 60:
                    candidate = {
                        "name":        name,
                        "position":    position,
                        "profile_url": profile_url,
                        "snippet":     snippet[:100],
                    }
                    # classify as PH candidate if mentions Philippines/Manila
                    if any(k in combined for k in ["philippin", "manila", "philippines"]):
                        people.append(candidate)
                        _log(f"  Employee (PH): {name} | {position}")
                    else:
                        # store in a temp list for fallback
                        if len(people) < 8:
                            people.append(candidate)
                            _log(f"  Employee (fallback): {name} | {position}")

        except Exception as e:
            _log(f"  SerpApi employee search error: {e}")

        time.sleep(1)  # Small delay between queries

    return people[:8]


# ── Batch helpers ─────────────────────────────────────────────────────────

def get_next_batch(all_df: pd.DataFrame, verified_names: set, batch_size: int = 50) -> pd.DataFrame:
    """
    From all_df, return up to batch_size rows that are:
    - Real company names (pass _is_real_company)
    - Not already in verified_names
    """
    if all_df.empty:
        return pd.DataFrame()
    mask = all_df["legal_name"].apply(
        lambda n: _is_real_company(str(n)) and str(n).lower().strip() not in verified_names
    )
    return all_df[mask].head(batch_size).copy()


def verify_batch(batch_df: pd.DataFrame, progress_bar=None) -> list:
    """
    Verify a batch DataFrame and return a list of dicts ready to upsert into
    the linkedin_results Supabase table (snake_case keys).
    """
    if batch_df.empty:
        return []
    result_df = verify_linkedin(batch_df, progress_bar)
    if result_df.empty:
        return []
    records = []
    for _, row in result_df.iterrows():
        records.append({
            "lender_name":      str(row.get("Lender Name", "") or ""),
            "website":          str(row.get("Website", "") or ""),
            "has_linkedin":     str(row.get("Has LinkedIn", "No") or "No"),
            "linkedin_company": str(row.get("LinkedIn Company", "") or ""),
            "members_found":    int(row.get("Members Found", 0) or 0),
            "member_details":   str(row.get("Member Details", "None found") or ""),
            "fit_score":        int(row.get("Fit Score", 3) or 3),
            "lender_type":      str(row.get("Type", "") or ""),
        })
    return records


# ── Main verification ──────────────────────────────────────────────────────
def verify_linkedin(lenders_df: pd.DataFrame, progress_bar=None) -> pd.DataFrame:
    results = []
    real_df = lenders_df[lenders_df["legal_name"].apply(_is_real_company)].copy()
    total   = len(real_df)
    skipped = len(lenders_df) - total

    _log(f"Verifying {total} companies ({skipped} garbage entries skipped)")
    _log(f"SerpApi key: {SERPAPI_KEY[:12]}...")

    for idx, (_, row) in enumerate(real_df.iterrows()):
        company_name = str(row.get("legal_name", "") or "").strip()
        if not company_name:
            continue

        pct = int(((idx + 1) / total) * 93) + 2
        if progress_bar:
            progress_bar.progress(
                min(pct, 95),
                text=f"Verifying [{idx+1}/{total}]: {company_name[:40]}..."
            )
        _log(f"\n[{idx+1}/{total}] {company_name}")

        # ── Step 1: existing stored value ──────────────────────────────────
        company_li = str(row.get("linkedin_company", "") or "").strip()
        if company_li:
            _log(f"  Using stored LinkedIn: {company_li}")

        # ── Step 2: known hardcoded map (instant, no API call) ─────────────
        if not company_li:
            company_li = _lookup_known(company_name)
            if company_li:
                _log(f"  Found in known map: {company_li}")

        # ── Step 3: SerpApi Google search (uses API credits) ───────────────
        if not company_li:
            _log(f"  Searching via SerpApi...")
            website = str(row.get("website", "") or "")
            company_li = _serpapi_company(company_name, website)
            time.sleep(1)

        # company_li may include a trailing debug string separated by '|'
        score_debug = ""
        if company_li:
            if "|" in company_li and company_li.startswith("http"):
                parts = company_li.split("|", 1)
                company_li = parts[0]
                score_debug = parts[1]
        has_linkedin = "Yes" if company_li else "No"
        _log(f"  LinkedIn: {has_linkedin} | {company_li} | debug={score_debug}")

        # ── Step 4: find employees ─────────────────────────────────────────
        employees = []

        if has_linkedin == "Yes":
            # Try SerpApi employee search
            _log(f"  Searching employees via SerpApi...")
            employees = _serpapi_employees(company_name)

        # If no employees found but company LinkedIn exists,
        # add direct link to company people page
        if not employees and company_li:
            employees = [{
                "name":        "Browse all employees",
                "position":    "Click to view on LinkedIn",
                "profile_url": company_li.rstrip("/") + "/people/",
                "snippet":     "",
            }]

        _log(f"  Employees found: {len(employees)}")

        # ── Format member details ──────────────────────────────────────────
        member_parts = []
        for emp in employees:
            label = emp["name"]
            if emp.get("position"):
                label += f" ({emp['position']})"
            label += f": {emp['profile_url']}"
            member_parts.append(label)

        members_str = " | ".join(member_parts) if member_parts else "None found"

        results.append({
            "Lender Name":      company_name,
            "Website":          str(row.get("website", "") or ""),
            "Has LinkedIn":     has_linkedin,
            "LinkedIn Company": company_li,
            "Score Debug":      score_debug,
            "Members Found":    len(employees),
            "Member Details":   members_str,
            "Fit Score":        row.get("fit_score", 3),
            "Type":             row.get("lender_type", ""),
        })

        # Polite delay between companies to preserve SerpApi credits
        time.sleep(2)

    _log(f"\nComplete. {len(results)} companies processed.")
    return pd.DataFrame(results)