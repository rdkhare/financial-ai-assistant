"use client";

import { useRouter } from "next/navigation";

export default function LogoutButton() {
    const router = useRouter();

    const handleLogout = () => {
        // Remove the JWT token from localStorage
        localStorage.removeItem("token");

        // Redirect to the login page
        router.push("/login");
    };

    return (
        <button
            onClick={handleLogout}
            className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600 transition-all"
        >
            Logout
        </button>
    );
}