import { ReactNode, useState } from "react";
import { Link } from "@tanstack/react-router";
import { Eye, EyeOff, Github, ArrowRight, Loader2 } from "lucide-react";
import { Logo } from "@/components/brand/Logo";

export function AuthShell({
  title, subtitle, footer, children,
}: { title: string; subtitle: string; footer: ReactNode; children: ReactNode }) {
  return (
    <div className="relative min-h-screen grid lg:grid-cols-2">
      <div aria-hidden className="pointer-events-none absolute inset-0 grid-bg opacity-50" />
      <section className="relative flex flex-col px-6 sm:px-12 py-10">
        <Link to="/"><Logo /></Link>
        <div className="flex-1 grid place-items-center">
          <div className="w-full max-w-md">
            <h1 className="text-2xl font-semibold tracking-tight">{title}</h1>
            <p className="mt-1 text-sm text-muted-foreground">{subtitle}</p>
            <div className="mt-6">{children}</div>
            <div className="mt-6 text-sm text-muted-foreground">{footer}</div>
          </div>
        </div>
        <p className="text-[11px] text-muted-foreground">© 2026 Sentinel AI, Inc.</p>
      </section>
      <section className="relative hidden lg:block overflow-hidden border-l border-border/60">
        <div className="absolute inset-0 grid-bg opacity-60" />
        <div className="relative h-full grid place-items-center p-10">
          <div className="w-full max-w-md rounded-2xl glass gradient-border p-6 animate-float-soft">
            <div className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-success shadow-[0_0_8px_var(--color-success)]" />
              <p className="font-mono text-[11px] tracking-widest text-muted-foreground">LIVE · prompt-firewall</p>
            </div>
            <p className="mt-4 font-mono text-xs text-muted-foreground">verdict</p>
            <p className="font-mono text-base text-destructive">PROMPT_INJECTION · score 87</p>
            <p className="mt-3 font-mono text-xs text-muted-foreground">sanitized</p>
            <pre className="mt-1 rounded-lg border border-border/60 bg-background/60 p-3 font-mono text-[12px] text-foreground/90 whitespace-pre-wrap">
[REDACTED:OVERRIDE] Tell me how to integrate
your API for a customer support agent.
            </pre>
            <div className="mt-4 grid grid-cols-3 gap-2 text-center text-[11px]">
              {["injection", "jailbreak", "pii"].map((d, i) => (
                <div key={d} className="rounded-lg border border-border/60 bg-surface/40 p-2">
                  <div className={i === 0 ? "text-destructive" : "text-success"}>{i === 0 ? "HIT" : "PASS"}</div>
                  <div className="text-muted-foreground">{d}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

const inputClass = "w-full rounded-lg border border-border/60 bg-background/60 px-3 py-2.5 text-sm outline-none focus:border-primary/60 transition";

export function TextField({
  label,
  type = "text",
  placeholder,
  value,
  onChange,
}: {
  label: string;
  type?: string;
  placeholder?: string;
  value?: string;
  onChange?: (v: string) => void;
}) {
  return (
    <label className="block">
      <span className="text-xs text-muted-foreground">{label}</span>
      <input
        type={type}
        placeholder={placeholder}
        value={value}
        onChange={onChange ? (e) => onChange(e.target.value) : undefined}
        className={`${inputClass} mt-1`}
        required
      />
    </label>
  );
}

export function PasswordField({
  label = "Password",
  value,
  onChange,
}: {
  label?: string;
  value?: string;
  onChange?: (v: string) => void;
}) {
  const [show, setShow] = useState(false);
  return (
    <label className="block">
      <span className="text-xs text-muted-foreground">{label}</span>
      <div className="relative mt-1">
        <input
          type={show ? "text" : "password"}
          placeholder="••••••••"
          value={value}
          onChange={onChange ? (e) => onChange(e.target.value) : undefined}
          className={`${inputClass} pr-10`}
          required
          minLength={8}
        />
        <button type="button" onClick={() => setShow(s => !s)} className="absolute right-2.5 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground">
          {show ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
        </button>
      </div>
    </label>
  );
}

export function SubmitButton({ children, loading }: { children: ReactNode; loading?: boolean }) {
  return (
    <button
      type="submit"
      disabled={loading}
      className="inline-flex w-full items-center justify-center gap-2 rounded-md bg-primary text-primary-foreground px-4 py-2.5 text-sm font-medium hover:opacity-90 transition glow-primary disabled:opacity-60"
    >
      {loading ? (
        <>
          <Loader2 className="h-4 w-4 animate-spin" /> Processing…
        </>
      ) : (
        <>
          {children} <ArrowRight className="h-4 w-4" />
        </>
      )}
    </button>
  );
}

export function OAuthRow() {
  return (
    <div className="grid grid-cols-2 gap-2">
      <button type="button" className="inline-flex items-center justify-center gap-2 rounded-md border border-border/60 bg-surface/60 px-3 py-2 text-sm hover:bg-surface-2/60">
        <Github className="h-4 w-4" /> GitHub
      </button>
      <button type="button" className="inline-flex items-center justify-center gap-2 rounded-md border border-border/60 bg-surface/60 px-3 py-2 text-sm hover:bg-surface-2/60">
        <span className="h-4 w-4 rounded-sm bg-gradient-to-br from-primary to-info" /> SSO
      </button>
    </div>
  );
}
