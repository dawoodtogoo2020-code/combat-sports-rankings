"use client";

import { useState, useRef, useCallback } from "react";
import { useAuth } from "@/components/auth/AuthProvider";
import { useApi } from "@/hooks/useApi";
import { admin as adminApi, athletes as athletesApi } from "@/lib/api";
import type { DashboardStats, AthleteListItem } from "@/types/index";
import { SkeletonCard, SkeletonRow } from "@/components/ui/Skeleton";

const tabs = ["Dashboard", "Athletes", "Users", "Import Data", "Audit Log"];

interface AdminUser {
  id: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  created_at: string;
}

interface DataSourceItem {
  id: string;
  name: string;
  slug: string;
  base_url: string | null;
  ingestion_method: string;
  robots_txt_status: string;
  tos_reviewed: boolean;
  is_active: boolean;
  last_sync_at: string | null;
}

interface AuditLogEntry {
  id: string;
  user_name: string;
  action: string;
  target_type: string;
  target_id: string;
  details: Record<string, unknown> | null;
  ip_address: string | null;
  created_at: string;
}

interface AuditLogResponse {
  entries: AuditLogEntry[];
  total_count: number;
  page: number;
  page_size: number;
}

export default function AdminPage() {
  const { user, token, isLoading: authLoading } = useAuth();
  const [activeTab, setActiveTab] = useState("Dashboard");

  if (authLoading) {
    return (
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
        <div className="space-y-4">
          <SkeletonCard />
          <SkeletonCard />
        </div>
      </div>
    );
  }

  if (!user || user.role !== "admin") {
    return (
      <div className="mx-auto max-w-7xl px-4 py-16 sm:px-6">
        <div className="card mx-auto max-w-md py-12 text-center">
          <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-clay-50 dark:bg-clay-900/20">
            <svg className="h-7 w-7 text-clay-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
          </div>
          <h2 className="text-lg font-semibold text-surface-900 dark:text-white">Access Denied</h2>
          <p className="mt-2 text-sm text-surface-500 dark:text-surface-400">
            {user ? "You don\u2019t have admin privileges." : "Please sign in with an admin account."}
          </p>
          {!user && (
            <a href="/auth" className="btn-primary mt-6 inline-flex text-sm">Sign In</a>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-surface-900 dark:text-white">Admin Panel</h1>
        <p className="mt-1 text-surface-500 dark:text-surface-400">Manage athletes, events, and rankings</p>
      </div>

      <div className="scrollbar-none mb-6 -mx-4 overflow-x-auto px-4 sm:mx-0 sm:px-0">
        <div className="flex gap-1 rounded-xl bg-surface-100 p-1 dark:bg-surface-800 sm:inline-flex">
          {tabs.map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`whitespace-nowrap rounded-lg px-4 py-2 text-sm font-medium transition-all ${
                activeTab === tab
                  ? "bg-white text-surface-900 shadow-soft dark:bg-surface-700 dark:text-white"
                  : "text-surface-500 hover:text-surface-900 dark:text-surface-400 dark:hover:text-white"
              }`}
            >
              {tab}
            </button>
          ))}
        </div>
      </div>

      {activeTab === "Dashboard" && <DashboardTab token={token!} />}
      {activeTab === "Athletes" && <AthletesTab token={token!} />}
      {activeTab === "Users" && <UsersTab token={token!} />}
      {activeTab === "Import Data" && <ImportDataTab token={token!} />}
      {activeTab === "Audit Log" && <AuditLogTab token={token!} />}
    </div>
  );
}

/* ─── Dashboard ─── */

