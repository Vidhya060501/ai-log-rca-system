import React, { useState } from "react";
import axios from "axios";
import { Upload, FileText, CheckCircle, AlertCircle } from "lucide-react";
import "./LogUpload.css";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

function LogUpload({ sessionId }) {
  // IMPORTANT: keep logs as STRING always
  const [logs, setLogs] = useState("");
  const [uploading, setUploading] = useState(false);
  const [status, setStatus] = useState(null);

  const normalizeToLines = (value) => {
    const text = typeof value === "string" ? value : String(value ?? "");
    return text
      .split("\n")
      .map((l) => (typeof l === "string" ? l.trim() : String(l).trim()))
      .filter(Boolean);
  };

  const handleUpload = async () => {
    // Make sure logs is treated as a string
    const logsText = typeof logs === "string" ? logs : String(logs ?? "");

    if (!logsText.trim()) {
      setStatus({ type: "error", message: "Please enter some logs" });
      return;
    }

    setUploading(true);
    setStatus(null);

    try {
      const logLines = normalizeToLines(logsText);

      const response = await axios.post(`${API_BASE_URL}/api/logs/upload`, {
        logs: logLines,
        metadata: {
          source: "manual_upload",
          timestamp: new Date().toISOString(),
          session_id: sessionId,
        },
      });

      setStatus({
        type: "success",
        message: `Successfully indexed ${response.data.indexed_count} log entries`,
      });
      setLogs(""); // clear after upload
    } catch (error) {
      console.error("Upload error:", error);
      setStatus({
        type: "error",
        message: error.response?.data?.detail || error.message || "Failed to upload logs",
      });
    } finally {
      setUploading(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setStatus(null);

    const reader = new FileReader();
    reader.onload = (event) => {
      const content = event?.target?.result ?? "";
      // Ensure we store STRING
      setLogs(typeof content === "string" ? content : String(content));
    };
    reader.onerror = () => {
      setStatus({ type: "error", message: "Failed to read file" });
    };

    reader.readAsText(file);

    // Reset input so picking the same file again triggers onChange
    e.target.value = "";
  };

  return (
    <div className="log-upload">
      <h3>Upload Logs</h3>

      <div className="upload-section">
        <label className="file-upload-label">
          <input
            type="file"
            accept=".log,.txt"
            onChange={handleFileUpload}
            disabled={uploading}
            className="file-input"
          />
          <div className="file-upload-button">
            <Upload size={20} />
            <span>Choose File</span>
          </div>
        </label>
      </div>

      <div className="text-area-section">
        <label htmlFor="logs-textarea">
          <FileText size={16} />
          Or paste logs directly:
        </label>
        <textarea
          id="logs-textarea"
          value={logs}
          onChange={(e) => setLogs(e.target.value)}
          placeholder="Paste your log entries here, one per line..."
          rows={10}
          disabled={uploading}
          className="logs-textarea"
        />
      </div>

      <button
        type="button"
        onClick={handleUpload}
        disabled={uploading || !String(logs ?? "").trim()}
        className="upload-button"
      >
        {uploading ? "Uploading..." : "Upload & Index Logs"}
      </button>

      {status && (
        <div className={`status-message ${status.type}`}>
          {status.type === "success" ? <CheckCircle size={16} /> : <AlertCircle size={16} />}
          <span>{status.message}</span>
        </div>
      )}

      <div className="info-box">
        <p><strong>Tips:</strong></p>
        <ul>
          <li>Upload logs to enable semantic search</li>
          <li>Each line is treated as a separate log entry</li>
          <li>Logs are indexed for AI analysis</li>
        </ul>
      </div>
    </div>
  );
}

export default LogUpload;
