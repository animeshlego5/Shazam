import psycopg2

connection_string = "postgresql://postgres.nesbwlqukdinudtwpbtu:Faltu%40993@aws-1-us-east-2.pooler.supabase.com:5432/postgres"

try:
    conn = psycopg2.connect(connection_string)
    print("✅ Connected to Supabase via Pooler!")
except Exception as e:
    print("❌ Connection failed:", e)
