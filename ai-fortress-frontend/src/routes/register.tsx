import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useState } from "react";
import { AuthShell, OAuthRow, PasswordField, SubmitButton, TextField } from "@/components/auth/AuthShell";
import { useAuth } from "@/lib/auth-store";

export const Route = createFileRoute("/register")({
  component: Register,
});

function Register() {
  const { register, isLoading, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [fullName, setFullName] = useState("");
  const [password, setPassword] = useState("");
  const [agreed, setAgreed] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (isAuthenticated) {
    navigate({ to: "/dashboard" });
    return null;
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!agreed) {
      setError("You must agree to the Terms and Privacy Policy.");
      return;
    }
    try {
      await register({
        email,
        username,
        password,
        full_name: fullName || undefined,
      });
      navigate({ to: "/dashboard" });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed.");
    }
  };

  return (
    <AuthShell
      title="Create your account"
      subtitle="Start scanning prompts in under five minutes"
      footer={<>Already on Sentinel? <Link to="/login" className="text-primary hover:underline">Sign in</Link></>}
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
        <div className="grid grid-cols-2 gap-3">
          <TextField label="Full name" placeholder="Alex Knox" value={fullName} onChange={setFullName} />
          <TextField label="Username" placeholder="alexknox" value={username} onChange={setUsername} />
        </div>
        <TextField label="Work email" type="email" placeholder="you@company.com" value={email} onChange={setEmail} />
        <PasswordField value={password} onChange={setPassword} />
        <label className="flex items-start gap-2 text-xs text-muted-foreground">
          <input
            type="checkbox"
            checked={agreed}
            onChange={(e) => setAgreed(e.target.checked)}
            className="mt-0.5 accent-[var(--color-primary)]"
          />
          I agree to the <a className="text-primary hover:underline" href="#">Terms</a> and <a className="text-primary hover:underline" href="#">Privacy Policy</a>.
        </label>
        <SubmitButton loading={isLoading}>Create account</SubmitButton>
      </form>
    </AuthShell>
  );
}
