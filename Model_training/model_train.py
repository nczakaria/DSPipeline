import os
import glob
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
import xgboost as xgb
import lightgbm as lgb
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import classification_report, accuracy_score, precision_score, recall_score, f1_score
from tqdm import tqdm
import joblib
import matplotlib.pyplot as plt
import shap
import lime
import lime.lime_tabular
from sklearn.model_selection import cross_val_score


# Set the matplotlib backend to 'Agg'
import matplotlib
matplotlib.use('Agg')


def feature_importance(model, X_train, save_dir):
    try:
        # Create a directory to save the feature importance
        print(f"Feature Importance for {model.__class__.__name__}")
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
        elif hasattr(model, 'coef_'):
            importances = model.coef_[0]
        else:
            # Use SHAP values for models that do not have built-in feature importance
            explainer = shap.Explainer(model, X_train)
            shap_values = explainer(X_train)
            importances = shap_values.abs.mean(0).values
        # Create a DataFrame to save the feature importance
        importance_df = pd.DataFrame({'feature': X_train.columns, 'importance': importances})
        importance_df.to_csv(os.path.join(save_dir, 'feature_importance.csv'), index=False)
        return importance_df
    except Exception as e:
        print(f"Error in feature_importance: {e}")


# Explain the model using LIME
def explain_model_with_lime(model, X_test, save_dir):
    try:
        # Create a directory to save the LIME explanation
        print(f"Explaining model {model.__class__.__name__} with LIME")
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        # Create a LIME explainer
        explainer = lime.lime_tabular.LimeTabularExplainer(
            X_test.values,
            feature_names=X_test.columns,
            class_names=['Non-Snore', 'Snore'],
            verbose=True,
            mode='classification'
        )
        
        # Explain a single instance (for demonstration)
        exp = explainer.explain_instance(X_test.iloc[0], model.predict_proba, num_features=10)
        print(f'LIME explanation created for {model.__class__.__name__}')
        
        # Save the explanation as an HTML file
        exp.save_to_file(os.path.join(save_dir, 'lime_explanation.html'))
        
        # For more detailed analysis, iterate through multiple instances
        explanations = []
        for i in range(10):  # Explain the first 10 instances as an example
            exp = explainer.explain_instance(X_test.iloc[i], model.predict_proba, num_features=10)
            explanations.append(exp.as_list())
        
        # Save explanations to CSV
        explanations_df = pd.DataFrame(explanations)
        explanations_df.to_csv(os.path.join(save_dir, 'lime_explanations.csv'), index=False)
    except MemoryError as mem_err:
        print(f"MemoryError in explain_model: {mem_err}")
    except Exception as e:
        print(f"Error in explain_model: {e}")

# Explain the model using SHAP 
def explain_model_with_kernel_explainer(model, X_test, save_dir):
    try:
        print(f"Explaining model {model.__class__.__name__} with Kernel Explainer")
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        # Use a sample of the data for the explainer initialization
        background = shap.sample(X_test, 100, random_state=42)
        explainer = shap.KernelExplainer(model.predict_proba, background)
        print(f'Kernel Explainer created for {model.__class__.__name__}')
        
        # Use a smaller sample of the data for SHAP value calculation to avoid memory issues
        shap_values = explainer.shap_values(X_test.sample(1000, random_state=42))
        print(f'Shap values created for {model.__class__.__name__}')
        
        shap.summary_plot(shap_values, X_test.sample(1000, random_state=42), show=False)
        plt.savefig(os.path.join(save_dir, 'shap_summary_plot.png'))
        plt.close()
        
        # Save the SHAP values to a CSV file
        shap_df = pd.DataFrame(shap_values[1], columns=X_test.columns) 
        shap_df.to_csv(os.path.join(save_dir, 'shap_values.csv'), index=False)
    except MemoryError as mem_err:
        print(f"MemoryError in explain_model: {mem_err}")
    except Exception as e:
        print(f"Error in explain_model: {e}")


# Cross Validation
def cross_validation(model, X, y, cv=5):
    scores = cross_val_score(model, X, y, cv=cv, scoring='accuracy')
    return scores.mean()

# Load the data
def load_data(path):
    file_list = glob.glob(os.path.join(path, "*.csv"))
    df_list = [pd.read_csv(file) for file in tqdm(file_list, desc="Loading CSV files")]
    data = pd.concat(df_list, axis=0, ignore_index=True)
    return data


