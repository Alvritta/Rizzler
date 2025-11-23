import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Crown } from "lucide-react";
import BottomNav from "@/components/BottomNav";

// Backend URL
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:8003";

const Leaderboard = () => {
  const [leaderboardData, setLeaderboardData] = useState<Array<{rank: number, nickname: string, score: number}>>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchLeaderboard = async () => {
      try {
        const response = await fetch(`${BACKEND_URL}/leaderboard/`);
        if (!response.ok) {
          throw new Error("Failed to fetch leaderboard");
        }
        const data = await response.json();
        
        // Transform data to match component format
        const transformed = data.leaderboard.map((entry: any, index: number) => ({
          rank: index + 1,
          nickname: entry.nickname || "Anonymous",
          score: entry.avg_rizz, // Keep 0-100 scale
          total_scores: entry.total_scores || 1
        }));
        
        setLeaderboardData(transformed);
      } catch (error) {
        console.error("Error fetching leaderboard:", error);
        // Keep empty array on error
        setLeaderboardData([]);
      } finally {
        setLoading(false);
      }
    };

    fetchLeaderboard();
  }, []);

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

        {/* Removed tabs - only showing all-time leaderboard */}

        {loading ? (
          <div className="text-center py-8 text-muted-foreground">
            Loading leaderboard...
          </div>
        ) : leaderboardData.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            No scores yet. Be the first to get on the leaderboard!
          </div>
        ) : (
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
                      {entry.nickname}
                    </p>
                    {index < 3 && (
                      <Badge variant="secondary" className="text-xs">
                        Top 3
                      </Badge>
                    )}
                  </div>
                </div>
                <div className="text-right">
                  <span className="text-xl font-bold text-primary">
                    {entry.score}/100
                  </span>
                  {entry.total_scores > 1 && (
                    <p className="text-xs text-muted-foreground">
                      {entry.total_scores} scores
                    </p>
                  )}
                </div>
              </div>
            </Card>
          ))}
          </div>
        )}
      </div>
      <BottomNav />
    </div>
  );
};

export default Leaderboard;
