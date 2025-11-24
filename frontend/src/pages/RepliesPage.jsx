import { useEffect, useState } from "react";
import { listEmails, updateEmail } from "../lib/api";
import EmailEditor from "../components/EmailEditor";

export default function RepliesPage() {
  const [campaignId, setCampaignId] = useState(null);
  const [emails, setEmails] = useState([]);
  const [selectedEmail, setSelectedEmail] = useState(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    const id = sessionStorage.getItem("campaign-id");
    if (id) setCampaignId(Number(id));
  }, []);

  const refresh = async () => {
    if (!campaignId) return;
    const data = await listEmails(campaignId);
    // Filter: we treat replies as those without sequence_step_id (or is_reply server-side)
    const replies = data.filter((e) => e.is_reply);
    setEmails(replies);
    if (replies.length > 0) setSelectedEmail(replies[0]);
  };

  useEffect(() => {
    if (campaignId) {
      refresh();
    }
  }, [campaignId]);

  const handleSend = async () => {
    if (!selectedEmail) return;
    setSaving(true);
    try {
      await updateEmail(selectedEmail.id, {
        subject: selectedEmail.subject,
        body_text: selectedEmail.body_text,
        status: "sent",
      });
      await refresh();
    } catch (err) {
      console.error(err);
      alert("Failed to update reply");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-4">
      <h1 className="text-lg font-semibold">6. AI replies</h1>
      <p className="text-sm text-gray-400">
        This shows AI-drafted replies. For simple queries, the backend will auto-send.
        For more complex ones, they appear here for review and editing.
      </p>

      <div className="grid grid-cols-[minmax(0,1fr),minmax(0,2fr)] gap-4 mt-4">
        <div
          style={{
            borderRadius: "0.75rem",
            border: "1px solid #1f2937",
            padding: "0.75rem",
            background: "rgba(15,23,42,0.7)",
            fontSize: "0.8rem",
          }}
        >
          <div className="mb-2 text-xs text-gray-400">Reply drafts</div>
          <div style={{ maxHeight: "60vh", overflowY: "auto" }}>
            {emails.map((e) => (
              <div
                key={e.id}
                onClick={() => setSelectedEmail(e)}
                style={{
                  padding: "0.4rem 0.5rem",
                  borderRadius: "0.5rem",
                  marginBottom: "0.25rem",
                  background:
                    selectedEmail && selectedEmail.id === e.id
                      ? "#1f2937"
                      : "transparent",
                  cursor: "pointer",
                }}
              >
                <div className="text-xs text-gray-400">Reply #{e.id}</div>
                <div className="text-sm truncate">{e.subject}</div>
                <div className="text-[10px] text-gray-500">
                  Status: {e.status}
                </div>
              </div>
            ))}
            {emails.length === 0 && (
              <div className="text-xs text-gray-500">
                No reply drafts. When recipients reply, the backend will create them here.
              </div>
            )}
          </div>
        </div>

        <div className="space-y-2">
          <EmailEditor
            email={selectedEmail}
            onChange={(updated) => setSelectedEmail(updated)}
          />
          {selectedEmail && (
            <button
              onClick={handleSend}
              disabled={saving}
              style={{
                background: "#22c55e",
                color: "black",
                padding: "0.4rem 0.9rem",
                borderRadius: "9999px",
                border: "none",
                fontSize: "0.85rem",
                opacity: saving ? 0.6 : 1,
              }}
            >
              {saving ? "Updating..." : "Mark as sent / confirm"}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
