"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation"; // Import useRouter for redirection
import { auth, googleProvider } from "../../lib/firebase";
import { signInWithEmailAndPassword, signInWithPopup } from "firebase/auth";

export default function Login() {
    const [formData, setFormData] = useState({ email: "", password: "" });
    const [message, setMessage] = useState("");
    const router = useRouter(); // Initialize useRouter

    const handleEmailLogin = async (e) => {
        e.preventDefault();
        try {
            const userCredential = await signInWithEmailAndPassword(auth, formData.email, formData.password);
            setMessage(`Welcome back, ${userCredential.user.email}!`);
            router.push("/account"); // Redirect to dashboard
        } catch (error) {
            setMessage(`Error: ${error.message}`);
        }
    };

    const handleGoogleLogin = async () => {
        try {
            const result = await signInWithPopup(auth, googleProvider);
            setMessage(`Welcome back, ${result.user.displayName || result.user.email}!`);
            router.push("/account"); // Redirect to dashboard
        } catch (error) {
            setMessage(`Error: ${error.message}`);
        }
    };

    return (
        <div className="p-4">
            <h1 className="text-2xl font-bold mb-4 text-white">Login</h1>
            <form onSubmit={handleEmailLogin}>
                <input
                    type="email"
                    placeholder="Email"
                    className="block border border-gray-300 p-2 mb-4 w-full"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                />
                <input
                    type="password"
                    placeholder="Password"
                    className="block border border-gray-300 p-2 mb-4 w-full"
                    value={formData.password}
                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                />
                <button type="submit" className="bg-blue-500 text-white p-2 rounded hover:bg-blue-600 w-full">
                    Login
                </button>
            </form>
            <button
                onClick={handleGoogleLogin}
                className="bg-red-500 text-white p-2 rounded hover:bg-red-600 w-full mt-4"
            >
                Log in with Google
            </button>
            {message && <p className="mt-4 text-red-500">{message}</p>}
            <div className="mt-4">
                <p className="text-white">
                    Don’t have an account?{" "}
                    <Link href="/signup" className="text-blue-500 hover:underline">
                        Sign Up
                    </Link>
                </p>
            </div>
        </div>
    );
}