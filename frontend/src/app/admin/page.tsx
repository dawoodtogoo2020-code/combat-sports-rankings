"use client";

import { useState } from "react";

const tabs = ["Dashboard", "Athletes", "Events", "Gyms", "Users", "Import Data"];

export default function AdminPage() {
  const [activeTab, setActiveTab] = useState("Dashboard");

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-surface-900 dark:text-white">Admin Panel</h1>
          <p className="mt-1 text-surface-500 dark:text-surface-400">Manage athletes, events, and rankings</p>
        </div>
        <button className="btn-primary">Recalculate All Rankings</button>
      </div>

      {/* Tabs */}
      <div className="mb-6 flex flex-wrap gap-1 rounded-xl bg-surface-100 p-1 dark:bg-surface-800">
        {tabs.map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`rounded-lg px-4 py-2 text-sm font-medium transition-all ${
              activeTab === tab
                ? "bg-white text-surface-900 shadow-soft dark:bg-surface-700 dark:text-white"
                : "text-surface-500 hover:text-surface-900 dark:text-surface-400 dark:hover:text-white"
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
              { label: "Total Athletes", value: "12,847", change: "+124 this month", icon: "M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" },
              { label: "Total Matches", value: "85,234", change: "+1,847 this month", icon: "M13 10V3L4 14h7v7l9-11h-7z" },
              { label: "Total Events", value: "2,431", change: "+42 this month", icon: "M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" },
              { label: "Active Gyms", value: "856", change: "+18 this month", icon: "M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" },
              { label: "Registered Users", value: "34,521", change: "+2,100 this month", icon: "M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" },
              { label: "Social Posts", value: "8,734", change: "+312 this month", icon: "M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" },
            ].map((stat) => (
              <div key={stat.label} className="card">
                <div className="flex items-start justify-between">
                  <div>
                    <div className="text-sm text-surface-500 dark:text-surface-400">{stat.label}</div>
                    <div className="mt-1 text-2xl font-bold text-surface-900 dark:text-white">{stat.value}</div>
                    <div className="mt-1 text-xs font-medium text-moss-600 dark:text-moss-400">{stat.change}</div>
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
        </div>
      )}

      {/* Athletes Management */}
      {activeTab === "Athletes" && (
        <div className="card overflow-hidden p-0">
          <div className="flex items-center justify-between p-5">
            <h2 className="text-lg font-semibold text-surface-900 dark:text-white">Manage Athletes</h2>
            <button className="btn-primary text-sm">Add Athlete</button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-t border-surface-200/50 bg-surface-50 dark:border-surface-700/30 dark:bg-surface-850">
                  <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wider text-surface-500 dark:text-surface-400">Name</th>
                  <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wider text-surface-500 dark:text-surface-400">Rating</th>
                  <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wider text-surface-500 dark:text-surface-400">Matches</th>
                  <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wider text-surface-500 dark:text-surface-400">Status</th>
                  <th className="px-5 py-3 text-right text-xs font-semibold uppercase tracking-wider text-surface-500 dark:text-surface-400">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-surface-100/80 dark:divide-surface-700/30">
                {[
                  { name: "Gordon Ryan", rating: 2145, matches: 48, verified: true },
                  { name: "Andre Galvao", rating: 2098, matches: 62, verified: true },
                  { name: "Felipe Pena", rating: 2067, matches: 55, verified: true },
                ].map((a) => (
                  <tr key={a.name} className="transition-colors hover:bg-surface-50/50 dark:hover:bg-surface-850/50">
                    <td className="px-5 py-3.5 text-sm font-medium text-surface-900 dark:text-white">{a.name}</td>
                    <td className="px-5 py-3.5 font-mono text-sm text-primary-600 dark:text-primary-400">{a.rating}</td>
                    <td className="px-5 py-3.5 text-sm text-surface-500 dark:text-surface-400">{a.matches}</td>
                    <td className="px-5 py-3.5">
                      <span className={`badge ${a.verified ? "bg-moss-100 text-moss-700 dark:bg-moss-900/30 dark:text-moss-400" : "bg-gold-100 text-gold-700 dark:bg-gold-900/30 dark:text-gold-400"}`}>
                        {a.verified ? "Verified" : "Pending"}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 text-right">
                      <div className="flex justify-end gap-2">
                        <button className="btn-secondary px-2.5 py-1 text-xs">Edit</button>
                        <button className="btn-secondary px-2.5 py-1 text-xs">Adjust ELO</button>
                        <button className="rounded-lg px-2.5 py-1 text-xs font-medium text-clay-600 transition-colors hover:bg-clay-50 dark:text-clay-400 dark:hover:bg-clay-900/20">Delete</button>
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
            <h2 className="mb-4 text-lg font-semibold text-surface-900 dark:text-white">CSV Import</h2>
            <p className="mb-4 text-sm text-surface-500 dark:text-surface-400">
              Upload a CSV file with match results to import into the system.
            </p>
            <div className="rounded-2xl border-2 border-dashed border-surface-200 p-10 text-center transition-colors hover:border-primary-300 dark:border-surface-600 dark:hover:border-primary-700">
              <svg className="mx-auto h-12 w-12 text-surface-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              <p className="mt-3 text-sm text-surface-500 dark:text-surface-400">
                Drag and drop a CSV file, or click to browse
              </p>
              <button className="btn-primary mt-4 text-sm">Upload CSV</button>
            </div>
          </div>

          <div className="card">
            <h2 className="mb-4 text-lg font-semibold text-surface-900 dark:text-white">Data Sources</h2>
            <div className="space-y-3">
              {[
                { name: "SmoothComp", status: "Ready", lastSync: "2 hours ago" },
                { name: "AJP Tour", status: "Ready", lastSync: "1 day ago" },
                { name: "IBJJF Results", status: "Pending Setup", lastSync: "Never" },
                { name: "Grappling Industries", status: "Ready", lastSync: "3 hours ago" },
              ].map((source) => (
                <div key={source.name} className="flex items-center justify-between rounded-xl border border-surface-100 p-4 transition-colors hover:bg-surface-50 dark:border-surface-700/30 dark:hover:bg-surface-850/50">
                  <div>
                    <div className="font-medium text-surface-900 dark:text-white">{source.name}</div>
                    <div className="text-xs text-surface-500 dark:text-surface-400">Last sync: {source.lastSync}</div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className={`badge ${source.status === "Ready" ? "bg-moss-100 text-moss-700 dark:bg-moss-900/30 dark:text-moss-400" : "bg-gold-100 text-gold-700 dark:bg-gold-900/30 dark:text-gold-400"}`}>
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

      {/* Placeholder tabs */}
      {activeTab === "Events" && (
        <div className="card py-12 text-center">
          <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-surface-100 dark:bg-surface-800">
            <svg className="h-7 w-7 text-surface-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
          <h2 className="text-lg font-semibold text-surface-900 dark:text-white">Manage Events</h2>
          <p className="mt-2 text-sm text-surface-500 dark:text-surface-400">Create, edit, and manage competition events.</p>
        </div>
      )}
      {activeTab === "Gyms" && (
        <div className="card py-12 text-center">
          <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-surface-100 dark:bg-surface-800">
            <svg className="h-7 w-7 text-surface-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
          </div>
          <h2 className="text-lg font-semibold text-surface-900 dark:text-white">Manage Gyms</h2>
          <p className="mt-2 text-sm text-surface-500 dark:text-surface-400">Approve and manage gym registrations.</p>
        </div>
      )}
      {activeTab === "Users" && (
        <div className="card py-12 text-center">
          <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-surface-100 dark:bg-surface-800">
            <svg className="h-7 w-7 text-surface-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
          </div>
          <h2 className="text-lg font-semibold text-surface-900 dark:text-white">Manage Users</h2>
          <p className="mt-2 text-sm text-surface-500 dark:text-surface-400">View and manage user accounts and roles.</p>
        </div>
      )}
    </div>
  );
}
