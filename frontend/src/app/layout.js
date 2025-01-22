import Footer from "../components/Footer";
import Navbar from "../components/Navbar";
import { AuthProvider } from "../context/AuthContext";
import "./globals.css";
import Script from "next/script";


export const metadata = {
    title: "Financial Assistant AI",
    description: "Manage your finances intelligently",
};

export default function RootLayout({ children }) {
    return (
        <html lang="en">
            <body>
                <AuthProvider>
                    <div className="flex h-screen">
                        {/* Navbar */}
                        <Navbar />
                        {/* Main Content */}
                        <div className="flex-1 flex flex-col">
                            <main className="flex-1">
                                {children}
                            </main>
                            <Footer />
                        </div>
                    </div>
                </AuthProvider>
                
                <Script
                    src="https://cdn.teller.io/connect/connect.js"
                    strategy="beforeInteractive"
                />
                <Script
                    src="https://cdn.plaid.com/link/v2/stable/link-initialize.js"
                    strategy="beforeInteractive"
                />
               
            </body>
        </html>
    );
}