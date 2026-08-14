import { useState } from "react";
import Login from "./Login";
import Chat from "./Chat";

export default function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(!!localStorage.getItem("token"));

  const handleLogout = () => {
    localStorage.removeItem("token");
    setIsLoggedIn(false);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {isLoggedIn && (
        <header className="bg-white border-b px-6 py-3 flex justify-between items-center shadow-sm">
          <h1 className="text-lg font-semibold text-gray-800">
            HR & GA Assistant
          </h1>
          <button
            onClick={handleLogout}
            className="text-sm text-gray-500 hover:text-red-600 border border-gray-300 rounded px-3 py-1"
          >
            Log out
          </button>
        </header>
      )}
      {isLoggedIn ? <Chat /> : <Login onLogin={() => setIsLoggedIn(true)} />}
    </div>
  );
}