function DashboardTab({ token }: { token: string }) {
  const { data, loading } = useApi<DashboardStats>(
    () => adminApi.dashboard(token) as Promise<DashboardStats>,
    [token]
  );

  if (loading) return <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">{Array.from({ length: 6 }).map((_, i) => <SkeletonCard key={i} />)}</div>;
  if (!data) return <div className="card py-8 text-center text-sm text-surface-400">Unable to load dashboard data.</div>;

  const stats = [
    { label: "Total Athletes", value: data.total_athletes.toLocaleString(), icon: "M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" },
    { label: "Total Matches", value: data.total_matches.toLocaleString(), icon: "M13 10V3L4 14h7v7l9-11h-7z" },
    { label: "Total Events", value: data.total_events.toLocaleString(), icon: "M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" },
    { label: "Active Gyms", value: data.total_gyms.toLocaleString(), icon: "M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" },
    { label: "Registered Users", value: data.total_users.toLocaleString(), icon: "M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" },
    { label: "Social Posts", value: data.total_posts.toLocaleString(), icon: "M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" },
  ];

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {stats.map((stat) => (
        <div key={stat.label} className="card">
          <div className="flex items-start justify-between">
            <div>
              <div className="text-sm text-surface-500 dark:text-surface-400">{stat.label}</div>
              <div className="mt-1 text-2xl font-bold text-surface-900 dark:text-white">{stat.value}</div>
            </div>
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary-50 dark:bg-primary-950/40">
              <svg className="h-5 w-5 text-primary-600 dark:text-primary-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d={stat.icon} />
              </svg>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

/* ─── Athletes with Adjust ELO Modal ─── */

function AthletesTab({ token }: { token: string }) {
  const { data, loading, refetch } = useApi<AthleteListItem[]>(
    () => athletesApi.list() as Promise<AthleteListItem[]>,
    []
  );
  const [eloModal, setEloModal] = useState<AthleteListItem | null>(null);
  const [eloValue, setEloValue] = useState("");
  const [eloReason, setEloReason] = useState("");
  const [adjusting, setAdjusting] = useState(false);
  const [adjustResult, setAdjustResult] = useState<string | null>(null);

  const openEloModal = (athlete: AthleteListItem) => {
    setEloModal(athlete);
    setEloValue(String(athlete.elo_rating));
    setEloReason("");
    setAdjustResult(null);
  };

  const handleAdjustElo = async () => {
    if (!eloModal || !eloReason.trim()) return;
    setAdjusting(true);
    try {
      await adminApi.adjustElo(
        eloModal.id,
        { new_rating: parseFloat(eloValue), reason: eloReason },
        token
      );
      setAdjustResult("Rating adjusted successfully");
      refetch();
      setTimeout(() => setEloModal(null), 1200);
    } catch (err) {
      setAdjustResult(err instanceof Error ? err.message : "Failed to adjust rating");
    } finally {
      setAdjusting(false);
    }
  };

  if (loading) return <div className="card space-y-1 p-4">{Array.from({ length: 5 }).map((_, i) => <SkeletonRow key={i} />)}</div>;
  if (!data || data.length === 0) return <div className="card py-8 text-center text-sm text-surface-400">No athletes found.</div>;

  return (
    <>
      <div className="card overflow-hidden p-0">
        <div className="flex items-center justify-between p-5">
          <h2 className="text-lg font-semibold text-surface-900 dark:text-white">Manage Athletes</h2>
        </div>

        <div className="hidden overflow-x-auto md:block">
          <table className="w-full">
            <thead>
              <tr className="border-b border-t border-surface-200/50 bg-surface-50 dark:border-surface-700/30 dark:bg-surface-850">
                <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wider text-surface-500">Name</th>
                <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wider text-surface-500">Rating</th>
                <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wider text-surface-500">Matches</th>
                <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wider text-surface-500">Status</th>
                <th className="px-5 py-3 text-right text-xs font-semibold uppercase tracking-wider text-surface-500">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-surface-100/80 dark:divide-surface-700/30">
              {data.map((a) => (
                <tr key={a.id} className="transition-colors hover:bg-surface-50/50 dark:hover:bg-surface-850/50">
                  <td className="px-5 py-3.5 text-sm font-medium text-surface-900 dark:text-white">{a.display_name}</td>
                  <td className="px-5 py-3.5 font-mono text-sm text-primary-600 dark:text-primary-400">{a.elo_rating}</td>
                  <td className="px-5 py-3.5 text-sm text-surface-500 dark:text-surface-400">{a.total_matches}</td>
                  <td className="px-5 py-3.5">
                    <span className={`badge ${a.is_verified ? "bg-moss-100 text-moss-700 dark:bg-moss-900/30 dark:text-moss-400" : "bg-gold-100 text-gold-700 dark:bg-gold-900/30 dark:text-gold-400"}`}>
                      {a.is_verified ? "Verified" : "Pending"}
                    </span>
                  </td>
                  <td className="px-5 py-3.5 text-right">
                    <button
                      onClick={() => openEloModal(a)}
                      className="btn-secondary px-2.5 py-1 text-xs"
                    >
                      Adjust ELO
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="space-y-2 p-4 md:hidden">
          {data.map((a) => (
            <div key={a.id} className="flex items-center justify-between rounded-xl border border-surface-100 p-3 dark:border-surface-700/30">
              <div>
                <div className="font-medium text-surface-900 dark:text-white">{a.display_name}</div>
                <div className="text-xs text-surface-500">
                  ELO {a.elo_rating} &middot; {a.total_matches} matches
                </div>
              </div>
              <button onClick={() => openEloModal(a)} className="btn-secondary px-2 py-1 text-xs">
                Adjust
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Adjust ELO Modal */}
      {eloModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4" onClick={() => setEloModal(null)}>
          <div className="card w-full max-w-md" onClick={(e) => e.stopPropagation()}>
            <h3 className="text-lg font-semibold text-surface-900 dark:text-white">Adjust ELO Rating</h3>
            <p className="mt-1 text-sm text-surface-500 dark:text-surface-400">{eloModal.display_name}</p>

            <div className="mt-5 space-y-4">
              <div>
                <label className="block text-sm font-medium text-surface-700 dark:text-surface-300">New Rating</label>
                <input
                  type="number"
                  value={eloValue}
                  onChange={(e) => setEloValue(e.target.value)}
                  min={100}
                  max={3000}
                  className="input mt-1.5 w-full"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-surface-700 dark:text-surface-300">Reason</label>
                <input
                  type="text"
                  value={eloReason}
                  onChange={(e) => setEloReason(e.target.value)}
                  placeholder="e.g. Correcting data entry error"
                  className="input mt-1.5 w-full"
                />
              </div>

              {adjustResult && (
                <div className={`text-sm ${adjustResult.includes("success") ? "text-moss-600" : "text-clay-600"}`}>
                  {adjustResult}
                </div>
              )}
            </div>

            <div className="mt-6 flex justify-end gap-3">
              <button onClick={() => setEloModal(null)} className="btn-secondary px-4 py-2 text-sm">Cancel</button>
              <button
                onClick={handleAdjustElo}
                disabled={adjusting || !eloReason.trim()}
                className="btn-primary px-4 py-2 text-sm disabled:opacity-50"
              >
                {adjusting ? "Saving..." : "Confirm"}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

/* ─── Users ─── */

function UsersTab({ token }: { token: string }) {
  const { data, loading } = useApi<AdminUser[]>(
    () => adminApi.users(token) as Promise<AdminUser[]>,
    [token]
  );

  if (loading) return <div className="card space-y-1 p-4">{Array.from({ length: 5 }).map((_, i) => <SkeletonRow key={i} />)}</div>;
  if (!data || data.length === 0) return <div className="card py-8 text-center text-sm text-surface-400">No users found.</div>;

  return (
    <div className="card overflow-hidden p-0">
      <div className="p-5">
        <h2 className="text-lg font-semibold text-surface-900 dark:text-white">Manage Users</h2>
        <p className="mt-1 text-xs text-surface-400">Showing minimum necessary user data only.</p>
      </div>

      <div className="hidden overflow-x-auto md:block">
        <table className="w-full">
          <thead>
            <tr className="border-b border-t border-surface-200/50 bg-surface-50 dark:border-surface-700/30 dark:bg-surface-850">
              <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wider text-surface-500">Name</th>
              <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wider text-surface-500">Email</th>
              <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wider text-surface-500">Role</th>
              <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wider text-surface-500">Status</th>
              <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wider text-surface-500">Joined</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-surface-100/80 dark:divide-surface-700/30">
            {data.map((u) => (
              <tr key={u.id} className="transition-colors hover:bg-surface-50/50 dark:hover:bg-surface-850/50">
                <td className="px-5 py-3.5 text-sm font-medium text-surface-900 dark:text-white">{u.full_name}</td>
                <td className="px-5 py-3.5 text-sm text-surface-500 dark:text-surface-400">{u.email}</td>
                <td className="px-5 py-3.5">
                  <span className="badge bg-primary-50 capitalize text-primary-700 dark:bg-primary-950/30 dark:text-primary-300">{u.role}</span>
                </td>
                <td className="px-5 py-3.5">
                  <span className={`badge ${u.is_active ? "bg-moss-100 text-moss-700 dark:bg-moss-900/30 dark:text-moss-400" : "bg-clay-100 text-clay-700 dark:bg-clay-900/30 dark:text-clay-400"}`}>
                    {u.is_active ? "Active" : "Inactive"}
                  </span>
                </td>
                <td className="px-5 py-3.5 text-sm text-surface-500 dark:text-surface-400">
                  {new Date(u.created_at).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="space-y-2 p-4 md:hidden">
        {data.map((u) => (
          <div key={u.id} className="rounded-xl border border-surface-100 p-3 dark:border-surface-700/30">
            <div className="flex items-center justify-between">
              <div className="font-medium text-surface-900 dark:text-white">{u.full_name}</div>
              <span className="badge bg-primary-50 text-xs capitalize text-primary-700 dark:bg-primary-950/30 dark:text-primary-300">{u.role}</span>
            </div>
            <div className="mt-1 text-xs text-surface-500">{u.email}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ─── Import Data — CSV Upload + Data Sources from API ─── */

function ImportDataTab({ token }: { token: string }) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [importing, setImporting] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<number | null>(null);
  const [importResult, setImportResult] = useState<{ message: string; events_imported: number; matches_imported: number; athletes_created: number } | null>(null);
  const [importError, setImportError] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  const { data: dataSources, loading: sourcesLoading } = useApi<DataSourceItem[]>(
    () => adminApi.dataSources(token) as Promise<DataSourceItem[]>,
    [token]
  );

  const handleImport = useCallback(async (file: File) => {
    if (!file.name.endsWith(".csv")) {
      setImportError("Only CSV files are accepted");
      return;
    }
    setImporting(true);
    setImportResult(null);
    setImportError(null);
    setUploadProgress(0);

    try {
      const result = await adminApi.importCsv(file, token, (pct) => setUploadProgress(pct));
      setImportResult(result);
    } catch (err) {
      setImportError(err instanceof Error ? err.message : "Import failed");
    } finally {
      setImporting(false);
      setUploadProgress(null);
    }
  }, [token]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleImport(file);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file) handleImport(file);
  };

  return (
    <div className="space-y-6">
      {/* CSV Import */}
      <div className="card">
        <h2 className="mb-4 text-lg font-semibold text-surface-900 dark:text-white">CSV Import</h2>
        <p className="mb-4 text-sm text-surface-500 dark:text-surface-400">
          Upload a CSV file with match results. Columns: event_name, event_date, event_tier, winner_first_name, winner_last_name, loser_first_name, loser_last_name, outcome, is_gi, round_name.
        </p>

        <div
          className={`rounded-2xl border-2 border-dashed p-10 text-center transition-colors ${
            isDragging
              ? "border-primary-400 bg-primary-50/30 dark:border-primary-600 dark:bg-primary-950/20"
              : "border-surface-200 hover:border-primary-300 dark:border-surface-600 dark:hover:border-primary-700"
          }`}
          onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          role="button"
          tabIndex={0}
        >
          <svg className="mx-auto h-12 w-12 text-surface-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
          <p className="mt-3 text-sm text-surface-500 dark:text-surface-400">
            {importing ? "Importing..." : "Drag and drop a CSV file, or click to browse"}
          </p>

          {uploadProgress !== null && (
            <div className="mx-auto mt-4 max-w-xs">
              <div className="h-1.5 w-full overflow-hidden rounded-full bg-surface-100 dark:bg-surface-700">
                <div className="h-full rounded-full bg-primary-500 transition-all" style={{ width: `${uploadProgress}%` }} />
              </div>
              <p className="mt-1 text-xs text-surface-400">{uploadProgress}%</p>
            </div>
          )}

          <input ref={fileInputRef} type="file" accept=".csv" onChange={handleFileChange} className="hidden" />
        </div>

        {importResult && (
          <div className="mt-4 rounded-xl border border-moss-200 bg-moss-50 p-4 dark:border-moss-800/50 dark:bg-moss-900/20">
            <div className="font-medium text-moss-700 dark:text-moss-400">Import Successful</div>
            <div className="mt-1 text-sm text-moss-600 dark:text-moss-400/80">
              {importResult.events_imported} events, {importResult.matches_imported} matches, {importResult.athletes_created} new athletes
            </div>
          </div>
        )}

        {importError && (
          <div className="mt-4 rounded-xl border border-clay-200 bg-clay-50 p-4 dark:border-clay-800/50 dark:bg-clay-900/20">
            <div className="text-sm text-clay-700 dark:text-clay-400">{importError}</div>
          </div>
        )}
      </div>

      {/* Data Sources — from backend API */}
      <div className="card">
        <h2 className="mb-4 text-lg font-semibold text-surface-900 dark:text-white">Data Sources</h2>
        <p className="mb-4 text-xs text-surface-400">
          Sources require review before enabling. Compliance with robots.txt and terms of service is verified per source.
        </p>

        {sourcesLoading ? (
          <div className="space-y-2">{Array.from({ length: 4 }).map((_, i) => <SkeletonRow key={i} />)}</div>
        ) : dataSources && dataSources.length > 0 ? (
          <div className="space-y-3">
            {dataSources.map((source) => (
              <div key={source.id} className="flex items-center justify-between rounded-xl border border-surface-100 p-4 dark:border-surface-700/30">
                <div>
                  <div className="font-medium text-surface-900 dark:text-white">{source.name}</div>
                  <div className="text-xs text-surface-500 dark:text-surface-400">
                    Method: {source.ingestion_method}
                    {source.base_url && <> &middot; {source.base_url}</>}
                  </div>
                  <div className="mt-1 flex items-center gap-2 text-xs">
                    <span className={source.tos_reviewed ? "text-moss-600 dark:text-moss-400" : "text-gold-600 dark:text-gold-400"}>
                      ToS: {source.tos_reviewed ? "Reviewed" : "Pending"}
                    </span>
                    <span className="text-surface-300 dark:text-surface-600">|</span>
                    <span className={`${
                      source.robots_txt_status === "allowed" ? "text-moss-600 dark:text-moss-400" :
                      source.robots_txt_status === "disallowed" ? "text-clay-600 dark:text-clay-400" :
                      "text-surface-400"
                    }`}>
                      robots.txt: {source.robots_txt_status}
                    </span>
                  </div>
                </div>
                <span className={`badge text-xs ${
                  source.is_active
                    ? "bg-moss-100 text-moss-700 dark:bg-moss-900/30 dark:text-moss-400"
                    : "bg-surface-100 text-surface-600 dark:bg-surface-800 dark:text-surface-300"
                }`}>
                  {source.is_active ? "Active" : "Inactive"}
                </span>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-surface-400">No data sources configured.</p>
        )}
      </div>
    </div>
  );
}

/* ─── Audit Log ─── */

function AuditLogTab({ token }: { token: string }) {
  const [page, setPage] = useState(1);
  const { data, loading } = useApi<AuditLogResponse>(
    () => adminApi.auditLog(token, { page: String(page), page_size: "25" }) as Promise<AuditLogResponse>,
    [token, page]
  );

  const entries = data?.entries ?? [];
  const totalPages = Math.ceil((data?.total_count ?? 0) / 25);

  if (loading) return <div className="card space-y-1 p-4">{Array.from({ length: 5 }).map((_, i) => <SkeletonRow key={i} />)}</div>;
  if (entries.length === 0) return <div className="card py-8 text-center text-sm text-surface-400">No audit log entries.</div>;

  return (
    <div className="card overflow-hidden p-0">
      <div className="p-5">
        <h2 className="text-lg font-semibold text-surface-900 dark:text-white">Audit Log</h2>
        <p className="mt-1 text-xs text-surface-400">All admin actions are logged with timestamps and IP addresses.</p>
      </div>

      {/* Desktop table */}
      <div className="hidden overflow-x-auto md:block">
        <table className="w-full">
          <thead>
            <tr className="border-b border-t border-surface-200/50 bg-surface-50 dark:border-surface-700/30 dark:bg-surface-850">
              <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wider text-surface-500">When</th>
              <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wider text-surface-500">User</th>
              <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wider text-surface-500">Action</th>
              <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wider text-surface-500">Target</th>
              <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wider text-surface-500">Details</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-surface-100/80 dark:divide-surface-700/30">
            {entries.map((entry) => (
              <tr key={entry.id} className="transition-colors hover:bg-surface-50/50 dark:hover:bg-surface-850/50">
                <td className="px-5 py-3 text-xs text-surface-500 dark:text-surface-400 whitespace-nowrap">
                  {new Date(entry.created_at).toLocaleDateString("en-US", { month: "short", day: "numeric" })}{" "}
                  {new Date(entry.created_at).toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" })}
                </td>
                <td className="px-5 py-3 text-sm text-surface-900 dark:text-white">{entry.user_name}</td>
                <td className="px-5 py-3">
                  <span className="badge bg-primary-50 text-xs text-primary-700 dark:bg-primary-950/30 dark:text-primary-300">
                    {entry.action}
                  </span>
                </td>
                <td className="px-5 py-3 text-xs text-surface-500 dark:text-surface-400">
                  {entry.target_type}/{entry.target_id.slice(0, 8)}
                </td>
                <td className="px-5 py-3 text-xs text-surface-500 dark:text-surface-400 max-w-[200px] truncate">
                  {entry.details ? JSON.stringify(entry.details) : "—"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Mobile cards */}
      <div className="space-y-2 p-4 md:hidden">
        {entries.map((entry) => (
          <div key={entry.id} className="rounded-xl border border-surface-100 p-3 dark:border-surface-700/30">
            <div className="flex items-center justify-between">
              <span className="badge bg-primary-50 text-xs text-primary-700 dark:bg-primary-950/30 dark:text-primary-300">{entry.action}</span>
              <span className="text-xs text-surface-400">
                {new Date(entry.created_at).toLocaleDateString("en-US", { month: "short", day: "numeric" })}
              </span>
            </div>
            <div className="mt-1 text-sm text-surface-900 dark:text-white">{entry.user_name}</div>
            <div className="text-xs text-surface-500">{entry.target_type}/{entry.target_id.slice(0, 8)}</div>
          </div>
        ))}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between border-t border-surface-200/50 px-5 py-3 dark:border-surface-700/30">
          <span className="text-sm text-surface-500">Page {page} of {totalPages}</span>
          <div className="flex gap-1">
            <button onClick={() => setPage(Math.max(1, page - 1))} disabled={page === 1} className="btn-secondary px-3 py-1.5 text-xs disabled:opacity-40">Prev</button>
            <button onClick={() => setPage(Math.min(totalPages, page + 1))} disabled={page >= totalPages} className="btn-secondary px-3 py-1.5 text-xs disabled:opacity-40">Next</button>
          </div>
        </div>
      )}
    </div>
  );
}
