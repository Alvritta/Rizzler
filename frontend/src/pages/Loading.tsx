import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Heart } from "lucide-react";
import { Progress } from "@/components/ui/progress";

const Loading = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const timer = setTimeout(() => {
      navigate("/results");
    }, 3000);

    return () => clearTimeout(timer);
  }, [navigate]);

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
          <Progress value={66} className="h-2" />
          <p className="text-xs text-muted-foreground">
            Processing your rizz metrics...
          </p>
        </div>
      </div>
    </div>
  );
};

export default Loading;
