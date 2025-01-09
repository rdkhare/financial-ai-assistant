"use client";

import { useAuth } from "../../context/AuthContext";
import { useState, useEffect } from "react";
import Link from "next/link"; // Import Link for navigation

export default function Account() {
    const { user } = useAuth(); // Access the logged-in user
    const [accounts, setAccounts] = useState([]);
    const [error, setError] = useState(null);
    const [isLoading, setIsLoading] = useState(true); // State for loading icon
    const [isConnecting, setIsConnecting] = useState(false); // State for Teller connect process

    console.log("User:", user);

    // Fetch connected accounts
    const fetchAccounts = async () => {
        if (user) {
            setIsLoading(true); // Show loading icon
            try {
                const response = await fetch("http://127.0.0.1:5001/get-connected-accounts", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ user_id: user.uid }),
                });

                const data = await response.json();
                setAccounts(data.accounts || []);
            } catch (err) {
                setError(err.message);
            } finally {
                setIsLoading(false); // Hide loading icon
            }
        }
    };

    // Initial fetch on component load
    useEffect(() => {
        fetchAccounts();
    }, [user]);

    const handleTellerConnect = () => {
        if (typeof window !== "undefined" && window.TellerConnect) {
            const tellerConnect = new window.TellerConnect.setup({
                applicationId: process.env.NEXT_PUBLIC_TELLER_APP_ID,
                environment: "development",
                onSuccess: async (response) => {
                    console.log("Access Token:", response.accessToken);
                    setIsConnecting(true); // Show connecting state
                    try {
                        // Send access token to the backend
                        const res = await fetch("http://127.0.0.1:5001/store-access-token", {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify({
                                access_token: response.accessToken,
                                user_id: user.uid, // Replace with your user ID field
                            }),
                        });

                        if (!res.ok) {
                            throw new Error("Failed to store access token");
                        }

                        // Re-fetch accounts to update the list dynamically
                        await fetchAccounts();
                    } catch (err) {
                        console.error("Error storing access token:", err);
                        alert("Failed to connect account");
                    } finally {
                        setIsConnecting(false); // Hide connecting state
                    }
                },
                onExit: (error) => {
                    console.error("Teller Connect error:", error);
                    alert("Failed to connect account");
                },
            });
            tellerConnect.open();
        } else {
            console.error("TellerConnect is not available on the window object.");
        }
    };

    return (
        <div className="p-6 bg-gradient-to-b from-black to-gray-900 min-h-screen text-green-400 font-sans">
            {/* Page Title */}
            <h1 className="text-4xl font-bold mb-4">Account</h1>
            <div className="border-b border-gray-600 mb-8"></div>

            {/* User Info Section */}
            <div className="bg-[#1a1a1a] p-6 rounded-lg shadow-lg hover:shadow-2xl transition-all mb-8">
                <h2 className="text-2xl font-semibold mb-4">User Information</h2>
                <p>
                    <span className="font-bold">Name:</span> {user?.displayName || "Not provided"}
                </p>
                <p>
                    <span className="font-bold">Email:</span> {user?.email || "Not provided"}
                </p>
            </div>

            {/* Connected Accounts Section */}
            <div className="bg-[#1a1a1a] p-6 rounded-lg shadow-lg">
                <h2 className="text-2xl font-semibold mb-4">Connected Accounts</h2>
                {error && <p className="text-red-500 mt-2">Error: {error}</p>}
                {isLoading ? (
                    <p className="text-green-300 mt-2">Loading connected accounts...</p>
                ) : accounts.length > 0 ? (
                    <div className="grid gap-6">
                        {accounts.map((account) => (
                            <Link
                                key={account.teller_id}
                                href={`/accounts/${account.teller_id}`} // Dynamic route for specific account
                                className="block"
                            >
                                <div
                                    className="p-4 bg-[#262626] rounded-lg border border-gray-300 shadow-md hover:shadow-[0_10px_15px_rgba(0,0,0,0.5)] hover:bg-white hover:text-black hover:translate-x-4 hover:brightness-110 transition-all"
                                >
                                    <p className="font-bold text-lg">{account.accountName}</p>
                                    <p>Bank: {account.bankName}</p>
                                    <p>Type: {account.subtype}</p>
                                    <p>Last 4 Digits: {account.accountNumber}</p>
                                    <p>Balance: ${account.balance}</p>
                                </div>
                            </Link>
                        ))}
                    </div>
                ) : (
                    <p className="mt-2 text-green-300">
                        No connected accounts yet. Connect your bank accounts to get started.
                    </p>
                )}
            </div>

            {/* Teller Connect Button */}
            <button
                onClick={handleTellerConnect}
                className={`mt-8 bg-green-500 text-black p-3 rounded-full hover:bg-green-600 hover:shadow-lg transition-transform ${
                    isConnecting ? "opacity-50 cursor-not-allowed" : ""
                }`}
                disabled={isConnecting}
            >
                {isConnecting ? "Connecting..." : "Connect Bank Account"}
            </button>
        </div>
    );
}
