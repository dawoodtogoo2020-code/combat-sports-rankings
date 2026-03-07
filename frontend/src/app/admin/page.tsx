"use client";

import { useState } from "react";

const tabs = ["Dashboard", "Athletes", "Events", "Gyms", "Users", "Import Data"];

export default function AdminPage() {
  const [activeTab, setActiveTab] = useState("Dashboard");

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white">Admin Panel</h1>
          <p className="mt-1 text-slate-600 dark:text-slate-400">Manage athletes, events, and rankings</p>
        </div>
        <button className="btn-primary">Recalculate All Rankings</button>
      </div>

      {/* Tabs */}
      <div className="mb-6 flex flex-wrap gap-1 rounded-lg bg-slate-100 p-1 dark:bg-surface-800">
        {tabs.map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`rounded-md px-4 py-2 text-sm font-medium transition-colors ${
              activeTab === tab
                ? "bg-white text-slate-900 shadow-sm dark:bg-surface-700 dark:text-white"
                : "text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white"
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Dashboard */}
      {activeTab === "Dashboard" && (
        <div>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {[
              { label: "Total Athletes", value: "12,847", change: "+124 this month" },
              { label: "Total Matches", value: "85,234", change: "+1,847 this month" },
              { label: "Total Events", value: "2,431", change: "+42 this month" },
              { label: "Active Gyms", value: "856", change: "+18 this month" },
              { label: "Registered Users", value: "34,521", change: "+2,100 this month" },
              { label: "Social Posts", value: "8,734", change: "+312 this month" },
            ].map((stat) => (
              <div key={stat.label} className="card">
                <div className="text-sm text-slate-600 dark:text-slate-400">{stat.label}</div>
                <div className="mt-1 text-2xl font-bold text-slate-900 dark:text-white">{stat.value}</div>
                <div className="mt-1 text-xs text-emerald-600 dark:text-emerald-400">{stat.change}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Athletes Management */}
      {activeTab === "Athletes" && (
        <div className="card">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-slate-900 dark:text-white">Manage Athletes</h2>
            <button className="btn-primary text-sm">Add Athlete</button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-200 dark:border-slate-700">
                  <th className="pb-2 text-left text-xs font-semibold uppercase text-slate-500">Name</th>
                  <th className="pb-2 text-left text-xs font-semibold uppercase text-slate-500">Rating</th>
                  <th className="pb-2 text-left text-xs font-semibold uppercase text-slate-500">Matches</th>
                  <th className="pb-2 text-left text-xs font-semibold uppercase text-slate-500">Status</th>
                  <th className="pb-2 text-right text-xs font-semibold uppercase text-slate-500">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
                {[
                  { name: "Gordon Ryan", rating: 2145, matches: 48, verified: true },
                  { name: "Andre Galvao", rating: 2098, matches: 62, verified: true },
                  { name: "Felipe Pena", rating: 2067, matches: 55, verified: true },
                ].map((a) => (
                  <tr key={a.name}>
                    <td className="py-3 text-sm font-medium text-slate-900 dark:text-white">{a.name}</td>
                    <td className="py-3 font-mono text-sm text-brand-600 dark:text-brand-400">{a.rating}</td>
                    <td className="py-3 text-sm text-slate-600 dark:text-slate-400">{a.matches}</td>
                    <td className="py-3">
                      <span className={`badge ${a.verified ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400" : "bg-amber-100 text-amber-700"}`}>
                        {a.verified ? "Verified" : "Pending"}
                      </span>
                    </td>
                    <td className="py-3 text-right">
                      <div className="flex justify-end gap-2">
                        <button className="btn-secondary px-2 py-1 text-xs">Edit</button>
                        <button className="btn-secondary px-2 py-1 text-xs">Adjust ELO</button>
                        <button className="btn px-2 py-1 text-xs text-red-600 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-900/20">Delete</button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Import Data */}
      {activeTab === "Import Data" && (
        <div className="space-y-6">
          <div className="card">
            <h2 className="mb-4 text-lg font-semibold text-slate-900 dark:text-white">CSV Import</h2>
            <p className="mb-4 text-sm text-slate-600 dark:text-slate-400">
              Upload a CSV file with match results to import into the system.
            </p>
            <div className="rounded-lg border-2 border-dashed border-slate-300 p-8 text-center dark:border-slate-600">
              <svg className="mx-auto h-12 w-12 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">
                Drag and drop a CSV file, or click to browse
              </p>
              <button className="btn-primary mt-4 text-sm">Upload CSV</button>
            </div>
          </div>

          <div className="card">
            <h2 className="mb-4 text-lg font-semibold text-slate-900 dark:text-white">Data Sources</h2>
            <div className="space-y-3">
              {[
                { name: "SmoothComp", status: "Ready", lastSync: "2 hours ago" },
                { name: "AJP Tour", status: "Ready", lastSync: "1 day ago" },
                { name: "IBJJF Results", status: "Pending Setup", lastSync: "Never" },
                { name: "Grappling Industries", status: "Ready", lastSync: "3 hours ago" },
              ].map((source) => (
                <div key={source.name} className="flex items-center justify-between rounded-lg border border-slate-100 p-3 dark:border-slate-700">
                  <div>
                    <div className="font-medium text-slate-900 dark:text-white">{source.name}</div>
                    <div className="text-xs text-slate-500">Last sync: {source.lastSync}</div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className={`badge ${source.status === "Ready" ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400" : "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400"}`}>
                      {source.status}
                    </span>
                    <button className="btn-secondary px-3 py-1 text-xs">Sync Now</button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Placeholder for other tabs */}
      {activeTab === "Events" && (
        <div className="card">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-white">Manage Events</h2>
          <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">Create, edit, and manage competition events.</p>
        </div>
      )}
      {activeTab === "Gyms" && (
        <div className="card">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-white">Manage Gyms</h2>
          <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">Approve and manage gym registrations.</p>
        </div>
      )}
      {activeTab === "Users" && (
        <div className="card">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-white">Manage Users</h2>
          <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">View and manage user accounts and roles.</p>
        </div>
      )}
    </div>
  );
}
