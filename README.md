🩺 ShwasNetra
AI-Guided Screening for Early Lung Cancer Detection — With Explainability and Trust Built-In

“The most meaningful technology is the kind that protects human life.”

ShwasNetra (“The Eye of Breath” in Sanskrit) is a clinical decision support system that analyzes chest X-rays to assist in the early identification of lung cancer, a disease often diagnosed too late.
It is built with three non-negotiable principles: accuracy, interpretability, and patient data privacy.

The project reflects a simple question that emerged from personal experience with respiratory health challenges:

Can we empower clinicians with reliable, interpretable insights — without replacing their judgment?

ShwasNetra is the result of that pursuit.

🎯 Problem

Lung cancer accounts for some of the highest global cancer mortality rates, largely due to late diagnosis. In many regions:

Radiologists face heavy caseloads

Specialized oncology expertise is limited

Subtle early-stage patterns are difficult to detect consistently

AI can augment, not replace, medical judgment — improving screening sensitivity while preserving clinician oversight.

🧠 Technical Overview
Dataset

1,491 clinically-labeled chest X-rays across:

Normal

Benign Nodules

Malignant Tumors

Other Lung Abnormalities

| Step                                      | Purpose                          |
| ----------------------------------------- | -------------------------------- |
| 224×224 resizing                          | Standard input shape             |
| Histogram equalization                    | Improved contrast                |
| Gaussian noise reduction                  | Visual clarity                   |
| Augmentation (±15° rotation, zoom, flips) | Class balance + model robustness |
| Per-channel normalization                 | Training stability               |

Split: 85% training, 15% validation

⚙️ Model Architecture

ShwasNetra uses MobileNetV2 for efficient, scalable inference — from clinical workstations to edge devices.

model = Sequential([
    base_model,
    GlobalAveragePooling2D(),
    Dropout(0.3),
    Dense(512, activation='relu'),
    BatchNormalization(),
    Dense(4, activation='softmax')
])

| Component       | Configuration             |
| --------------- | ------------------------- |
| Optimizer       | Adam (1e-3)               |
| Loss            | Categorical Cross-Entropy |
| Learning Policy | ReduceLROnPlateau         |
| Regularization  | Dropout + BatchNorm       |
| Early Stopping  | Patience = 10             |

Outcome: Stable convergence in ~30 epochs with balanced generalization.

| Metric                 | Result                      |
| ---------------------- | --------------------------- |
| Training Accuracy      | **97.4%**                   |
| Validation Accuracy    | **88.3%**                   |
| Validation Loss        | **0.46**                    |
| Average Inference Time | **1.8 seconds/image** (CPU) |

Notably:

Smooth learning curves
No high-frequency oscillations
Strong generalization without aggressive regularization

🔍 Explainability (Grad-CAM)

Medical AI must be interpretable.

ShwasNetra overlays gradient-based activation heatmaps to show exactly which regions influenced the prediction.

This enables:
Radiologist verification
Avoidance of “black-box” decision risks
Improved clinician trust and adoption viability

🔒 Data Privacy & Security: AES-GCM Encryption

Medical images are encrypted before leaving the user device.

| Stage    | Mechanism                         |
| -------- | --------------------------------- |
| Frontend | WebCrypto AES-GCM                 |
| Backend  | PBKDF2-derived AES-GCM decryption |

AES-GCM ensures:

Confidentiality
Integrity verification
Resistance to padding and replay attacks

Security is not optional in healthcare — it is foundational.

💬 Conversational Support (Grok AI)

Integrates a contextual conversational model to:
Explain predictions in accessible language
Assist clinicians in summarizing imaging findings
Offer reasoning transparency to patients

This shifts AI from diagnostic output system → collaborative clinical assistant.

🧪 Robustness Evaluation

5-fold cross-validation (variance < 1.2%)
CPU-only inference benchmarked for realistic deployment
Encryption pipeline stress-tested over 200+ secure uploads

System behavior remains consistent under varied conditions.

🛠️ Future Roadmap
| Focus Area                                        | Rationale                                        |
| ------------------------------------------------- | ------------------------------------------------ |
| Multimodal data fusion (X-ray + clinical history) | Improve diagnostic context                       |
| TensorFlow Lite / ONNX optimization               | Edge and mobile deployment                       |
| Federated learning capabilities                   | Multi-hospital training without sharing raw data |
| SHAP / LIME explainability expansion              | Pixel-level transparency                         |
| Clinical pilot partnerships                       | Real-world validation                            |

Closing Note

ShwasNetra is built on the belief that technology should extend care, not distance it.

If even one life can be improved or one clinician’s decision supported more confidently, every hour spent on this project is justified.

AI should not replace doctors. It should support them with clarity, confidence, and compassion.