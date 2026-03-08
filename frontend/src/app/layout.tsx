import type { Metadata, Viewport } from "next";
import "@/styles/globals.css";
import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { ThemeProvider } from "@/components/layout/ThemeProvider";
import { AuthProvider } from "@/components/auth/AuthProvider";

export const metadata: Metadata = {
  title: "CS Rankings — Combat Sports Rankings",
  description:
    "The global ranking platform for combat sports athletes. ELO-based rankings for BJJ, grappling, MMA, and more.",
  keywords: ["BJJ", "rankings", "combat sports", "ELO", "grappling", "martial arts"],
  icons: {
    icon: "/favicon.svg",
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="min-h-screen flex flex-col antialiased">
        <ThemeProvider>
          <AuthProvider>
            <Navbar />
            <main className="flex-1">{children}</main>
            <Footer />
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
