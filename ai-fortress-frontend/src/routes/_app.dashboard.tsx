import { createFileRoute } from "@tanstack/react-router";
import { motion } from "framer-motion";
import { Topbar } from "@/components/app/Topbar";
import {
  Area, AreaChart, CartesianGrid, Cell,
  Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis, BarChart, Bar,
} from "recharts";
import { useEffect, useState } from "react";
import { Activity, ShieldAlert, ShieldCheck, Zap, TrendingUp, ArrowUpRight, ArrowDownRight, Loader2 } from "lucide-react";
import { analyticsService, scanService, type DashboardStats, type TopThreat, type RiskTrendPoint } from "@/lib/api-services";

export const Route = createFileRoute("/_app/dashboard")({
  component: Dashboard,
});

const PIE_COLORS = [
  "var(--color-destructive)",
  "var(--color-warning)",
  "var(--color-info)",
  "var(--color-success)",
  "var(--color-muted-foreground)",
];

function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [topThreats, setTopThreats] = useState<TopThreat[]>([]);
  const [trends, setTrends] = useState<RiskTrendPoint[]>([]);
  const [recentScans, setRecentScans] = useState<{ severity: string; message: string; time: string }[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const [dashboardData, threatsData, trendsData, historyData] = await Promise.all([
          analyticsService.getDashboard(),
          analyticsService.getTopThreats(5),
          analyticsService.getDailyStats(30),
          scanService.getHistory(1, 6),
        ]);
        setStats(dashboardData);
        setTopThreats(threatsData.threats);

        // Map daily stats to trend format
        setTrends(trendsData.stats.map((s) => ({
          date: s.date,
          avg_risk_score: s.avg_risk,
          total_scans: s.scans,
          threats_detected: s.threats,
        })));

        // Map recent scans to feed items
        setRecentScans(historyData.scans.map((s) => ({
          severity: s.result.overall_severity === "CRITICAL" ? "Critical" :
            s.result.overall_severity === "HIGH" ? "High" :
            s.result.overall_severity === "MEDIUM" ? "Medium" : "Low",
          message: s.result.is_safe
            ? `Safe prompt scanned · ${s.target_llm ?? "unknown"}`
            : `${s.result.threat_matches[0]?.category.replace(/_/g, " ") ?? "Threat"} blocked · ${s.target_llm ?? "unknown"}`,
          time: formatTimeAgo(s.created_at),
        })));
      } catch {
        // Fallback silently — user may have no data yet
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) {
    return (
      <div>
        <Topbar title="Analytics" subtitle="Real-time security telemetry" />
        <div className="flex items-center justify-center h-96">
          <div className="flex flex-col items-center gap-3">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
            <p className="text-sm text-muted-foreground">Loading analytics…</p>
          </div>
        </div>
      </div>
    );
  }

  const trendData = trends.map((t) => ({
    d: t.date.slice(5), // MM-DD
    scanned: t.total_scans,
    blocked: t.threats_detected,
  }));

  const pieData = topThreats.map((t, i) => ({
    n: t.category.replace(/_/g, " "),
    v: t.percentage,
    c: PIE_COLORS[i % PIE_COLORS.length],
  }));

  const barData = topThreats.map((t) => ({
    n: t.category.replace(/_/g, " "),
    v: t.count,
  }));

  return (
    <div>
      <Topbar title="Analytics" subtitle="Real-time security telemetry across all workspaces" />
      <div className="p-6 space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
          <Kpi label="Prompts scanned" value={stats?.total_scans ?? 0} delta={`${stats?.total_scans ?? 0} total`} icon={Activity} up />
          <Kpi label="Attacks blocked" value={stats?.attacks_blocked ?? 0} delta={`${stats?.threats_detected ?? 0} threats`} icon={ShieldAlert} up />
          <Kpi label="Avg risk score" value={`${stats?.avg_risk_score?.toFixed(1) ?? "0.0"}`} delta="per prompt" icon={Zap} />
          <Kpi label="Safe prompts" value={stats?.safe_prompts ?? 0} delta={`of ${stats?.total_scans ?? 0}`} icon={ShieldCheck} up />
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
          <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="xl:col-span-2 rounded-2xl glass p-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-mono text-[10px] tracking-widest text-primary">TRENDS · 30D</p>
                <h3 className="mt-1 font-semibold">Prompts scanned vs blocked</h3>
              </div>
              <div className="flex gap-2 text-[11px] text-muted-foreground">
                <Legend dot="var(--color-primary)" label="Scanned" />
                <Legend dot="var(--color-destructive)" label="Blocked" />
              </div>
            </div>
            <div className="mt-4 h-72">
              {trendData.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={trendData}>
                    <defs>
                      <linearGradient id="a1" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="var(--color-primary)" stopOpacity={0.35} />
                        <stop offset="100%" stopColor="var(--color-primary)" stopOpacity={0} />
                      </linearGradient>
                      <linearGradient id="a2" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="var(--color-destructive)" stopOpacity={0.35} />
                        <stop offset="100%" stopColor="var(--color-destructive)" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid stroke="var(--color-border)" strokeDasharray="3 3" vertical={false} />
                    <XAxis dataKey="d" stroke="var(--color-muted-foreground)" fontSize={10} tickLine={false} axisLine={false} />
                    <YAxis stroke="var(--color-muted-foreground)" fontSize={10} tickLine={false} axisLine={false} />
                    <Tooltip contentStyle={tooltipStyle} />
                    <Area type="monotone" dataKey="scanned" stroke="var(--color-primary)" strokeWidth={2} fill="url(#a1)" />
                    <Area type="monotone" dataKey="blocked" stroke="var(--color-destructive)" strokeWidth={2} fill="url(#a2)" />
                  </AreaChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-full grid place-items-center text-sm text-muted-foreground">
                  No trend data yet. Scan some prompts to see activity.
                </div>
              )}
            </div>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 }} className="rounded-2xl glass p-5">
            <p className="font-mono text-[10px] tracking-widest text-primary">THREAT MIX</p>
            <h3 className="mt-1 font-semibold">Distribution by class</h3>
            {pieData.length > 0 ? (
              <>
                <div className="mt-2 h-56">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie data={pieData} dataKey="v" nameKey="n" innerRadius={45} outerRadius={70} stroke="none">
                        {pieData.map((p) => <Cell key={p.n} fill={p.c} />)}
                      </Pie>
                      <Tooltip contentStyle={tooltipStyle} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                <ul className="space-y-1.5 text-xs">
                  {pieData.map((p) => (
                    <li key={p.n} className="flex items-center justify-between">
                      <span className="flex items-center gap-2"><span className="h-2 w-2 rounded-full" style={{ background: p.c }} />{p.n}</span>
                      <span className="font-mono text-muted-foreground">{p.v.toFixed(1)}%</span>
                    </li>
                  ))}
                </ul>
              </>
            ) : (
              <div className="mt-8 text-center text-sm text-muted-foreground">No threats detected yet.</div>
            )}
          </motion.div>
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
          <div className="xl:col-span-2 rounded-2xl glass p-5">
            <div>
              <p className="font-mono text-[10px] tracking-widest text-primary">TOP THREATS</p>
              <h3 className="mt-1 font-semibold">Most frequent detections</h3>
            </div>
            <div className="mt-4 h-64">
              {barData.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={barData} layout="vertical" margin={{ left: 24 }}>
                    <CartesianGrid stroke="var(--color-border)" strokeDasharray="3 3" horizontal={false} />
                    <XAxis type="number" stroke="var(--color-muted-foreground)" fontSize={10} tickLine={false} axisLine={false} />
                    <YAxis dataKey="n" type="category" stroke="var(--color-muted-foreground)" fontSize={11} tickLine={false} axisLine={false} width={130} />
                    <Tooltip contentStyle={tooltipStyle} cursor={{ fill: "var(--color-surface-2)" }} />
                    <Bar dataKey="v" fill="var(--color-primary)" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-full grid place-items-center text-sm text-muted-foreground">No data yet.</div>
              )}
            </div>
          </div>
          <div className="rounded-2xl glass p-5 flex flex-col">
            <div className="flex items-center justify-between">
              <p className="font-mono text-[10px] tracking-widest text-primary">RECENT SCANS</p>
              <LivePulse />
            </div>
            <h3 className="mt-1 font-semibold">Latest activity</h3>
            <ul className="mt-3 space-y-2 flex-1 overflow-auto max-h-72 pr-1">
              {recentScans.length > 0 ? recentScans.map((f, i) => (
                <li key={i} className="rounded-lg border border-border/60 bg-surface/40 p-3 text-xs">
                  <div className="flex items-center justify-between">
                    <SevPill s={f.severity} />
                    <span className="font-mono text-muted-foreground">{f.time}</span>
                  </div>
                  <p className="mt-1.5 text-foreground/90">{f.message}</p>
                </li>
              )) : (
                <li className="text-center text-sm text-muted-foreground py-8">No scans yet.</li>
              )}
            </ul>
          </div>
        </div>

        <SystemHealth />
      </div>
    </div>
  );
}

