import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { Topbar } from "@/components/app/Topbar";
import { SeverityBadge } from "./_app.scanner";
import { Download, ChevronLeft, ChevronRight, Search, Loader2 } from "lucide-react";
import { scanService, type ScanRecord } from "@/lib/api-services";
import { extractError } from "@/lib/api-client";

export const Route = createFileRoute("/_app/history")({
  component: History,
});

function History() {
  const [scans, setScans] = useState<ScanRecord[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(10);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");

  const loadHistory = async (targetPage: number) => {
    setLoading(true);
    setError(null);
    try {
      const data = await scanService.getHistory(targetPage, pageSize);
      setScans(data.scans);
      setTotal(data.total);
      setTotalPages(data.total_pages);
      setPage(data.page);
    } catch (err) {
      setError(extractError(err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHistory(page);
  }, [page]);

  const handleExportCSV = () => {
    if (scans.length === 0) return;
    const headers = ["ID", "Timestamp", "Target LLM", "Risk Score", "Severity", "Safe", "Prompt", "Sanitized Prompt"];
    const rows = scans.map((s) => [
      s.id,
      s.created_at,
      s.target_llm || "N/A",
      s.result.risk_score,
      s.result.overall_severity,
      s.result.is_safe ? "Yes" : "No",
      `"${s.prompt.replace(/"/g, '""')}"`,
      `"${s.result.sanitized_prompt.replace(/"/g, '""')}"`,
    ]);
    const csvContent = [headers.join(","), ...rows.map((e) => e.join(","))].join("\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `sentinel_scan_history_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Client-side search filtering as the backend doesn't have search query parameters yet
  const filteredScans = scans.filter((s) => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      s.id.toLowerCase().includes(query) ||
      (s.target_llm || "").toLowerCase().includes(query) ||
      s.prompt.toLowerCase().includes(query) ||
      s.result.overall_severity.toLowerCase().includes(query)
    );
  });

  return (
    <div>
      <Topbar title="Scan History" subtitle={`${total.toLocaleString()} events total`} />
      <div className="p-6 space-y-4">
        <div className="rounded-2xl glass p-3 flex flex-wrap items-center gap-2">
          <div className="flex items-center gap-2 rounded-lg border border-border/70 bg-surface/60 px-3 py-1.5 flex-1 min-w-[220px]">
            <Search className="h-3.5 w-3.5 text-muted-foreground" />
            <input
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Filter current page by ID, target, severity or content…"
              className="bg-transparent text-xs outline-none flex-1 placeholder:text-muted-foreground"
            />
          </div>
          <button
            onClick={handleExportCSV}
            disabled={scans.length === 0}
            className="inline-flex items-center gap-1.5 rounded-lg bg-primary text-primary-foreground px-3 py-1.5 text-xs font-medium hover:opacity-90 disabled:opacity-50"
          >
            <Download className="h-3.5 w-3.5" /> Export CSV
          </button>
        </div>

        {error && (
          <div className="rounded-lg border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
            {error}
          </div>
        )}

        <div className="rounded-2xl glass overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-surface-2/40 text-left">
                <tr className="text-[11px] font-mono tracking-widest text-muted-foreground">
                  {["ID", "Timestamp", "Target LLM", "Severity", "Score", "Safe Status", "Prompt snippet"].map((h) => (
                    <th key={h} className="px-4 py-3 font-medium">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr>
                    <td colSpan={7} className="px-4 py-10 text-center">
                      <div className="flex items-center justify-center gap-2 text-muted-foreground">
                        <Loader2 className="h-4 w-4 animate-spin text-primary" />
                        <span>Loading scan history…</span>
                      </div>
                    </td>
                  </tr>
                ) : filteredScans.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="px-4 py-10 text-center text-muted-foreground text-sm">
                      No scan events found on this page.
                    </td>
                  </tr>
                ) : (
                  filteredScans.map((r) => (
                    <tr key={r.id} className="border-t border-border/60 hover:bg-primary/[0.03] transition-colors">
                      <td className="px-4 py-3 font-mono text-xs text-primary">{r.id}</td>
                      <td className="px-4 py-3 font-mono text-xs text-muted-foreground">
                        {new Date(r.created_at).toLocaleString()}
                      </td>
                      <td className="px-4 py-3 font-mono text-xs capitalize">{r.target_llm || "General"}</td>
                      <td className="px-4 py-3">
                        <SeverityBadge severity={r.result.overall_severity} />
                      </td>
                      <td className="px-4 py-3 font-mono">{r.result.risk_score}</td>
                      <td className="px-4 py-3">
                        <span className={`text-xs ${r.result.is_safe ? "text-success" : "text-destructive"}`}>
                          {r.result.is_safe ? "Allowed" : "Sanitized"}
                        </span>
                      </td>
                      <td className="px-4 py-3 font-mono text-xs text-muted-foreground max-w-xs truncate">
                        {r.prompt}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
          <div className="flex items-center justify-between border-t border-border/60 px-4 py-3 text-xs text-muted-foreground">
            <span>Page {page} of {totalPages} (Total scans: {total})</span>
            <div className="flex items-center gap-1">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1 || loading}
                className="rounded-md border border-border/70 px-2 py-1 disabled:opacity-40 hover:bg-surface-2/60"
              >
                <ChevronLeft className="h-3.5 w-3.5" />
              </button>
              <button
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page >= totalPages || loading}
                className="rounded-md border border-border/70 px-2 py-1 disabled:opacity-40 hover:bg-surface-2/60"
              >
                <ChevronRight className="h-3.5 w-3.5" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
