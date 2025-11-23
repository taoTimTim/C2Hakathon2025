# API Reference - Client Endpoints

Base URL: `http://localhost:5000/api`

All endpoints (except `/auth/login`) require authentication via `Authorization: Bearer <session_token>` header.

---

## 🔐 Authentication

### `POST /auth/login`
Login with Canvas API token and sync courses/groups.

**Request:**
```json
{
  "canvas_token": "your_canvas_api_token"
}
```

**Response:**
```json
{
  "session_token": "abc123...",
  "user": {
    "canvas_user_id": "832034",
    "name": "John Doe",
    "role": "student"
  }
}
```

**Side Effects:**
- Creates/updates user in database
- Syncs Canvas courses as `room_type='class'`
- Syncs Canvas groups as `room_type='project'`
- Creates room memberships for all enrolled courses/groups

---

### `POST /auth/logout`
Invalidate current session token.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "message": "Logged out successfully"
}
```

---

### `GET /auth/verify`
Verify session token and get user info.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "user": {
    "canvas_user_id": "832034",
    "name": "John Doe",
    "role": "student"
  }
}
```

---

## 👤 Users

### `GET /users/me`
Get current authenticated user info.

**Response:**
```json
{
  "canvas_user_id": "832034",
  "name": "John Doe",
  "role": "student"
}
```

---

### `GET /users/{user_id}`
Get specific user by ID.

**Response:**
```json
{
  "canvas_user_id": "832034",
  "name": "John Doe",
  "role": "student"
}
```

---

### `GET /users?ids=123,456,789`
Get multiple users by IDs (comma-separated).

**Response:**
```json
[
  {"canvas_user_id": "123", "name": "Alice", "role": "student"},
  {"canvas_user_id": "456", "name": "Bob", "role": "student"}
]
```

---

## 🏠 Rooms (All Types)

### `GET /rooms?user_id={user_id}`
Get all rooms a user is a member of.

**Response:**
```json
[
  {
    "id": 173488,
    "name": "COSC 305 Project Management",
    "room_type": "class",
    "scope_id": null,
    "created_at": "2025-01-15T10:00:00"
  },
  {
    "id": 42,
    "name": "Chess Club",
    "room_type": "club",
    "description": "Weekly tournaments",
    "max_members": null,
    "created_at": "2025-01-20T15:30:00"
  }
]
```

**Room Types:**
- `class` - Canvas courses (unlimited members)
- `project` - Canvas groups (unlimited members)
- `club` - User-created clubs (unlimited members)
- `personal` - Private study groups (max 10 members)
- `subgroup` - Class subgroups

---

### `POST /rooms`
Create a new room (for personal/custom rooms).

**Request:**
```json
{
  "name": "Study Group - Alice & Bob",
  "room_type": "personal",
  "max_members": 10,
  "created_by": "832034"
}
```

**Response:**
```json
{
  "status": "success",
  "room_id": 124
}
```

---

## 💬 Messages

### `GET /rooms/{room_id}/messages?limit=50&offset=0`
Get message history for a room.

**Query Params:**
- `limit` (default: 50)
- `offset` (default: 0)

**Response:**
```json
[
  {
    "id": 1,
    "room_id": 173488,
    "user_id": "832034",
    "content": "Hello everyone!",
    "created_at": "2025-01-22T10:30:00",
    "is_edited": false,
    "edited_at": null
  }
]
```

---

### `POST /rooms/{room_id}/messages`
Send a message to a room.

**Request:**
```json
{
  "user_id": "832034",
  "content": "Hello everyone!"
}
```

**Response:**
```json
{
  "status": "success",
  "message_id": 123
}
```

---

### `PATCH /messages/{message_id}`
Edit a message.

**Request:**
```json
{
  "content": "Updated message content"
}
```

**Response:**
```json
{
  "status": "success"
}
```

---

### `DELETE /messages/{message_id}`
Delete a message.

**Response:**
```json
{
  "status": "success"
}
```

---

## 📚 Classes (Canvas Courses)

### `GET /classes?user_id={user_id}`
Get all classes a user is enrolled in.

**Response:**
```json
[
  {
    "id": 173488,
    "name": "COSC 305 Project Management",
    "room_type": "class",
    "created_at": "2025-01-15T10:00:00"
  }
]
```

---

### `GET /classes/{class_id}/members`
Get all members of a class.

**Response:**
```json
[
  {
    "canvas_user_id": "832034",
    "name": "John Doe",
    "role": "student",
    "joined_at": "2025-01-15T10:00:00"
  }
]
```

