"use client";

import { useAuth } from "../../context/AuthContext";
import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { FaSync } from "react-icons/fa";

export default function Account() {
    const router = useRouter();
    const { user } = useAuth();
    const [accounts, setAccounts] = useState([]);
    const [error, setError] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [isConnecting, setIsConnecting] = useState(false);

    useEffect(() => {
        fetchAccounts();
    }, [user]);

    const fetchAccounts = async () => {
        if (user) {
            setIsLoading(true);
            try {
                const response = await fetch("http://127.0.0.1:5001/get-plaid-accounts", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ user_id: user.uid}),
                });

                const data = await response.json();
                setAccounts(data || []);
            } catch (err) {
                setError(err.message);
            } finally {
                setIsLoading(false);
            }
        }
    };

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
        <div className="p-6 bg-gray-900 min-h-screen text-green-400">
            <h1 className="text-4xl mb-4">Account</h1>
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
            <div className="bg-gray-800 p-6 rounded-lg shadow-lg mb-8">
                <h2 className="text-2xl font-semibold mb-4">Connected Accounts</h2>
                {isLoading ? (
                    <p>Loading connected accounts...</p>
                ) : accounts.length > 0 ? (
                    <div className="grid gap-6">
                        {accounts.map((account) => (
                            <Link
                                key={account.account_id}
                                href={`/accounts/${account.account_id}`}
                                className="block"
                            >
                                <div className="p-4 bg-gray-700 rounded-lg">
                                    <p className="font-bold">{account.accountName}</p>
                                    <p>Type: {account.subtype}</p>
                                    <p>Balance: ${account.balance}</p>
                                </div>
                            </Link>
                        ))}
                    </div>
                ) : (
                    <p>No connected accounts yet.</p>
                )}
            </div>

            <button
                onClick={handlePlaidLink}
                className="mt-4 bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            >
                Connect Bank Account
            </button>
        </div>
    );
}