"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { GhostLogo } from "@/components/ghost";
import { Button } from "@/components/ui/button";
import { PixelHero } from "@/components/ui/pixel-perfect-hero";
import { Show, SignInButton, UserButton } from "@clerk/nextjs";
import {
  Eye,
  Brain,
  Zap,
  BarChart3,
  ArrowRight,
  TrendingUp,
  Activity,
  Shield,
} from "lucide-react";

const features = [
  {
    icon: Eye,
    title: "We See First",
    description: "We spot the signals others miss.",
  },
  {
    icon: Brain,
    title: "We Analyze Deep",
    description: "We decode patterns before they surface.",
  },
  {
    icon: Zap,
    title: "You Stay Ahead",
    description: "Actionable insight. Real advantage.",
  },
  {
    icon: BarChart3,
    title: "Outcomes That Matter",
    description: "Better decisions today. Bigger impact tomorrow.",
  },
];

const differentiators = [
  {
    icon: TrendingUp,
    title: "Narrative Velocity Engine",
    description: "Track how fast conviction is spreading, not just sentiment. 200 mentions → 20,000 mentions in 72 hours matters more than static sentiment.",
  },
  {
    icon: Activity,
    title: "Cross-Platform Correlation",
    description: "We correlate TikTok, YouTube transcripts, podcasts, comments, reels, Reddit, X/Twitter, news, and creator communities.",
  },
  {
    icon: Shield,
    title: "Event Probability AI",
    description: "We estimate probability of event happening, timeframe, acceleration, and confidence score — not just 'people are talking.'",
  },
];

// Shared glass surface so every section echoes the hero's frosted look.
const GLASS_CARD =
  "rounded-2xl border border-white/5 bg-gradient-to-b from-card/70 to-card/20 backdrop-blur-md ring-1 ring-white/5 shadow-[inset_0_1px_0_rgba(255,255,255,0.06),0_24px_48px_-24px_rgba(0,0,0,0.7)] transition-all duration-300";
const ICON_TILE =
  "inline-flex items-center justify-center w-12 h-12 rounded-xl bg-gradient-to-b from-white/10 to-white/[0.03] ring-1 ring-white/10 text-foreground";
const EYEBROW =
  "text-xs uppercase tracking-[0.25em] text-muted-foreground/80 font-medium";

