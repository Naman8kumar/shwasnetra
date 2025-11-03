import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

const FAQs = () => {
  const faqs = [
    {
      question: "What is ShwasNetra?",
      answer: "ShwasNetra is an AI-powered platform that analyzes chest X-rays to help detect early signs of lung cancer. It uses advanced deep learning models to provide screening insights with Grad-CAM visualizations."
    },
    {
      question: "Is ShwasNetra a replacement for a doctor?",
      answer: "No. ShwasNetra is a screening tool designed to assist healthcare professionals. It is not a diagnostic device and should not replace professional medical consultation. Always consult with qualified medical practitioners about your health."
    },
    {
      question: "What file formats are supported?",
      answer: "ShwasNetra supports JPEG, PNG, and DICOM (.dcm) files. The maximum file size is 20MB. We recommend high-quality, clear chest X-ray images for best results."
    },
    {
      question: "How accurate is the AI analysis?",
      answer: "Our AI models are trained on extensive medical datasets and show high accuracy in screening. However, no AI system is 100% accurate. Results include confidence scores and should always be reviewed by healthcare professionals."
    },
    {
      question: "What languages are supported?",
      answer: "ShwasNetra supports over 100 languages including English, Hindi, Tamil, Bengali, Spanish, French, Arabic, Chinese, and many more. The interface automatically detects your browser language and provides a manual language selector."
    },
    {
      question: "Is my medical data secure?",
      answer: "Yes. We follow HIPAA compliance standards and use encryption to protect your data. Your uploaded images and personal information are handled with the highest security standards. We never share your data without explicit consent."
    },
    {
      question: "What is a Grad-CAM heatmap?",
      answer: "Grad-CAM (Gradient-weighted Class Activation Mapping) is a visualization technique that highlights the areas of the X-ray image that the AI model focused on when making its prediction. This helps doctors understand the AI's reasoning."
    },
    {
      question: "How long does analysis take?",
      answer: "Analysis typically takes just a few seconds after uploading your scan. You'll receive instant results including the prediction label, confidence score, and Grad-CAM visualization."
    },
    {
      question: "Can I get a PDF report?",
      answer: "Yes. After analysis, you can download a comprehensive PDF report that includes the prediction, confidence scores, Grad-CAM heatmap, and patient information. This can be shared with your healthcare provider."
    },
    {
      question: "What if my image is blurry?",
      answer: "ShwasNetra includes automatic blur detection. If your image is too blurry or low resolution, you'll receive a warning to upload a clearer scan for accurate analysis."
    },
    {
      question: "Do I need to create an account?",
      answer: "For basic screening, no account is required. However, clinicians can create accounts to access prediction history and store patient records securely."
    },
    {
      question: "What should I do if the result shows cancer?",
      answer: "First, stay calm. A positive result is a screening indication, not a final diagnosis. Immediately consult with your healthcare provider who will perform additional tests and provide proper medical guidance."
    }
  ];

  return (
    <main className="min-h-screen py-12">
      <div className="container mx-auto px-4 max-w-4xl">
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            Frequently Asked Questions
          </h1>
          <p className="text-xl text-muted-foreground">
            Find answers to common questions about ShwasNetra
          </p>
        </div>

        <Accordion type="single" collapsible className="space-y-4">
          {faqs.map((faq, index) => (
            <AccordionItem
              key={index}
              value={`item-${index}`}
              className="bg-card border rounded-lg px-6 shadow-soft"
            >
              <AccordionTrigger className="text-left hover:no-underline">
                <span className="font-semibold">{faq.question}</span>
              </AccordionTrigger>
              <AccordionContent className="text-muted-foreground">
                {faq.answer}
              </AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>

        <div className="mt-12 p-6 bg-accent-light/50 rounded-2xl">
          <h2 className="text-2xl font-bold mb-4">Still Have Questions?</h2>
          <p className="text-muted-foreground mb-4">
            Can't find what you're looking for? Our support team is here to help.
          </p>
          <a
            href="/contact"
            className="inline-flex items-center justify-center px-6 py-3 bg-gradient-to-r from-primary to-accent text-white font-medium rounded-lg hover:shadow-glow transition-all"
          >
            Contact Support
          </a>
        </div>
      </div>
    </main>
  );
};

export default FAQs;
