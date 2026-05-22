import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { Topbar } from "@/components/app/Topbar";
import { Eye, EyeOff, KeyRound, Plus, Trash2, Shield, Calendar, Award } from "lucide-react";
import { useAuth } from "@/lib/auth-store";

export const Route = createFileRoute("/_app/settings")({
  component: Settings,
});

function Settings() {
  return (
    <div>
      <Topbar title="Settings" subtitle="Profile, account details, and API configuration" />
      <div className="p-6 grid grid-cols-1 xl:grid-cols-3 gap-6">
        <ProfileCard />
        <ThemeCard />
        <NotificationsCard />
        <ApiKeysCard />
      </div>
    </div>
  );
}

function Card({ title, eyebrow, children, className = "" }: { title: string; eyebrow: string; children: React.ReactNode; className?: string }) {
  return (
    <div className={`rounded-2xl glass p-5 ${className}`}>
      <p className="font-mono text-[10px] tracking-widest text-primary">{eyebrow}</p>
      <h3 className="mt-1 font-semibold">{title}</h3>
      <div className="mt-4">{children}</div>
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="block">
      <span className="text-xs text-muted-foreground">{label}</span>
      <div className="mt-1">{children}</div>
    </label>
  );
}

const inputClass = "w-full rounded-lg border border-border/60 bg-background/60 px-3 py-2 text-sm outline-none focus:border-primary/60 transition";

function ProfileCard() {
  const { user } = useAuth();

  const initials = user
    ? (user.full_name || user.username || "U")
        .split(" ")
        .map((w) => w[0])
        .join("")
        .toUpperCase()
        .slice(0, 2)
    : "AK";

  return (
    <Card title="Account Overview" eyebrow="PROFILE">
      <div className="flex items-center gap-3">
        <div className="h-14 w-14 rounded-full bg-gradient-to-br from-primary/60 to-info/60 grid place-items-center text-base font-semibold text-primary-foreground">
          {initials}
        </div>
        <div>
          <h4 className="text-sm font-semibold">{user?.full_name || user?.username}</h4>
          <p className="text-xs text-muted-foreground capitalize">{user?.role} Workspace</p>
        </div>
      </div>
      <div className="mt-6 space-y-4">
        <Field label="Username">
          <input value={user?.username || ""} readOnly className={`${inputClass} opacity-80 cursor-default`} />
        </Field>
        <Field label="Email Address">
          <input value={user?.email || ""} readOnly className={`${inputClass} opacity-80 cursor-default`} />
        </Field>
        <Field label="Full Name">
          <input value={user?.full_name || ""} readOnly className={`${inputClass} opacity-80 cursor-default`} />
        </Field>
        <Field label="Created On">
          <div className="flex items-center gap-2 rounded-lg border border-border/60 bg-surface/20 px-3 py-2 text-xs font-mono text-muted-foreground">
            <Calendar className="h-4 w-4" />
            {user?.created_at ? new Date(user.created_at).toLocaleDateString() : "N/A"}
          </div>
        </Field>
      </div>
    </Card>
  );
}

function NotificationsCard() {
  const items = [
    ["Critical threats", "Real-time email + Slack on critical detections.", true],
    ["Weekly digest", "Summary of activity every Monday.", true],
    ["Detector updates", "When new detectors are released.", false],
    ["Billing", "Invoices and usage alerts.", true],
  ] as const;
  return (
    <Card title="Security Alerts" eyebrow="ALERTS">
      <ul className="divide-y divide-border/60">
        {items.map(([t, d, on]) => <Toggle key={t} t={t} d={d} on={on} />)}
      </ul>
    </Card>
  );
}

function Toggle({ t, d, on }: { t: string; d: string; on: boolean }) {
  const [v, setV] = useState(on);
  return (
    <li className="flex items-start justify-between gap-4 py-3">
      <div>
        <p className="text-sm font-medium">{t}</p>
        <p className="text-xs text-muted-foreground">{d}</p>
      </div>
      <button onClick={() => setV(!v)} className={`relative h-5 w-9 rounded-full transition ${v ? "bg-primary" : "bg-surface-2"}`}>
        <span className={`absolute top-0.5 h-4 w-4 rounded-full bg-background transition-transform ${v ? "translate-x-4" : "translate-x-0.5"}`} />
      </button>
    </li>
  );
}

function ThemeCard() {
  const accents = [
    { n: "Cyan", v: "oklch(0.78 0.13 195)" },
    { n: "Indigo", v: "oklch(0.70 0.14 270)" },
    { n: "Emerald", v: "oklch(0.72 0.16 155)" },
    { n: "Amber", v: "oklch(0.78 0.16 75)" },
  ];
  const [a, setA] = useState(0);
  return (
    <Card title="Appearance" eyebrow="THEME">
      <p className="text-xs text-muted-foreground">Sentinel is dark-mode native. Choose an accent for charts and CTAs.</p>
      <div className="mt-3 grid grid-cols-4 gap-2">
        {accents.map((ac, i) => (
          <button key={ac.n} onClick={() => setA(i)} className={`rounded-lg border p-3 text-left ${a === i ? "border-primary/40 bg-primary/10" : "border-border/60 bg-surface/40 hover:bg-surface-2/40"}`}>
            <span className="block h-6 w-full rounded-md" style={{ background: ac.v }} />
            <span className="mt-2 block text-[11px]">{ac.n}</span>
          </button>
        ))}
      </div>
      <div className="mt-4 rounded-lg border border-border/60 bg-surface/40 p-3">
        <p className="text-xs text-muted-foreground">Density</p>
        <input type="range" min={0} max={2} defaultValue={1} className="mt-2 w-full accent-[var(--color-primary)]" />
      </div>
    </Card>
  );
}

function ApiKeysCard() {
  const { user } = useAuth();
  const [show, setShow] = useState(false);
  const keys = [
    { n: "Production Gateway Key", k: "sk_live_sentinel_gateway_key_" + (user?.id || "default"), c: user?.created_at ? new Date(user.created_at).toLocaleDateString() : "Today" },
  ];
  return (
    <Card title="API credentials" eyebrow="SECURITY" className="xl:col-span-3">
      <div className="flex items-center justify-between">
        <p className="text-xs text-muted-foreground">Use this credential to authenticate backend client SDK libraries.</p>
        <div className="flex items-center gap-1.5 text-xs text-success border border-success/30 bg-success/5 px-2.5 py-1.5 rounded-lg">
          <Award className="h-3.5 w-3.5" /> API Gateway Active
        </div>
      </div>
      <div className="mt-4 divide-y divide-border/60 rounded-xl border border-border/60 bg-surface/40">
        {keys.map((k) => (
          <div key={k.n} className="flex items-center gap-3 p-4">
            <div className="h-8 w-8 grid place-items-center rounded-md bg-primary/10 border border-primary/20 text-primary">
              <KeyRound className="h-4 w-4" />
            </div>
            <div className="min-w-0 flex-1">
              <div className="text-sm font-medium">{k.n}</div>
              <div className="font-mono text-xs text-muted-foreground truncate">
                {show ? k.k : k.k.replace(/(?<=sk_(live|test)_).+(?=.{4})/, "•".repeat(28))}
              </div>
            </div>
            <button onClick={() => setShow(s => !s)} className="text-muted-foreground hover:text-foreground">
              {show ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </button>
            <span className="hidden md:inline text-[11px] text-muted-foreground font-mono">created {k.c}</span>
          </div>
        ))}
      </div>
    </Card>
  );
}
