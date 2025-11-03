import csv
import os
from sklearn.metrics import classification_report, confusion_matrix

# Paths
annotations_file = "LUNA16/annotations.csv"
predictions_file = "validation/clinical_predictions.txt"
sample_ids_file = "validation/sampled_ids.txt"

# Step 1: Load ground truth from annotations.csv
nodule_positive_scans = set()
with open(annotations_file, newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        scan_id = row['seriesuid']
        nodule_positive_scans.add(scan_id)

# Step 2: Load sampled scan IDs
with open(sample_ids_file) as f:
    sampled_ids = [line.strip() for line in f.readlines()]

# Step 3: Build ground truth labels
ground_truth = []
for scan_id in sampled_ids:
    label = 1 if scan_id in nodule_positive_scans else 0
    ground_truth.append((scan_id, label))

# Step 4: Load model predictions
pred_dict = {}
with open(predictions_file) as f:
    for line in f:
        scan_id, pred = line.strip().split(',')
        pred_dict[scan_id] = int(pred)

# Step 5: Match predictions with ground truth
y_true, y_pred = [], []
for scan_id, label in ground_truth:
    if scan_id in pred_dict:
        y_true.append(label)
        y_pred.append(pred_dict[scan_id])
    else:
        print(f"⚠️ Missing prediction for {scan_id}")

# Step 6: Print metrics
print("✅ Evaluation Report:\n")
print("Confusion Matrix:")
print(confusion_matrix(y_true, y_pred))
print("\nClassification Report:")
print(classification_report(y_true, y_pred, target_names=["No Nodule", "Nodule"]))
