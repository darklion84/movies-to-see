-- Migration: Add media_type column for TV shows support
-- Run: sqlite3 movies.db < migrations/001_add_media_type.sql

ALTER TABLE movies ADD COLUMN media_type TEXT DEFAULT 'movie';
