import { Link, useLocation } from "react-router-dom";
import { ROUTES } from "@/config/routes";

const menuItems = [
  { path: ROUTES.DASHBOARD, label: "Dashboard", icon: "📊" },
  { path: ROUTES.CHANNELS, label: "Channels", icon: "📺" },
  { path: ROUTES.POSTS, label: "Posts", icon: "📝" },
  { path: ROUTES.MEDIA, label: "Media", icon: "🖼️" },
  { path: ROUTES.ANALYTICS, label: "Analytics", icon: "📈" },
];

export const Sidebar = () => {
  const location = useLocation();

  return (
    <aside className="w-64 bg-white border-r min-h-screen sticky top-16">
      <nav className="p-4 space-y-2">
        {menuItems.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-3 px-4 py-3 rounded-lg transition ${
                isActive
                  ? "bg-blue-500 text-white shadow-md"
                  : "text-gray-700 hover:bg-gray-100"
              }`}
            >
              <span className="text-xl">{item.icon}</span>
              <span className="font-medium">{item.label}</span>
            </Link>
          );
        })}
      </nav>
    </aside>
  );
};
