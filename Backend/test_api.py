"""Test the /products endpoint via HTTP"""
import requests
import json

BASE = "http://localhost:8000"

# Login
r = requests.post(f"{BASE}/auth/login", json={"username": "test", "password": "test123"})
data = r.json()
token = data.get("access_token")
if not token:
    print(f"Login failed: {data}")
    exit(1)

print(f"Token obtained: {token[:30]}...")

# Get products
headers = {"Authorization": f"Bearer {token}"}
r = requests.get(f"{BASE}/products", headers=headers)
products = r.json()

print(f"\nGot {len(products)} products")

# Check taxes_display distribution
from collections import Counter
c = Counter(p.get("taxes_display", "MISSING") for p in products)
print("\nTaxes display distribution:")
for k, v in c.most_common():
    print(f"  {k!r}: {v}")

# Show first 5 products with their taxes
print("\nFirst 5 products:")
for p in products[:5]:
    print(f"  {p['name'][:40]:40s} taxes_display={p.get('taxes_display', 'NONE')!r} taxes_id={p.get('taxes_id')!r}")
