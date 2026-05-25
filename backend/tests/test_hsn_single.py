import requests
import time

# Trigger recommendation for file_id 111
print('Triggering recommendation for file_id 111...')
r = requests.post('http://localhost:8000/api/v1/hsn/recommend/single/111')
print('Trigger Status:', r.status_code, r.json())

print('Waiting for background task to complete...')
time.sleep(12)

# Check status again
print('Checking updated status...')
r = requests.get('http://localhost:8000/api/v1/hsn/status/12')
data = r.json()
print('Missing HSN rows:', len(data))
for row in data:
    if row['file_id'] == 111:
        print(f"vendor: {row['vendor_name']}")
        print(f"recommendation: {row['recommendation']}")
