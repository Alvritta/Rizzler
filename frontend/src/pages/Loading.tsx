import { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { Heart } from "lucide-react";
import { Progress } from "@/components/ui/progress";

// Backend URL - Update this to your backend URL
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:8003";

const Loading = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [progress, setProgress] = useState(0);
  const imageUrl = location.state?.imageUrl;
  const nickname = location.state?.nickname;

  useEffect(() => {
    if (!imageUrl || !nickname) {
      // If no image URL or nickname, redirect back to analyzer
      navigate("/");
      return;
    }

    // Simulate progress
    const progressInterval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 90) return prev;
        return prev + 10;
      });
    }, 300);

    // Call the API
    const analyzeRizz = async () => {
      try {
        const response = await fetch(`${BACKEND_URL}/calculate_rizz/`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ image_url: imageUrl, nickname: nickname }),
        });

        if (!response.ok) {
          const error = await response.json();
          throw new Error(error.detail || "Failed to calculate rizz score");
        }

        const result = await response.json();
        setProgress(100);
        
        // Ensure image_url is included in result
        console.log("API Result:", result);
        console.log("Image URL:", result.image_url);
        
        // Navigate to results with the data
        setTimeout(() => {
          navigate("/results", { state: result });
        }, 500);
      } catch (error) {
        console.error("Analysis error:", error);
        navigate("/", { 
          state: { 
            error: error instanceof Error ? error.message : "Failed to calculate rizz score" 
          } 
        });
      }
    };

    analyzeRizz();

    return () => {
      clearInterval(progressInterval);
    };
  }, [navigate, imageUrl, nickname]);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-4">
      <div className="text-center space-y-8 max-w-md">
        <Heart className="w-24 h-24 mx-auto text-primary animate-pulse-glow" />
        
        <div className="space-y-4">
          <h2 className="text-3xl font-bold text-foreground">
            Calculating...
          </h2>
          <p className="text-muted-foreground">
            Analyzing your conversation with AI
          </p>
        </div>

        <div className="w-full space-y-2">
          <Progress value={progress} className="h-2" />
          <p className="text-xs text-muted-foreground">
            Processing your rizz metrics... {progress}%
          </p>
        </div>
      </div>
    </div>
  );
};

export default Loading;
