"use client";

import { useState, useRef } from "react";
import { useApi } from "@/hooks/useApi";
import { useAuth } from "@/components/auth/AuthProvider";
import { social, upload, mediaUrl } from "@/lib/api";
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

interface Comment {
  id: string;
  post_id: string;
  author_id: string;
  author_name: string | null;
  author_avatar: string | null;
  parent_id: string | null;
  content: string;
  created_at: string;
}

export default function SocialPage() {
  const { user, token } = useAuth();
  const [newPost, setNewPost] = useState("");
  const [postType, setPostType] = useState("general");
  const [mediaFiles, setMediaFiles] = useState<File[]>([]);
  const [mediaPreviews, setMediaPreviews] = useState<string[]>([]);
  const [posting, setPosting] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<number | null>(null);
  const [postError, setPostError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Comments state
  const [expandedComments, setExpandedComments] = useState<Record<string, boolean>>({});
  const [commentsByPost, setCommentsByPost] = useState<Record<string, Comment[]>>({});
  const [loadingComments, setLoadingComments] = useState<Record<string, boolean>>({});
  const [commentText, setCommentText] = useState<Record<string, string>>({});
  const [postingComment, setPostingComment] = useState<Record<string, boolean>>({});

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
    setUploadProgress(null);

    try {
      // Upload media files first
      const uploadedUrls: string[] = [];
      if (mediaFiles.length > 0) {
        for (let i = 0; i < mediaFiles.length; i++) {
          setUploadProgress(Math.round(((i) / mediaFiles.length) * 100));
          const result = await upload.media(mediaFiles[i], token, (pct) => {
            const overallPct = Math.round(((i + pct / 100) / mediaFiles.length) * 100);
            setUploadProgress(overallPct);
          });
          uploadedUrls.push(result.url);
        }
        setUploadProgress(100);
      }

      // Extract hashtags from content
      const hashtags = newPost.match(/#\w+/g) || [];

      await social.createPost(
        {
          content: newPost,
          post_type: postType,
          hashtags,
          media_urls: uploadedUrls,
        },
        token
      );
      setNewPost("");
      setPostType("general");
      setMediaFiles([]);
      setMediaPreviews([]);
      setUploadProgress(null);
      refetch();
    } catch (err) {
      setPostError(err instanceof Error ? err.message : "Failed to create post");
    } finally {
      setPosting(false);
      setUploadProgress(null);
    }
  };

  const handleLike = async (postId: string) => {
    if (!token) return;
    try {
      await social.toggleLike(postId, token);
      refetch();
    } catch {
      // Silently fail
    }
  };

  const toggleComments = async (postId: string) => {
    const isExpanded = expandedComments[postId];
    setExpandedComments((prev) => ({ ...prev, [postId]: !isExpanded }));

    // Load comments if expanding and not already loaded
    if (!isExpanded && !commentsByPost[postId]) {
      setLoadingComments((prev) => ({ ...prev, [postId]: true }));
      try {
        const comments = await social.getComments(postId) as Comment[];
        setCommentsByPost((prev) => ({ ...prev, [postId]: comments }));
      } catch {
        // Silently fail
      } finally {
        setLoadingComments((prev) => ({ ...prev, [postId]: false }));
      }
    }
  };

  const handleComment = async (postId: string) => {
    const text = commentText[postId]?.trim();
    if (!text || !token) return;

    setPostingComment((prev) => ({ ...prev, [postId]: true }));
    try {
      const comment = await social.createComment(postId, { content: text }, token) as Comment;
      setCommentsByPost((prev) => ({
        ...prev,
        [postId]: [...(prev[postId] || []), comment],
      }));
      setCommentText((prev) => ({ ...prev, [postId]: "" }));
      refetch(); // Update comment count
    } catch {
      // Silently fail
    } finally {
      setPostingComment((prev) => ({ ...prev, [postId]: false }));
    }
  };

  return (
    <div className="mx-auto max-w-2xl px-4 py-8 sm:px-6">
      <h1 className="mb-6 text-3xl font-bold text-surface-900 dark:text-white">Social Feed</h1>

      {/* Compose */}
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

          {/* Upload progress bar */}
          {uploadProgress !== null && (
            <div className="mt-3">
              <div className="flex items-center justify-between text-xs text-surface-500 dark:text-surface-400 mb-1">
                <span>Uploading media...</span>
                <span>{uploadProgress}%</span>
              </div>
              <div className="h-1.5 w-full overflow-hidden rounded-full bg-surface-100 dark:bg-surface-700">
                <div
                  className="h-full rounded-full bg-primary-500 transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>
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
              {posting ? (uploadProgress !== null ? "Uploading..." : "Posting...") : "Post"}
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
                <div className={`mt-3 grid gap-2 ${post.media_urls.length === 1 ? "grid-cols-1" : "grid-cols-2"}`}>
                  {post.media_urls.map((url, i) => {
                    const resolved = mediaUrl(url);
                    if (url.match(/\.(mp4|mov)$/i)) {
                      return (
                        <video
                          key={i}
                          src={resolved}
                          controls
                          className="w-full rounded-xl"
                          preload="metadata"
                        />
                      );
                    }
                    return (
                      <img
                        key={i}
                        src={resolved}
                        alt=""
                        className="rounded-xl object-cover w-full"
                        loading="lazy"
                      />
                    );
                  })}
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
                <button
                  onClick={() => toggleComments(post.id)}
                  className={`flex items-center gap-1.5 text-sm transition-colors ${
                    expandedComments[post.id]
                      ? "text-primary-600 dark:text-primary-400"
                      : "text-surface-500 hover:text-primary-600 dark:text-surface-400 dark:hover:text-primary-400"
                  }`}
                >
                  <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                  {post.comment_count}
                </button>
              </div>

              {/* Comments section — expandable */}
              {expandedComments[post.id] && (
                <div className="mt-3 border-t border-surface-100 pt-3 dark:border-surface-700/30">
                  {/* Loading */}
                  {loadingComments[post.id] && (
                    <div className="py-3 text-center text-xs text-surface-400">Loading comments...</div>
                  )}

                  {/* Comments list */}
                  {commentsByPost[post.id] && commentsByPost[post.id].length > 0 && (
                    <div className="space-y-3 mb-3">
                      {commentsByPost[post.id].map((comment) => (
                        <div key={comment.id} className="flex gap-2.5">
                          <div className="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full bg-surface-100 text-xs font-bold text-surface-500 dark:bg-surface-700 dark:text-surface-400">
                            {comment.author_name?.[0]?.toUpperCase() || "?"}
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-baseline gap-2">
                              <span className="text-sm font-medium text-surface-900 dark:text-white">
                                {comment.author_name || "Unknown"}
                              </span>
                              <span className="text-xs text-surface-400">
                                {new Date(comment.created_at).toLocaleDateString("en-US", { month: "short", day: "numeric" })}
                              </span>
                            </div>
                            <p className="mt-0.5 text-sm text-surface-600 dark:text-surface-300">{comment.content}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Empty comments */}
                  {commentsByPost[post.id] && commentsByPost[post.id].length === 0 && !loadingComments[post.id] && (
                    <p className="py-2 text-center text-xs text-surface-400">No comments yet</p>
                  )}

                  {/* Comment input */}
                  {user && (
                    <div className="flex gap-2">
                      <input
                        type="text"
                        value={commentText[post.id] || ""}
                        onChange={(e) => setCommentText((prev) => ({ ...prev, [post.id]: e.target.value }))}
                        onKeyDown={(e) => {
                          if (e.key === "Enter" && !e.shiftKey) {
                            e.preventDefault();
                            handleComment(post.id);
                          }
                        }}
                        placeholder="Write a comment..."
                        className="input flex-1 py-1.5 text-sm"
                      />
                      <button
                        onClick={() => handleComment(post.id)}
                        disabled={!commentText[post.id]?.trim() || postingComment[post.id]}
                        className="btn-primary px-3 py-1.5 text-xs disabled:opacity-50"
                      >
                        {postingComment[post.id] ? "..." : "Send"}
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
