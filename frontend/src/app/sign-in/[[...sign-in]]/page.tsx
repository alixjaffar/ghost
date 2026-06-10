import { SignIn } from "@clerk/nextjs";
import { GhostLogo } from "@/components/ghost";
import Link from "next/link";

export default function SignInPage() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-background px-4 py-12">
      <Link href="/" className="mb-8">
        <GhostLogo size="lg" />
      </Link>
      <SignIn
        appearance={{
          variables: {
            colorPrimary: "#22c55e",
            colorBackground: "#0a0a0a",
          },
        }}
      />
    </div>
  );
}
