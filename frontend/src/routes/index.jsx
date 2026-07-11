import { Routes, Route } from "react-router-dom";

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<h1>Home</h1>} />
    </Routes>
  );
}