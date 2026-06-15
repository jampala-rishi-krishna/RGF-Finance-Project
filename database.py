import re
import pandas as pd
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY

_client: Client = None

def get_client() -> Client:
    global _client
    if _client is None:
        _client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _client

def init_db():
    try:
        get_client().table("lenders").select("id").limit(1).execute()
    except Exception:
        pass

def get_lenders() -> pd.DataFrame:
    try:
        resp = get_client().table("lenders").select("*").order("fit_score", desc=True).execute()
        if resp.data:
            return pd.DataFrame(resp.data)
    except Exception:
        pass
    return pd.DataFrame()

def save_lenders(df: pd.DataFrame) -> tuple[int, int]:
    if df.empty:
        return 0, 0
    client = get_client()
    saved = 0
    dupes = 0

    try:
        existing = client.table("lenders").select("legal_name, website").execute()
        existing_names   = {r["legal_name"].lower().strip() for r in (existing.data or []) if r.get("legal_name")}
        existing_domains = set()
        for r in (existing.data or []):
            web = r.get("website", "") or ""
            if web:
                domain = re.sub(r"https?://(www\.)?", "", web).split("/")[0].lower().strip()
                if domain:
                    existing_domains.add(domain)
    except Exception:
        existing_names   = set()
        existing_domains = set()

    to_insert = []
    for rec in df.to_dict("records"):
        name   = str(rec.get("legal_name", "")).lower().strip()
        web    = str(rec.get("website", "") or "")
        domain = re.sub(r"https?://(www\.)?", "", web).split("/")[0].lower().strip()

        # Check 1 — exact name match
        if name and name in existing_names:
            dupes += 1
            continue

        # Check 2 — same website domain
        if domain and domain in existing_domains:
            dupes += 1
            continue

        # Check 3 — partial name match (catches abbreviations)
        is_dupe = False
        for existing_name in existing_names:
            if len(name) > 5 and len(existing_name) > 5:
                if name in existing_name or existing_name in name:
                    is_dupe = True
                    break
        if is_dupe:
            dupes += 1
            continue

        clean = {k: (v if v is not None else "") for k, v in rec.items()}
        clean.pop("id", None)
        for bool_col in ["invoice_finance", "inventory_finance", "po_finance",
                         "import_finance", "working_capital", "asset_based"]:
            clean[bool_col] = bool(clean.get(bool_col, False))
        clean["fit_score"]          = int(clean.get("fit_score", 3) or 3)
        clean["min_years_business"] = int(clean.get("min_years_business", 0) or 0)

        to_insert.append(clean)
        existing_names.add(name)
        if domain:
            existing_domains.add(domain)

    if to_insert:
        try:
            for i in range(0, len(to_insert), 50):
                get_client().table("lenders").insert(to_insert[i:i+50]).execute()
            saved = len(to_insert)
        except Exception as e:
            raise RuntimeError(f"DB insert failed: {e}")

    return saved, dupes

def update_lender(lender_id: int, fields: dict):
    try:
        get_client().table("lenders").update(fields).eq("id", lender_id).execute()
    except Exception as e:
        raise RuntimeError(f"Update failed: {e}")

# ── LinkedIn Results ───────────────────────────────────────────────────────

def get_linkedin_results() -> pd.DataFrame:
    """Fetch all stored LinkedIn verification results ordered by most recent."""
    try:
        resp = (get_client()
                .table("linkedin_results")
                .select("*")
                .order("verified_at", desc=True)
                .execute())
        if resp.data:
            return pd.DataFrame(resp.data)
    except Exception:
        pass
    return pd.DataFrame()

def get_verified_names() -> set:
    """Return the set of lender names already in the linkedin_results table."""
    try:
        resp = get_client().table("linkedin_results").select("lender_name").execute()
        return {r["lender_name"].lower().strip() for r in (resp.data or [])}
    except Exception:
        return set()

def save_linkedin_results(records: list) -> int:
    """
    Upsert a list of linkedin result dicts into the DB.
    If the lender_name already exists, the row is updated (re-verification).
    Returns the number of rows upserted.
    """
    if not records:
        return 0
    try:
        from datetime import datetime, timezone
        ts = datetime.now(timezone.utc).isoformat()
        for r in records:
            r["verified_at"] = ts
        get_client().table("linkedin_results").upsert(
            records, on_conflict="lender_name"
        ).execute()
        return len(records)
    except Exception as e:
        raise RuntimeError(f"LinkedIn results save failed: {e}")
