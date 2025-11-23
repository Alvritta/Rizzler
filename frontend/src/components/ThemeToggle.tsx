import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Palette } from "lucide-react";

const ThemeToggle = () => {
  const [isVintage, setIsVintage] = useState(() => {
    // Check localStorage for saved preference
    const saved = localStorage.getItem("vintageTheme");
    return saved === "true";
  });

  useEffect(() => {
    // Apply theme class to document
    if (isVintage) {
      document.documentElement.classList.add("vintage-theme");
    } else {
      document.documentElement.classList.remove("vintage-theme");
    }
    // Save preference
    localStorage.setItem("vintageTheme", isVintage.toString());
  }, [isVintage]);

  return (
    <Button
      onClick={() => setIsVintage(!isVintage)}
      variant="outline"
      size="sm"
      className="fixed top-4 right-4 z-50 bg-background/80 backdrop-blur-sm"
      title={isVintage ? "Switch to Modern UI" : "Switch to Vintage UI"}
    >
      <Palette className="w-4 h-4 mr-2" />
      {isVintage ? "Modern" : "Vintage"}
    </Button>
  );
};

export default ThemeToggle;

