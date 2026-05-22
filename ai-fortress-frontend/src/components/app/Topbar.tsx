import { Bell, Command, Search } from "lucide-react";
import { useAuth } from "@/lib/auth-store";

export function Topbar({ title, subtitle }: { title: string; subtitle?: string }) {
  const { user } = useAuth();

  const initials = user
    ? (user.full_name || user.username || "U")
        .split(" ")
        .map((w) => w[0])
        .join("")
        .toUpperCase()
        .slice(0, 2)
    : "??";

  return (
    <header className="sticky top-0 z-30 border-b border-border/60 bg-background/60 backdrop-blur-xl">
      <div className="flex items-center gap-4 px-6 py-4">
        <div className="min-w-0">
          <h1 className="text-lg font-semibold tracking-tight truncate">{title}</h1>
          {subtitle && <p className="text-xs text-muted-foreground truncate">{subtitle}</p>}
        </div>
        <div className="ml-auto flex items-center gap-3">
          <div className="hidden md:flex items-center gap-2 rounded-lg border border-border/70 bg-surface/60 px-3 py-1.5 w-72">
            <Search className="h-3.5 w-3.5 text-muted-foreground" />
            <input
              placeholder="Search threats, scans, endpoints…"
              className="bg-transparent text-xs outline-none flex-1 placeholder:text-muted-foreground"
            />
            <kbd className="hidden md:inline-flex items-center gap-1 font-mono text-[10px] text-muted-foreground border border-border/70 rounded px-1.5 py-0.5">
              <Command className="h-3 w-3" /> K
            </kbd>
          </div>
          <button className="relative grid place-items-center h-9 w-9 rounded-lg border border-border/70 bg-surface/60 hover:bg-surface-2/60 transition">
            <Bell className="h-4 w-4 text-muted-foreground" />
            <span className="absolute top-2 right-2 h-1.5 w-1.5 rounded-full bg-destructive" />
          </button>
          <div className="h-9 w-9 rounded-full bg-gradient-to-br from-primary/60 to-info/60 grid place-items-center text-xs font-semibold text-primary-foreground">
            {initials}
          </div>
        </div>
      </div>
    </header>
  );
}
