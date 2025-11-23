-- Supabase Storage Policies for chat-images bucket (GUEST MODE)
-- Run this entire script in SQL Editor
-- This allows public/unauthenticated uploads for guest mode

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Authenticated users can upload" ON storage.objects;
DROP POLICY IF EXISTS "Public can upload" ON storage.objects;
DROP POLICY IF EXISTS "Public can view images" ON storage.objects;
DROP POLICY IF EXISTS "Users can update own files" ON storage.objects;
DROP POLICY IF EXISTS "Users can delete own files" ON storage.objects;
DROP POLICY IF EXISTS "Public can update files" ON storage.objects;
DROP POLICY IF EXISTS "Public can delete files" ON storage.objects;

-- Policy 1: Allow PUBLIC (unauthenticated) users to upload (for guest mode)
CREATE POLICY "Public can upload"
ON storage.objects FOR INSERT
TO public
WITH CHECK (bucket_id = 'chat-images');

-- Policy 2: Allow public read access (so images can be viewed)
CREATE POLICY "Public can view images"
ON storage.objects FOR SELECT
TO public
USING (bucket_id = 'chat-images');

-- Policy 3: Allow public to update files (for upsert functionality)
CREATE POLICY "Public can update files"
ON storage.objects FOR UPDATE
TO public
USING (bucket_id = 'chat-images');

-- Policy 4: Allow public to delete files (for cleanup)
CREATE POLICY "Public can delete files"
ON storage.objects FOR DELETE
TO public
USING (bucket_id = 'chat-images');


