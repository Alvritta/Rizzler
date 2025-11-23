import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Analyzer from "./pages/Analyzer";
import Loading from "./pages/Loading";
import Results from "./pages/Results";
import Leaderboard from "./pages/Leaderboard";
import ShareMeme from "./pages/ShareMeme";
import NotFound from "./pages/NotFound";
import ThemeToggle from "./components/ThemeToggle";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <ThemeToggle />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Analyzer />} />
          <Route path="/loading" element={<Loading />} />
          <Route path="/results" element={<Results />} />
          <Route path="/leaderboard" element={<Leaderboard />} />
          <Route path="/share/:memeId" element={<ShareMeme />} />
          <Route path="/share" element={<ShareMeme />} />
          {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
