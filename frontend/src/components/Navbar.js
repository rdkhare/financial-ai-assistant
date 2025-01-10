"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter, usePathname } from "next/navigation";
import { useAuth } from "../context/AuthContext";
import { FiMenu, FiLogOut, FiLogIn, FiHome, FiUser, FiDollarSign, FiTool } from "react-icons/fi";
import { VscGraph } from "react-icons/vsc";
import { GrTransaction } from "react-icons/gr";


export default function Navbar({children}) {
    const { user, logout } = useAuth();
    const router = useRouter();
    const pathname = usePathname(); // Get the current path
    const [isExpanded, setIsExpanded] = useState(false);
    const [isClient, setIsClient] = useState(false);

    useEffect(() => {
        setIsClient(true);
    }, []);

    const handleLogout = async () => {
        await logout();
        router.push("/");
    };

    const toggleExpand = () => {
        setIsExpanded(!isExpanded);
    };

    if (!isClient) return null;

    const isActive = (path) => pathname === path;

    return (
        <div className="flex h-screen">
            {/* Sidebar */}
            <nav
                className={`text-white h-full ${
                    isExpanded ? "w-64" : "w-20"
                } transition-all duration-300 ease-in-out flex flex-col`}
            >
                {/* Logo and Toggle */}
                <div className="flex flex-col items-center w-full p-4">
                    <button onClick={toggleExpand} className="text-white hover:text-gray-400 focus:outline-none mb-2">
                        <FiMenu size={24} />
                    </button>
                    <Link href="/" className="text-lg font-bold text-center">
                        {isExpanded ? "QuantizedAI" : "QA"}
                    </Link>
                    {/* Divider Line */}
                    <div className="w-full border-t border-gray-700 mt-4" />
                </div>

                {/* Navigation Links */}
                <ul className="flex flex-col w-full mt-4 space-y-4">
                    <li>
                        <Link
                            href="/"
                            className={`flex items-center w-full px-4 py-2 hover:bg-gray-700 rounded-md ${
                                isExpanded ? "justify-start" : "justify-center"
                            } ${isActive("/") ? "bg-gray-800" : ""}`}
                        >
                            <FiHome size={24} className={`${isExpanded ? "mr-4" : ""}`} />
                            {isExpanded && <span>Home</span>}
                        </Link>
                    </li>
                    {user && (
                        <li>
                            <Link
                                href="/dashboard"
                                className={`flex items-center w-full px-4 py-2 hover:bg-gray-700 rounded-md ${
                                    isExpanded ? "justify-start" : "justify-center"
                                } ${isActive("/dashboard") ? "bg-gray-800" : ""}`}
                            >
                                <VscGraph size={24} className={`${isExpanded ? "mr-4" : ""}`} />
                                {isExpanded && <span>Dashboard</span>}
                            </Link>
                        </li>
                    )}
                    {user && (
                    <li>
                        <Link
                            href="/account"
                            className={`flex items-center w-full px-4 py-2 hover:bg-gray-700 rounded-md ${
                                isExpanded ? "justify-start" : "justify-center"
                            } ${isActive("/account") ? "bg-gray-800" : ""}`}
                        >
                            <FiUser size={24} className={`${isExpanded ? "mr-4" : ""}`} />
                            {isExpanded && <span>Account</span>}
                        </Link>
                    </li>
                    )}
                    <li>
                        <Link
                            href="/pricing"
                            className={`flex items-center w-full px-4 py-2 hover:bg-gray-700 rounded-md ${
                                isExpanded ? "justify-start" : "justify-center"
                            } ${isActive("/pricing") ? "bg-gray-800" : ""}`}
                        >
                            <FiDollarSign size={24} className={`${isExpanded ? "mr-4" : ""}`} />
                            {isExpanded && <span>Pricing</span>}
                        </Link>
                    </li>
                    <li>
                        <Link
                            href="/tools"
                            className={`flex items-center w-full px-4 py-2 hover:bg-gray-700 rounded-md ${
                                isExpanded ? "justify-start" : "justify-center"
                            } ${isActive("/tools") ? "bg-gray-800" : ""}`}
                        >
                            <FiTool size={24} className={`${isExpanded ? "mr-4" : ""}`} />
                            {isExpanded && <span>Tools</span>}
                        </Link>
                    </li>
                    {user && (
                        <li>
                            <Link
                                href="/transactions"
                                className={`flex items-center w-full px-4 py-2 hover:bg-gray-700 rounded-md ${
                                    isExpanded ? "justify-start" : "justify-center"
                                } ${isActive("/transactions") ? "bg-gray-800" : ""}`}
                            >
                                <GrTransaction size={24} className={`${isExpanded ? "mr-4" : ""}`} />
                                {isExpanded && <span>Transactions</span>}
                            </Link>
                        </li>
                    )}
                    {/* Sign In/Sign Out */}
                <div className="mt-auto w-full">
                    {user ? (
                        <button
                            onClick={handleLogout}
                            className={`flex items-center w-full px-4 py-2 hover:bg-gray-700 rounded-md ${
                                isExpanded ? "justify-start" : "justify-center"
                            }`}
                        >
                            <FiLogOut size={24} className={`${isExpanded ? "mr-4" : ""}`} />
                            {isExpanded && <span>Sign Out</span>}
                        </button>
                    ) : (
                        <Link
                            href="/login"
                            className={`flex items-center w-full px-4 py-2 hover:bg-gray-700 rounded-md ${
                                isExpanded ? "justify-start" : "justify-center"
                            } ${isActive("/login") ? "bg-gray-800" : ""}`}
                        >
                            <FiLogIn size={24} className={`${isExpanded ? "mr-4" : ""}`} />
                            {isExpanded && <span>Sign In</span>}
                        </Link>
                    )}
                </div>
                </ul>

                
            </nav>

            {/* Main Content Placeholder */}
            <main className="flex-1">
                {children}
            </main>
        </div>
    );
}