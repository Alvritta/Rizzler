import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Clock } from "lucide-react";
import BottomNav from "@/components/BottomNav";

const History = () => {
  const historyData = [
    { id: 1, date: "2 hours ago", score: 8.5, style: "Playful" },
    { id: 2, date: "1 day ago", score: 7.2, style: "Sincere" },
    { id: 3, date: "3 days ago", score: 9.1, style: "Confident" },
    { id: 4, date: "1 week ago", score: 6.8, style: "Playful" },
    { id: 5, date: "2 weeks ago", score: 8.0, style: "Witty" },
  ];

  return (
    <div className="min-h-screen pb-20 px-4">
      <div className="max-w-lg mx-auto pt-8 space-y-6">
        <header className="text-center animate-fade-in">
          <Clock className="w-12 h-12 mx-auto mb-2 text-primary" />
          <h1 className="text-3xl font-bold mb-2 text-foreground">
            Your History
          </h1>
          <p className="text-muted-foreground text-sm">
            Past rizz analyses
          </p>
        </header>

        <div className="space-y-3 animate-fade-in">
          {historyData.map((entry) => (
            <Card
              key={entry.id}
              className="p-5 bg-card border-border hover:border-primary transition-all cursor-pointer"
            >
              <div className="flex items-center justify-between mb-3">
                <span className="text-sm text-muted-foreground">
                  {entry.date}
                </span>
                <span className="text-2xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
                  {entry.score}/10
                </span>
              </div>
              <div className="flex items-center justify-between">
                <Badge
                  variant={entry.score >= 7 ? "default" : "secondary"}
                  className="text-xs"
                >
                  {entry.score >= 7 ? "W RIZZ" : "L RIZZ"}
                </Badge>
                <span className="text-sm text-muted-foreground">
                  Style: {entry.style}
                </span>
              </div>
            </Card>
          ))}
        </div>
      </div>
      <BottomNav />
    </div>
  );
};

export default History;
