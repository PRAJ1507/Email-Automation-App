import { Table, TableHeader, TableBody, TableHead, TableRow, TableCell } from "./ui/table";

export default function StatusTable({ summary }) {
  if (!summary) return null;

  const items = [
    { label: "Total emails", key: "total_emails" },
    { label: "Sent", key: "sent" },
    { label: "Delivered", key: "delivered" },
    { label: "Failed", key: "failed" },
    { label: "Replied", key: "replied" },
    { label: "Draft", key: "draft" },
  ];

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
        {items.map((item) => (
          <div
            key={item.key}
            style={{
              borderRadius: "0.75rem",
              border: "1px solid #1f2937",
              padding: "0.75rem",
              background: "rgba(15,23,42,0.8)",
              fontSize: "0.8rem",
            }}
          >
            <div className="text-gray-400">{item.label}</div>
            <div className="mt-1 text-lg font-semibold">
              {summary[item.key] ?? 0}
            </div>
          </div>
        ))}
      </div>

      {summary.sent_emails && summary.sent_emails.length > 0 && (
        <div>
          <h2 className="text-md font-semibold mb-2">Sent Emails Analytics</h2>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Subject</TableHead>
                <TableHead>Recipient</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Sent At</TableHead>
                <TableHead>Opens</TableHead>
                <TableHead>Clicks</TableHead>
                <TableHead>Bounced</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {summary.sent_emails.map((email) => (
                <TableRow key={email.id}>
                  <TableCell>{email.subject}</TableCell>
                  <TableCell>{email.recipient_name} ({email.recipient_email})</TableCell>
                  <TableCell>{email.status}</TableCell>
                  <TableCell>{email.sent_at ? new Date(email.sent_at).toLocaleDateString() : 'N/A'}</TableCell>
                  <TableCell>{email.open_count}</TableCell>
                  <TableCell>{email.click_count}</TableCell>
                  <TableCell>{email.bounce ? 'Yes' : 'No'}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}
    </div>
  );
}
