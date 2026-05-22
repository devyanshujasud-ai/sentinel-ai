import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useState } from "react";
import { AuthShell, OAuthRow, PasswordField, SubmitButton, TextField } from "@/components/auth/AuthShell";
import { useAuth } from "@/lib/auth-store";

export const Route = createFileRoute("/login")({
  component: Login,
});

function Login() {
  const { login, isLoading, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);

  // Redirect if already logged in
  if (isAuthenticated) {
    navigate({ to: "/dashboard" });
    return null;
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      await login(email, password);
      navigate({ to: "/dashboard" });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed.");
    }
  };

  return (
    <AuthShell
      title="Welcome back"
      subtitle="Sign in to your Sentinel workspace"
      footer={<>Don't have an account? <Link to="/register" className="text-primary hover:underline">Create one</Link></>}
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        <OAuthRow />
        <div className="flex items-center gap-3 text-[11px] font-mono text-muted-foreground">
          <span className="h-px flex-1 bg-border" /> OR EMAIL <span className="h-px flex-1 bg-border" />
        </div>
        {error && (
          <div className="rounded-lg border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
            {error}
          </div>
        )}
        <TextField label="Email" type="email" placeholder="you@company.com" value={email} onChange={setEmail} />
        <PasswordField value={password} onChange={setPassword} />
        <div className="flex items-center justify-between text-xs">
          <label className="inline-flex items-center gap-2 text-muted-foreground">
            <input type="checkbox" className="accent-[var(--color-primary)]" /> Remember me
          </label>
          <a className="text-primary hover:underline" href="#">Forgot password?</a>
        </div>
        <SubmitButton loading={isLoading}>Sign in</SubmitButton>
      </form>
    </AuthShell>
  );
}
