export async function fetchTransactions(accessToken, startDate, endDate) {
    try {
        const response = await fetch("http://127.0.0.1:5001/fetch-transactions", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                access_token: accessToken,
                start_date: startDate,
                end_date: endDate,
            }),
        });

        if (!response.ok) {
            throw new Error(`Error: ${response.status}`);
        }

        const data = await response.json();
        return data.transactions; // Assuming transactions is in the response
    } catch (error) {
        console.error("Error fetching transactions:", error);
        throw error;
    }
}