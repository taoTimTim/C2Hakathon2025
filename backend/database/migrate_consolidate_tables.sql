-- Migration: Consolidate classes/clubs tables into rooms
-- This migration adds fields to rooms/room_members and migrates data

-- Start transaction
START TRANSACTION;

-- Step 1: Add new fields to rooms table (check if column exists first)
SET @col_exists = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
                   WHERE TABLE_SCHEMA = 'c2hackathon'
                   AND TABLE_NAME = 'rooms'
                   AND COLUMN_NAME = 'description');

SET @sql = IF(@col_exists = 0,
              'ALTER TABLE rooms ADD COLUMN description TEXT AFTER name',
              'SELECT "Column description already exists" AS message');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @col_exists = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
                   WHERE TABLE_SCHEMA = 'c2hackathon'
                   AND TABLE_NAME = 'rooms'
                   AND COLUMN_NAME = 'max_members');

SET @sql = IF(@col_exists = 0,
              'ALTER TABLE rooms ADD COLUMN max_members INT DEFAULT NULL AFTER description',
              'SELECT "Column max_members already exists" AS message');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Step 2: Add role field to room_members table
SET @col_exists = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
                   WHERE TABLE_SCHEMA = 'c2hackathon'
                   AND TABLE_NAME = 'room_members'
                   AND COLUMN_NAME = 'role');

SET @sql = IF(@col_exists = 0,
              'ALTER TABLE room_members ADD COLUMN role VARCHAR(50) DEFAULT ''member'' AFTER user_id',
              'SELECT "Column role already exists" AS message');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Step 3: Migrate existing clubs data to rooms
-- Find the max room_id to avoid conflicts
SET @max_room_id = (SELECT IFNULL(MAX(id), 0) FROM rooms);

-- Migrate clubs to rooms (only if clubs table exists and has data)
INSERT INTO rooms (id, name, description, room_type, max_members, is_system_generated, created_by, created_at)
SELECT
    c.id + @max_room_id AS id,  -- Offset by max_room_id to avoid conflicts
    c.name,
    c.description,
    'club' AS room_type,
    NULL AS max_members,  -- Clubs have unlimited members
    FALSE AS is_system_generated,
    c.created_by,
    c.created_at
FROM clubs c
WHERE NOT EXISTS (
    -- Don't migrate if a club room already exists with this scope_id
    SELECT 1 FROM rooms r
    WHERE r.room_type = 'club' AND r.scope_id = CAST(c.id AS CHAR)
);

-- Step 4: Update existing club rooms to have descriptions
-- (In case clubs were already synced to rooms via the club creation endpoint)
UPDATE rooms r
JOIN clubs c ON r.scope_id = CAST(c.id AS CHAR)
SET r.description = c.description
WHERE r.room_type = 'club' AND c.description IS NOT NULL;

-- Step 5: Migrate club_members to room_members
-- First, find the room_id for each club
INSERT INTO room_members (room_id, user_id, role, joined_at)
SELECT
    r.id AS room_id,
    cm.user_id,
    cm.role,
    NOW() AS joined_at
FROM club_members cm
JOIN clubs c ON cm.club_id = c.id
JOIN rooms r ON r.room_type = 'club' AND (r.scope_id = CAST(c.id AS CHAR) OR r.id = c.id + @max_room_id)
WHERE NOT EXISTS (
    -- Don't duplicate if already exists
    SELECT 1 FROM room_members rm
    WHERE rm.room_id = r.id AND rm.user_id = cm.user_id
);

-- Step 6: Drop old tables (commented out for safety - uncomment after verification)
-- DROP TABLE IF EXISTS club_members;
-- DROP TABLE IF EXISTS clubs;
-- DROP TABLE IF EXISTS class_members;
-- DROP TABLE IF EXISTS classes;

-- Commit transaction
COMMIT;

-- Verification queries (run these to check the migration)
-- SELECT 'Rooms with descriptions:' AS check_type, COUNT(*) AS count FROM rooms WHERE description IS NOT NULL;
-- SELECT 'Room members with roles:' AS check_type, COUNT(*) AS count FROM room_members WHERE role != 'member';
-- SELECT 'Club-type rooms:' AS check_type, COUNT(*) AS count FROM rooms WHERE room_type = 'club';
