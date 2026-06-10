"use client";

import { SignalLegend } from "@/components/ghost";

export function GlobalElements() {
  return (
    <>
      {/* Floating Legend Chat */}
      <SignalLegend />
      
      {/* Powered By Avallon Footer */}
      <footer className="fixed bottom-0 left-0 right-0 z-40 pointer-events-none">
        <div className="container mx-auto px-4 py-3">
          <p className="text-xs text-muted-foreground/50 text-center">
            Powered by <span className="font-semibold text-muted-foreground/70">Avallon</span>
          </p>
        </div>
      </footer>
    </>
  );
}
