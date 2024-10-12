import "./globals.css";
import Head from "next/head";

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <Head>
        <link rel="icon" href="/path-to-your-favicon.ico" />
      </Head>
      <body className="antialiased bg-gray-100 text-gray-800">
        <header className="w-full p-4 bg-blue-500 text-white shadow-lg">
          <nav className="flex justify-between items-center max-w-7xl mx-auto">
            <a href="/" className="font-bold text-xl">Player Performance Predictor</a>
            <div className="space-x-4">
              <a href="/predictions" className="hover:text-yellow-300">Predictions</a>
            </div>
          </nav>
        </header>

        <main className="max-w-7xl mx-auto">
          {children}
        </main>
      </body>
    </html>
  );
}
