import AthleteDetailClient from "./AthleteDetailClient";

export function generateStaticParams() {
  // Pre-render a range of IDs for static export; Cloudflare _redirects handles the rest
  return Array.from({ length: 100 }, (_, i) => ({ id: String(i + 1) }));
}

export default function AthleteDetailPage() {
  return <AthleteDetailClient />;
}
