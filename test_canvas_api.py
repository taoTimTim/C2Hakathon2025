import requests
import sys

# Get Canvas token from command line
if len(sys.argv) < 2:
    print("Usage: python test_canvas_api.py <canvas_token>")
    sys.exit(1)

canvas_token = sys.argv[1]
base_url = "https://canvas.ubc.ca/api/v1"
headers = {
    'Authorization': f'Bearer {canvas_token}',
    'Content-Type': 'application/json'
}

print("Testing Canvas API Endpoints...\n")
print("="*60)

# Test 1: Get user info
print("\n1. GET /users/self")
print("-"*60)
try:
    response = requests.get(f"{base_url}/users/self", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        user = response.json()
        print(f"User ID: {user.get('id')}")
        print(f"Name: {user.get('name')}")
        print(f"Email: {user.get('email')}")
        print("✅ SUCCESS")
    else:
        print(f"❌ FAILED: {response.text}")
except Exception as e:
    print(f"❌ ERROR: {str(e)}")

# Test 2: Get courses (using enrollment_state=active)
print("\n2. GET /courses?enrollment_state=active")
print("-"*60)
try:
    params = {
        'enrollment_state': 'active',
        'per_page': 100
    }
    response = requests.get(f"{base_url}/courses", headers=headers, params=params)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        courses = response.json()
        print(f"Found {len(courses)} active courses\n")

        # Show all courses
        print("All Courses:")
        for i, course in enumerate(courses, 1):
            course_id = course.get('id')
            course_name = course.get('name', 'Unknown')
            course_code = course.get('course_code', 'N/A')
            workflow = course.get('workflow_state', 'unknown')
            print(f"  {i}. {course_name}")
            print(f"     ID: {course_id}, Code: {course_code}, State: {workflow}")

        print(f"\n✅ SUCCESS - Found {len(courses)} courses")
    else:
        print(f"❌ FAILED: {response.text}")
except Exception as e:
    print(f"❌ ERROR: {str(e)}")

# Test 3: Get user groups
print("\n3. GET /users/self/groups")
print("-"*60)
try:
    response = requests.get(f"{base_url}/users/self/groups", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        groups = response.json()
        print(f"Found {len(groups)} groups")
        for i, group in enumerate(groups[:5], 1):  # Show first 5
            print(f"  {i}. {group.get('name')} (ID: {group.get('id')})")
        if len(groups) > 5:
            print(f"  ... and {len(groups) - 5} more")
        print("✅ SUCCESS")
    else:
        print(f"❌ FAILED: {response.text}")
except Exception as e:
    print(f"❌ ERROR: {str(e)}")

# Test 4: Get course users (from courses)
print("\n4. GET /courses/:course_id/users")
print("-"*60)
try:
    response = requests.get(f"{base_url}/courses", headers=headers, params={'enrollment_state': 'active'})
    if response.status_code == 200:
        courses = response.json()
        if courses:
            course_id = courses[0].get('id')
            course_name = courses[0].get('name', 'Unknown')
            print(f"Testing with course: {course_name}")
            response = requests.get(f"{base_url}/courses/{course_id}/users", headers=headers, params={'per_page': 100})
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                users = response.json()
                print(f"Found {len(users)} users in course")
                for i, user in enumerate(users[:5], 1):
                    print(f"  {i}. {user.get('name')} (ID: {user.get('id')})")
                if len(users) > 5:
                    print(f"  ... and {len(users) - 5} more")
                print("✅ SUCCESS")
            else:
                print(f"❌ FAILED: {response.text}")
        else:
            print("⚠️  SKIPPED: No courses found")
except Exception as e:
    print(f"❌ ERROR: {str(e)}")

# Test 5: Get group members (if groups exist)
print("\n5. GET /groups/:group_id/users")
print("-"*60)
try:
    response = requests.get(f"{base_url}/users/self/groups", headers=headers)
    if response.status_code == 200:
        groups = response.json()
        if groups:
            group_id = groups[0]['id']
            group_name = groups[0].get('name')
            print(f"Testing with group: {group_name}")
            response = requests.get(f"{base_url}/groups/{group_id}/users", headers=headers)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                users = response.json()
                print(f"Found {len(users)} users in group")
                for i, user in enumerate(users[:5], 1):
                    print(f"  {i}. {user.get('name')} (ID: {user.get('id')})")
                if len(users) > 5:
                    print(f"  ... and {len(users) - 5} more")
                print("✅ SUCCESS")
            else:
                print(f"❌ FAILED: {response.text}")
        else:
            print("⚠️  SKIPPED: No groups found")
except Exception as e:
    print(f"❌ ERROR: {str(e)}")

print("\n" + "="*60)
print("Testing complete!")
print("="*60)