---

### `GET /classes/{class_id}/messages`
Get messages in a class room (same as `/rooms/{room_id}/messages`).

---

### `GET /classes/{class_id}/posts`
Get announcements/posts for a class.

**Response:**
```json
[
  {
    "id": 1,
    "scope": "class",
    "scope_id": "173488",
    "author": "832034",
    "title": "Assignment Due",
    "content": "Remember to submit by Friday!",
    "image_url": null,
    "created_at": "2025-01-22T10:00:00"
  }
]
```

---

## 🎯 Clubs

### `GET /clubs/all`
Get all clubs (for browsing/search).

**Response:**
```json
[
  {
    "id": 42,
    "name": "Chess Club",
    "description": "Weekly chess tournaments",
    "created_by": "832034",
    "created_at": "2025-01-20T15:30:00",
    "members_count": 15
  }
]
```

---

### `GET /clubs?user_id={user_id}`
Get clubs the user is a member of.

**Response:**
```json
[
  {
    "id": 42,
    "name": "Chess Club",
    "description": "Weekly chess tournaments",
    "created_at": "2025-01-20T15:30:00",
    "role": "leader"
  }
]
```

---

### `POST /clubs`
Create a new club.

**Request:**
```json
{
  "name": "Chess Club",
  "description": "Weekly chess tournaments every Friday!",
  "created_by": "832034"
}
```

**Response:**
```json
{
  "status": "success",
  "club_id": 42,
  "room_id": 42
}
```

**Note:** Creator is automatically added as `role='leader'`.

---

### `GET /clubs/{club_id}`
Get club details.

**Response:**
```json
{
  "id": 42,
  "name": "Chess Club",
  "description": "Weekly chess tournaments",
  "room_type": "club",
  "created_by": "832034",
  "created_at": "2025-01-20T15:30:00"
}
```

---

### `POST /clubs/{club_id}/join`
Join a club.

**Request:**
```json
{
  "user_id": "832034"
}
```

**Response:**
```json
{
  "status": "success",
  "club_id": 42,
  "user_id": "832034"
}
```

---

### `DELETE /clubs/{club_id}/leave?user_id={user_id}`
Leave a club.

**Response:**
```json
{
  "status": "success",
  "club_id": 42,
  "user_id": "832034"
}
```

---

### `GET /clubs/{club_id}/members`
Get all members of a club.

**Response:**
```json
[
  {
    "canvas_user_id": "832034",
    "name": "John Doe",
    "role": "leader"
  },
  {
    "canvas_user_id": "123456",
    "name": "Jane Smith",
    "role": "member"
  }
]
```

---

### `GET /clubs/{club_id}/messages`
Get messages in the club chat.

---

### `GET /clubs/{club_id}/posts`
Get announcements/posts for the club.

---

## 👥 Subgroups (Class Study Groups)

### `POST /classes/{class_id}/subgroups`
Create a subgroup within a class.

**Request:**
```json
{
  "name": "Study Group A",
  "class_id": "173488",
  "created_by": "832034"
}
```

**Response:**
```json
{
  "status": "success",
  "subgroup_id": 125,
  "name": "Study Group A"
}
```

---

### `GET /classes/{class_id}/subgroups`
Get all subgroups for a class.

**Response:**
```json
[
  {
    "id": 125,
    "name": "Study Group A",
    "created_by": "832034",
    "created_at": "2025-01-22T14:00:00",
    "members_count": 5
  }
]
```

---

### `POST /subgroups/{subgroup_id}/join`
Join a subgroup.

**Request:**
```json
{
  "user_id": "832034"
}
```

---

### `DELETE /subgroups/{subgroup_id}/leave?user_id={user_id}`
Leave a subgroup.

---

### `GET /subgroups/{subgroup_id}/members`
Get subgroup members.

---

### `GET /subgroups/{subgroup_id}/messages`
Get subgroup messages.

---

### `GET /subgroups/{subgroup_id}/posts`
Get subgroup posts.

---

## 🔖 Posts (Announcements)

### `GET /posts?scope={scope}&scope_id={id}`
Get posts filtered by scope.

**Query Params:**
- `scope` - "class", "club", "subgroup", "school"
- `scope_id` - ID of the scope entity

**Response:**
```json
[
  {
    "id": 1,
    "scope": "class",
    "scope_id": "173488",
    "author": "832034",
    "title": "Assignment Due",
    "content": "Remember to submit by Friday!",
    "image_url": "https://...",
    "created_at": "2025-01-22T10:00:00"
  }
]
```

