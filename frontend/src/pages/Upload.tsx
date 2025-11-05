import { useState } from "react";
import { Upload as UploadIcon, FileImage, Brain } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";

// ---------- API BASE (from Vercel env) ----------
const API_BASE = (import.meta.env.VITE_API_BASE || "").replace(/\/$/, "");

// For labels coming from backend
const labelMap: Record<string, string> = {
  Benign: "Benign",
  Malignant: "Malignant",
  Normal: "Normal",
  Unchest: "Unchest",
};

// ---------- AES-GCM ENCRYPTION ----------
async function encryptFileAES(file: File, password: string) {
  const salt = crypto.getRandomValues(new Uint8Array(16));
  const nonce = crypto.getRandomValues(new Uint8Array(12));

  const keyMaterial = await crypto.subtle.importKey("raw", new TextEncoder().encode(password), { name: "PBKDF2" }, false, [
    "deriveKey",
  ]);

  const key = await crypto.subtle.deriveKey(
    { name: "PBKDF2", salt, iterations: 200000, hash: "SHA-256" },
    keyMaterial,
    { name: "AES-GCM", length: 256 },
    false,
    ["encrypt"],
  );

  const arrayBuffer = await file.arrayBuffer();
  const encrypted = await crypto.subtle.encrypt({ name: "AES-GCM", iv: nonce }, key, arrayBuffer);

  return {
    encryptedBytes: new Uint8Array(encrypted),
    saltHex: Array.from(salt).map((b) => b.toString(16).padStart(2, "0")).join(""),
    nonceHex: Array.from(nonce).map((b) => b.toString(16).padStart(2, "0")).join(""),
  };
}

// ---------- Quick blur check to warn the user ----------
async function isImageBlurry(file: File, threshold = 100) {
  const img = document.createElement("img");
  img.src = URL.createObjectURL(file);
  await new Promise((res) => (img.onload = res));

  const canvas = document.createElement("canvas");
  const ctx = canvas.getContext("2d");
  if (!ctx) return false;

  canvas.width = img.naturalWidth;
  canvas.height = img.naturalHeight;
  ctx.drawImage(img, 0, 0);

  const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
  const gray = new Float32Array(imageData.data.length / 4);
  for (let i = 0, j = 0; i < imageData.data.length; i += 4, j++) {
    gray[j] = 0.299 * imageData.data[i] + 0.587 * imageData.data[i + 1] + 0.114 * imageData.data[i + 2];
  }

  const w = canvas.width,
    h = canvas.height;
  let sum = 0,
    mean = 0;
  const lap = new Float32Array((w - 2) * (h - 2));
  let idx = 0;

  for (let y = 1; y < h - 1; y++) {
    for (let x = 1; x < w - 1; x++) {
      const c = gray[y * w + x] * 4;
      const n = -gray[(y - 1) * w + x];
      const s = -gray[(y + 1) * w + x];
      const e = -gray[y * w + (x + 1)];
      const wv = -gray[y * w + (x - 1)];
      const val = c + n + s + e + wv;
      lap[idx++] = val;
      mean += val;
    }
  }
  mean /= lap.length;
  for (let i = 0; i < lap.length; i++) {
    const d = lap[i] - mean;
    sum += d * d;
  }
  const variance = sum / lap.length;
  URL.revokeObjectURL(img.src);
  return variance < threshold;
}

type AnalysisResult = {
  result: string;
  confidence: number;
  xray_url?: string;
  heatmap_url?: string;
  message?: string;
};

