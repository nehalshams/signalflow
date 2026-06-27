import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import {
  Activity,
  ArrowRight,
  BarChart3,
  Brain,
  Check,
  ChevronRight,
  LineChart,
  Menu,
  PieChart,
  Shield,
  Sparkles,
  TrendingUp,
  X,
  Zap,
} from "lucide-react";
import heroChart from "@/assets/hero-chart.jpg";
import { Link } from "react-router-dom";

const tickers = [
  { sym: "AAPL", price: "229.84", chg: "+1.24%", up: true },
  { sym: "NVDA", price: "142.07", chg: "+3.81%", up: true },
  { sym: "TSLA", price: "248.50", chg: "-0.62%", up: false },
  { sym: "MSFT", price: "428.13", chg: "+0.94%", up: true },
  { sym: "GOOGL", price: "175.20", chg: "+2.15%", up: true },
  { sym: "META", price: "562.40", chg: "-0.31%", up: false },
  { sym: "AMZN", price: "201.66", chg: "+1.07%", up: true },
  { sym: "BTC", price: "68,420", chg: "+4.22%", up: true },
];

const features = [
  {
    icon: Brain,
    title: "AI-Powered Predictions",
    desc: "Deep learning models trained on 20+ years of market data forecast price movement with calibrated confidence intervals.",
  },
  {
    icon: Activity,
    title: "Real-Time Market Insights",
    desc: "Sub-second tick data, sentiment streams, and breaking news flow surface opportunities the moment they appear.",
  },
  {
    icon: LineChart,
    title: "Technical Analysis",
    desc: "60+ indicators, automatic pattern detection, and multi-timeframe charting that mirrors institutional desks.",
  },
  {
    icon: PieChart,
    title: "Portfolio Tracking",
    desc: "Unify every brokerage, monitor allocation drift, and benchmark performance against custom indices in real time.",
  },
  {
    icon: Shield,
    title: "Risk Assessment",
    desc: "VaR, stress tests, and exposure scoring quantify downside before you trade — not after.",
  },
  {
    icon: Zap,
    title: "Smart Alerts",
    desc: "Conditional triggers across price, volume, sentiment, and AI signal strength delivered the instant they fire.",
  },
];

const testimonials = [
  {
    quote: "SignalFlow flagged the NVDA breakout 48 hours before it hit the tape. The forecast confidence scoring is unlike anything I've used.",
    name: "Marcus Chen",
    role: "Portfolio Manager, Vertex Capital",
    initials: "MC",
  },
  {
    quote: "The risk dashboard alone replaced three internal tools. I trust the numbers because the methodology is transparent.",
    name: "Sofia Ramirez",
    role: "Quant Researcher",
    initials: "SR",
  },
  {
    quote: "I'm a retail trader and SignalFlow makes me feel like I'm running a desk. Clean, fast, and the AI calls are genuinely sharp.",
    name: "Jordan Lee",
    role: "Independent Trader",
    initials: "JL",
  },
];

const plans = [
  {
    name: "Starter",
    price: "$0",
    blurb: "Get a feel for the platform.",
    perks: ["5 AI predictions / day", "Delayed market data", "Basic portfolio tracking"],
    cta: "Start free",
    featured: false,
  },
  {
    name: "Pro",
    price: "$49",
    blurb: "For serious active traders.",
    perks: ["Unlimited AI signals", "Real-time data & alerts", "Full technical suite", "Risk dashboard"],
    cta: "Start 14-day trial",
    featured: true,
  },
  {
    name: "Institutional",
    price: "Custom",
    blurb: "For desks, funds, and teams.",
    perks: ["API access", "Custom models", "Dedicated support", "SOC 2 compliance"],
    cta: "Contact sales",
    featured: false,
  },
];

