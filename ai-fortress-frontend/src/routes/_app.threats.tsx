import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Topbar } from "@/components/app/Topbar";
import { ShieldAlert, Bug, Lock, Eye, KeyRound, Cpu, ShieldAlert as AlertIcon, Terminal, Code2, AlertCircle, Loader2 } from "lucide-react";
import { threatsService, type ThreatDefinition } from "@/lib/api-services";
import { extractError } from "@/lib/api-client";

export const Route = createFileRoute("/_app/threats")({
  component: Threats,
});

// Map backend categories to icons
const iconMap: Record<string, React.ComponentType<any>> = {
  PROMPT_INJECTION: Bug,
  JAILBREAK: Lock,
  SQL_INJECTION: KeyRound,
  SHELL_COMMAND: Terminal,
  TOXICITY: AlertCircle,
  SENSITIVE_DATA_LEAKAGE: Eye,
  UNSAFE_CODE: Code2,
  ROLE_MANIPULATION: Cpu,
};

function Threats() {
  const [threats, setThreats] = useState<ThreatDefinition[]>([]);
  const [activeCategory, setActiveCategory] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadThreats() {
      setLoading(true);
      setError(null);
      try {
        const res = await threatsService.getAll();
        setThreats(res.threats);
        if (res.threats.length > 0) {
          setActiveCategory(res.threats[0].category);
        }
      } catch (err) {
        setError(extractError(err));
      } finally {
        setLoading(false);
      }
    }
    loadThreats();
  }, []);

  const activeThreat = threats.find((t) => t.category === activeCategory);

  if (loading) {
    return (
      <div>
        <Topbar title="Threat Intelligence" subtitle="Threat categories and definitions" />
        <div className="flex items-center justify-center h-96">
          <div className="flex flex-col items-center gap-3">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
            <p className="text-sm text-muted-foreground">Loading threat catalog…</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div>
      <Topbar title="Threat Intelligence" subtitle="Active gateway security catalog" />
      <div className="p-6">
        {error && (
          <div className="mb-4 rounded-lg border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          <aside className="lg:col-span-1 space-y-2">
            {threats.map((c) => {
              const Icon = iconMap[c.category] || ShieldAlert;
              const Active = c.category === activeCategory;
              return (
                <button
                  key={c.id}
                  onClick={() => setActiveCategory(c.category)}
                  className={`w-full flex items-center gap-3 rounded-xl border p-3 text-left transition ${
                    Active
                      ? "border-primary/40 bg-primary/10"
                      : "border-border/60 bg-surface/40 hover:bg-surface-2/40"
                  }`}
                >
                  <div
                    className={`h-8 w-8 grid place-items-center rounded-md border ${
                      Active ? "border-primary/40 text-primary" : "border-border/60 text-muted-foreground"
                    }`}
                  >
                    <Icon className="h-4 w-4" />
                  </div>
                  <div>
                    <div className="text-sm font-medium">{c.name}</div>
                    <div className="text-[11px] text-muted-foreground line-clamp-1">Severity: {c.severity}</div>
                  </div>
                </button>
              );
            })}
          </aside>

          <div className="lg:col-span-3">
            {activeThreat ? (
              <motion.section
                key={activeThreat.id}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                className="rounded-2xl glass gradient-border p-6"
              >
                <p className="font-mono text-[10px] tracking-widest text-primary">CONCEPT</p>
                <h2 className="mt-1 text-2xl font-semibold tracking-tight">{activeThreat.name}</h2>
                <p className="mt-2 text-muted-foreground">{activeThreat.description}</p>

                <div className="mt-6">
                  <p className="font-mono text-[10px] tracking-widest text-muted-foreground">SAMPLE ATTACK / PROBE PATTERNS</p>
                  <div className="space-y-2 mt-2">
                    {activeThreat.examples.map((ex, idx) => (
                      <pre
                        key={idx}
                        className="rounded-lg border border-border/60 bg-background/60 p-4 font-mono text-sm text-foreground/90 whitespace-pre-wrap"
                      >
                        {ex}
                      </pre>
                    ))}
                  </div>
                </div>

                <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-3">
                  <div className="rounded-xl border border-border/60 bg-surface/40 p-4">
                    <p className="font-mono text-[10px] tracking-widest text-primary">MITIGATION STRATEGY</p>
                    <p className="mt-1 text-sm text-muted-foreground">
                      Sentinel automatically filters detected segments and replaces them with a secure placeholder token. Ensure safe parsing and re-contextualization downstream.
                    </p>
                  </div>
                  <div className="rounded-xl border border-border/60 bg-surface/40 p-4">
                    <p className="font-mono text-[10px] tracking-widest text-primary">GATEWAY WEIGHT</p>
                    <p className="mt-1 text-sm text-muted-foreground">
                      This threat is heavily weighted at <strong className="text-foreground">{activeThreat.weight * 10}</strong> points out of 100 towards the aggregated risk score composition.
                    </p>
                  </div>
                </div>

                <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-3">
                  {[
                    { k: "Detector ID", v: activeThreat.category.toLowerCase() },
                    { k: "Default Severity", v: activeThreat.severity },
                    { k: "Risk Weight", v: `${activeThreat.weight}x` },
                    { k: "Status", v: activeThreat.is_active ? "ACTIVE" : "DISABLED" },
                  ].map((s) => (
                    <div key={s.k} className="rounded-lg border border-border/60 bg-surface/40 p-3">
                      <p className="text-[11px] text-muted-foreground">{s.k}</p>
                      <p className="text-sm font-medium uppercase">{s.v}</p>
                    </div>
                  ))}
                </div>
              </motion.section>
            ) : (
              <div className="rounded-2xl glass gradient-border p-6 text-center text-muted-foreground">
                Select a threat category to view details.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
