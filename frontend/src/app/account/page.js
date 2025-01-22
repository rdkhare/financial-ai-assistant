"use client";

import { useAuth } from "../../context/AuthContext";
import { useState, useEffect } from "react";
import Link from "next/link"; 
import { FaSync } from "react-icons/fa";

export default function Account() {
    const { user } = useAuth(); // Access the logged-in user
    const [accounts, setAccounts] = useState([]);
    const [error, setError] = useState(null);
    const [isLoading, setIsLoading] = useState(false); // State for loading icon
    const [isConnecting, setIsConnecting] = useState(false); // State for Teller connect process
    const [isSyncing, setIsSyncing] = useState(false);

    useEffect(() => {
        fetchAccounts();
    }, [user])

    // Fetch connected accounts
    const fetchAccounts = async () => {
        if (user) {
            setIsLoading(true); // Show loading icon

            try {
                const response = await fetch("http://127.0.0.1:5001/get-plaid-accounts", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ user_id: user.uid }),
                });

                const data = await response.json();
                setAccounts(data.accounts || []);
                console.log(data.accounts);
            } catch (err) {
                setError(err.message);
            } finally {
                setIsLoading(false); // Hide loading icon
            }
        }
    };

    // const syncBalancesAndTransactions = async () => {
    //     if (user) {
    //         setIsSyncing(true);
    //         try {
    //             const response = await fetch("http://127.0.0.1:5001/sync-balances-and-transactions", {
    //                 method: "POST",
    //                 headers: { "Content-Type": "application/json" },
    //                 body: JSON.stringify({ user_id: user.uid }),
    //             });

    //             const data = await response.json();
    //             if (response.ok) {
    //                 setAccounts(data.accounts || []);
    //             } else {
    //                 setError(data.error || "Failed to sync balances and transactions");
    //             }
    //         } catch (err) {
    //             setError(err.message);
    //         } finally {
    //             setIsSyncing(false);
    //         }
    //     }
    // };

    const handlePlaidLink = async () => {
        try {
            const response = await fetch("http://127.0.0.1:5001/create-link-token", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ user_id: user.uid }),
            });

            const data = await response.json();
            if (response.ok) {
                const handler = Plaid.create({
                    token: data.link_token,
                    onSuccess: async (public_token) => {
                        try {
                            const res = await fetch("http://127.0.0.1:5001/exchange-public-token", {
                                method: "POST",
                                headers: { "Content-Type": "application/json" },
                                body: JSON.stringify({
                                    public_token,
                                    user_id: user.uid,
                                }),
                            });

                            if (!res.ok) {
                                throw new Error("Failed to exchange public token");
                            }

                            // Fetch accounts to update the list dynamically
                            await fetchAccounts();
                        } catch (err) {
                            console.error("Error exchanging public token:", err);
                            alert("Failed to connect account");
                        }
                    },
                    onExit: (error) => {
                        console.error("Plaid Link error:", error);
                        alert("Failed to connect account");
                    },
                });
                handler.open();
            } else {
                throw new Error(data.error || "Failed to create link token");
            }
        } catch (err) {
            console.error("Error creating link token:", err);
            alert("Failed to initiate Plaid Link");
        }
    };

    return (
        <div className="p-6 bg-gradient-to-b from-black to-gray-900 min-h-screen text-green-400 font-sans">
            {/* Page Title */}
            <h1 className="text-4xl mb-4">Account</h1>
            <div className="border-b border-gray-600 mb-8"></div>

            {/* User Info Section */}
            <div className="bg-[#1a1a1a] p-6 rounded-lg shadow-lg hover:shadow-2xl transition-all mb-8">
                <h2 className="text-2xl font-semibold mb-4">User Information</h2>
                <div className="border-b border-gray-600 mb-8"></div>

                <p>
                    <span className="font-bold">Name:</span> {user?.displayName || "Not provided"}
                </p>
                <p>
                    <span className="font-bold">Email:</span> {user?.email || "Not provided"}
                </p>
            </div>

            {/* Connected Accounts Section */}
            <div className="bg-[#1a1a1a] p-6 rounded-lg shadow-lg relative">
                <div className="flex justify-between items-center mb-4">
                    <h2 className="text-2xl font-semibold">Connected Accounts</h2>
                    {/* Sync Button */}
                    {/* <button
                        onClick={syncBalancesAndTransactions}
                        className={`p-2 rounded-full ${
                            isSyncing
                                ? "text-gray-400 animate-spin"
                                : "text-green-400 hover:text-green-500 transition-colors"
                        }`}
                        disabled={isSyncing}
                        aria-label="Sync Balances and Transactions"
                    >
                        <FaSync className="w-6 h-6" />
                    </button> */}
                </div>
                <div className="border-b border-gray-600 mb-8"></div>

                {error && <p className="text-red-500 mt-2">Error: {error}</p>}
                {isLoading ? (
                    <p className="text-green-300 mt-2">Loading connected accounts...</p>
                ) : accounts.length > 0 ? (
                    <div className="grid gap-6">
                        {accounts.map((account) => (
                            <Link
                                key={account.account_id}
                                href={`/accounts/${account.account_id}`} // Dynamic route for specific account
                                className="block"
                            >
                                <div
                                    className="p-4 bg-[#262626] rounded-lg border border-gray-300 shadow-md hover:shadow-[0_10px_15px_rgba(0,0,0,0.5)] hover:bg-white hover:text-black hover:translate-x-4 hover:brightness-110 transition-all"
                                >
                                    <p className="font-bold text-lg">{account.accountName}</p>
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
            {/* {user &&<button
                onClick={handleTellerConnect}
                className={`mt-8 border-2 border-black bg-black text-white p-3 rounded-md hover:bg-white hover:shadow-lg transition-transform hover:text-black ${
                    isConnecting ? "opacity-50 cursor-not-allowed" : ""
                }`}
                disabled={isConnecting}
            >
                {isConnecting ? "Connecting..." : "Connect Bank Account"}
            </button>} */}
            {user && (
                <button
                    onClick={handlePlaidLink}
                    className={`mt-8 border-2 border-black bg-black text-white p-3 rounded-md hover:bg-white hover:shadow-lg transition-transform hover:text-black ${
                        isConnecting ? "opacity-50 cursor-not-allowed" : ""
                    }`}
                    disabled={isConnecting}
                >
                    {isConnecting ? "Connecting..." : "Connect Bank Account with Plaid"}
                </button>
            )}
        </div>
    );
}
