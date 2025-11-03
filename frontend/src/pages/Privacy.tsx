const Privacy = () => {
  return (
    <main className="min-h-screen py-12">
      <div className="container mx-auto px-4 max-w-4xl">
        <h1 className="text-4xl md:text-5xl font-bold mb-8">Privacy Policy</h1>
        
        <div className="prose prose-lg max-w-none space-y-8 text-muted-foreground">
          <section>
            <p className="text-sm text-muted-foreground mb-4">Last updated: October 2025</p>
            <p>
              At ShwasNetra, we take your privacy seriously. This Privacy Policy explains how we 
              collect, use, and protect your personal and medical information.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-foreground mb-4">Information We Collect</h2>
            <ul className="space-y-2">
              <li>• Medical images (chest X-rays and DICOM files)</li>
              <li>• Patient demographic information (age, gender)</li>
              <li>• Medical history information (smoking status, symptoms)</li>
              <li>• Technical information (IP address, browser type, device information)</li>
              <li>• Usage data and analytics</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-foreground mb-4">How We Use Your Information</h2>
            <ul className="space-y-2">
              <li>• To perform AI analysis on uploaded medical images</li>
              <li>• To generate screening reports and visualizations</li>
              <li>• To improve our AI models and algorithms</li>
              <li>• To provide customer support and respond to inquiries</li>
              <li>• To comply with legal and regulatory requirements</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-foreground mb-4">Data Security</h2>
            <p>
              We implement industry-standard security measures to protect your data:
            </p>
            <ul className="space-y-2 mt-4">
              <li>• End-to-end encryption for data transmission</li>
              <li>• Secure cloud storage with access controls</li>
              <li>• Regular security audits and updates</li>
              <li>• HIPAA-compliant infrastructure</li>
              <li>• Limited access to authorized personnel only</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-foreground mb-4">Data Sharing</h2>
            <p>
              We do not sell your personal or medical information. We may share data only in the 
              following circumstances:
            </p>
            <ul className="space-y-2 mt-4">
              <li>• With your explicit consent</li>
              <li>• With healthcare providers you authorize</li>
              <li>• To comply with legal obligations</li>
              <li>• For research purposes (anonymized data only)</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-foreground mb-4">Your Rights</h2>
            <p>You have the right to:</p>
            <ul className="space-y-2 mt-4">
              <li>• Access your personal and medical data</li>
              <li>• Request correction of inaccurate data</li>
              <li>• Request deletion of your data</li>
              <li>• Withdraw consent for data processing</li>
              <li>• Export your data in a portable format</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-foreground mb-4">Data Retention</h2>
            <p>
              We retain your data for as long as necessary to provide our services and comply with 
              legal obligations. Medical images and analysis results are typically retained for 
              7 years unless you request earlier deletion.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-foreground mb-4">International Data Transfers</h2>
            <p>
              Your data may be transferred to and processed in countries other than your own. 
              We ensure appropriate safeguards are in place for international transfers.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-foreground mb-4">Children's Privacy</h2>
            <p>
              Our service is not intended for children under 13. We do not knowingly collect 
              information from children without parental consent.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-foreground mb-4">Changes to This Policy</h2>
            <p>
              We may update this Privacy Policy from time to time. We will notify you of significant 
              changes by email or through our platform.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-foreground mb-4">Contact Us</h2>
            <p>
              If you have questions about this Privacy Policy or wish to exercise your rights, 
              please contact us at:
            </p>
            <p className="mt-4">
              <strong>Email:</strong> <br />
              shwasnetra.care@gmail.com
            </p>
          </section>
        </div>
      </div>
    </main>
  );
};

export default Privacy;
