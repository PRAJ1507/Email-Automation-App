import { useEffect, useState } from "react";
import { sendEmails } from "../lib/api";

export default function SendPage() {
  const [campaignId, setCampaignId] = useState(null);
  const [stepNumber, setStepNumber] = useState(1);
  const [loading, setLoading] = useState(false);
  const [lastSent, setLastSent] = useState(null);

  useEffect(() => {
    const id = sessionStorage.getItem("campaign-id");
    if (id) setCampaignId(Number(id));
  }, []);

  const handleSend = async () => {
    if (!campaignId) return;
    setLoading(true);
    try {
      const count = await sendEmails(campaignId, stepNumber);
      setLastSent({ step: stepNumber, count });
    } catch (err) {
      console.error(err);
      alert("Failed to send emails");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <h1 className="text-lg font-semibold">4. Send emails</h1>
      {!campaignId && (
        <p className="text-sm text-gray-400">
          No campaign selected. Go back to Preview and confirm contacts.
        </p>
      )}

      <div className="space-y-2 text-sm">
        <label className="block text-xs text-gray-400">Sequence step</label>
        <select
          value={stepNumber}
          onChange={(e) => setStepNumber(Number(e.target.value))}
          style={{
            background: "#020617",
            borderRadius: "0.5rem",
            border: "1px solid #1f2937",
            padding: "0.4rem 0.6rem",
            color: "white",
          }}
        >
          <option value={1}>1 - Initial email</option>
          <option value={2}>2 - Follow-up</option>
          <option value={3}>3 - Final reminder</option>
        </select>
      </div>

      <button
        onClick={handleSend}
        disabled={!campaignId || loading}
        style={{
          background: "#f97316",
          color: "black",
          padding: "0.5rem 1rem",
          borderRadius: "9999px",
          border: "none",
          fontSize: "0.9rem",
          opacity: !campaignId || loading ? 0.6 : 1,
        }}
      >
        {loading ? "Sending..." : "Send now"}
      </button>

      {lastSent && (
        <p className="text-xs text-gray-400">
          Sent {lastSent.count} emails for step {lastSent.step}.
        </p>
      )}
    </div>
  );
}
