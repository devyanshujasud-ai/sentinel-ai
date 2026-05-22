import { ShieldCheck } from "lucide-react";
import { cn } from "@/lib/utils";

export function Logo({ className, withText = true }: { className?: string; withText?: boolean }) {
  return (
    <div className={cn("flex items-center gap-2.5", className)}>
      <div className="relative grid place-items-center h-8 w-8 rounded-md bg-gradient-to-br from-primary/30 to-primary/5 border border-primary/30">
        <ShieldCheck className="h-4 w-4 text-primary" />
        <div className="absolute inset-0 rounded-md ring-1 ring-primary/40 animate-pulse opacity-60" />
      </div>
      {withText && (
        <div className="leading-tight">
          <div className="text-sm font-semibold tracking-tight">Sentinel<span className="text-primary"> AI</span></div>
          <div className="font-mono text-[10px] text-muted-foreground tracking-widest">SECURITY · v1.4</div>
        </div>
      )}
    </div>
  );
}
