import { useParams } from "react-router-dom";
import { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Share2, Copy, Check } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

const ShareMeme = () => {
  const { memeId } = useParams<{ memeId: string }>();
  const [memeUrl, setMemeUrl] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    // In a real app, you'd fetch meme by ID from backend
    // For now, we'll use URL parameter or localStorage
    const shareUrl = new URLSearchParams(window.location.search).get("url");
    if (shareUrl) {
      const decoded = decodeURIComponent(shareUrl);
      // Normalize URL to avoid mixed-content or malformed URLs in prod
      const normalized = (() => {
        try {
          const u = new URL(decoded);
          // Force https for production safety if incoming URL is http
          if (u.protocol === "http:") u.protocol = "https:";
          return u.toString();
        } catch (e) {
          // If it's not a full URL, return as-is
          return decoded;
        }
      })();
      setMemeUrl(normalized);
      setLoading(false);
    } else {
      // Fallback: try to get from localStorage or show error
      setLoading(false);
    }
  }, [memeId]);

  const currentUrl = window.location.href;
  const canonicalShareLink = memeUrl
    ? `${window.location.origin}/share?url=${encodeURIComponent(memeUrl)}`
    : currentUrl;
  
  const handleCopyLink = async () => {
    try {
      await navigator.clipboard.writeText(canonicalShareLink);
      setCopied(true);
      toast({
        title: "Link copied!",
        description: "Share this link with your friends",
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

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: "Check out my Rizz Score!",
          text: "I got a rizz score meme!",
          url: canonicalShareLink,
        });
      } catch (err) {
        // User cancelled or error
      }
    } else {
      handleCopyLink();
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-muted-foreground">Loading meme...</p>
      </div>
    );
  }

  if (!memeUrl) {
    return (
      <div className="min-h-screen flex items-center justify-center px-4">
        <Card className="p-8 text-center max-w-md">
          <h1 className="text-2xl font-bold mb-4">Meme not found</h1>
          <p className="text-muted-foreground mb-4">
            This meme link is invalid or has expired.
          </p>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen pb-20 px-4 bg-gradient-to-b from-background to-muted/20">
      <div className="max-w-lg mx-auto pt-8 space-y-6">
        <header className="text-center">
          <h1 className="text-3xl font-bold mb-2 bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
            My Rizz Meme
          </h1>
          <p className="text-muted-foreground text-sm">
            Share this meme with your friends!
          </p>
        </header>

        <Card className="p-4 bg-card border-border">
          <img
            src={memeUrl}
            alt="Rizz score meme"
            className="w-full rounded-lg border border-border"
          />
        </Card>

        <div className="flex gap-3">
          <Button
            onClick={handleShare}
            className="flex-1 bg-gradient-to-r from-primary to-secondary"
          >
            <Share2 className="w-4 h-4 mr-2" />
            Share
          </Button>
          <Button
            onClick={handleCopyLink}
            variant="outline"
            className="flex-1"
          >
            {copied ? (
              <>
                <Check className="w-4 h-4 mr-2" />
                Copied!
              </>
            ) : (
              <>
                <Copy className="w-4 h-4 mr-2" />
                Copy Link
              </>
            )}
          </Button>
        </div>
      </div>
    </div>
  );
};

export default ShareMeme;

