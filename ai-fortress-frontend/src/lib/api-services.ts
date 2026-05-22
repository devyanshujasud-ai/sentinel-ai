/**
 * Sentinel AI — API Service Layer
 *
 * Typed service functions for every backend endpoint.
 * Each function returns the unwrapped `data` payload.
 */

import { api } from "./api-client";

// ====================================================================
// Types
// ====================================================================
export interface AuthUser {
  id: string;
  email: string;
  username: string;
  full_name?: string;
  role: string;
  is_active: boolean;
  total_scans: number;
  threats_blocked: number;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: AuthUser;
}

export interface ThreatMatch {
  category: string;
  severity: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  confidence: number;
  matched_text: string;
  explanation: string;
}

export interface ScanResult {
  risk_score: number;
  overall_severity: string;
  is_safe: boolean;
  threats_detected: number;
  threat_matches: ThreatMatch[];
  original_prompt: string;
  sanitized_prompt: string;
  target_llm?: string;
}

export interface ScanRecord {
  id: string;
  user_id: string;
  prompt: string;
  target_llm?: string;
  result: ScanResult;
  created_at: string;
}

export interface ScanHistoryResponse {
  scans: ScanRecord[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface DashboardStats {
  total_scans: number;
  threats_detected: number;
  attacks_blocked: number;
  avg_risk_score: number;
  safe_prompts: number;
  unsafe_prompts: number;
}

export interface TopThreat {
  category: string;
  count: number;
  percentage: number;
}

export interface RiskTrendPoint {
  date: string;
  avg_risk_score: number;
  total_scans: number;
  threats_detected: number;
}

export interface DailyStatsPoint {
  date: string;
  scans: number;
  threats: number;
  attacks_blocked: number;
  avg_risk: number;
}

export interface ThreatDefinition {
  id: string;
  category: string;
  name: string;
  description: string;
  severity: string;
  examples: string[];
  weight: number;
  is_active: boolean;
}

// ====================================================================
// Auth Service
// ====================================================================
export const authService = {
  async register(data: {
    email: string;
    username: string;
    password: string;
    full_name?: string;
  }): Promise<AuthResponse> {
    const res = await api.post<AuthResponse>("/auth/register", data);
    return res.data;
  },

  async login(data: { email: string; password: string }): Promise<AuthResponse> {
    const res = await api.post<AuthResponse>("/auth/login", data);
    return res.data;
  },

  async getProfile(): Promise<AuthUser> {
    const res = await api.get<{ status: string; data: AuthUser }>("/auth/profile");
    return res.data.data;
  },
};

// ====================================================================
// Scan Service
// ====================================================================
export const scanService = {
  async scanPrompt(data: {
    prompt: string;
    target_llm?: string;
  }): Promise<ScanRecord> {
    const res = await api.post<{ status: string; data: ScanRecord }>("/scan", data);
    return res.data.data;
  },

  async getScan(scanId: string): Promise<ScanRecord> {
    const res = await api.get<{ status: string; data: ScanRecord }>(`/scan/${scanId}`);
    return res.data.data;
  },

  async getHistory(
    page = 1,
    pageSize = 20,
  ): Promise<ScanHistoryResponse> {
    const res = await api.get<{ status: string; data: ScanHistoryResponse }>(
      "/history",
      { params: { page, page_size: pageSize } },
    );
    return res.data.data;
  },
};

// ====================================================================
// Analytics Service
// ====================================================================
export const analyticsService = {
  async getDashboard(): Promise<DashboardStats> {
    const res = await api.get<{ status: string; data: DashboardStats }>(
      "/analytics/dashboard",
    );
    return res.data.data;
  },

  async getTopThreats(limit = 10): Promise<{ threats: TopThreat[]; total_threats: number }> {
    const res = await api.get<{
      status: string;
      data: { threats: TopThreat[]; total_threats: number };
    }>("/analytics/top-threats", { params: { limit } });
    return res.data.data;
  },

  async getRiskTrends(days = 30): Promise<{ trends: RiskTrendPoint[]; period_days: number }> {
    const res = await api.get<{
      status: string;
      data: { trends: RiskTrendPoint[]; period_days: number };
    }>("/analytics/risk-trends", { params: { days } });
    return res.data.data;
  },

  async getDailyStats(days = 30): Promise<{ stats: DailyStatsPoint[]; period_days: number }> {
    const res = await api.get<{
      status: string;
      data: { stats: DailyStatsPoint[]; period_days: number };
    }>("/analytics/daily-stats", { params: { days } });
    return res.data.data;
  },
};

// ====================================================================
// Threats Service
// ====================================================================
export const threatsService = {
  async getAll(): Promise<{ threats: ThreatDefinition[]; total: number }> {
    const res = await api.get<{
      status: string;
      data: { threats: ThreatDefinition[]; total: number };
    }>("/threats");
    return res.data.data;
  },

  async getByCategory(category: string): Promise<{ threats: ThreatDefinition[]; total: number }> {
    const res = await api.get<{
      status: string;
      data: { threats: ThreatDefinition[]; total: number; category: string };
    }>(`/threats/${category}`);
    return res.data.data;
  },
};
