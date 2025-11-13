# Supabase Setup Instructions

Follow these steps to set up your Supabase database and storage.

## 1. Create Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Sign up/login
3. Create a new project
4. Wait for project to finish provisioning
5. Note your project URL and anon key from Settings > API

## 2. Run Database Schema

Open the SQL Editor in your Supabase dashboard and run this SQL:

```sql
-- Create profiles table (extends auth.users)
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    username TEXT UNIQUE NOT NULL,
    avatar_url TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- RLS Policies for profiles
CREATE POLICY "Users can view own profile" 
    ON profiles FOR SELECT 
    USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" 
    ON profiles FOR UPDATE 
    USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile" 
    ON profiles FOR INSERT 
    WITH CHECK (auth.uid() = id);

-- Create scores table
CREATE TABLE IF NOT EXISTS scores (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE NOT NULL,
    rizz_score INTEGER CHECK (rizz_score >= 0 AND rizz_score <= 100) NOT NULL,
    chat_text TEXT,
    suggestions TEXT[] NOT NULL,
    image_url TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security for scores
ALTER TABLE scores ENABLE ROW LEVEL SECURITY;

-- RLS Policies for scores
CREATE POLICY "Users can insert own scores" 
    ON scores FOR INSERT 
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Anyone can view all scores" 
    ON scores FOR SELECT 
    USING (true);

CREATE POLICY "Users can view own scores" 
    ON scores FOR SELECT 
    USING (auth.uid() = user_id);

-- Function to get leaderboard (top 10 by average rizz score)
CREATE OR REPLACE FUNCTION get_leaderboard()
RETURNS TABLE (username TEXT, avg_rizz INTEGER) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COALESCE(p.username, 'Anonymous') as username,
        ROUND(AVG(s.rizz_score)::numeric, 0)::INTEGER as avg_rizz
    FROM scores s
    LEFT JOIN profiles p ON s.user_id = p.id
    GROUP BY p.id, p.username
    HAVING COUNT(s.id) > 0
    ORDER BY avg_rizz DESC
    LIMIT 10;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to auto-create profile on user signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, username)
    VALUES (
        NEW.id,
        COALESCE(NEW.raw_user_meta_data->>'username', split_part(NEW.email, '@', 1))
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to create profile on signup
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
```

## 3. Set Up Storage Bucket

1. Go to Storage in Supabase dashboard
2. Click "New bucket"
3. Name: `chat-images`
4. Public bucket: **NO** (private, authenticated access)
5. Click "Create bucket"

### Storage Policies

After creating the bucket, go to Policies and add:

**Policy 1: Allow authenticated users to upload**
```sql
CREATE POLICY "Authenticated users can upload"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (bucket_id = 'chat-images');
```

**Policy 2: Allow authenticated users to update own files**
```sql
CREATE POLICY "Users can update own files"
ON storage.objects FOR UPDATE
TO authenticated
USING (bucket_id = 'chat-images' AND auth.uid()::text = (storage.foldername(name))[1]);
```

**Policy 3: Allow public read access**
```sql
CREATE POLICY "Public can view images"
ON storage.objects FOR SELECT
TO public
USING (bucket_id = 'chat-images');
```

**Policy 4: Allow users to delete own files**
```sql
CREATE POLICY "Users can delete own files"
ON storage.objects FOR DELETE
TO authenticated
USING (bucket_id = 'chat-images' AND auth.uid()::text = (storage.foldername(name))[1]);
```

## 4. Configure Authentication

1. Go to Authentication > Providers
2. Enable **Email** provider
3. (Optional) Enable **Google** provider for OAuth
4. Configure email templates if needed

## 5. Test Your Setup

Run this query in SQL Editor to verify:

```sql
-- Check tables exist
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('profiles', 'scores');

-- Check function exists
SELECT routine_name FROM information_schema.routines 
WHERE routine_schema = 'public' 
AND routine_name = 'get_leaderboard';

-- Check storage bucket exists
SELECT name FROM storage.buckets WHERE name = 'chat-images';
```

All should return results. You're ready to go! 🚀

## Notes

- RLS (Row Level Security) ensures users can only insert their own scores
- The leaderboard function is public (anyone can view top scores)
- Storage is organized by user_id folders for easy management
- Profiles are auto-created when users sign up

