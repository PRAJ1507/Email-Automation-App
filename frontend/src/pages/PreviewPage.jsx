import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import ContactsTable from "../components/ContactsTable";
import { confirmContacts } from "../lib/api";

export default function PreviewPage() {
  const [rows, setRows] = useState([]);
  const [meta, setMeta] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const raw = sessionStorage.getItem("upload-preview");
    const rawMeta = sessionStorage.getItem("upload-meta");
    if (raw) {
      setRows(JSON.parse(raw));
    }
    if (rawMeta) {
      setMeta(JSON.parse(rawMeta));
    }
  }, []);

  const handleConfirm = async () => {
    if (!rows.length || !meta) return;
    setLoading(true);
    try {
      const payload = {
        campaign_name: meta.campaign_name,
        product_name: meta.product_name,
        product_description: meta.product_description,
        contacts: rows,
      };
      const res = await confirmContacts(payload);
      sessionStorage.setItem("campaign-id", String(res.id));
      navigate("/generate");
    } catch (err) {
      console.error(err);
      alert("Failed to create campaign");
    } finally {
      setLoading(false);
    }
  };

  if (!rows.length) {
    return <p className="text-sm text-gray-400">No data found. Go back to Upload.</p>;
  }

  return (
    <div className="space-y-4">
      <h1 className="text-lg font-semibold">2. Preview contacts</h1>
      {meta && (
        <p className="text-sm text-gray-400">
          Campaign: <span className="text-gray-200">{meta.campaign_name}</span> • Product:{" "}
          <span className="text-gray-200">{meta.product_name}</span>
        </p>
      )}
      <ContactsTable rows={rows} />
      <button
        onClick={handleConfirm}
        disabled={loading}
        style={{
          marginTop: "1rem",
          background: "#22c55e",
          color: "black",
          padding: "0.5rem 1rem",
          borderRadius: "9999px",
          border: "none",
          fontSize: "0.9rem",
          opacity: loading ? 0.6 : 1,
        }}
      >
        {loading ? "Creating campaign..." : "Confirm & create campaign"}
      </button>
    </div>
  );
}