const Upload = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [blurry, setBlurry] = useState(false);
  const [aiExplanation, setAiExplanation] = useState("");

  const [age, setAge] = useState("");
  const [gender, setGender] = useState("");
  const [smoking, setSmoking] = useState("");
  const [cough, setCough] = useState("");

  const { toast } = useToast();

  // ---------- File selection ----------
  const handleFileSelect = async (file: File) => {
    const validTypes = ["image/jpeg", "image/png", "application/dicom", "application/dicom+json"];
    if (!validTypes.includes(file.type) && !file.name.endsWith(".dcm")) {
      toast({
        title: "Invalid File Type",
        description: "Please upload a JPEG, PNG, or DICOM (.dcm) file",
        variant: "destructive",
      });
      return;
    }

    setSelectedFile(file);
    toast({ title: "Checking Image Quality...", description: "Analyzing for blurriness..." });
    const blurryDetected = await isImageBlurry(file, 120);
    setBlurry(blurryDetected);

    toast({
      title: "File Selected",
      description: blurryDetected
        ? `${file.name} may be blurry. Consider re-uploading a clearer scan.`
        : `${file.name} is ready for analysis.`,
      variant: blurryDetected ? "destructive" : "default",
    });
  };

  // ---------- Analyze (calls /predict on your Render backend) ----------
  const handleAnalyze = async () => {
    if (!selectedFile) {
      toast({ title: "No File Selected", description: "Please upload a file first.", variant: "destructive" });
      return;
    }
    if (!API_BASE) {
      toast({
        title: "Configuration error",
        description: "VITE_API_BASE is not set in Vercel project settings.",
        variant: "destructive",
      });
      return;
    }

    setAnalyzing(true);
    setAiExplanation("");
    const password = "shwasnetra2025";

    try {
      const { encryptedBytes, saltHex, nonceHex } = await encryptFileAES(selectedFile, password);

      const formData = new FormData();
      formData.append("file", new Blob([encryptedBytes]), selectedFile.name);
      formData.append("salt", saltHex);
      formData.append("nonce", nonceHex);

      const response = await fetch(`${API_BASE}/predict`, { method: "POST", body: formData });
      const data = await response.json();

      if (data.status === "rejected") {
        toast({
          title: "Rejected File",
          description: data.message,
          variant: "destructive",
        });
        setResult(null);
        return;
      }

      if (response.ok && data.status === "success") {
        const confidence = typeof data.confidence === "number" ? data.confidence : parseFloat(data.confidence || 0);

        const xrayUrl = data.xray_image ? `${API_BASE}/static/heatmaps/${data.xray_image}` : undefined;
        const heatmapUrl = data.gradcam ? `${API_BASE}/static/heatmaps/${data.gradcam}` : undefined;

        const normalized: AnalysisResult = {
          result: data.prediction,
          confidence,
          xray_url: xrayUrl,
          heatmap_url: heatmapUrl,
          message: data.message,
        };
        setResult(normalized);

        toast({
          title: "Analysis Complete",
          description: `${labelMap[normalized.result] ?? normalized.result} detected (Confidence: ${normalized.confidence}%)`,
        });
      } else {
        toast({
          title: "Analysis Failed",
          description: data.error || data.message || "Please try again.",
          variant: "destructive",
        });
      }
    } catch (err) {
      console.error(err);
      toast({
        title: "Error",
        description: "Upload or analysis failed.",
        variant: "destructive",
      });
    } finally {
      setAnalyzing(false);
    }
  };

  // ---------- Download PDF (calls /download_report) ----------
  const handleDownloadReport = async () => {
    if (!result) {
      toast({ title: "No result yet", description: "Run analysis first", variant: "destructive" });
      return;
    }
    if (!API_BASE) {
      toast({
        title: "Configuration error",
        description: "VITE_API_BASE is not set in Vercel project settings.",
        variant: "destructive",
      });
      return;
    }

    const patient = { age, gender, smoking, cough };
    const payload = {
      patient,
      result: {
        result: result.result,
        confidence: result.confidence,
        gradcam: result.heatmap_url ? result.heatmap_url.split("/").pop() : undefined,
      },
      ai_explanation: aiExplanation || "",
    };

    try {
      const res = await fetch(`${API_BASE}/download_report`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "ShwasNetra_Report.pdf";
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      toast({ title: "Error", description: "Report generation failed.", variant: "destructive" });
    }
  };

  // ---------- Simple explanation (calls /chat) ----------
  const explainPrediction = async () => {
    if (!result) return;
    if (!API_BASE) {
      setAiExplanation("Configuration error: VITE_API_BASE missing.");
      return;
    }

    setAiExplanation("Explaining in layman's terms...");
    const question = `Explain this lung scan result in simple terms: ${labelMap[result.result] ?? result.result} with ${result.confidence}% confidence.`;
    try {
      const res = await fetch(`${API_BASE}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: question }),
      });
      const data = await res.json();
      setAiExplanation(data.reply || "Explanation unavailable right now.");
    } catch (err) {
      console.error(err);
      setAiExplanation("Unable to contact chatbot right now.");
    }
  };

  return (
    <main className="min-h-screen py-12 bg-background">
      <div className="container mx-auto px-4 max-w-5xl">
        <div className="text-center mb-8">
          <h1 className="text-3xl md:text-4xl font-bold mb-4">Upload Chest X-ray</h1>
          <p className="text-lg text-muted-foreground">Secure AI-based lung cancer detection powered by ShwasNetra</p>
        </div>

        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Patient Information</CardTitle>
            <CardDescription>Provide basic details for personalized report</CardDescription>
          </CardHeader>
          <CardContent className="grid md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="age">Age</Label>
              <Input id="age" type="number" value={age} onChange={(e) => setAge(e.target.value)} />
            </div>
            <div>
              <Label htmlFor="gender">Gender</Label>
              <Select value={gender} onValueChange={setGender}>
                <SelectTrigger>
                  <SelectValue placeholder="Select gender" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="male">Male</SelectItem>
                  <SelectItem value="female">Female</SelectItem>
                  <SelectItem value="other">Other</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Smoking Status</Label>
              <Select value={smoking} onValueChange={setSmoking}>
                <SelectTrigger>
                  <SelectValue placeholder="Select status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="never">Never Smoked</SelectItem>
                  <SelectItem value="former">Former Smoker</SelectItem>
                  <SelectItem value="current">Current Smoker</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Cough</Label>
              <Select value={cough} onValueChange={setCough}>
                <SelectTrigger>
                  <SelectValue placeholder="Persistent cough?" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="no">No</SelectItem>
                  <SelectItem value="yes">Yes</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Upload Scan</CardTitle>
            <CardDescription>Drag & drop or browse file</CardDescription>
          </CardHeader>
          <CardContent>
            <div
              onDragOver={(e) => {
                e.preventDefault();
                setIsDragging(true);
              }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={(e) => {
                e.preventDefault();
                setIsDragging(false);
                if (e.dataTransfer.files[0]) handleFileSelect(e.dataTransfer.files[0]);
              }}
              className={`border-2 border-dashed rounded-2xl p-12 text-center transition-all ${
                isDragging ? "border-primary bg-primary/5" : "border-border hover:border-primary/50"
              }`}
            >
              {selectedFile ? (
                <div className="space-y-4">
                  <FileImage className="h-16 w-16 mx-auto text-primary" />
                  <p className="font-semibold">{selectedFile.name}</p>
                  {blurry && <p className="text-sm text-amber-600">⚠️ Image appears blurry. Accuracy may be affected.</p>}
                  <Button variant="outline" onClick={() => setSelectedFile(null)}>
                    Remove File
                  </Button>
                </div>
              ) : (
                <div className="space-y-4">
                  <UploadIcon className="h-16 w-16 mx-auto text-muted-foreground" />
                  <p>Drop your X-ray or click below to browse</p>
                  <Button variant="outline" onClick={() => document.getElementById("file-input")?.click()}>
                    Choose File
                  </Button>
                  <input
                    id="file-input"
                    type="file"
                    accept=".jpg,.jpeg,.png,.dcm"
                    className="hidden"
                    onChange={(e) => e.target.files?.[0] && handleFileSelect(e.target.files[0])}
                  />
                </div>
              )}
            </div>

            <div className="mt-6 flex flex-col gap-3">
              <Button
                onClick={handleAnalyze}
                disabled={!selectedFile || analyzing}
                className="w-full bg-gradient-to-r from-primary to-accent text-white"
                size="lg"
              >
                {analyzing ? "Analyzing..." : "Analyze Scan"}
              </Button>

              {result && (
                <>
                  <div className="mt-6 text-center">
                    <h2 className="text-2xl font-bold">{labelMap[result.result] ?? result.result}</h2>
                    <p className="text-muted-foreground">Confidence: {result.confidence}%</p>

                    {result.xray_url && (
                      <img src={result.xray_url} alt="Chest X-ray" className="mx-auto mt-4 rounded-lg max-h-96" />
                    )}

                    {result.heatmap_url && (
                      <img src={result.heatmap_url} alt="Grad-CAM Heatmap" className="mx-auto mt-4 rounded-lg max-h-96" />
                    )}
                  </div>

                  <div className="flex flex-wrap justify-center gap-3 mt-6">
                    <Button onClick={handleDownloadReport} className="bg-primary text-white">
                      📄 Download Report
                    </Button>
                    <Button variant="outline" onClick={explainPrediction}>
                      <Brain className="mr-2 h-4 w-4" /> Explain in Layman's Terms
                    </Button>
                  </div>

                  {aiExplanation && (
                    <div className="mt-4 p-4 bg-blue-50 rounded-lg text-sm text-blue-900">
                      <strong>AI Explanation:</strong>
                      <p className="mt-2">{aiExplanation}</p>
                    </div>
                  )}
                </>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </main>
  );
};

export default Upload;
