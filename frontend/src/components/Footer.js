export default function Footer() {
    return (
        <footer className="bg-gray-900 text-white p-4 text-center">
            <p>&copy; {new Date().getFullYear()} Financial Assistant AI. All rights reserved.</p>
        </footer>
    );
}