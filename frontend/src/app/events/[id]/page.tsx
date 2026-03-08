import EventDetailClient from "./EventDetailClient";

export function generateStaticParams() {
  return [{ id: "1" }];
}

export default function EventDetailPage() {
  return <EventDetailClient />;
}
