"use client"

import { useEffect, useState } from "react";
import { LineChart, Line,  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { useAuth } from "../../context/AuthContext";

export default function Dashboard() {
    const [categoryData, setCategoryData] = useState([]);
    const { user } = useAuth(); // Access the logged-in user
    const [isLoading, setIsLoading] = useState(false); // State for loading icon
    const [error, setError] = useState(null);
    const [dateRange, setDateRange] = useState({ start_date: "", end_date: "" }); // Date range state
    const [balanceData, setBalanceData] = useState([]);

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


    const fetchBalanceOverTime = async () => {
        if (user) {
            setIsLoading(true); // Show loading icon
            try {
                const response = await fetch("http://127.0.0.1:5001/get-balance-over-time", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ 
                        user_id: user.uid, 
                        start_date: dateRange.start_date, 
                        end_date: dateRange.end_date 
                    }),
                });

                if (!response.ok) {
                    throw new Error("Failed to fetch balance over time");
                }

                const data = await response.json();
                setBalanceData(data.balanceOverTime);
            } catch (err) {
                setError(err.message);
            } finally {
                setIsLoading(false); // Hide loading icon
            }
        }
    };

    useEffect(() => {
        fetchTransactionsPerCat();
        fetchBalanceOverTime();
    }, [user, dateRange]);

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
            <h2>Balance Over Time</h2>

            {/* Date Range Filters */}
            <div>
                <input 
                    type="date" 
                    value={dateRange.start_date} 
                    onChange={(e) => setDateRange({ ...dateRange, start_date: e.target.value })} 
                    placeholder="Start Date"
                />
                <input 
                    type="date" 
                    value={dateRange.end_date} 
                    onChange={(e) => setDateRange({ ...dateRange, end_date: e.target.value })} 
                    placeholder="End Date"
                />
                <button onClick={fetchBalanceOverTime}>Apply Filters</button>
            </div>

            {/* Line Chart */}
            <ResponsiveContainer width="100%" height={300}>
                <LineChart data={balanceData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Line type="monotone" dataKey="balance" stroke="#8884d8" />
                </LineChart>
            </ResponsiveContainer>
        </div>
        
    );
}
