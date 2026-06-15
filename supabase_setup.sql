-- =========================================================
-- RARE Global Food — Lender Target Database
-- Run this ONCE in your Supabase SQL Editor
-- Project: kmglkxozbinkukqrrboz
-- =========================================================

CREATE TABLE IF NOT EXISTS lenders (
    id                      BIGSERIAL PRIMARY KEY,

    -- Company Identity
    legal_name              TEXT NOT NULL,
    trade_name              TEXT DEFAULT '',
    website                 TEXT DEFAULT '',
    linkedin_company        TEXT DEFAULT '',
    active_status           TEXT DEFAULT 'Active',

    -- Contact
    contact_person          TEXT DEFAULT '',
    contact_position        TEXT DEFAULT '',
    contact_email           TEXT DEFAULT '',
    contact_phone           TEXT DEFAULT '',
    linkedin_profile        TEXT DEFAULT '',

    -- Classification
    lender_type             TEXT DEFAULT 'Direct Lender',
    fit_score               INT  DEFAULT 3,

    -- Products Offered
    invoice_finance         BOOLEAN DEFAULT FALSE,
    inventory_finance       BOOLEAN DEFAULT FALSE,
    po_finance              BOOLEAN DEFAULT FALSE,
    import_finance          BOOLEAN DEFAULT FALSE,
    working_capital         BOOLEAN DEFAULT FALSE,
    asset_based             BOOLEAN DEFAULT FALSE,

    -- Borrower Requirements
    min_years_business      INT  DEFAULT 0,
    audited_fs_required     TEXT DEFAULT 'Unknown',
    profitability_required  TEXT DEFAULT 'Unknown',
    typical_loan_size       TEXT DEFAULT '',

    -- Rates
    rates                   TEXT DEFAULT 'Not Disclosed',
    rate_source_url         TEXT DEFAULT '',

    -- Meta
    notes                   TEXT DEFAULT '',
    source                  TEXT DEFAULT '',
    created_at              TIMESTAMPTZ DEFAULT NOW(),
    updated_at              TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_lenders_fit_score  ON lenders(fit_score DESC);
CREATE INDEX IF NOT EXISTS idx_lenders_type       ON lenders(lender_type);
CREATE INDEX IF NOT EXISTS idx_lenders_name       ON lenders(legal_name);

-- Auto-update updated_at
CREATE OR REPLACE FUNCTION update_lender_updated_at()
RETURNS TRIGGER AS $$
BEGIN NEW.updated_at = NOW(); RETURN NEW; END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_lenders_updated ON lenders;
CREATE TRIGGER trg_lenders_updated
    BEFORE UPDATE ON lenders
    FOR EACH ROW EXECUTE FUNCTION update_lender_updated_at();

-- RLS
ALTER TABLE lenders ENABLE ROW LEVEL SECURITY;
CREATE POLICY "open_access" ON lenders FOR ALL USING (true);

-- Done. Your lenders table is ready.
-- =========================================================

-- ── LinkedIn Verification Results ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS linkedin_results (
    lender_name      TEXT PRIMARY KEY,
    website          TEXT DEFAULT '',
    has_linkedin     TEXT DEFAULT 'No',
    linkedin_company TEXT DEFAULT '',
    members_found    INTEGER DEFAULT 0,
    member_details   TEXT DEFAULT '',
    fit_score        INTEGER DEFAULT 3,
    lender_type      TEXT DEFAULT '',
    verified_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_li_has_linkedin ON linkedin_results(has_linkedin);
CREATE INDEX IF NOT EXISTS idx_li_verified_at  ON linkedin_results(verified_at DESC);

ALTER TABLE linkedin_results ENABLE ROW LEVEL SECURITY;
CREATE POLICY "open_access_li" ON linkedin_results FOR ALL USING (true);
-- =========================================================