---

### `POST /posts`
Create a new post/announcement.

**Request:**
```json
{
  "scope": "class",
  "scope_id": "173488",
  "author": "832034",
  "title": "Assignment Due",
  "content": "Remember to submit by Friday!",
  "image_url": "https://example.com/image.jpg"
}
```

**Response:**
```json
{
  "status": "success",
  "post_id": 1
}
```

---

### `DELETE /posts/{post_id}?author={user_id}`
Delete a post (must be author).

---

## 🔄 Canvas Sync

### `POST /sync`
Manually trigger Canvas sync.

**Request:**
```json
{
  "canvas_token": "your_canvas_api_token"
}
```

**Response:**
```json
{
  "message": "Sync completed successfully",
  "synced_courses": 11,
  "synced_groups": 2,
  "synced_members": 150
}
```

---

## 🔌 WebSocket Events

Connect to: `ws://localhost:5000` (using Socket.IO)

### Client → Server Events

**`connect`**
```javascript
socket.emit('connect', {
  session_token: "your_session_token"
})
```

**`join_room`**
```javascript
socket.emit('join_room', {
  room_id: 173488
})
```

**`leave_room`**
```javascript
socket.emit('leave_room', {
  room_id: 173488
})
```

**`send_message`**
```javascript
socket.emit('send_message', {
  room_id: 173488,
  content: "Hello everyone!"
})
```

**`edit_message`**
```javascript
socket.emit('edit_message', {
  message_id: 123,
  content: "Updated message"
})
```

**`typing`**
```javascript
socket.emit('typing', {
  room_id: 173488,
  is_typing: true
})
```

**`ping`**
```javascript
socket.emit('ping')
// Responds with: pong
```

---

### Server → Client Events

**`authenticated`**
```javascript
socket.on('authenticated', (data) => {
  // {user_id: "832034", message: "..."}
})
```

**`room_joined`**
```javascript
socket.on('room_joined', (data) => {
  // {room_id: 173488, message: "..."}
})
```

**`user_joined`**
```javascript
socket.on('user_joined', (data) => {
  // {user_id: "123456", room_id: 173488}
})
```

**`room_left`**
```javascript
socket.on('room_left', (data) => {
  // {room_id: 173488, message: "..."}
})
```

**`user_left`**
```javascript
socket.on('user_left', (data) => {
  // {user_id: "123456", room_id: 173488}
})
```

**`new_message`**
```javascript
socket.on('new_message', (data) => {
  // {message_id: 123, room_id: 173488, user_id: "832034", content: "...", created_at: "..."}
})
```

**`message_edited`**
```javascript
socket.on('message_edited', (data) => {
  // {message_id: 123, content: "...", edited_at: "..."}
})
```

**`user_typing`**
```javascript
socket.on('user_typing', (data) => {
  // {user_id: "123456", room_id: 173488, is_typing: true}
})
```

**`error`**
```javascript
socket.on('error', (data) => {
  // {message: "Error description"}
})
```

**`pong`**
```javascript
socket.on('pong', (data) => {
  // Response to ping
})
```

---

## 🏗️ Room Type Summary

| Type | Created By | Max Members | Discoverable | Use Case |
|------|-----------|-------------|--------------|----------|
| `class` | Canvas sync (auto) | Unlimited | No | Course-wide discussions |
| `project` | Canvas sync (auto) | Unlimited | No | Canvas group projects |
| `club` | User (manual) | Unlimited | **Yes** | School-wide organizations |
| `personal` | User (manual) | **10 max** | No | Private study groups |
| `subgroup` | User (manual) | Unlimited | No | Class-specific study groups |

---

## 🔒 Permission Model

**System-Generated Rooms (class, project):**
- Members auto-added via Canvas enrollment
- All members can add/invite others (Canvas handles enrollment)

**User-Created Rooms (club, personal, subgroup):**
- Only creator can add members
- Creator has `role='leader'`
- Other members have `role='member'`

**Clubs:**
- Public/discoverable via `/clubs/all`
- Anyone can join

**Personal Rooms:**
- Private (not discoverable)
- Creator-only invites
- Max 10 members enforced

---

## 📊 Error Responses

All endpoints may return:

**401 Unauthorized**
```json
{
  "error": "Unauthorized"
}
```

**404 Not Found**
```json
{
  "error": "Club not found"
}
```

**400 Bad Request**
```json
{
  "error": "Room is at maximum capacity (10 members)"
}
```

**500 Internal Server Error**
```json
{
  "error": "Internal server error"
}
```
