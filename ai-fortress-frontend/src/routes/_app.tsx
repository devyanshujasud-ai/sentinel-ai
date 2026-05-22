import { createFileRoute, Outlet, useNavigate } from "@tanstack/react-router";
import { useEffect } from "react";
import { Sidebar } from "@/components/app/Sidebar";
import { useAuth } from "@/lib/auth-store";

export const Route = createFileRoute("/_app")({
  component: AppLayout,
});

function AppLayout() {
  const { isAuthenticated, isLoading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      navigate({ to: "/login" });
    }
  }, [isAuthenticated, isLoading, navigate]);

  // Show nothing while checking auth / redirecting
  if (isLoading || !isAuthenticated) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <div className="h-8 w-8 rounded-full border-2 border-primary border-t-transparent animate-spin" />
          <p className="text-sm text-muted-foreground font-mono">Verifying session…</p>
        </div>
      </div>
    );
  }

  return (
    <div className="relative min-h-screen flex">
      <div aria-hidden className="pointer-events-none fixed inset-0 grid-bg opacity-60" />
      <Sidebar />
      <main className="relative flex-1 min-w-0">
        <Outlet />
      </main>
    </div>
  );
}