const Index = () => {
  const [open, setOpen] = useState(false);

  return (
    <div className="px-8 min-h-screen bg-background text-foreground font-sans overflow-x-hidden">
      {/* Nav */}
      <header className="px-8 fixed top-0 left-0 right-0 z-50 border-b border-border/40 bg-background/70 backdrop-blur-xl">
        <div className="container flex h-16 items-center justify-between">
          <a href="#" className="flex items-center gap-2 font-display font-bold text-lg">
            <span className="grid h-8 w-8 place-items-center rounded-lg bg-gradient-primary shadow-glow">
              <TrendingUp className="h-4 w-4 text-primary-foreground" strokeWidth={2.5} />
            </span>
            <span>Signal<span className="text-gradient">Flow</span></span>
          </a>
          <nav className="hidden md:flex items-center gap-8 text-sm text-muted-foreground">
            <a href="#features" className="hover:text-foreground transition-smooth">Features</a>
            <a href="#insights" className="hover:text-foreground transition-smooth">Insights</a>
            <a href="#pricing" className="hover:text-foreground transition-smooth">Pricing</a>
            <a href="#testimonials" className="hover:text-foreground transition-smooth">Customers</a>
          </nav>
          <div className="hidden md:flex items-center gap-2">
            <Button asChild variant="outline" className="flex-1">
                <Link to="/login" onClick={() => setOpen(false)}>Login</Link>
            </Button>
            <Button className="bg-gradient-primary text-primary-foreground font-semibold hover:opacity-90 shadow-elegant">
              Register <ArrowRight className="ml-1 h-4 w-4" />
            </Button>
          </div>
          <button
            className="md:hidden p-2 text-foreground"
            onClick={() => setOpen(!open)}
            aria-label="Toggle menu"
          >
            {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>
        {open && (
          <div className="md:hidden border-t border-border/40 bg-background/95 backdrop-blur-xl animate-fade-in">
            <div className="container py-4 flex flex-col gap-3 text-sm">
              <a href="#features" onClick={() => setOpen(false)} className="py-2">Features</a>
              <a href="#insights" onClick={() => setOpen(false)} className="py-2">Insights</a>
              <a href="#pricing" onClick={() => setOpen(false)} className="py-2">Pricing</a>
              <a href="#testimonials" onClick={() => setOpen(false)} className="py-2">Customers</a>
              <div className="flex gap-2 pt-2">
                <Button variant="outline" className="flex-1">Login</Button>
                <Button className="flex-1 bg-gradient-primary text-primary-foreground">Register</Button>
              </div>
            </div>
          </div>
        )}
      </header>

      {/* Hero */}
      <section className="relative pt-32 pb-20 md:pt-40 md:pb-28">
        <div className="absolute inset-0 bg-gradient-hero pointer-events-none" />
        <div className="absolute inset-0 grid-bg pointer-events-none" />
        <div className="container relative grid lg:grid-cols-2 gap-12 items-center">
          <div className="space-y-8 animate-fade-in-up">
            <Badge variant="outline" className="border-primary/30 bg-primary/10 text-primary font-medium gap-1.5 py-1.5 px-3">
              <Sparkles className="h-3.5 w-3.5" />
              AI signals · Live now
            </Badge>
            <h1 className="font-display text-4xl sm:text-5xl lg:text-6xl xl:text-7xl font-bold leading-[1.05] tracking-tight">
              Trade the market with <span className="text-gradient">predictive intelligence</span>.
            </h1>
            <p className="text-lg text-muted-foreground max-w-xl leading-relaxed">
              SignalFlow fuses real-time market data with deep learning forecasts so you spot the move before the crowd. Built for traders who want signal, not noise.
            </p>
            <div className="flex flex-col sm:flex-row gap-3">
              <Button size="lg" className="bg-gradient-primary text-primary-foreground font-semibold text-base h-12 px-8 shadow-elegant hover:opacity-90 transition-smooth">
                Create free account <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
              <Button size="lg" variant="outline" className="h-12 px-8 text-base border-border/60 hover:bg-secondary transition-smooth">
                Login to dashboard
              </Button>
            </div>
            <div className="flex flex-wrap items-center gap-6 pt-4 text-sm text-muted-foreground">
              <div className="flex items-center gap-2"><Check className="h-4 w-4 text-primary" /> No credit card</div>
              <div className="flex items-center gap-2"><Check className="h-4 w-4 text-primary" /> 50k+ traders</div>
              <div className="flex items-center gap-2"><Check className="h-4 w-4 text-primary" /> SOC 2 secure</div>
            </div>
          </div>

          <div className="relative animate-scale-in">
            <div className="absolute -inset-6 bg-gradient-primary opacity-20 blur-3xl rounded-full" />
            <Card className="relative overflow-hidden border-border/60 bg-gradient-card backdrop-blur-xl shadow-elegant">
              <div className="flex items-center justify-between px-5 py-3 border-b border-border/40">
                <div className="flex items-center gap-2">
                  <span className="h-2.5 w-2.5 rounded-full bg-destructive/70" />
                  <span className="h-2.5 w-2.5 rounded-full bg-yellow-500/70" />
                  <span className="h-2.5 w-2.5 rounded-full bg-primary/70" />
                </div>
                <span className="text-xs font-mono text-muted-foreground">signalflow / NVDA</span>
                <Badge className="bg-primary/15 text-primary border-0 text-xs">LIVE</Badge>
              </div>
              <img
                src={heroChart}
                alt="SignalFlow AI prediction chart showing upward trend"
                width={1536}
                height={1024}
                className="w-full h-64 sm:h-80 object-cover"
              />
              <div className="grid grid-cols-3 divide-x divide-border/40 border-t border-border/40">
                <div className="p-4">
                  <div className="text-xs text-muted-foreground">AI Forecast 7d</div>
                  <div className="font-display text-lg font-bold text-primary">+8.4%</div>
                </div>
                <div className="p-4">
                  <div className="text-xs text-muted-foreground">Confidence</div>
                  <div className="font-display text-lg font-bold">92%</div>
                </div>
                <div className="p-4">
                  <div className="text-xs text-muted-foreground">Risk</div>
                  <div className="font-display text-lg font-bold text-accent">Low</div>
                </div>
              </div>
            </Card>
            <div className="absolute -bottom-6 -left-6 hidden sm:block animate-float">
              <Card className="bg-card/95 backdrop-blur border-border/60 shadow-card p-3 flex items-center gap-3">
                <span className="grid h-9 w-9 place-items-center rounded-md bg-primary/15">
                  <Zap className="h-4 w-4 text-primary" />
                </span>
                <div>
                  <div className="text-xs text-muted-foreground">New signal</div>
                  <div className="text-sm font-semibold">AAPL · Buy · 94%</div>
                </div>
              </Card>
            </div>
          </div>
        </div>
      </section>

      {/* Ticker */}
      <section className="border-y border-border/40 bg-card/40 backdrop-blur overflow-hidden">
        <div className="flex animate-ticker py-4 whitespace-nowrap">
          {[...tickers, ...tickers].map((t, i) => (
            <div key={i} className="flex items-center gap-3 px-8 font-mono text-sm">
              <span className="font-semibold tracking-wider">{t.sym}</span>
              <span className="text-muted-foreground">${t.price}</span>
              <span className={t.up ? "text-primary" : "text-destructive"}>{t.chg}</span>
              <span className="text-border">·</span>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-24 md:py-32">
        <div className="container">
          <div className="max-w-2xl mb-16">
            <Badge variant="outline" className="border-primary/30 bg-primary/10 text-primary mb-4">Features</Badge>
            <h2 className="font-display text-3xl md:text-5xl font-bold tracking-tight mb-4">
              Everything you need to <span className="text-gradient">decode the market</span>.
            </h2>
            <p className="text-muted-foreground text-lg">
              One platform, built end-to-end for traders who treat the market like a craft.
            </p>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {features.map((f) => (
              <Card
                key={f.title}
                className="group relative overflow-hidden border-border/60 bg-gradient-card p-7 transition-smooth hover:border-primary/40 hover:-translate-y-1 hover:shadow-elegant"
              >
                <div className="absolute inset-0 bg-gradient-primary opacity-0 group-hover:opacity-5 transition-smooth" />
                <div className="relative">
                  <span className="inline-grid h-12 w-12 place-items-center rounded-xl bg-primary/10 text-primary mb-5 group-hover:bg-gradient-primary group-hover:text-primary-foreground transition-smooth">
                    <f.icon className="h-5 w-5" />
                  </span>
                  <h3 className="font-display text-xl font-semibold mb-2">{f.title}</h3>
                  <p className="text-sm text-muted-foreground leading-relaxed">{f.desc}</p>
                </div>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Insights strip */}
      <section id="insights" className="py-24 md:py-32 border-y border-border/40 bg-card/30">
        <div className="container grid lg:grid-cols-4 gap-10 items-center">
          <div className="lg:col-span-2 space-y-6">
            <Badge variant="outline" className="border-primary/30 bg-primary/10 text-primary">Performance</Badge>
            <h2 className="font-display text-3xl md:text-4xl font-bold tracking-tight">
              Numbers our community already trusts.
            </h2>
            <p className="text-muted-foreground">
              Live, audited, and benchmarked monthly. We publish what works — and what doesn't.
            </p>
          </div>
          {[
            { k: "73.4%", v: "Signal accuracy (12m)" },
            { k: "$2.1B", v: "Assets tracked daily" },
            { k: "50k+", v: "Active traders" },
            { k: "<120ms", v: "Median signal latency" },
          ].map((s) => (
            <div key={s.v} className="space-y-1">
              <div className="font-display text-4xl font-bold text-gradient">{s.k}</div>
              <div className="text-sm text-muted-foreground">{s.v}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Testimonials */}
      <section id="testimonials" className="py-24 md:py-32">
        <div className="container">
          <div className="max-w-2xl mb-16">
            <Badge variant="outline" className="border-primary/30 bg-primary/10 text-primary mb-4">Loved by traders</Badge>
            <h2 className="font-display text-3xl md:text-5xl font-bold tracking-tight">
              Built with the desks. Trusted by the street.
            </h2>
          </div>
          <div className="grid md:grid-cols-3 gap-5">
            {testimonials.map((t) => (
              <Card key={t.name} className="border-border/60 bg-gradient-card p-7 transition-smooth hover:border-primary/40">
                <div className="flex gap-1 mb-5 text-primary">
                  {Array.from({ length: 5 }).map((_, i) => (
                    <svg key={i} className="h-4 w-4 fill-current" viewBox="0 0 20 20"><path d="M10 1.5l2.6 5.3 5.9.9-4.2 4.1 1 5.8L10 14.9l-5.3 2.7 1-5.8L1.5 7.7l5.9-.9z" /></svg>
                  ))}
                </div>
                <p className="text-foreground/90 leading-relaxed mb-6">"{t.quote}"</p>
                <div className="flex items-center gap-3">
                  <span className="grid h-10 w-10 place-items-center rounded-full bg-gradient-primary text-primary-foreground font-display font-semibold text-sm">
                    {t.initials}
                  </span>
                  <div>
                    <div className="font-semibold text-sm">{t.name}</div>
                    <div className="text-xs text-muted-foreground">{t.role}</div>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing teaser */}
      <section id="pricing" className="py-24 md:py-32 border-y border-border/40 bg-card/30">
        <div className="container">
          <div className="max-w-2xl mb-16 text-center mx-auto">
            <Badge variant="outline" className="border-primary/30 bg-primary/10 text-primary mb-4">Pricing</Badge>
            <h2 className="font-display text-3xl md:text-5xl font-bold tracking-tight mb-4">
              Simple plans. Serious upside.
            </h2>
            <p className="text-muted-foreground text-lg">Start free, scale when the signals start paying for themselves.</p>
          </div>
          <div className="grid md:grid-cols-3 gap-5 max-w-5xl mx-auto">
            {plans.map((p) => (
              <Card
                key={p.name}
                className={`relative p-8 border-border/60 bg-gradient-card transition-smooth ${
                  p.featured ? "border-primary/50 shadow-elegant scale-[1.02]" : "hover:border-primary/30"
                }`}
              >
                {p.featured && (
                  <Badge className="absolute -top-3 left-1/2 -translate-x-1/2 bg-gradient-primary text-primary-foreground border-0">
                    Most popular
                  </Badge>
                )}
                <h3 className="font-display text-lg font-semibold">{p.name}</h3>
                <p className="text-sm text-muted-foreground mt-1 mb-5">{p.blurb}</p>
                <div className="flex items-baseline gap-1 mb-6">
                  <span className="font-display text-4xl font-bold">{p.price}</span>
                  {p.price.startsWith("$") && p.price !== "$0" && <span className="text-muted-foreground text-sm">/mo</span>}
                </div>
                <ul className="space-y-3 mb-8 text-sm">
                  {p.perks.map((perk) => (
                    <li key={perk} className="flex items-start gap-2">
                      <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                      <span>{perk}</span>
                    </li>
                  ))}
                </ul>
                <Button
                  className={`w-full ${
                    p.featured
                      ? "bg-gradient-primary text-primary-foreground hover:opacity-90"
                      : "bg-secondary text-secondary-foreground hover:bg-secondary/80"
                  }`}
                >
                  {p.cta}
                </Button>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="py-24 md:py-32">
        <div className="container">
          <Card className="relative overflow-hidden border-primary/30 bg-gradient-card p-10 md:p-16 text-center shadow-elegant">
            <div className="absolute inset-0 bg-gradient-hero opacity-60" />
            <div className="absolute inset-0 grid-bg opacity-40" />
            <div className="relative space-y-6 max-w-2xl mx-auto">
              <BarChart3 className="h-10 w-10 text-primary mx-auto" />
              <h2 className="font-display text-3xl md:text-5xl font-bold tracking-tight">
                Your next trade deserves a <span className="text-gradient">smarter signal</span>.
              </h2>
              <p className="text-muted-foreground text-lg">
                Join thousands of traders already running their book on SignalFlow.
              </p>
              <div className="flex flex-col sm:flex-row gap-3 justify-center pt-2">
                <Button size="lg" className="bg-gradient-primary text-primary-foreground font-semibold h-12 px-8 shadow-elegant hover:opacity-90">
                  Register free <ChevronRight className="ml-1 h-4 w-4" />
                </Button>
                <Button size="lg" variant="outline" className="h-12 px-8 border-border/60 hover:bg-secondary">
                  Login
                </Button>
              </div>
            </div>
          </Card>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border/40 bg-card/40">
        <div className="container py-14 grid md:grid-cols-5 gap-10">
          <div className="md:col-span-2 space-y-4">
            <a href="#" className="flex items-center gap-2 font-display font-bold text-lg">
              <span className="grid h-8 w-8 place-items-center rounded-lg bg-gradient-primary shadow-glow">
                <TrendingUp className="h-4 w-4 text-primary-foreground" strokeWidth={2.5} />
              </span>
              Signal<span className="text-gradient">Flow</span>
            </a>
            <p className="text-sm text-muted-foreground max-w-sm">
              AI-powered market intelligence for modern investors. Make sharper calls, faster.
            </p>
          </div>
          {[
            { title: "Product", items: ["Features", "Pricing", "API", "Changelog"] },
            { title: "Company", items: ["About", "Careers", "Press", "Contact"] },
            { title: "Legal", items: ["Privacy", "Terms", "Disclosures", "Security"] },
          ].map((col) => (
            <div key={col.title}>
              <div className="font-display font-semibold text-sm mb-4">{col.title}</div>
              <ul className="space-y-2 text-sm text-muted-foreground">
                {col.items.map((i) => (
                  <li key={i}><a href="#" className="hover:text-foreground transition-smooth">{i}</a></li>
                ))}
              </ul>
            </div>
          ))}
        </div>
        <div className="border-t border-border/40">
          <div className="container py-5 flex flex-col sm:flex-row justify-between items-center gap-3 text-xs text-muted-foreground">
            <div>© 2026 SignalFlow Labs, Inc. All rights reserved.</div>
            <div>Investing involves risk. Forecasts are not guarantees.</div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Index;