function formatTimeAgo(isoDate: string): string {
  const diff = Date.now() - new Date(isoDate).getTime();
  const secs = Math.floor(diff / 1000);
  if (secs < 60) return `${secs}s ago`;
  const mins = Math.floor(secs / 60);
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

function Kpi({ label, value, delta, icon: Icon, up }: { label: string; value: number | string; delta: string; icon: React.ComponentType<{ className?: string }>; up?: boolean }) {
  const display = useCount(value);
  return (
    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="rounded-2xl glass p-5">
      <div className="flex items-center justify-between">
        <p className="text-xs text-muted-foreground">{label}</p>
        <div className="h-7 w-7 rounded-md bg-primary/10 grid place-items-center border border-primary/20">
          <Icon className="h-3.5 w-3.5 text-primary" />
        </div>
      </div>
      <div className="mt-2 text-3xl font-semibold tracking-tight">{display}</div>
      <div className={`mt-1 inline-flex items-center gap-1 text-[11px] ${up ? "text-success" : "text-muted-foreground"}`}>
        {up ? <ArrowUpRight className="h-3 w-3" /> : <ArrowDownRight className="h-3 w-3" />} {delta}
      </div>
    </motion.div>
  );
}

function useCount(value: number | string) {
  const isNum = typeof value === "number";
  const [n, setN] = useState(isNum ? 0 : value);
  useEffect(() => {
    if (!isNum) return;
    const target = value as number;
    const dur = 900; const start = performance.now();
    let raf = 0;
    const tick = (t: number) => {
      const p = Math.min(1, (t - start) / dur);
      setN(Math.round(target * (1 - Math.pow(1 - p, 3))));
      if (p < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [value, isNum]);
  return isNum ? (n as number).toLocaleString() : (n as string);
}

const tooltipStyle = { background: "var(--color-surface-2)", border: "1px solid var(--color-border)", borderRadius: 8, fontSize: 11, color: "var(--color-foreground)" };

function Legend({ dot, label }: { dot: string; label: string }) {
  return <span className="flex items-center gap-1.5"><span className="h-2 w-2 rounded-full" style={{ background: dot }} />{label}</span>;
}

function SevPill({ s }: { s: string }) {
  const map: Record<string, string> = {
    Critical: "text-destructive bg-destructive/10 border-destructive/30",
    High: "text-destructive bg-destructive/10 border-destructive/20",
    Medium: "text-warning bg-warning/10 border-warning/25",
    Low: "text-success bg-success/10 border-success/25",
  };
  return <span className={`inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[10px] ${map[s] ?? ""}`}><span className="h-1.5 w-1.5 rounded-full bg-current" />{s}</span>;
}

function LivePulse() {
  return (
    <span className="inline-flex items-center gap-1.5 font-mono text-[10px] text-success">
      <span className="relative inline-flex h-2 w-2">
        <span className="absolute inset-0 rounded-full bg-success animate-ping opacity-60" />
        <span className="relative inline-flex h-2 w-2 rounded-full bg-success" />
      </span>
      LIVE
    </span>
  );
}

function SystemHealth() {
  const services = [
    { n: "Edge gateway", s: "Operational", l: "9ms" },
    { n: "Detector cluster", s: "Operational", l: "12ms" },
    { n: "Policy engine", s: "Operational", l: "4ms" },
    { n: "Audit log pipeline", s: "Operational", l: "8ms" },
  ];
  return (
    <div className="rounded-2xl glass p-5">
      <div className="flex items-center justify-between">
        <div>
          <p className="font-mono text-[10px] tracking-widest text-primary">SYSTEM HEALTH</p>
          <h3 className="mt-1 font-semibold">Services & SLOs</h3>
        </div>
        <a className="text-xs text-muted-foreground hover:text-foreground inline-flex items-center gap-1" href="#"><TrendingUp className="h-3 w-3" /> status page</a>
      </div>
      <div className="mt-4 grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-3">
        {services.map((s) => (
          <div key={s.n} className="rounded-lg border border-border/60 bg-surface/40 p-3">
            <div className="flex items-center justify-between">
              <span className="text-sm">{s.n}</span>
              <span className={`h-2 w-2 rounded-full ${s.s === "Operational" ? "bg-success" : "bg-warning"}`} />
            </div>
            <div className="mt-1 text-[11px] text-muted-foreground font-mono">{s.s} · {s.l}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
