import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "JEE Learning Platform",
  description: "Adaptive learning platform for JEE Main preparation with AI-powered personalized quizzes and comprehensive analytics",
  keywords: ["JEE Main", "IIT", "engineering entrance", "adaptive learning", "AI tutoring", "mathematics", "physics", "chemistry"],
  authors: [{ name: "JEE Learning Platform Team" }],
  viewport: "width=device-width, initial-scale=1",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="min-h-screen bg-gray-50">
          {children}
        </div>
      </body>
    </html>
  );
}
