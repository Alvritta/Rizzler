# Frontend - Rizz Calculator

React/TypeScript frontend integrated with the backend API.

## Setup

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   # or
   bun install
   ```

2. **Configure backend URL:**
   
   Create a `.env` file in the `frontend/` directory:
   ```env
   VITE_BACKEND_URL=http://localhost:8003
   ```
   
   Or update the default in `src/pages/Analyzer.tsx` and `src/pages/Loading.tsx`:
   ```typescript
   const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:8003";
   ```

3. **Run the development server:**
   ```bash
   npm run dev
   # or
   bun dev
   ```
   
   The frontend will be available at `http://localhost:8080`

## Features

### Button 1: Upload Screenshot
- Click "Select Screenshot" to choose an image file
- Shows image preview
- Click "Upload Screenshot" to upload to backend
- Calls `/upload_screenshot/` endpoint
- Enables "Analyze My Rizz" button after successful upload

### Button 2: Analyze My Rizz
- Only enabled after successful upload
- Navigates to loading page
- Loading page calls `/calculate_rizz/` endpoint with image_url
- Shows progress while analyzing
- Navigates to results page with score and suggestions

## Flow

```
1. User selects image → Preview shown
2. User clicks "Upload Screenshot" → Calls /upload_screenshot/
   → Returns: { success: true, image_url: "..." }
   → Button 2 enabled
3. User clicks "Analyze My Rizz" → Navigate to /loading
   → Loading page calls /calculate_rizz/ with image_url
   → Returns: { score: 85, suggestions: [...], reasoning: "..." }
4. Navigate to /results → Display score and feedback
```

## API Integration

- **Upload Screenshot**: `POST /upload_screenshot/` (multipart/form-data)
- **Calculate Rizz**: `POST /calculate_rizz/` (JSON body with image_url)

## Notes

- No authentication required (guest mode)
- Image validation: max 5MB, image files only
- Toast notifications for success/error feedback
- Responsive design with modern UI
