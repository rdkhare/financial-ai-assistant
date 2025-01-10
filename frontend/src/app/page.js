"use client";

import { useEffect, useState } from "react";

export default function Home() {
    const [message, setMessage] = useState("");

    // useEffect(() => {
    //     fetch("http://127.0.0.1:5001/")
    //         .then((response) => response.json())
    //         .then((data) => setMessage(data.message))
    //         .catch((error) => console.error("Error fetching data:", error));
    // }, []);

    return (
        <div className="flex flex-col items-center justify-center h-screen">
            <h1 className="text-4xl text-gray-100">
                Welcome to the Financial Assistant AI
            </h1>
        </div>
    );
}