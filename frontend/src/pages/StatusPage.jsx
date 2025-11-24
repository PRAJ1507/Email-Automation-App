import { useEffect, useState } from "react";
import { getCampaignStatus } from "../lib/api";
import StatusTable from "../components/StatusTable";

export default function StatusPage() {
  const [campaignId, setCampaignId] = useState(null);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const id = sessionStorage.getItem("campaign-id");
    if (id) setCampaignId(Number(id));
  }, []);

  useEffect(() => {
    const fetchStatus = async () => {
      if (!campaignId) return;
      setLoading(true);
      try {
        const data = await getCampaignStatus(campaignId);
        setSummary(data);
      } catch (err) {
        console.error(err);
        alert("Failed to fetch status");
      } finally {
        setLoading(false);
      }
    };
    fetchStatus();
  }, [campaignId]);

  return (
    <div className="space-y-4">
      <h1 className="text-lg font-semibold">5. Campaign status</h1>
      {!campaignId && (
        <p className="text-sm text-gray-400">
          No campaign selected. Go back to Preview and confirm contacts.
        </p>
      )}

      {loading && <p className="text-xs text-gray-400">Loading...</p>}
      <StatusTable summary={summary} />
    </div>
  );
}
