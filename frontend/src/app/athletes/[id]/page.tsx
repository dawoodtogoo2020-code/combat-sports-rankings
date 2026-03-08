import AthleteDetailClient from "./AthleteDetailClient";

export function generateStaticParams() {
  return [{ id: "1" }];
}

export default function AthleteDetailPage() {
  return <AthleteDetailClient />;
}