# Model Evaluation
def model_evaluation(model, X_train, y_train, X_test, y_test, name, save_dir):
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    # Get the classification report for the model
    report = classification_report(y_test, y_pred, output_dict=True)
    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred),
        "recall": recall_score(y_test, y_pred),
        "f1": f1_score(y_test, y_pred),
        'classification_report': report,
    }

    # Save the model
    save_name = os.path.join(save_dir, f"{name}.pkl")
    joblib.dump(model, save_name)

    return metrics

# Model Initialization
def model_initialization():
    random_forest = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1, verbose=5)
    gradient_boost = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=3, random_state=42)
    xgboost = xgb.XGBClassifier(use_label_encoder=False, eval_metric='mlogloss', random_state=42)
    lightgbm = lgb.LGBMClassifier(random_state=42)
    svm = SVC(kernel='rbf', C=1, gamma='scale', verbose=True, cache_size=500, random_state=42)
    KNN = KNeighborsClassifier(n_neighbors=5, n_jobs=-1)

    models = {
        "Random Forest": random_forest,
        "Gradient Boosting": gradient_boost,
        "XGBoost": xgboost,
        "LightGBM": lightgbm,
        "KNN": KNN
    }

    return models

# Load and evaluate pretrained_models
def load_and_evaluate_models(model_names, X_test, y_test, weight_dir):
    results = {}
    pretrained_models = {}
    for name in model_names:
        if name == 'KNN':
            continue
        model_path = os.path.join(weight_dir, f"{name}.pkl")
        if os.path.exists(model_path):
            print(f"Loading model {name}")
            model = joblib.load(model_path)
            pretrained_models[name] = model
            y_pred = model.predict(X_test)
            report = classification_report(y_test, y_pred, output_dict=True)
            metrics = {
                "accuracy": accuracy_score(y_test, y_pred),
                "precision": precision_score(y_test, y_pred),
                "recall": recall_score(y_test, y_pred),
                "f1": f1_score(y_test, y_pred),
                'classification_report': report,
            }
            results[name] = metrics
        else:
            print(f"Model {name} not found.")
    return pretrained_models, results

# Print the results
def print_results(results, is_plot=True):
    # Create a DataFrame to compare results
    comparison_df = pd.DataFrame(results).T
    print(comparison_df[['accuracy', 'precision', 'recall', 'f1']])

    # Plot the comparison
    if is_plot:
        comparison_df[['accuracy', 'precision', 'recall', 'f1']].plot(kind='bar', figsize=(12, 8))
        plt.title('Model Comparison')
        plt.xlabel('Models')
        plt.ylabel('Scores')
        plt.ylim(0, 1)
        plt.legend(loc='lower right')
        plt.xticks(rotation=45)
        plt.show()

    for name, metrics in results.items():
        print(f"Classification Report for {name}:\n")
        print(pd.DataFrame(metrics['classification_report']).transpose())
        print("\n")


if __name__ == "__main__":

    path = r"Audio_csv/Audio"
    save_dir = r"model_weights"
    is_load = True

    # Create the directory if it does not exist
    os.makedirs(save_dir, exist_ok=True)

    # Load the CSV files
    data = load_data(path)

    # Encode labels
    data['label'] = data['label'].apply(lambda x: 1 if x in ('Snore', 'Snoring') else 0)

    label_counts = data['label'].value_counts()
    print("Label Counts:", label_counts)


    X = data.drop(['label', 'timestamp'], axis=1)
    y = data['label']

    # Split test train data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    models = model_initialization()

    results = {}

    if not is_load:
        for name, model in models.items():  
            print(f"Evaluating {name}")
            results[name] = model_evaluation(model, X_train, y_train, X_test, y_test, name, save_dir)
    else:
        model_weights_dir = os.path.join(save_dir, "full")
        models, results = load_and_evaluate_models(list(models.keys()), X_test, y_test, model_weights_dir)
        print(f'Loaded {len(models)} models.')
        analysis_dir = r'Analysis'
        os.makedirs(analysis_dir, exist_ok=True)
        for name, model in models.items():
            save_path = os.path.join(analysis_dir, name)
            os.makedirs(save_path, exist_ok=True)
            feature_importance(model, X_train[:1000], save_path)
            explain_model_with_lime(model, X_test, save_path)
            print(f"Cross Validation Score for {name}: {cross_validation(model, X_train, y_train)}")

    print_results(results, is_plot=False)
