export default function ContactsTable({ rows }) {
  if (!rows || rows.length === 0) {
    return <p className="text-sm text-gray-400">No preview data.</p>;
  }

  const cols = ["email", "first_name", "company", "role", "hobbies", "mbti_type"];

  return (
    <div
      style={{
        borderRadius: "0.75rem",
        border: "1px solid #1f2937",
        overflow: "hidden",
      }}
    >
      <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.85rem" }}>
        <thead style={{ background: "#111827" }}>
          <tr>
            {cols.map((col) => (
              <th
                key={col}
                style={{
                  padding: "0.5rem 0.75rem",
                  textAlign: "left",
                  borderBottom: "1px solid #1f2937",
                  textTransform: "capitalize",
                }}
              >
                {col.replace("_", " ")}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((r, idx) => (
            <tr key={idx} style={{ background: idx % 2 === 0 ? "#020617" : "#020617" }}>
              {cols.map((col) => (
                <td
                  key={col}
                  style={{
                    padding: "0.4rem 0.75rem",
                    borderBottom: "1px solid #111827",
                    color: "#e5e7eb",
                  }}
                >
                  {r[col] ?? ""}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
