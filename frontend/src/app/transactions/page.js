// "use client";

// import { useEffect, useState } from "react";
// import { fetchTransactions } from "../../lib/api";

// export default function Transactions() {
//     const [transactions, setTransactions] = useState([]);
//     const [loading, setLoading] = useState(true);
//     const [error, setError] = useState("");

//     useEffect(() => {
//         const accessToken = "access-sandbox-249dae0e-6245-446c-83e9-88b9845e0585"; // Replace with a dynamic token
//         const startDate = "2023-12-01";
//         const endDate = "2023-12-31";

//         async function loadTransactions() {
//             try {
//                 const data = await fetchTransactions(accessToken, startDate, endDate);
//                 setTransactions(data);
//             } catch (err) {
//                 setError(err.message);
//             } finally {
//                 setLoading(false);
//             }
//         }

//         loadTransactions();
//     }, []);

//     if (loading) {
//         return <p>Loading transactions...</p>;
//     }

//     if (error) {
//         return <p>Error: {error}</p>;
//     }

//     return (
//         <div className="p-4">
//             <h1 className="text-2xl font-bold mb-4 text-white">Transactions</h1>
//             <table className="table-auto w-full border-collapse border border-gray-300 bg-white shadow mb-6">
//                 <thead>
//                     <tr className="bg-gray-700 text-white">
//                         <th className="border border-gray-300 p-2">Account</th>
//                         <th className="border border-gray-300 p-2">Name</th>
//                         <th className="border border-gray-300 p-2">Type</th>
//                         <th className="border border-gray-300 p-2">Current Balance</th>
//                         <th className="border border-gray-300 p-2">Available Balance</th>
//                     </tr>
//                 </thead>
//                 <tbody>
//                     {transactions.accounts.map((account) => (
//                         <tr key={account.account_id} className="hover:bg-gray-100">
//                             <td className="border border-gray-300 p-2 text-black">{account.mask}</td>
//                             <td className="border border-gray-300 p-2 text-black">{account.name}</td>
//                             <td className="border border-gray-300 p-2 text-black">{account.type}</td>
//                             <td className="border border-gray-300 p-2 text-black">
//                                 ${account.balances.current.toFixed(2)}
//                             </td>
//                             <td className="border border-gray-300 p-2 text-black">
//                                 ${account.balances.available?.toFixed(2) || "N/A"}
//                             </td>
//                         </tr>
//                     ))}
//                 </tbody>
//             </table>
//         </div>
//     );
// }