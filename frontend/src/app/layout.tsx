import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { ClerkProvider } from "@clerk/nextjs";
import { dark } from "@clerk/themes";
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
        // Clerk's official dark theme keeps the whole Account/UserProfile modal
        // and the UserButton dropdown readable (was dark-on-dark / grey before).
        baseTheme: dark,
        variables: {
          colorPrimary: "#22c55e",
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
