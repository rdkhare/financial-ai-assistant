"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "../../context/AuthContext";
import { fetchTransactions } from "../../lib/api"; // Import API helper


export default function Dashboard() {
    const { user } = useAuth();
    const router = useRouter();
    const [error, setError] = useState(null);

    // Redirect if not logged in
    useEffect(() => {
        if (!user) {
            router.push("/"); // Redirect to home if not logged in
            return;
        }

    }, [user, router]);


    return (
        <div className="p-4">
            {/* Welcome message */}
            <h1 className="text-3xl font-bold mb-4 text-white">Welcome, {user?.displayName || "User"}</h1>

            {/* Error Message */}
            {error && <p className="text-red-500 mb-4">Error: {error}</p>}

            
        </div>
    );
}