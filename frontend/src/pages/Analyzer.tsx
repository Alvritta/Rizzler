import { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ImagePlus, Upload, CheckCircle2, User } from "lucide-react";
import BottomNav from "@/components/BottomNav";
import { useToast } from "@/hooks/use-toast";

// Backend URL - Update this to your backend URL
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:8003";

const Analyzer = () => {
  const [nickname, setNickname] = useState<string>("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();
  const { toast } = useToast();

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      // Validate file type
      if (!file.type.startsWith("image/")) {
        toast({
          title: "Invalid file type",
          description: "Please select an image file",
          variant: "destructive",
        });
        return;
      }
      
      // Validate file size (5MB max)
      if (file.size > 5 * 1024 * 1024) {
        toast({
          title: "File too large",
          description: "Image must be less than 5MB",
          variant: "destructive",
        });
        return;
      }

      setSelectedFile(file);
      
      // Create preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleUploadScreenshot = async () => {
    if (!selectedFile) {
      toast({
        title: "No file selected",
        description: "Please select an image first",
        variant: "destructive",
      });
      return;
    }

    setIsUploading(true);
    
    try {
      const formData = new FormData();
      formData.append("file", selectedFile);

      const response = await fetch(`${BACKEND_URL}/upload_screenshot/`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Failed to upload screenshot");
      }

      const data = await response.json();
      setImageUrl(data.image_url);
      
      toast({
        title: "Upload successful!",
        description: "Screenshot uploaded. Click 'Analyze My Rizz' to get your score.",
      });
    } catch (error) {
      console.error("Upload error:", error);
      toast({
        title: "Upload failed",
        description: error instanceof Error ? error.message : "Failed to upload screenshot",
        variant: "destructive",
      });
    } finally {
      setIsUploading(false);
    }
  };

  const handleAnalyze = () => {
    if (!nickname.trim()) {
      toast({
        title: "Nickname required",
        description: "Please enter a nickname first",
        variant: "destructive",
      });
      return;
    }

    if (!imageUrl) {
      toast({
        title: "No image uploaded",
        description: "Please upload a screenshot first",
        variant: "destructive",
      });
      return;
    }

    // Navigate to loading page, which will call the API
    navigate("/loading", { state: { imageUrl, nickname: nickname.trim() } });
  };

  return (
    <div className="min-h-screen pb-20 px-4">
      <div className="max-w-lg mx-auto pt-8">
        <header className="text-center mb-8 animate-fade-in">
          <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent drop-shadow-[0_0_30px_rgba(320,90%,60%,0.5)]">
            Let's see if you're HIM or mid
          </h1>
          <p className="text-muted-foreground text-sm">
            Drop your chat. Get judged. 👩‍⚖️💘
          </p>
        </header>

        <div className="space-y-4 animate-fade-in">
          {/* Nickname Input */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-foreground flex items-center gap-2">
              <User className="w-4 h-4" />
              Your Nickname
            </label>
            <Input
              type="text"
              placeholder="Enter your nickname (e.g., RizzMaster99)"
              value={nickname}
              onChange={(e) => setNickname(e.target.value)}
              maxLength={30}
              className="w-full bg-card/50 backdrop-blur-sm border-border/50 focus:border-primary rounded-xl h-12"
            />
            <p className="text-xs text-muted-foreground">
              This will be used for the leaderboard
            </p>
          </div>

          {/* File Input (hidden) */}
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileSelect}
            accept="image/*"
            className="hidden"
          />

          {/* Image Preview */}
          {imagePreview && (
            <div className="relative rounded-2xl overflow-hidden border border-border bg-card/50 backdrop-blur-sm">
              <img
                src={imagePreview}
                alt="Preview"
                className="w-full h-auto max-h-[400px] object-contain"
              />
              {imageUrl && (
                <div className="absolute top-2 right-2 bg-green-500 rounded-full p-1">
                  <CheckCircle2 className="w-5 h-5 text-white" />
                </div>
              )}
            </div>
          )}

          {/* Upload Screenshot Button */}
          <Button
            onClick={() => fileInputRef.current?.click()}
            variant="outline"
            className="w-full border-border/50 hover:border-primary bg-card/30 backdrop-blur-sm hover:bg-card/50 transition-all duration-300 h-12 rounded-xl hover:shadow-[0_0_15px_rgba(320,90%,60%,0.3)]"
          >
            <ImagePlus className="w-4 h-4 mr-2" />
            {selectedFile ? "Change Screenshot" : "Select Screenshot"}
          </Button>

          {selectedFile && !imageUrl && (
            <Button
              onClick={handleUploadScreenshot}
              disabled={isUploading}
              className="w-full bg-gradient-to-r from-blue-500 to-purple-500 hover:opacity-90 hover:scale-[1.02] text-white font-bold py-6 text-lg transition-all duration-300 rounded-xl shadow-[0_0_30px_rgba(59,130,246,0.4)] hover:shadow-[0_0_40px_rgba(59,130,246,0.6)]"
            >
              <Upload className="w-4 h-4 mr-2" />
              {isUploading ? "Uploading..." : "Upload Screenshot"}
            </Button>
          )}

          {/* Analyze My Rizz Button */}
          <Button
            onClick={handleAnalyze}
            disabled={!imageUrl || !nickname.trim()}
            className="w-full bg-gradient-to-r from-primary to-secondary hover:opacity-90 hover:scale-[1.02] hover:brightness-110 text-primary-foreground font-bold py-6 text-lg animate-pulse-glow disabled:opacity-50 disabled:animate-none transition-all duration-300 rounded-xl shadow-[0_0_30px_rgba(320,90%,60%,0.4)] hover:shadow-[0_0_40px_rgba(320,90%,60%,0.6)]"
          >
            Analyze My Rizz
          </Button>
        </div>
      </div>
      <BottomNav />
    </div>
  );
};

export default Analyzer;
