import { useState } from "react";
import api from "./api";

export default function Login({ onLogin }) {
  const [employeeId, setEmployeeId] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      const response = await api.post("/auth/login", {
        employee_id: employeeId,
        password: password,
      });
      localStorage.setItem("token", response.data.access_token);
      onLogin();
    } catch (err) {
      setError("Invalid employee ID or password.");
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="max-w-sm mx-auto mt-20 p-6 bg-white rounded-lg shadow"
    >
      <h1 className="text-xl font-semibold mb-4">HR & GA Assistant</h1>
      <input
        className="w-full border rounded px-3 py-2 mb-3"
        placeholder="Employee ID"
        value={employeeId}
        onChange={(e) => setEmployeeId(e.target.value)}
      />
      <input
        className="w-full border rounded px-3 py-2 mb-3"
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      {error && <p className="text-red-500 text-sm mb-3">{error}</p>}
      <button className="w-full bg-blue-600 text-white rounded py-2 hover:bg-blue-700">
        Log In
      </button>
    </form>
  );
}
