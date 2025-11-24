import { useState } from "react";
import { useNavigate } from "react-router-dom";
import FileUpload from "../components/FileUpload";
import { uploadContacts } from "../lib/api";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";

export default function UploadPage() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [preview, setPreview] = useState(null);
  const [campaignName, setCampaignName] = useState("");
  const [productName, setProductName] = useState("");
  const [productDescription, setProductDescription] = useState("");
  const navigate = useNavigate();

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    try {
      const res = await uploadContacts(file);
      setPreview(res);
      sessionStorage.setItem(
        "upload-preview",
        JSON.stringify(res.preview_rows)
      );
      sessionStorage.setItem(
        "upload-meta",
        JSON.stringify({
          campaign_name: campaignName || "My Campaign",
          product_name: productName || "My Product",
          product_description: productDescription || "",
        })
      );
      navigate("/preview");
    } catch (err) {
      console.error(err);
      alert("Failed to upload file");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <h1 className="text-lg font-semibold">1. Upload contacts</h1>

      <div className="grid sm:grid-cols-3 gap-3 text-sm">
        <div>
          <Label className="block text-xs mb-1">Campaign name</Label>
          <Input
            value={campaignName}
            onChange={(e) => setCampaignName(e.target.value)}
          />
        </div>
        <div>
          <Label className="block text-xs mb-1">Product name</Label>
          <Input
            value={productName}
            onChange={(e) => setProductName(e.target.value)}
          />
        </div>
        <div>
          <Label className="block text-xs mb-1">Product description</Label>
          <Input
            value={productDescription}
            onChange={(e) => setProductDescription(e.target.value)}
          />
        </div>
      </div>

      <FileUpload onFileSelected={setFile} />

      <Button
        disabled={!file || loading}
        onClick={handleUpload}
        className="mt-4"
      >
        {loading ? "Uploading..." : "Upload & preview"}
      </Button>
    </div>
  );
}
