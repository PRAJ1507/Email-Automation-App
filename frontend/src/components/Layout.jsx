import { NavLink, useLocation } from "react-router-dom";

const navItems = [
  { to: "/upload", label: "Upload" },
  { to: "/preview", label: "Preview" },
  { to: "/generate", label: "Generate" },
  { to: "/send", label: "Send" },
  { to: "/status", label: "Status" },
  { to: "/replies", label: "Replies" }
];

export default function Layout({ children }) {
  const location = useLocation();

  return (
    <div className="min-h-screen bg-[#050711] text-gray-100">
      <header className="border-b border-gray-800 px-6 py-4 flex items-center justify-between">
        <div className="font-semibold tracking-tight text-sm sm:text-base">
          MailFlow (demo)
        </div>
        <nav className="flex gap-3 text-xs sm:text-sm text-gray-400">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={
                location.pathname === item.to
                  ? "text-indigo-300"
                  : "hover:text-gray-200"
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
      </header>
      <main className="max-w-5xl mx-auto px-4 py-6">{children}</main>
    </div>
  );
}
