import { useState, useEffect } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "./ui/dialog";
import { Button } from "./ui/button";
import { Checkbox } from "./ui/checkbox";

const ConsentModal = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [accepted, setAccepted] = useState(false);

  useEffect(() => {
    const hasConsented = localStorage.getItem("shwasnetra-consent");
    if (!hasConsented) {
      setTimeout(() => setIsOpen(true), 1000); // open after short delay
    }
  }, []);

  const handleAccept = () => {
    if (accepted) {
      const timestamp = new Date().toISOString();
      localStorage.setItem("shwasnetra-consent", timestamp);
      setIsOpen(false);
    } else {
      alert("Please check the box to proceed.");
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogContent className="sm:max-w-[550px] rounded-2xl shadow-2xl border border-primary/20">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold text-primary">
            🩺 Informed Patient Consent
          </DialogTitle>

          <DialogDescription asChild>
            <div className="text-base space-y-4 pt-4 leading-relaxed text-muted-foreground">
              <p>
                Welcome to <strong>ShwasNetra</strong>, an AI-powered lung cancer
                detection and screening platform. Before using our service,
                please review the consent details carefully.
              </p>

              <div>
                <p className="font-semibold mb-1">
                  By using this AI service, you acknowledge and agree that:
                </p>
                <ul className="list-disc list-inside space-y-2">
                  <li>
                    This AI tool provides preliminary screening assistance, not a
                    definitive medical diagnosis.
                  </li>
                  <li>
                    All predictions should be reviewed by a qualified healthcare
                    professional.
                  </li>
                  <li>
                    Uploaded scans are processed securely and not stored
                    permanently.
                  </li>
                  <li>
                    This platform does <strong>not replace professional medical
                    consultation</strong>.
                  </li>
                </ul>
              </div>

              <p>
                ShwasNetra complies with HIPAA and relevant medical data privacy
                standards. You can learn more by visiting our{" "}
                <a
                  href="/privacy"
                  className="text-primary underline hover:text-primary/80"
                >
                  Privacy Policy
                </a>
                .
              </p>
            </div>
          </DialogDescription>
        </DialogHeader>

        {/* Checkbox Section */}
        <div className="flex items-center space-x-3 py-4 border-t mt-4">
          <Checkbox
            id="consent"
            checked={accepted}
            onCheckedChange={(checked) => setAccepted(checked as boolean)}
          />
          <label
            htmlFor="consent"
            className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
          >
            I understand and accept the terms above.
          </label>
        </div>

        {/* Footer Buttons */}
        <DialogFooter>
          <Button
            onClick={handleAccept}
            disabled={!accepted}
            className="w-full bg-gradient-to-r from-primary to-accent text-white shadow-md hover:shadow-lg transition-all"
          >
            I Accept & Continue
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default ConsentModal;
