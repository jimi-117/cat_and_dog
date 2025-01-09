import os
import numpy as np
from keras.models import load_model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.metrics import classification_report, accuracy_score

# Paths to dataset and models
DATASET_DIR = './animals'  # Directory containing the dataset (folders: cat, dog)
MODEL_DIR = './app/models'  # Directory containing model files
IMG_SIZE = (128, 128)  # Image size (adjust to match the model input size)
BATCH_SIZE = 128

# Create a data generator for testing
datagen = ImageDataGenerator(rescale=1.0 / 255.0)
test_generator = datagen.flow_from_directory(
    DATASET_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='binary',
    shuffle=False  # Disable shuffling for class-wise evaluation
)

# Class labels
class_labels = list(test_generator.class_indices.keys())

# Evaluate a single model
def evaluate_model(model_path):
    print(f"Evaluating model: {model_path}")
    model = load_model(model_path)
    predictions = model.predict(test_generator)
    predicted_classes = np.argmax(predictions, axis=1) if predictions.shape[1] > 1 else np.round(predictions).astype(int)

    true_classes = test_generator.classes

    # Compute evaluation metrics
    accuracy = accuracy_score(true_classes, predicted_classes)
    report = classification_report(true_classes, predicted_classes, target_names=class_labels)

    print(f"\nAccuracy: {accuracy:.2f}")
    print("\nClassification Report:")
    print(report)
    return accuracy, report

# Get all .keras files in the models directory
model_files = [f for f in os.listdir(MODEL_DIR) if f.endswith('.keras')]

# Store evaluation results for each model
results = {}

for model_file in model_files:
    model_path = os.path.join(MODEL_DIR, model_file)
    accuracy, report = evaluate_model(model_path)
    results[model_file] = {
        'accuracy': accuracy,
        'classification_report': report
    }

# Output summary of all model performances
# print("\nSummary of Model Performance:")
# for model_file, metrics in results.items():
#     print(f"Model: {model_file}")
#     print(f"  Accuracy: {metrics['accuracy']:.2f}")
#     print(f"  Classification Report:\n{metrics['classification_report']}")
