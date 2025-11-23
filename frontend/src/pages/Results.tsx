import { useLocation, useNavigate } from "react-router-dom";
import { Card } from "@/components/ui/card";
import { AlertCircle, TrendingUp, Sparkles, ArrowLeft, Share2, Copy, Check } from "lucide-react";
import BottomNav from "@/components/BottomNav";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import { useState } from "react";
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  ResponsiveContainer,
} from "recharts";

const Results = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [copied, setCopied] = useState(false);
  
  // Get results from navigation state
  const resultData = location.state;
  
  // If no data, redirect back
  if (!resultData) {
    navigate("/");
    return null;
  }

  const score = resultData.score || 0;
  const suggestions = resultData.suggestions || [];
  const reasoning = resultData.reasoning || "";
  const imageUrl = resultData.image_url || "";
  const memeUrl = resultData.meme_url || "";
  
  // Generate shareable link for meme
  const shareableLink = memeUrl 
    ? `${window.location.origin}/share?url=${encodeURIComponent(
        // normalize scheme - prefer https in production
        (() => {
          try {
            const u = new URL(memeUrl);
            if (u.protocol === "http:") u.protocol = "https:";
            return u.toString();
          } catch (e) {
            return memeUrl;
          }
        })()
      )}`
    : null;
  
  const handleShareMeme = async () => {
    if (!shareableLink) {
      toast({
        title: "No meme to share",
        description: "Meme not available",
        variant: "destructive",
      });
      return;
    }

    if (navigator.share) {
      try {
        await navigator.share({
          title: "Check out my Rizz Score!",
          text: `I got ${score}/100 on the Rizz Calculator!`,
          url: shareableLink,
        });
      } catch (err) {
        // User cancelled or error
      }
    } else {
      handleCopyMemeLink();
    }
  };

  const handleCopyMemeLink = async () => {
    if (!shareableLink) return;
    
    try {
      await navigator.clipboard.writeText(shareableLink);
      setCopied(true);
      toast({
        title: "Link copied!",
        description: "Share this link to show your meme",
      });
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      toast({
        title: "Failed to copy",
        description: "Please copy the link manually",
        variant: "destructive",
      });
    }
  };

  // Generate radar data from score (0-100 scale)
  const radarData = [
    { skill: "Confidence", value: Math.min(100, Math.round(score)) },
    { skill: "Wit", value: Math.min(100, Math.round(score * 0.9)) },
    { skill: "Personal", value: Math.min(100, Math.round(score * 0.85)) },
    { skill: "Vibe", value: Math.min(100, Math.round(score)) },
    { skill: "Original", value: Math.min(100, Math.round(score * 0.9)) },
  ];

  return (
    <div className="min-h-screen pb-20 px-4">
      <div className="max-w-lg mx-auto pt-8 space-y-6">
        <header className="text-center animate-fade-in">
          <div className="flex items-center justify-between mb-4">
            <Button
              variant="ghost"
              onClick={() => navigate("/")}
              className="text-muted-foreground"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back
            </Button>
            <h1 className="text-3xl font-bold text-foreground flex-1">
              Your Rizz Report
            </h1>
            <div className="w-20"></div> {/* Spacer for centering */}
          </div>
        </header>

        {/* Score Section */}
        <Card className="p-8 text-center bg-card border-border animate-fade-in">
          <div className="flex items-center justify-center gap-4">
            <span className="text-6xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
              {score}
            </span>
            <span className="text-3xl text-muted-foreground">/100</span>
          </div>
        </Card>

        {/* Radar Chart */}
        <Card className="p-6 bg-card border-border animate-fade-in">
          <h2 className="text-xl font-bold mb-4 text-foreground flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-primary" />
            Rizz Breakdown
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <RadarChart data={radarData}>
              <PolarGrid stroke="hsl(var(--border))" />
              <PolarAngleAxis
                dataKey="skill"
                tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }}
              />
              <Radar
                name="Score"
                dataKey="value"
                stroke="hsl(var(--primary))"
                fill="hsl(var(--primary))"
                fillOpacity={0.6}
              />
            </RadarChart>
          </ResponsiveContainer>
        </Card>

        {/* Reasoning */}
        {reasoning && (
          <Card className="p-6 bg-card border-border animate-fade-in">
            <h2 className="text-xl font-bold mb-2 text-foreground flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-primary" />
              Analysis
            </h2>
            <p className="text-sm text-muted-foreground">{reasoning}</p>
          </Card>
        )}

        {/* AI Coach Feedback */}
        <Card className="p-6 bg-card border-border animate-fade-in">
          <h2 className="text-xl font-bold mb-4 text-foreground">
            Your Coach's Feedback
          </h2>
          <ul className="space-y-3">
            {suggestions.map((item: string, index: number) => (
              <li key={index} className="flex gap-3 text-sm text-muted-foreground">
                <span className="text-primary font-bold">•</span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </Card>

        {/* Meme Preview */}
        {memeUrl && (
          <Card className="p-4 bg-card border-border animate-fade-in">
            <div className="flex items-center justify-between mb-2">
              <h2 className="text-lg font-bold text-foreground">Your Rizz Meme</h2>
              {shareableLink && (
                <div className="flex gap-2">
                  <Button
                    onClick={handleShareMeme}
                    size="sm"
                    variant="outline"
                    className="h-8"
                  >
                    <Share2 className="w-4 h-4 mr-1" />
                    Share
                  </Button>
                  <Button
                    onClick={handleCopyMemeLink}
                    size="sm"
                    variant="outline"
                    className="h-8"
                  >
                    {copied ? (
                      <Check className="w-4 h-4" />
                    ) : (
                      <Copy className="w-4 h-4" />
                    )}
                  </Button>
                </div>
              )}
            </div>
            <img
              src={memeUrl}
              alt="Rizz score meme"
              className="w-full rounded-lg border border-border"
              onError={(e) => {
                console.error("Meme failed to load:", memeUrl);
                e.currentTarget.style.display = "none";
              }}
              onLoad={() => {
                console.log("Meme loaded successfully:", memeUrl);
              }}
            />
          </Card>
        )}

        {/* Image Preview */}
        {imageUrl ? (
          <Card className="p-4 bg-card border-border animate-fade-in">
            <h2 className="text-lg font-bold mb-2 text-foreground">Your Screenshot</h2>
            <img
              src={imageUrl}
              alt="Analyzed screenshot"
              className="w-full rounded-lg border border-border"
              onError={(e) => {
                console.error("Image failed to load:", imageUrl);
                e.currentTarget.style.display = "none";
              }}
              onLoad={() => {
                console.log("Image loaded successfully:", imageUrl);
              }}
            />
          </Card>
        ) : (
          <Card className="p-4 bg-card border-border animate-fade-in">
            <h2 className="text-lg font-bold mb-2 text-foreground">Your Screenshot</h2>
            <div className="text-sm text-muted-foreground text-center py-4">
              Image URL not available
            </div>
          </Card>
        )}
      </div>
      <BottomNav />
    </div>
  );
};

export default Results;
