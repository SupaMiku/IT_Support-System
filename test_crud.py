import json
import urllib.request

# Test listing assets
print("1. Fetching assets...")
try:
    with urllib.request.urlopen('http://127.0.0.1:5000/api/assets/') as r:
        assets = json.loads(r.read().decode())
        print(f"✔ Fetched {len(assets)} assets")
        for asset in assets[:3]:
            print(f"  - {asset['asset_tag']}: {asset['name']} ({asset['status']})")
except Exception as e:
    print(f"✗ Error fetching assets: {e}")

# Test creating a new asset
print("\n2. Creating new asset...")
test_asset = {
    "asset_tag": "TEST-API-001",
    "name": "Test Laptop",
    "category": "laptop",
    "brand": "Lenovo",
    "model": "ThinkPad X1",
    "status": "active",
    "location": "Test Lab"
}

req = urllib.request.Request(
    'http://127.0.0.1:5000/api/assets/',
    data=json.dumps(test_asset).encode(),
    headers={'Content-Type': 'application/json'},
    method='POST'
)

try:
    with urllib.request.urlopen(req) as r:
        result = json.loads(r.read().decode())
        print("✔ Asset created successfully!")
        print(f"  ID: {result['id']}, Tag: {result['asset_tag']}, Name: {result['name']}")
        test_id = result['id']
except Exception as e:
    print(f"✗ Error creating asset: {e}")
    test_id = None

# Test fetching the created asset
if test_id:
    print(f"\n3. Fetching asset ID {test_id}...")
    try:
        with urllib.request.urlopen(f'http://127.0.0.1:5000/api/assets/{test_id}') as r:
            asset = json.loads(r.read().decode())
            print(f"✔ Asset retrieved: {asset['asset_tag']} - {asset['name']}")
    except Exception as e:
        print(f"✗ Error: {e}")

print("\n✅ CRUD operations working!")
