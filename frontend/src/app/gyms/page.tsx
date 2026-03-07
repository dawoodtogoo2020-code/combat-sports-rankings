"use client";

import { useState } from "react";
import Link from "next/link";

const demoGyms = [
  { id: "1", name: "New Wave Jiu-Jitsu", city: "Austin", country: "US", members: 45, avgRating: 1680, verified: true },
  { id: "2", name: "Atos Jiu-Jitsu", city: "San Diego", country: "US", members: 120, avgRating: 1620, verified: true },
  { id: "3", name: "Alliance BJJ", city: "Atlanta", country: "US", members: 200, avgRating: 1590, verified: true },
  { id: "4", name: "Gracie Barra HQ", city: "Rio de Janeiro", country: "BR", members: 180, avgRating: 1570, verified: true },
  { id: "5", name: "Renzo Gracie Academy", city: "New York", country: "US", members: 150, avgRating: 1560, verified: true },
  { id: "6", name: "Dream Art BJJ", city: "Sao Paulo", country: "BR", members: 80, avgRating: 1640, verified: true },
];

export default function GymsPage() {
  const [search, setSearch] = useState("");

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white">Gyms</h1>
          <p className="mt-1 text-slate-600 dark:text-slate-400">Combat sports academies and training centers</p>
        </div>
        <input
          type="text"
          placeholder="Search gyms..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="input w-full sm:w-72"
        />
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {demoGyms
          .filter((g) => g.name.toLowerCase().includes(search.toLowerCase()))
          .map((gym) => (
            <Link
              key={gym.id}
              href={`/gyms/${gym.id}`}
              className="card group transition-shadow hover:shadow-md"
            >
              <div className="flex items-start gap-3">
                <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-brand-100 text-lg font-bold text-brand-600 dark:bg-brand-900/30 dark:text-brand-400">
                  {gym.name[0]}
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <h3 className="font-semibold text-slate-900 group-hover:text-brand-600 dark:text-white dark:group-hover:text-brand-400">
                      {gym.name}
                    </h3>
                    {gym.verified && (
                      <svg className="h-4 w-4 text-brand-500" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                    )}
                  </div>
                  <p className="text-sm text-slate-500 dark:text-slate-400">
                    {gym.city}, {gym.country}
                  </p>
                </div>
              </div>
              <div className="mt-4 grid grid-cols-2 gap-4 border-t border-slate-100 pt-4 dark:border-slate-700">
                <div className="text-center">
                  <div className="text-lg font-bold text-slate-900 dark:text-white">{gym.members}</div>
                  <div className="text-xs text-slate-500 dark:text-slate-400">Members</div>
                </div>
                <div className="text-center">
                  <div className="font-mono text-lg font-bold text-brand-600 dark:text-brand-400">{gym.avgRating}</div>
                  <div className="text-xs text-slate-500 dark:text-slate-400">Avg Rating</div>
                </div>
              </div>
            </Link>
          ))}
      </div>
    </div>
  );
}
