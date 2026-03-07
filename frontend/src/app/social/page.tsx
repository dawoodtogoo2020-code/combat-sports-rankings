"use client";

import { useState } from "react";

const demoPosts = [
  {
    id: "1",
    author: "Gordon Ryan",
    avatar: "GR",
    type: "result",
    content: "Gold at ADCC 2024! Submitted every opponent. Thank you to my team and coaches at New Wave. Road to 2025 starts now.",
    hashtags: ["#ADCC", "#GoldMedal", "#NoGi"],
    likes: 1243,
    comments: 89,
    timeAgo: "2h ago",
  },
  {
    id: "2",
    author: "Atos Jiu-Jitsu",
    avatar: "AT",
    type: "tournament",
    content: "Incredible performance by our team at the IBJJF Worlds! 8 gold medals across all belt divisions. Proud of every competitor who represented us.",
    hashtags: ["#IBJJF", "#Worlds", "#AtosBJJ"],
    likes: 876,
    comments: 45,
    timeAgo: "5h ago",
  },
  {
    id: "3",
    author: "Mica Galvao",
    avatar: "MG",
    type: "training",
    content: "Back to the grind. Working on new leg lock sequences for the next competition. The journey never stops.",
    hashtags: ["#Training", "#BJJ", "#LegLocks"],
    likes: 654,
    comments: 32,
    timeAgo: "1d ago",
  },
];

const typeIcons: Record<string, string> = {
  result: "Trophy",
  medal: "Medal",
  tournament: "Calendar",
  training: "Dumbbell",
  general: "MessageCircle",
};

export default function SocialPage() {
  const [newPost, setNewPost] = useState("");

  return (
    <div className="mx-auto max-w-2xl px-4 py-8 sm:px-6">
      <h1 className="mb-6 text-3xl font-bold text-slate-900 dark:text-white">Social Feed</h1>

      {/* Compose */}
      <div className="card mb-6">
        <textarea
          value={newPost}
          onChange={(e) => setNewPost(e.target.value)}
          placeholder="Share a competition result, training update, or post..."
          className="input w-full resize-none"
          rows={3}
        />
        <div className="mt-3 flex items-center justify-between">
          <div className="flex gap-2">
            {["Result", "Training", "Tournament"].map((type) => (
              <button key={type} className="btn-secondary px-2 py-1 text-xs">
                {type}
              </button>
            ))}
          </div>
          <button className="btn-primary px-4 py-1.5 text-sm" disabled={!newPost.trim()}>
            Post
          </button>
        </div>
      </div>

      {/* Feed */}
      <div className="space-y-4">
        {demoPosts.map((post) => (
          <div key={post.id} className="card">
            {/* Author */}
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-brand-100 text-sm font-bold text-brand-600 dark:bg-brand-900/30 dark:text-brand-400">
                {post.avatar}
              </div>
              <div className="flex-1">
                <div className="font-semibold text-slate-900 dark:text-white">{post.author}</div>
                <div className="text-xs text-slate-500 dark:text-slate-400">{post.timeAgo}</div>
              </div>
              <span className="badge bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300">
                {post.type}
              </span>
            </div>

            {/* Content */}
            <p className="mt-3 text-sm text-slate-700 dark:text-slate-300">{post.content}</p>

            {/* Hashtags */}
            {post.hashtags && (
              <div className="mt-2 flex flex-wrap gap-1">
                {post.hashtags.map((tag) => (
                  <span key={tag} className="text-xs font-medium text-brand-600 dark:text-brand-400">
                    {tag}
                  </span>
                ))}
              </div>
            )}

            {/* Actions */}
            <div className="mt-4 flex items-center gap-6 border-t border-slate-100 pt-3 dark:border-slate-700">
              <button className="flex items-center gap-1.5 text-sm text-slate-500 hover:text-brand-600 dark:text-slate-400 dark:hover:text-brand-400">
                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                </svg>
                {post.likes}
              </button>
              <button className="flex items-center gap-1.5 text-sm text-slate-500 hover:text-brand-600 dark:text-slate-400 dark:hover:text-brand-400">
                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
                {post.comments}
              </button>
              <button className="flex items-center gap-1.5 text-sm text-slate-500 hover:text-brand-600 dark:text-slate-400 dark:hover:text-brand-400">
                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
                </svg>
                Share
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
