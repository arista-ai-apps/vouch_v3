import requests

# Test HSN status endpoint for RB Systems (engagement 12)
r = requests.get('http://localhost:8000/api/v1/hsn/status/12')
print('STATUS CODE:', r.status_code)
data = r.json()
print('Missing HSN rows:', len(data))
for row in data:
    print(f"  file_id={row['file_id']} vendor={row['vendor_name']} rec={row['recommendation']}")
