export default function FileUpload({ onFileSelected }) {
  return (
    <div
      style={{
        border: "1px dashed #4b5563",
        borderRadius: "0.75rem",
        padding: "1.5rem",
        textAlign: "center",
        background: "rgba(15,23,42,0.7)",
      }}
    >
      <p className="mb-2 text-sm text-gray-300">
        Upload a CSV or Excel file with your contacts.
      </p>
      <input
        type="file"
        accept=".csv, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel"
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) onFileSelected(file);
        }}
      />
    </div>
  );
}