export default function LandingPage() {
  const router = useRouter();

  return (
    <div className="min-h-screen bg-background text-foreground">
      <header className="fixed top-0 left-0 right-0 z-50 bg-background/70 backdrop-blur-xl border-b border-white/5">
        <div className="container mx-auto px-4">
          <div className="flex h-16 items-center justify-between">
            <GhostLogo size="sm" />
            <div className="flex items-center gap-4">
              <Show when="signed-out">
                <SignInButton mode="modal">
                  <Button variant="ghost">Sign in</Button>
                </SignInButton>
                <Link href="/sign-up">
                  <Button className="rounded-xl">
                    Get Started
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </Link>
              </Show>
              <Show when="signed-in">
                <Link href="/signals">
                  <Button variant="ghost">Signals</Button>
                </Link>
                <UserButton />
              </Show>
            </div>
          </div>
        </div>
      </header>

      <main>
        <PixelHero
          word1="The future is hiding"
          word2="in plain sight."
          tagline="Ghost detects signals before they become headlines."
          description="We scan millions of conversations across the internet, analyze them in real time, and turn noise into actionable intelligence — so you can predict events before the market catches on."
          primaryCta="Enter Ghost"
          primaryCtaMobile="Enter"
          secondaryCta="View GitHub"
          secondaryCtaMobile="GitHub"
          onPrimaryClick={() => router.push("/signals")}
          githubUrl="https://github.com/alixjaffar/ghost"
          partnersLabel="Scanning signals across"
          partners={[
            "YouTube",
            "Reddit",
            "X / Twitter",
            "StockTwits",
            "Polymarket",
            "Financial News",
            "Polygon",
            "Podcasts",
          ]}
        />

        {/* The edge */}
        <section className="relative py-24 px-4 border-t border-white/5">
          <div className="container mx-auto max-w-6xl">
            <div className="text-center mb-14">
              <span className={EYEBROW}>The edge</span>
              <h2 className="mt-4 text-3xl md:text-5xl font-bold tracking-tight">
                See it first.{" "}
                <span className="font-serif italic font-medium text-muted-foreground">
                  Act first.
                </span>
              </h2>
            </div>
            <div className="grid md:grid-cols-4 gap-6">
              {features.map((feature) => {
                const Icon = feature.icon;
                return (
                  <div
                    key={feature.title}
                    className={`${GLASS_CARD} p-6 text-center hover:ring-white/15 hover:from-card/90`}
                  >
                    <div className={`${ICON_TILE} mx-auto mb-4`}>
                      <Icon className="h-6 w-6" />
                    </div>
                    <h3 className="font-semibold mb-2">{feature.title}</h3>
                    <p className="text-sm text-muted-foreground">
                      {feature.description}
                    </p>
                  </div>
                );
              })}
            </div>
          </div>
        </section>

        {/* What makes Ghost different */}
        <section className="relative py-24 px-4 border-t border-white/5 overflow-hidden">
          <div className="pointer-events-none absolute -top-24 left-1/2 -translate-x-1/2 h-72 w-[42rem] rounded-full bg-[radial-gradient(circle,oklch(1_0_0_/_0.06),transparent_70%)] blur-2xl" />
          <div className="container mx-auto px-0 max-w-5xl relative">
            <div className="text-center mb-16">
              <span className={EYEBROW}>Why Ghost</span>
              <h2 className="mt-4 text-3xl md:text-5xl font-bold tracking-tight mb-4">
                What makes Ghost{" "}
                <span className="font-serif italic font-medium text-muted-foreground">
                  different
                </span>
              </h2>
              <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                Most tools do ONE thing well. Nobody combines internet scraping,
                narrative detection, event probability, acceleration velocity,
                cross-platform intelligence, and retail-friendly UX into ONE
                consumer platform.
              </p>
            </div>

            <div className="space-y-5">
              {differentiators.map((item, index) => {
                const Icon = item.icon;
                return (
                  <div
                    key={item.title}
                    className={`${GLASS_CARD} flex gap-6 p-6 hover:ring-white/15 hover:from-card/90`}
                  >
                    <div className="shrink-0">
                      <div className={ICON_TILE}>
                        <Icon className="h-6 w-6 text-foreground" />
                      </div>
                    </div>
                    <div>
                      <div className="flex items-center gap-3 mb-2">
                        <span className="text-xs text-muted-foreground font-medium uppercase tracking-wider">
                          {String(index + 1).padStart(2, "0")}
                        </span>
                        <h3 className="text-xl font-semibold">{item.title}</h3>
                      </div>
                      <p className="text-muted-foreground">{item.description}</p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </section>

        {/* Ghost is NOT / IS */}
        <section className="relative py-24 px-4 border-t border-white/5">
          <div className="container mx-auto max-w-4xl grid md:grid-cols-2 gap-6">
            <div className={`${GLASS_CARD} p-8`}>
              <span className={EYEBROW}>Ghost is NOT</span>
              <ul className="mt-5 space-y-3 text-lg text-muted-foreground">
                <li>Social sentiment software</li>
                <li>A stock screener</li>
                <li>A dashboard</li>
                <li>A news feed</li>
              </ul>
            </div>
            <div className={`${GLASS_CARD} p-8 ring-white/10`}>
              <span className={EYEBROW}>Ghost IS</span>
              <p className="mt-5 text-2xl font-semibold leading-snug">
                A{" "}
                <span className="font-serif italic font-medium">predictive</span>{" "}
                intelligence engine for financial markets.
              </p>
              <p className="mt-4 text-muted-foreground">
                Built to surface what matters before the market catches on.
              </p>
            </div>
          </div>
        </section>

        {/* Final CTA */}
        <section className="relative py-24 px-4 border-t border-white/5 overflow-hidden">
          <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_center,oklch(0.18_0_0_/_0.6),transparent_70%)]" />
          <div className={`${GLASS_CARD} container mx-auto max-w-3xl text-center p-12 relative`}>
            <h2 className="text-3xl md:text-5xl font-bold mb-4 tracking-tight">
              Predict.{" "}
              <span className="font-serif italic font-medium text-muted-foreground">
                Prepare.
              </span>{" "}
              Profit.
            </h2>
            <p className="text-lg text-muted-foreground mb-10">
              See it first. Act first.
            </p>
            <Show when="signed-out">
              <Link href="/sign-up">
                <Button size="lg" className="text-lg px-8 py-6 rounded-xl">
                  Start free
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
              </Link>
            </Show>
            <Show when="signed-in">
              <Link href="/signals">
                <Button size="lg" className="text-lg px-8 py-6 rounded-xl">
                  Explore Signals
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
              </Link>
            </Show>
          </div>
        </section>
      </main>

      <footer className="py-12 border-t border-white/5">
        <div className="container mx-auto px-4">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <GhostLogo size="sm" />
            <p className="text-sm text-muted-foreground">
              Demo for illustrative purposes. Not financial advice.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
