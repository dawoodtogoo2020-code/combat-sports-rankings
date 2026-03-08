"use client";

import { useState, useRef } from "react";
import { useApi } from "@/hooks/useApi";
import { useAuth } from "@/components/auth/AuthProvider";
import { social } from "@/lib/api";
import type { Post } from "@/types/index";
import { SkeletonCard } from "@/components/ui/Skeleton";
import { EmptyState, SocialIcon } from "@/components/ui/EmptyState";

const typeBadgeStyles: Record<string, string> = {
  result: "bg-gold-100 text-gold-700 dark:bg-gold-900/30 dark:text-gold-400",
  tournament: "bg-primary-50 text-primary-700 dark:bg-primary-950/30 dark:text-primary-300",
  training: "bg-moss-100 text-moss-700 dark:bg-moss-900/30 dark:text-moss-400",
  general: "bg-surface-100 text-surface-600 dark:bg-surface-800 dark:text-surface-300",
};

const ACCEPTED_IMAGE = "image/jpeg,image/png,image/webp,image/gif";
const ACCEPTED_VIDEO = "video/mp4,video/quicktime";
const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB

export default function SocialPage() {
  const { user, token } = useAuth();
  const [newPost, setNewPost] = useState("");
  const [postType, setPostType] = useState("general");
  const [mediaFiles, setMediaFiles] = useState<File[]>([]);
  const [mediaPreviews, setMediaPreviews] = useState<string[]>([]);
  const [posting, setPosting] = useState(false);
  const [postError, setPostError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const { data: posts, loading, refetch } = useApi<Post[]>(
    () => social.feed() as Promise<Post[]>,
    []
  );

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    const valid = files.filter((f) => {
      if (f.size > MAX_FILE_SIZE) return false;
      return f.type.startsWith("image/") || f.type.startsWith("video/");
    });

    if (valid.length === 0) return;

    setMediaFiles((prev) => [...prev, ...valid]);
    valid.forEach((file) => {
      if (file.type.startsWith("image/")) {
        const reader = new FileReader();
        reader.onload = (e) => {
          setMediaPreviews((prev) => [...prev, e.target?.result as string]);
        };
        reader.readAsDataURL(file);
      } else {
        setMediaPreviews((prev) => [...prev, "video"]);
      }
    });

    // Reset input
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const removeMedia = (index: number) => {
    setMediaFiles((prev) => prev.filter((_, i) => i !== index));
    setMediaPreviews((prev) => prev.filter((_, i) => i !== index));
  };

  const handlePost = async () => {
    if (!newPost.trim() || !token) return;
    setPosting(true);
    setPostError(null);

    try {
      // Extract hashtags from content
      const hashtags = newPost.match(/#\w+/g) || [];

      await social.createPost(
        {
          content: newPost,
          post_type: postType,
          hashtags,
          media_urls: [], // Media upload would go through a separate upload endpoint
        },
        token
      );
      setNewPost("");
      setPostType("general");
      setMediaFiles([]);
      setMediaPreviews([]);
      refetch();
    } catch (err) {
      setPostError(err instanceof Error ? err.message : "Failed to create post");
    } finally {
      setPosting(false);
    }
  };

  const handleLike = async (postId: string) => {
    if (!token) return;
    try {
      await social.toggleLike(postId, token);
      refetch();
    } catch {
      // Silently fail — user sees no change
    }
  };

  return (
    <div className="mx-auto max-w-2xl px-4 py-8 sm:px-6">
      <h1 className="mb-6 text-3xl font-bold text-surface-900 dark:text-white">Social Feed</h1>

      {/* Compose — only shown to authenticated users */}
      {user ? (
        <div className="card mb-6">
          <textarea
            value={newPost}
            onChange={(e) => setNewPost(e.target.value)}
            placeholder="Share a competition result, training update, or post..."
            className="input w-full resize-none"
            rows={3}
          />

          {/* Media previews */}
          {mediaPreviews.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-2">
              {mediaPreviews.map((preview, i) => (
                <div key={i} className="group relative">
                  {preview === "video" ? (
                    <div className="flex h-20 w-20 items-center justify-center rounded-lg bg-surface-100 dark:bg-surface-700">
                      <svg className="h-8 w-8 text-surface-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                      </svg>
                    </div>
                  ) : (
                    <img src={preview} alt="" className="h-20 w-20 rounded-lg object-cover" />
                  )}
                  <button
                    onClick={() => removeMedia(i)}
                    className="absolute -right-1 -top-1 flex h-5 w-5 items-center justify-center rounded-full bg-clay-500 text-white opacity-0 transition-opacity group-hover:opacity-100"
                  >
                    <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              ))}
            </div>
          )}

          {postError && (
            <div className="mt-2 text-sm text-clay-600 dark:text-clay-400">{postError}</div>
          )}

          <div className="mt-3 flex items-center justify-between">
            <div className="flex items-center gap-2">
              {["general", "result", "training", "tournament"].map((type) => (
                <button
                  key={type}
                  onClick={() => setPostType(type)}
                  className={`rounded-full px-3 py-1 text-xs font-medium capitalize transition-all ${
                    postType === type
                      ? "bg-primary-100 text-primary-700 dark:bg-primary-950/40 dark:text-primary-300"
                      : "bg-surface-100 text-surface-500 hover:bg-surface-200 dark:bg-surface-800 dark:text-surface-400 dark:hover:bg-surface-700"
                  }`}
                >
                  {type}
                </button>
              ))}
              {/* Media upload button */}
              <button
                onClick={() => fileInputRef.current?.click()}
                className="rounded-full p-1.5 text-surface-400 transition-colors hover:bg-surface-100 hover:text-surface-600 dark:hover:bg-surface-700 dark:hover:text-surface-300"
                title="Add media"
              >
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </button>
              <input
                ref={fileInputRef}
                type="file"
                accept={`${ACCEPTED_IMAGE},${ACCEPTED_VIDEO}`}
                multiple
                onChange={handleFileSelect}
                className="hidden"
              />
            </div>
            <button
              onClick={handlePost}
              disabled={!newPost.trim() || posting}
              className="btn-primary px-4 py-1.5 text-sm disabled:opacity-50"
            >
              {posting ? "Posting..." : "Post"}
            </button>
          </div>
        </div>
      ) : (
        <div className="card mb-6 py-6 text-center">
          <p className="text-sm text-surface-500 dark:text-surface-400">
            <a href="/auth" className="font-medium text-primary-600 hover:text-primary-700 dark:text-primary-400">
              Sign in
            </a>{" "}
            to share updates with the community.
          </p>
        </div>
      )}

      {/* Feed */}
      {loading ? (
        <div className="space-y-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <SkeletonCard key={i} />
          ))}
        </div>
      ) : !posts || posts.length === 0 ? (
        <EmptyState
          icon={<SocialIcon />}
          title="No posts yet"
          description="Be the first to share a competition result or training update."
        />
      ) : (
        <div className="space-y-4">
          {posts.map((post) => (
            <div key={post.id} className="card transition-all hover:shadow-soft-lg">
              {/* Author */}
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary-50 text-sm font-bold text-primary-600 dark:bg-primary-950/40 dark:text-primary-400">
                  {post.author_name?.[0]?.toUpperCase() || "?"}
                </div>
                <div className="flex-1">
                  <div className="font-semibold text-surface-900 dark:text-white">{post.author_name || "Unknown"}</div>
                  <div className="text-xs text-surface-500 dark:text-surface-400">
                    {new Date(post.created_at).toLocaleDateString("en-US", { month: "short", day: "numeric" })}
                  </div>
                </div>
                <span className={`badge ${typeBadgeStyles[post.post_type] || typeBadgeStyles.general}`}>
                  {post.post_type}
                </span>
              </div>

              {/* Content */}
              <p className="mt-3 text-sm leading-relaxed text-surface-700 dark:text-surface-300">{post.content}</p>

              {/* Media */}
              {post.media_urls && post.media_urls.length > 0 && (
                <div className="mt-3 grid grid-cols-2 gap-2">
                  {post.media_urls.map((url, i) => (
                    <img key={i} src={url} alt="" className="rounded-xl object-cover" />
                  ))}
                </div>
              )}

              {/* Hashtags */}
              {post.hashtags && post.hashtags.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-1.5">
                  {post.hashtags.map((tag) => (
                    <span key={tag} className="text-xs font-medium text-primary-600 dark:text-primary-400">
                      {tag}
                    </span>
                  ))}
                </div>
              )}

              {/* Actions */}
              <div className="mt-4 flex items-center gap-6 border-t border-surface-100 pt-3 dark:border-surface-700/30">
                <button
                  onClick={() => handleLike(post.id)}
                  className={`flex items-center gap-1.5 text-sm transition-colors ${
                    post.is_liked
                      ? "text-accent-600 dark:text-accent-400"
                      : "text-surface-500 hover:text-accent-600 dark:text-surface-400 dark:hover:text-accent-400"
                  }`}
                >
                  <svg className="h-4 w-4" fill={post.is_liked ? "currentColor" : "none"} viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                  </svg>
                  {post.like_count}
                </button>
                <button className="flex items-center gap-1.5 text-sm text-surface-500 transition-colors hover:text-primary-600 dark:text-surface-400 dark:hover:text-primary-400">
                  <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                  {post.comment_count}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
