import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL         = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY         = os.getenv("SUPABASE_KEY", "")
SERPAPI_KEY          = os.getenv("SERPAPI_KEY", "")

ADMIN_PASSWORD       = os.getenv("ADMIN_PASSWORD", "")
MANAGER_PASSWORD     = os.getenv("MANAGER_PASSWORD", "")
ADMIN_EMAIL_PASSWORD = os.getenv("ADMIN_EMAIL_PASSWORD", "")
RISHI_EMAIL_PASSWORD = os.getenv("RISHI_EMAIL_PASSWORD", "")
