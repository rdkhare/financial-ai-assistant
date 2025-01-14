"use client"

import { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { useAuth } from "../../context/AuthContext";

export default function Dashboard() {
    const [categoryData, setCategoryData] = useState([]);
    const { user } = useAuth(); // Access the logged-in user
    const [isLoading, setIsLoading] = useState(false); // State for loading icon
    const [error, setError] = useState(null);

    const fetchTransactionsPerCat = async () => {
        if (user) {
            setIsLoading(true); // Show loading icon
            try {
                // Pass the user ID as a query parameter
                const response = await fetch(`http://127.0.0.1:5001/get-transactions-per-category?user_id=${user.uid}`, {
                    method: "GET",
                    headers: { "Content-Type": "application/json" },
                });
    
                if (!response.ok) {
                    throw new Error("Failed to fetch transactions per category");
                }
    
                const data = await response.json();
                const formattedData = Object.entries(data.transactionsPerCategory).map(([category, count]) => ({
                    category,
                    count,
                }));
                setCategoryData(formattedData);
            } catch (err) {
                setError(err.message);
            } finally {
                setIsLoading(false); // Hide loading icon
            }
        }
    };
    

    useEffect(() => {

        fetchTransactionsPerCat();
    }, [user]);

    return (
        <div>
            <h2>Transactions Per Category</h2>
            <ResponsiveContainer width="100%" height={300}>
                <BarChart data={categoryData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="category" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="count" fill="#8884d8" />
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
}
