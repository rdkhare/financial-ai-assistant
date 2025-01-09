"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "../../context/AuthContext";
import { fetchTransactions } from "../../lib/api"; // Import API helper
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    Tooltip,
    ResponsiveContainer,
    CartesianGrid,
} from "recharts";

export default function Dashboard() {
    const { user } = useAuth();
    const router = useRouter();
    const [transactions, setTransactions] = useState([]);
    const [error, setError] = useState(null);
    const [chartData, setChartData] = useState([]); // State for chart data

    // Redirect if not logged in
    useEffect(() => {
        if (!user) {
            router.push("/"); // Redirect to home if not logged in
            return;
        }

        const fetchData = async () => {
            try {
                const data = await fetchTransactions(
                    "2023-12-01", // Example start date
                    "2023-12-31", // Example end date
                    "access-sandbox-249dae0e-6245-446c-83e9-88b9845e0585" // Replace with your sandbox token
                );
                setTransactions(data.transactions || []);
                generateChartData(data.transactions || []);
            } catch (err) {
                console.error("Error fetching transactions:", err);
                setError(err.message);
            }
        };

        fetchData();
    }, [user, router]);

    // Generate chart data based on transactions
    const generateChartData = (transactions) => {
        const categoryData = transactions.reduce((acc, transaction) => {
            acc[transaction.category] = (acc[transaction.category] || 0) + transaction.amount;
            return acc;
        }, {});

        const formattedChartData = Object.keys(categoryData).map((category) => ({
            category,
            amount: categoryData[category],
        }));

        setChartData(formattedChartData);
    };

    return (
        <div className="p-4">
            {/* Welcome message */}
            <h1 className="text-3xl font-bold mb-4 text-white">Welcome, {user?.displayName || "User"}</h1>

            {/* Error Message */}
            {error && <p className="text-red-500 mb-4">Error: {error}</p>}

            {/* Transactions Summary */}
            <div className="flex justify-between items-center bg-blue-200 text-blue-900 p-4 rounded-lg shadow mb-6">
                <p className="text-lg font-semibold">
                    Total Spending: $
                    {transactions.reduce((total, transaction) => total + transaction.amount, 0).toFixed(2)}
                </p>
            </div>

            {/* Transactions Table */}
            <table className="table-auto w-full border-collapse border border-gray-300 shadow mb-6">
                <thead>
                    <tr className="bg-gray-700 text-white">
                        <th className="border border-gray-300 p-2">ID</th>
                        <th className="border border-gray-300 p-2">Category</th>
                        <th className="border border-gray-300 p-2">Amount</th>
                        <th className="border border-gray-300 p-2">Date</th>
                    </tr>
                </thead>
                <tbody>
                    {transactions.map((transaction) => (
                        <tr key={transaction.id} className="hover:bg-gray-50">
                            <td className="border border-gray-300 p-2 text-center">{transaction.id}</td>
                            <td className="border border-gray-300 p-2 text-center">{transaction.category}</td>
                            <td className="border border-gray-300 p-2 text-center">
                                ${transaction.amount.toFixed(2)}
                            </td>
                            <td className="border border-gray-300 p-2 text-center">{transaction.date}</td>
                        </tr>
                    ))}
                </tbody>
            </table>

            {/* Bar Chart Section */}
            <div className="bg-white p-4 rounded-lg shadow">
                <h2 className="text-xl font-bold mb-4">Spending by Category</h2>
                <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={chartData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="category" />
                        <YAxis />
                        <Tooltip />
                        <Bar dataKey="amount" fill="#8884d8" />
                    </BarChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
}