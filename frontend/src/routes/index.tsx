import { createBrowserRouter } from "react-router-dom";
import MainLayout from "@/components/layout/MainLayout";
import Dashboard from "@/pages/Dashboard";
import ChannelsList from "@/pages/Channels/ChannelsList";
import PostsList from "@/pages/Posts/PostsList";
import PostCreate from "@/pages/Posts/PostCreate";
import VideosList from "@/pages/Videos/VideosList";
import ScheduleCalendar from "@/pages/Schedule/ScheduleCalendar";
import MediaLibrary from "@/pages/Media/MediaLibrary";
import TemplatesList from "@/pages/Templates/TemplatesList";
import UsersManagement from "@/pages/Admin/UsersManagement";
import Login from "@/pages/Auth/Login";

export const router = createBrowserRouter([
  {
    path: "/login",
    element: <Login />,
  },
  {
    path: "/",
    element: <MainLayout />,
    children: [
      {
        index: true,
        element: <Dashboard />,
      },
      {
        path: "channels",
        element: <ChannelsList />,
      },
      {
        path: "posts",
        element: <PostsList />,
      },
      {
        path: "posts/create",
        element: <PostCreate />,
      },
      {
        path: "videos",
        element: <VideosList />,
      },
      {
        path: "schedule",
        element: <ScheduleCalendar />,
      },
      {
        path: "media",
        element: <MediaLibrary />,
      },
      {
        path: "templates",
        element: <TemplatesList />,
      },
      {
        path: "admin/users",
        element: <UsersManagement />,
      },
    ],
  },
]);
