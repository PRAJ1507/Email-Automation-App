export default function EmailEditor({ email, onChange }) {
  if (!email) return null;

  return (
    <div
      style={{
        borderRadius: "0.75rem",
        border: "1px solid #1f2937",
        padding: "1rem",
        background: "rgba(15,23,42,0.8)",
      }}
    >
      <div className="mb-2 text-xs text-gray-400">
        Contact #{email.contact_id} • Step {email.sequence_step_id ?? "N/A"}
      </div>
      <label className="block text-xs text-gray-400 mb-1">Subject</label>
      <input
        className="w-full mb-3"
        style={{
          background: "#020617",
          borderRadius: "0.5rem",
          border: "1px solid #1f2937",
          padding: "0.5rem",
          color: "white",
          fontSize: "0.85rem",
        }}
        value={email.subject}
        onChange={(e) => onChange({ ...email, subject: e.target.value })}
      />
      <label className="block text-xs text-gray-400 mb-1">Body</label>
      <textarea
        rows={8}
        className="w-full"
        style={{
          background: "#020617",
          borderRadius: "0.5rem",
          border: "1px solid #1f2937",
          padding: "0.5rem",
          color: "white",
          fontSize: "0.85rem",
        }}
        value={email.body_text}
        onChange={(e) => onChange({ ...email, body_text: e.target.value })}
      />
    </div>
  );
}
