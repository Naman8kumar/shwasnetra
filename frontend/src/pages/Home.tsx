import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Upload, Shield, Globe, MessageSquare, FileText, Activity } from "lucide-react";
import heroImage from "@/assets/hero-medical.jpg";
import aiAnalysisImage from "@/assets/ai-analysis.jpg";

const Home = () => {
  return (
    <main className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-transparent to-accent/10"></div>
        
        <div className="container mx-auto px-4 py-16 md:py-24">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div className="space-y-6 animate-fade-in-up">
              <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold leading-tight">
                Early Lung Cancer Detection with{" "}
                <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                  AI Technology
                </span>
              </h1>
              
              <p className="text-lg text-muted-foreground">
                ShwasNetra uses advanced artificial intelligence to analyze chest X-rays 
                and provide early detection insights with compassionate, multilingual support.
              </p>

              <div className="flex flex-col sm:flex-row gap-4">
                <Button
                  asChild
                  size="lg"
                  className="bg-gradient-to-r from-primary to-accent text-white hover:shadow-glow transition-all"
                >
                  <Link to="/upload">Upload Scan</Link>
                </Button>
                
                <Button asChild size="lg" variant="outline">
                  <Link to="/about">Learn More</Link>
                </Button>
              </div>

              <div className="flex items-center space-x-2 text-sm text-muted-foreground pt-4">
                <Shield className="h-4 w-4 text-accent" />
                <span>HIPAA Compliant • Secure • Confidential</span>
              </div>
            </div>

            <div className="relative animate-fade-in">
              <div className="absolute inset-0 bg-gradient-to-br from-primary/20 to-accent/20 rounded-3xl blur-3xl"></div>
              <img
                src={heroImage}
                alt="Medical professional using AI technology for lung cancer detection"
                className="relative rounded-3xl shadow-strong w-full h-auto"
              />
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 bg-secondary/30">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Why Choose ShwasNetra?
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Advanced AI technology combined with compassionate care for accurate lung cancer screening
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                icon: Upload,
                title: "Easy Upload",
                description: "Drag & drop your chest X-rays or DICOM files for instant analysis"
              },
              {
                icon: Activity,
                title: "AI-Powered Analysis",
                description: "Advanced deep learning models provide accurate predictions with confidence scores"
              },
              {
                icon: FileText,
                title: "Detailed Reports",
                description: "Grad-CAM heatmaps and comprehensive PDF reports for healthcare providers"
              },
              {
                icon: Globe,
                title: "Multilingual Support",
                description: "Available in 100+ languages including all major Indian and global languages"
              },
              {
                icon: MessageSquare,
                title: "AI Chatbot",
                description: "Get instant answers about lung health and understand your results"
              },
              {
                icon: Shield,
                title: "Secure & Private",
                description: "Your medical data is encrypted and handled with utmost care"
              },
            ].map((feature, index) => (
              <div
                key={index}
                className="p-6 bg-card rounded-2xl shadow-soft hover:shadow-medium transition-all duration-300 animate-fade-in"
                style={{ animationDelay: `${index * 100}ms` }}
              >
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center mb-4">
                  <feature.icon className="h-6 w-6 text-white" />
                </div>
                <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
                <p className="text-muted-foreground">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-16">
        <div className="container mx-auto px-4">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div className="order-2 lg:order-1">
              <img
                src={aiAnalysisImage}
                alt="AI neural network analyzing chest X-ray"
                className="rounded-3xl shadow-strong w-full h-auto"
              />
            </div>

            <div className="order-1 lg:order-2 space-y-6">
              <h2 className="text-3xl md:text-4xl font-bold">
                How ShwasNetra Works
              </h2>
              
              <div className="space-y-4">
                {[
                  {
                    step: "1",
                    title: "Upload Your Scan",
                    description: "Upload chest X-ray or DICOM files securely"
                  },
                  {
                    step: "2",
                    title: "AI Analysis",
                    description: "Our AI model analyzes the image in seconds"
                  },
                  {
                    step: "3",
                    title: "Get Results",
                    description: "Receive predictions with Grad-CAM heatmap visualization"
                  },
                  {
                    step: "4",
                    title: "Consult Professional",
                    description: "Share results with your healthcare provider"
                  },
                ].map((item) => (
                  <div key={item.step} className="flex space-x-4">
                    <div className="flex-shrink-0 w-12 h-12 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center text-white font-bold text-lg">
                      {item.step}
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold mb-1">{item.title}</h3>
                      <p className="text-muted-foreground">{item.description}</p>
                    </div>
                  </div>
                ))}
              </div>

              <Button
                asChild
                size="lg"
                className="bg-gradient-to-r from-primary to-accent text-white"
              >
                <Link to="/upload">Start Your Screening</Link>
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 bg-gradient-to-r from-primary to-accent">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            Ready to Get Started?
          </h2>
          <p className="text-xl text-white/90 mb-8 max-w-2xl mx-auto">
            Early detection saves lives. Upload your chest X-ray today for AI-powered analysis.
          </p>
          <Button
            asChild
            size="lg"
            variant="secondary"
            className="bg-white text-primary hover:bg-white/90"
          >
            <Link to="/upload">Upload Your Scan Now</Link>
          </Button>
        </div>
      </section>
    </main>
  );
};

export default Home;
