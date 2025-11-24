import { useEffect, useState } from "react";
import { generateEmails, listEmails, updateEmail, listContacts } from "../lib/api";
import EmailEditor from "../components/EmailEditor";

export default function GeneratePage() {
  const [campaignId, setCampaignId] = useState(null);
  const [contacts, setContacts] = useState([]);
  const [selectedContacts, setSelectedContacts] = useState([]);
  const [emails, setEmails] = useState([]);
  const [selectedEmail, setSelectedEmail] = useState(null);
  const [loadingGen, setLoadingGen] = useState(false);
  const [saving, setSaving] = useState(false);

  const handleGenerate = async () => {
    if (!campaignId) return;
    setLoadingGen(true);
    try {
      const contactIds = selectedContacts.length > 0 ? selectedContacts : undefined;
      await generateEmails(campaignId, contactIds);
      await refreshEmails();
    } catch (err) {
      console.error(err);
      alert("Failed to generate emails");
    } finally {
      setLoadingGen(false);
    }
  };

  useEffect(() => {
    const id = sessionStorage.getItem("campaign-id");
    if (id) setCampaignId(Number(id));
  }, []);

  useEffect(() => {
    const fetchContacts = async () => {
      try {
        const data = await listContacts();
        setContacts(data);
      } catch (err) {
        console.error(err);
      }
    };
    fetchContacts();
  }, []);

  const refreshEmails = async () => {
    if (!campaignId) return;
    const data = await listEmails(campaignId);
    setEmails(data);
    if (data.length > 0) setSelectedEmail(data[0]);
  };

  useEffect(() => {
    if (campaignId) {
      refreshEmails();
    }
  }, [campaignId]);

  const handleSave = async () => {
    if (!selectedEmail) return;
    setSaving(true);
    try {
      await updateEmail(selectedEmail.id, {
        subject: selectedEmail.subject,
        body_text: selectedEmail.body_text,
      });
      await refreshEmails();
    } catch (err) {
      console.error(err);
      alert("Failed to save email");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-4">
      <h1 className="text-lg font-semibold">3. Generate & edit emails</h1>
      {!campaignId && (
        <p className="text-sm text-gray-400">
          No campaign selected. Go back to Preview and confirm contacts.
        </p>
      )}

      <button
        onClick={handleGenerate}
        disabled={!campaignId || loadingGen}
        style={{
          background: "#4f46e5",
          color: "white",
          padding: "0.5rem 1rem",
          borderRadius: "9999px",
          border: "none",
          fontSize: "0.9rem",
          opacity: !campaignId || loadingGen ? 0.6 : 1,
        }}
      >
        {loadingGen ? "Generating..." : "Generate sequence"}
      </button>

      {contacts.length > 0 && (
        <div className="mt-4">
          <p className="text-sm text-gray-500">Generating for all {contacts.length} contacts (idempotent, no duplicates).</p>
        </div>
      )}

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
          <div className="mb-2 text-xs text-gray-400">Drafts</div>
          <div
            style={{
              maxHeight: "60vh",
              overflowY: "auto",
            }}
          >
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
                <div className="text-xs text-gray-400">
                  #{e.id} • Contact {e.contact_id} • Step{" "}
                  {e.sequence_step_id ?? "N/A"}
                </div>
                <div className="text-sm truncate">{e.subject}</div>
              </div>
            ))}
            {emails.length === 0 && (
              <div className="text-xs text-gray-500">
                No drafts yet. Click "Generate sequence".
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
              onClick={handleSave}
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
              {saving ? "Saving..." : "Save draft"}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
