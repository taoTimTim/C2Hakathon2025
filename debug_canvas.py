import requests
import sys
import json

if len(sys.argv) < 2:
    print("Usage: python debug_canvas.py <canvas_token>")
    sys.exit(1)

canvas_token = sys.argv[1]
base_url = "https://canvas.ubc.ca/api/v1"
headers = {
    'Authorization': f'Bearer {canvas_token}',
    'Content-Type': 'application/json'
}

print("="*60)
print("DEBUG: Raw Canvas API Response for /courses")
print("="*60)

# Try different variations
variations = [
    ('courses', {}),
    ('courses', {'enrollment_state': 'active'}),
    ('courses', {'enrollment_state': 'active', 'per_page': 100}),
    ('courses', {'include[]': 'total_students'}),
]

for endpoint, params in variations:
    print(f"\nTrying: GET /{endpoint}")
    if params:
        print(f"Params: {params}")
    print("-"*60)

    try:
        response = requests.get(f"{base_url}/{endpoint}", headers=headers, params=params)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers:")
        print(f"  Content-Type: {response.headers.get('Content-Type')}")
        print(f"  Link: {response.headers.get('Link', 'No pagination link')}")

        if response.status_code == 200:
            data = response.json()
            print(f"\nResults: {len(data)} items")

            if data:
                print(f"\nFirst item (full JSON):")
                print(json.dumps(data[0], indent=2))
            else:
                print("\n⚠️ Empty array returned!")
        else:
            print(f"\n❌ Error Response:")
            print(response.text)
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

print("\n" + "="*60)
print("Also checking enrollment endpoint directly:")
print("="*60)

try:
    response = requests.get(f"{base_url}/users/self/enrollments", headers=headers)
    print(f"GET /users/self/enrollments")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        enrollments = response.json()
        print(f"Found {len(enrollments)} enrollments")
        for i, enroll in enumerate(enrollments[:5], 1):
            print(f"  {i}. Course ID: {enroll.get('course_id')}, State: {enroll.get('enrollment_state')}, Type: {enroll.get('type')}")
except Exception as e:
    print(f"❌ Error: {str(e)}")
