import "./globals.css";
import type { ReactNode } from "react";

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-bg text-slate-50">
        <div className="flex h-screen flex-col">
          <header className="flex items-center justify-between border-b border-slate-800 px-6 py-3">
            <div className="text-sm font-semibold text-slate-200">
              Answer Quality Evaluator
            </div>
            <div className="text-xs text-slate-400">
              Internal evaluation workbench · pipelines A/B/C
            </div>
          </header>
          <main className="flex-1 overflow-hidden">{children}</main>
        </div>
      </body>
    </html>
  );
}

