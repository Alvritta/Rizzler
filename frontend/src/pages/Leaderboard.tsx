import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Crown } from "lucide-react";
import BottomNav from "@/components/BottomNav";

const Leaderboard = () => {
  const [period, setPeriod] = useState("weekly");

  const leaderboardData = [
    { rank: 1, username: "Rizzler99", score: 9.8 },
    { rank: 2, username: "CharmKing", score: 9.5 },
    { rank: 3, username: "SmoothTalker", score: 9.3 },
    { rank: 4, username: "FlirtMaster", score: 9.1 },
    { rank: 5, username: "RizzGod", score: 9.0 },
    { rank: 6, username: "CharmLord", score: 8.9 },
    { rank: 7, username: "SmileWizard", score: 8.8 },
    { rank: 8, username: "ChatPro", score: 8.7 },
  ];

  return (
    <div className="min-h-screen pb-20 px-4">
      <div className="max-w-lg mx-auto pt-8 space-y-6">
        <header className="text-center animate-fade-in">
          <Crown className="w-12 h-12 mx-auto mb-2 text-primary" />
          <h1 className="text-3xl font-bold mb-2 bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
            Rizz Gods
          </h1>
          <p className="text-muted-foreground text-sm">
            Top performers this period
          </p>
        </header>

        <Tabs value={period} onValueChange={setPeriod} className="w-full">
          <TabsList className="grid w-full grid-cols-3 bg-card">
            <TabsTrigger value="weekly">Weekly</TabsTrigger>
            <TabsTrigger value="monthly">Monthly</TabsTrigger>
            <TabsTrigger value="alltime">All-Time</TabsTrigger>
          </TabsList>
        </Tabs>

        <div className="space-y-2 animate-fade-in">
          {leaderboardData.map((entry, index) => (
            <Card
              key={entry.rank}
              className={`p-4 bg-card border-border transition-all hover:border-primary ${
                index < 3 ? "border-primary/50" : ""
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <span
                    className={`text-2xl font-bold ${
                      index === 0
                        ? "text-primary"
                        : index === 1
                        ? "text-secondary"
                        : index === 2
                        ? "text-accent"
                        : "text-muted-foreground"
                    }`}
                  >
                    {entry.rank}
                  </span>
                  <div>
                    <p className="font-semibold text-foreground">
                      {entry.username}
                    </p>
                    {index < 3 && (
                      <Badge variant="secondary" className="text-xs">
                        Top 3
                      </Badge>
                    )}
                  </div>
                </div>
                <span className="text-xl font-bold text-primary">
                  {entry.score}/10
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

export default Leaderboard;
