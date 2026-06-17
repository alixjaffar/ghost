import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { ClerkProvider } from "@clerk/nextjs";
import { TooltipProvider } from "@/components/ui/tooltip";
import { GlobalElements } from "@/components/layout/global-elements";
import "./globals.css";

const inter = Inter({
  variable: "--font-sans",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Ghost | Predictive Intelligence for Financial Markets",
  description: "The future is hiding in plain sight. Ghost detects signals before they become headlines.",
  openGraph: {
    title: "Ghost | Predictive Intelligence for Financial Markets",
    description: "The future is hiding in plain sight. Ghost detects signals before they become headlines.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <ClerkProvider
      afterSignOutUrl="/"
      appearance={{
        variables: {
          colorPrimary: "#22c55e",
          colorBackground: "#0a0a0a",
          // Dark-theme text/input colors so Clerk menus (e.g. the UserButton
          // dropdown) aren't dark-on-dark and invisible.
          colorText: "#ededed",
          colorTextSecondary: "#a1a1aa",
          colorInputBackground: "#171717",
          colorInputText: "#ededed",
          colorNeutral: "#ffffff",
        },
      }}
    >
      <html lang="en" className={`${inter.variable} dark h-full antialiased`}>
        <body className="min-h-full flex flex-col bg-background pb-10">
          <TooltipProvider>
            {children}
            <GlobalElements />
          </TooltipProvider>
        </body>
      </html>
    </ClerkProvider>
  );
}
