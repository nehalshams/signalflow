import { useNavigate } from "react-router-dom";
import { LogOut, TrendingUp } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { useAuth } from "@/context/AuthContext";
import { StockSearch } from "@/components/StockSearch";
import { Watchlist } from "@/components/Watchlist";

const Dashboard = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  async function handleLogout() {
    await logout();
    toast.success("Signed out");
    navigate("/login");
  }

  return (
    <main className="relative min-h-screen overflow-hidden bg-background text-foreground">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_top,hsl(var(--primary)/0.15),transparent_60%)]" />

      <div className="relative z-10 mx-auto flex min-h-screen w-full max-w-3xl flex-col px-6 py-8">
        <header className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/15 shadow-glow">
              <TrendingUp className="h-5 w-5 text-primary" />
            </div>
            <span className="font-display text-xl font-bold tracking-tight">SignalFlow</span>
          </div>
          <Button variant="outline" onClick={handleLogout}>
            <LogOut className="mr-2 h-4 w-4" />
            Sign out
          </Button>
        </header>

        <div className="mt-6">
          <h1 className="font-display text-2xl font-bold tracking-tight">Dashboard</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Signed in as <span className="text-foreground">{user?.email}</span>.
          </p>
        </div>

        <Card className="mt-8 border-border/60 bg-card/60 p-6 backdrop-blur-xl">
          <h2 className="mb-4 font-display text-lg font-semibold">Find stocks</h2>
          <StockSearch />
        </Card>

        <Card className="mt-6 border-border/60 bg-card/60 p-6 backdrop-blur-xl">
          <h2 className="mb-4 font-display text-lg font-semibold">My watchlist</h2>
          <Watchlist />
        </Card>
      </div>
    </main>
  );
};

export default Dashboard;
