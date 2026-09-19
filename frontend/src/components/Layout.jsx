import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const NAV_ITEMS = [
  { to: "/dashboard", label: "Dashboard" },
  { to: "/urge", label: "Log an urge" },
  { to: "/onboarding", label: "Add a behavior" },
  { to: "/analytics", label: "Analytics" },
  { to: "/history", label: "History" },
  { to: "/profile", label: "Profile" },
];

export default function Layout() {
  const { user } = useAuth();

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar-brand">Break the Loop</div>
        <nav className="sidebar-nav">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) => `sidebar-link${isActive ? " active" : ""}`}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-footer">{user?.name}</div>
      </aside>
      <main className="main-area">
        <div className="content">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
