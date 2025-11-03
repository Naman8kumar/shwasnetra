import { Shield, Users, Award, Heart } from "lucide-react";

const About = () => {
  return (
    <main className="min-h-screen py-12">
      <div className="container mx-auto px-4 max-w-4xl">
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">About ShwasNetra</h1>
          <p className="text-xl text-muted-foreground">
            Advanced AI technology for early lung cancer detection
          </p>
        </div>

        <div className="prose prose-lg max-w-none space-y-8">
          <section>
            <h2 className="text-3xl font-bold mb-4">Our Mission</h2>
            <p className="text-muted-foreground">
              ShwasNetra is dedicated to revolutionizing lung cancer screening through 
              cutting-edge artificial intelligence. Our mission is to make early detection 
              accessible, accurate, and compassionate for everyone, regardless of language 
              or location.
            </p>
          </section>

          <section className="grid md:grid-cols-2 gap-6 my-12">
            {[
              {
                icon: Shield,
                title: "Medical Trust",
                description: "Our AI models are trained on extensive medical datasets and validated by healthcare professionals"
              },
              {
                icon: Users,
                title: "Global Access",
                description: "Supporting 100+ languages to ensure healthcare equity worldwide"
              },
              {
                icon: Award,
                title: "Clinical Accuracy",
                description: "High precision in detecting early-stage lung cancer indicators"
              },
              {
                icon: Heart,
                title: "Compassionate Care",
                description: "Designed with empathy and patient-centered communication"
              }
            ].map((item, index) => (
              <div key={index} className="p-6 bg-card rounded-2xl shadow-soft">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center mb-4">
                  <item.icon className="h-6 w-6 text-white" />
                </div>
                <h3 className="text-xl font-semibold mb-2">{item.title}</h3>
                <p className="text-muted-foreground">{item.description}</p>
              </div>
            ))}
          </section>

          <section>
            <h2 className="text-3xl font-bold mb-4">How Our AI Works</h2>
            <p className="text-muted-foreground mb-4">
              ShwasNetra uses deep learning models trained on thousands of chest X-rays to 
              identify patterns associated with lung cancer. Our technology includes:
            </p>
            <ul className="space-y-2 text-muted-foreground">
              <li>• Advanced convolutional neural networks for image analysis</li>
              <li>• Grad-CAM visualization to highlight areas of concern</li>
              <li>• Confidence scoring for transparent decision-making</li>
              <li>• Multi-language AI chatbot for patient education</li>
              <li>• Blur detection to ensure image quality</li>
            </ul>
          </section>

          <section>
            <h2 className="text-3xl font-bold mb-4">Medical Disclaimer</h2>
            <div className="p-6 bg-accent-light/50 rounded-lg border border-accent/20">
              <p className="text-muted-foreground">
                <strong>Important:</strong> ShwasNetra is a screening tool designed to assist 
                healthcare professionals. It is not a diagnostic device and should not replace 
                professional medical consultation. All results should be reviewed by qualified 
                medical practitioners. If you have concerns about your lung health, please 
                consult your doctor immediately.
              </p>
            </div>
          </section>

          <section>
            <h2 className="text-3xl font-bold mb-4">Our Commitment</h2>
            <p className="text-muted-foreground">
              We are committed to continuous improvement of our AI models, maintaining the 
              highest standards of data security and privacy, and making lung cancer screening 
              accessible to communities worldwide. Your trust and health are our top priorities.
            </p>
          </section>
        </div>
      </div>
    </main>
  );
};

export default About;
