import { Link, useRouterState, useNavigate } from "@tanstack/react-router";
import {
  LayoutDashboard,
  ScanLine,
  History,
  Shield,
  BookOpen,
  Settings,
  LogOut,
} from "lucide-react";
import { Logo } from "@/components/brand/Logo";
import { cn } from "@/lib/utils";
import { useAuth } from "@/lib/auth-store";

const nav = [
  { to: "/scanner", label: "Prompt Scanner", icon: ScanLine },
  { to: "/dashboard", label: "Analytics", icon: LayoutDashboard },
  { to: "/history", label: "Scan History", icon: History },
  { to: "/threats", label: "Threat Intelligence", icon: Shield },
  { to: "/docs", label: "API Docs", icon: BookOpen },
  { to: "/settings", label: "Settings", icon: Settings },
] as const;

export function Sidebar() {
  const { location } = useRouterState();
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate({ to: "/login" });
  };

  const initials = user
    ? (user.full_name || user.username || user.email)
        .split(" ")
        .map((w) => w[0])
        .join("")
        .toUpperCase()
        .slice(0, 2)
    : "??";

  return (
    <aside className="hidden lg:flex h-screen sticky top-0 w-64 shrink-0 flex-col border-r border-border/60 bg-surface/40 backdrop-blur-xl">
      <div className="px-5 py-5 border-b border-border/60">
        <Link to="/"><Logo /></Link>
      </div>
      <nav className="flex-1 px-3 py-4 space-y-1">
        <p className="px-3 mb-2 font-mono text-[10px] tracking-widest text-muted-foreground">WORKSPACE</p>
        {nav.map(({ to, label, icon: Icon }) => {
          const active = location.pathname.startsWith(to);
          return (
            <Link
              key={to}
              to={to}
              className={cn(
                "group flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-all",
                active
                  ? "bg-primary/10 text-foreground border border-primary/20"
                  : "text-muted-foreground hover:text-foreground hover:bg-surface-2/60 border border-transparent",
              )}
            >
              <Icon className={cn("h-4 w-4", active && "text-primary")} />
              <span>{label}</span>
              {active && <span className="ml-auto h-1.5 w-1.5 rounded-full bg-primary shadow-[0_0_8px_var(--color-primary)]" />}
            </Link>
          );
        })}
      </nav>
      <div className="m-3 rounded-xl glass gradient-border p-4">
        <p className="font-mono text-[10px] tracking-widest text-primary">SYSTEM</p>
        <div className="mt-2 flex items-center gap-2">
          <span className="relative inline-flex h-2 w-2">
            <span className="absolute inset-0 rounded-full bg-success animate-ping opacity-60" />
            <span className="relative inline-flex h-2 w-2 rounded-full bg-success" />
          </span>
          <p className="text-xs">All systems operational</p>
        </div>
        {user && (
          <p className="mt-1 text-[11px] text-muted-foreground truncate">
            {user.username} · {user.total_scans} scans
          </p>
        )}
      </div>
      <div className="p-3 border-t border-border/60">
        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-3 rounded-lg px-3 py-2 text-sm text-muted-foreground hover:text-foreground hover:bg-surface-2/60"
        >
          <LogOut className="h-4 w-4" /> Sign out
        </button>
      </div>
    </aside>
  );
}
