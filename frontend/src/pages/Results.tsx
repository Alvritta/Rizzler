import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { AlertCircle, TrendingUp, Sparkles } from "lucide-react";
import BottomNav from "@/components/BottomNav";
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  ResponsiveContainer,
} from "recharts";

const Results = () => {
  const score = 8.5;
  const isWRizz = score >= 7;

  const radarData = [
    { skill: "Confidence", value: 9 },
    { skill: "Wit", value: 8 },
    { skill: "Personal", value: 7 },
    { skill: "Vibe", value: 9 },
    { skill: "Original", value: 8 },
  ];

  const feedback = [
    "Your confidence is strong, but try asking more personalized questions to build a deeper connection.",
    "Great use of humor! Keep the banter light and natural.",
    "Consider varying your response times to maintain mystery and interest.",
  ];

  return (
    <div className="min-h-screen pb-20 px-4">
      <div className="max-w-lg mx-auto pt-8 space-y-6">
        <header className="text-center animate-fade-in">
          <h1 className="text-3xl font-bold mb-2 text-foreground">
            Your Rizz Report
          </h1>
        </header>

        {/* Score Section */}
        <Card className="p-8 text-center bg-card border-border animate-fade-in">
          <div className="flex items-center justify-center gap-4 mb-4">
            <span className="text-6xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
              {score}
            </span>
            <span className="text-3xl text-muted-foreground">/10</span>
          </div>
          <Badge
            variant={isWRizz ? "default" : "destructive"}
            className="text-lg px-6 py-2 font-bold"
          >
            {isWRizz ? "W RIZZ" : "L RIZZ"}
          </Badge>
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

        {/* Flirting Style */}
        <Card className="p-6 bg-card border-border animate-fade-in">
          <h2 className="text-xl font-bold mb-2 text-foreground flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-primary" />
            Your Style
          </h2>
          <Badge variant="secondary" className="text-sm px-4 py-1">
            Playful & Confident
          </Badge>
        </Card>

        {/* AI Coach Feedback */}
        <Card className="p-6 bg-card border-border animate-fade-in">
          <h2 className="text-xl font-bold mb-4 text-foreground">
            Your Coach's Feedback
          </h2>
          <ul className="space-y-3">
            {feedback.map((item, index) => (
              <li key={index} className="flex gap-3 text-sm text-muted-foreground">
                <span className="text-primary font-bold">•</span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </Card>

        {/* Cringe Detection */}
        <Card className="p-4 bg-destructive/10 border-destructive/20 animate-fade-in">
          <div className="flex gap-3">
            <AlertCircle className="w-5 h-5 text-destructive flex-shrink-0" />
            <div>
              <p className="text-sm font-semibold text-destructive mb-1">
                Awkward Moment Detected
              </p>
              <p className="text-xs text-muted-foreground">
                The phrase "Are you a parking ticket?" might have come on too strong.
              </p>
            </div>
          </div>
        </Card>
      </div>
      <BottomNav />
    </div>
  );
};

export default Results;
