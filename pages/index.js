import { useState } from "react";

export default function Home() {
  const [udid, setUdid] = useState("");
  const [loading, setLoading] = useState(false);

  const handleGenerate = async () => {
    if (!udid) {
      alert("Please enter a UDID.");
      return;
    }

    setLoading(true);

    try {
      const res = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ udid }),
      });

      if (!res.ok) throw new Error(await res.text());

      const blob = await res.blob();
      const link = document.createElement("a");
      link.href = window.URL.createObjectURL(blob);
      link.download = `${udid}_bundle.zip`;
      link.click();
    } catch (err) {
      alert("Error generating certificate: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "2rem", fontFamily: "Arial, sans-serif" }}>
      <h1>Certificate Generator</h1>
      <p>Enter your UDID to generate a private certificate bundle.</p>
      <input
        type="text"
        placeholder="Enter UDID"
        value={udid}
        onChange={(e) => setUdid(e.target.value)}
        style={{ padding: "0.5rem", marginRight: "1rem", width: "300px" }}
      />
      <button
        onClick={handleGenerate}
        style={{ padding: "0.5rem 1rem" }}
        disabled={loading}
      >
        {loading ? "Generating..." : "Generate"}
      </button>
    </div>
  );
}
