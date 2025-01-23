"use client";

import { useEffect, useState } from "react";
import { useAuth } from "../../context/AuthContext";

export default function Transactions() {
    const { user } = useAuth();
    const [transactions, setTransactions] = useState([]);
    const [error, setError] = useState(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        fetchTransactions();
    }, [user]);

    const fetchTransactions = async () => {
        if (user) {
            try {
                const response = await fetch("http://127.0.0.1:5001/transactions/sync", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ user_id: user.uid }),
                });

                const data = await response.json();
                if (response.ok) {
                    setTransactions(data.transactions || []);
                } else {
                    setError(data.error || "Failed to fetch transactions");
                }
            } catch (err) {
                setError(err.message);
            } finally {
                setIsLoading(false);
            }
        }
    };

    return (
        <div className="p-6 bg-gray-900 text-white">
            <h1 className="text-2xl font-bold mb-4">Transactions</h1>
            {isLoading ? (
                <p>Loading transactions...</p>
            ) : error ? (
                <p className="text-red-500">{error}</p>
            ) : transactions.length > 0 ? (
                <ul>
                    {transactions.map((tx, idx) => (
                        <li key={idx} className="border-b border-gray-700 p-2">
                            <p>{tx.date} - {tx.personal_finance_category.primary}</p>
                            <p>${tx.amount.toFixed(2)}</p>
                        </li>
                    ))}
                </ul>
            ) : (
                <p>No transactions found.</p>
            )}
        </div>
    );
}