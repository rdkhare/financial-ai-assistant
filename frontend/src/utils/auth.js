export function isAuthenticated() {
    const token = localStorage.getItem("token");
    return !!token; // Returns true if a token exists
}