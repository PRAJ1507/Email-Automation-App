import { Routes, Route, Navigate } from "react-router-dom";
import Layout from "./components/Layout";
import UploadPage from "./pages/UploadPage";
import PreviewPage from "./pages/PreviewPage";
import GeneratePage from "./pages/GeneratePage";
import SendPage from "./pages/SendPage";
import StatusPage from "./pages/StatusPage";
import RepliesPage from "./pages/RepliesPage";

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Navigate to="/upload" replace />} />
        <Route path="/upload" element={<UploadPage />} />
        <Route path="/preview" element={<PreviewPage />} />
        <Route path="/generate" element={<GeneratePage />} />
        <Route path="/send" element={<SendPage />} />
        <Route path="/status" element={<StatusPage />} />
        <Route path="/replies" element={<RepliesPage />} />
      </Routes>
    </Layout>
  );
}
