"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation"; // For redirecting
import { auth, googleProvider } from "../../lib/firebase";
import { createUserWithEmailAndPassword, signInWithPopup } from "firebase/auth";

export default function Signup() {
    const [formData, setFormData] = useState({ email: "", password: "" });
    const [message, setMessage] = useState("");
    const router = useRouter(); // Initialize Next.js router

    const handleEmailSignup = async (e) => {
        e.preventDefault();
        try {
            // Firebase Email/Password Signup
            const userCredential = await createUserWithEmailAndPassword(auth, formData.email, formData.password);
            const user = userCredential.user;

            // Send user data to the backend
            const response = await fetch("http://127.0.0.1:5001/signup", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    user_id: user.uid,
                    email: user.email,
                    name: user.displayName || "Anonymous", // Default name if not provided
                }),
            });

            const data = await response.json();

            if (response.ok) {
                setMessage("Account created successfully! Redirecting...");
                router.push("/account"); // Redirect to account (dashboard later)
            } else {
                setMessage(`Error: ${data.message}`);
            }
        } catch (error) {
            setMessage(`Error: ${error.message}`);
        }
    };

    const handleGoogleSignup = async () => {
        try {
            // Firebase Google Signup
            const result = await signInWithPopup(auth, googleProvider);
            const user = result.user;

            // Send user data to the backend
            const response = await fetch("http://127.0.0.1:5001/signup", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    user_id: user.uid,
                    email: user.email,
                    name: user.displayName || "Anonymous", // Default name if not provided
                }),
            });

            const data = await response.json();

            if (response.ok) {
                setMessage("Account created successfully! Redirecting...");
                router.push("/account"); // Redirect to account
            } else {
                setMessage(`Error: ${data.message}`);
            }
        } catch (error) {
            setMessage(`Error: ${error.message}`);
        }
    };

    return (
        <div className="p-4">
            <h1 className="text-2xl font-bold mb-4">Signup</h1>
            <form onSubmit={handleEmailSignup}>
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
                    Sign Up
                </button>
            </form>
            <button
                onClick={handleGoogleSignup}
                className="bg-red-500 text-white p-2 rounded hover:bg-red-600 w-full mt-4"
            >
                Sign Up with Google
            </button>
            {message && <p className="mt-4 text-red-500">{message}</p>}
            <div className="mt-4">
                <p>
                    Already have an account?{" "}
                    <Link href="/login" className="text-blue-500 hover:underline">
                        Login
                    </Link>
                </p>
            </div>
        </div>
    );
}