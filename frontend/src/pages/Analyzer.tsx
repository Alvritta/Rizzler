import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ImagePlus } from "lucide-react";
import BottomNav from "@/components/BottomNav";

const Analyzer = () => {
  const [chatText, setChatText] = useState("");
  const [isFocused, setIsFocused] = useState(false);
  const navigate = useNavigate();

  const handleAnalyze = () => {
    if (chatText.trim()) {
      navigate("/loading");
    }
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
          <div className="relative group">
            <Textarea
              placeholder={isFocused ? "No judgment… ok maybe a little judgment 😈" : "Drop your chat receipts… don't be shy 👀"}
              value={chatText}
              onChange={(e) => setChatText(e.target.value)}
              onFocus={() => setIsFocused(true)}
              onBlur={() => setIsFocused(false)}
              className="min-h-[300px] bg-card/50 backdrop-blur-sm border-border resize-none text-foreground placeholder:text-muted-foreground rounded-2xl shadow-[inset_0_0_20px_rgba(0,0,0,0.3)] focus:shadow-[inset_0_0_30px_rgba(0,0,0,0.4),0_0_20px_rgba(320,90%,60%,0.2)] transition-all duration-300"
            />
          </div>

          <Button
            variant="outline"
            className="w-full border-border/50 hover:border-primary bg-card/30 backdrop-blur-sm hover:bg-card/50 transition-all duration-300 h-12 rounded-xl hover:shadow-[0_0_15px_rgba(320,90%,60%,0.3)]"
          >
            <ImagePlus className="w-4 h-4 mr-2" />
            Upload Screenshot
          </Button>

          <Button
            onClick={handleAnalyze}
            disabled={!chatText.trim()}
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
