import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server";

// App routes that require a signed-in user. The landing page ("/"),
// sign-in, and sign-up remain public.
const isProtectedRoute = createRouteMatcher([
  "/signals(.*)",
  "/watchlist(.*)",
  "/search(.*)",
]);

export default clerkMiddleware(async (auth, req) => {
  if (isProtectedRoute(req)) {
    await auth.protect();
  }
});

export const config = {
  matcher: [
    // Skip Next.js internals and static files
    "/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)",
    // Always run for API routes
    "/(api|trpc)(.*)",
  ],
};
