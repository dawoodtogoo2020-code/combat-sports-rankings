import GymDetailClient from "./GymDetailClient";

export function generateStaticParams() {
  return [{ id: "1" }];
}

export default function GymDetailPage() {
  return <GymDetailClient />;
}
