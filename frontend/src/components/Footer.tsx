import { Link } from "react-router-dom";
import { AlertTriangle } from "lucide-react";

const Footer = () => {
  return (
    <footer className="border-t bg-secondary/30 mt-auto">
      {/* Medical Disclaimer */}
      <div className="bg-accent-light/50 border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-start space-x-3">
            <AlertTriangle className="h-5 w-5 text-accent flex-shrink-0 mt-0.5" />
            <p className="text-sm text-muted-foreground">
              <strong>Medical Disclaimer:</strong> This AI tool is not a substitute for professional medical advice, diagnosis, or treatment. 
              Always consult a qualified healthcare provider for medical decisions.
            </p>
          </div>
        </div>
      </div>

      {/* Footer Content */}
      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <div className="flex items-center space-x-2 mb-4">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-accent flex items-center justify-center">
                <span className="text-white font-bold text-lg">S</span>
              </div>
              <span className="font-bold text-lg">ShwasNetra</span>
            </div>
            <p className="text-sm text-muted-foreground">
              AI-powered early lung cancer detection for better healthcare outcomes.
            </p>
          </div>

          <div>
            <h3 className="font-semibold mb-4">Quick Links</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link to="/about" className="text-muted-foreground hover:text-foreground transition-colors">
                  About Us
                </Link>
              </li>
              <li>
                <Link to="/faqs" className="text-muted-foreground hover:text-foreground transition-colors">
                  FAQs
                </Link>
              </li>
              <li>
                <Link to="/contact" className="text-muted-foreground hover:text-foreground transition-colors">
                  Contact
                </Link>
              </li>
            </ul>
          </div>

          <div>
            <h3 className="font-semibold mb-4">Legal</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link to="/privacy" className="text-muted-foreground hover:text-foreground transition-colors">
                  Privacy Policy
                </Link>
              </li>
              <li>
                <Link to="/terms" className="text-muted-foreground hover:text-foreground transition-colors">
                  Terms of Service
                </Link>
              </li>
            </ul>
          </div>

          <div>
            <h3 className="font-semibold mb-4">Support</h3>
            <p className="text-sm text-muted-foreground mb-2">
              For medical emergencies, please contact your local emergency services immediately.
            </p>
            <p className="text-sm text-muted-foreground">
              Support: shwasnetra.care@gmail.com
            </p>
          </div>
        </div>

        <div className="border-t mt-8 pt-8 text-center text-sm text-muted-foreground">
          <p>© {new Date().getFullYear()} ShwasNetra. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
