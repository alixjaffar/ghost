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
  Shield
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

export default function LandingPage() {
  const router = useRouter();
  return (
    <div className="min-h-screen bg-background">
      <header className="fixed top-0 left-0 right-0 z-50 bg-background/80 backdrop-blur-md border-b border-border">
        <div className="container mx-auto px-4">
          <div className="flex h-16 items-center justify-between">
            <GhostLogo size="sm" />
            <div className="flex items-center gap-4">
              <Show when="signed-out">
                <SignInButton mode="modal">
                  <Button variant="ghost">Sign in</Button>
                </SignInButton>
                <Link href="/sign-up">
                  <Button>
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
          word1="See"
          word2="First."
          description="Ghost detects signals before they become headlines — turning millions of conversations across the internet into real-time, actionable market intelligence."
          primaryCta="Enter Ghost"
          primaryCtaMobile="Enter"
          secondaryCta="View GitHub"
          secondaryCtaMobile="GitHub"
          onPrimaryClick={() => router.push("/signals")}
          githubUrl="https://github.com/alixjaffar/ghost"
        />

        <section className="py-20 border-t border-border">
          <div className="container mx-auto px-4">
            <div className="grid md:grid-cols-4 gap-8">
              {features.map((feature) => {
                const Icon = feature.icon;
                return (
                  <div key={feature.title} className="text-center">
                    <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-muted mb-4">
                      <Icon className="h-6 w-6" />
                    </div>
                    <h3 className="font-semibold mb-2">{feature.title}</h3>
                    <p className="text-sm text-muted-foreground">{feature.description}</p>
                  </div>
                );
              })}
            </div>
          </div>
        </section>

        <section className="py-20 border-t border-border">
          <div className="container mx-auto px-4 max-w-5xl">
            <div className="text-center mb-16">
              <h2 className="text-3xl md:text-4xl font-bold mb-4">
                What Makes Ghost Different
              </h2>
              <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                Most tools do ONE thing well. Nobody combines internet scraping, narrative detection, 
                event probability, acceleration velocity, cross-platform intelligence, and retail-friendly UX 
                into ONE consumer platform.
              </p>
            </div>

            <div className="space-y-8">
              {differentiators.map((item, index) => {
                const Icon = item.icon;
                return (
                  <div 
                    key={item.title}
                    className="flex gap-6 p-6 rounded-xl border border-border bg-card hover:border-border/80 transition-colors"
                  >
                    <div className="shrink-0">
                      <div className="w-12 h-12 rounded-xl bg-muted flex items-center justify-center">
                        <Icon className="h-6 w-6" />
                      </div>
                    </div>
                    <div>
                      <div className="flex items-center gap-3 mb-2">
                        <span className="text-xs text-muted-foreground font-medium uppercase tracking-wider">
                          {index + 1}.
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

        <section className="py-20 border-t border-border">
          <div className="container mx-auto px-4 max-w-3xl text-center">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Ghost is NOT
            </h2>
            <div className="text-lg text-muted-foreground space-y-2 mb-12">
              <p>Social sentiment software</p>
              <p>A stock screener</p>
              <p>A dashboard</p>
              <p>A news feed</p>
            </div>
            
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Ghost IS
            </h2>
            <p className="text-xl text-muted-foreground border-l-2 border-foreground/30 pl-6 py-2 inline-block text-left">
              A predictive intelligence engine for financial markets.
            </p>
          </div>
        </section>

        <section className="py-20 border-t border-border bg-muted/20">
          <div className="container mx-auto px-4 max-w-3xl text-center">
            <h2 className="text-3xl md:text-4xl font-bold mb-6">
              Predict. Prepare. Profit.
            </h2>
            <p className="text-lg text-muted-foreground mb-10">
              See it first. Act first.
            </p>
            <Show when="signed-out">
              <Link href="/sign-up">
                <Button size="lg" className="text-lg px-8 py-6">
                  Start free
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
              </Link>
            </Show>
            <Show when="signed-in">
              <Link href="/signals">
                <Button size="lg" className="text-lg px-8 py-6">
                  Explore Signals
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
              </Link>
            </Show>
          </div>
        </section>
      </main>

      <footer className="py-12 border-t border-border">
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
