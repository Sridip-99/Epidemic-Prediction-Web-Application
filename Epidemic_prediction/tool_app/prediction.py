import os
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # To prevent GUI backend issues

# Load population density data
def load_population_density_data():
    # Define BASE_DIR as the project directory
    BASE_DIR = Path(__file__).resolve().parent.parent
    # Use BASE_DIR to define the file path dynamically
    population_density_path = os.path.join(BASE_DIR, "static", "Country data", "Country_Population_Year.csv")
    # Load the CSV file
    population_density_df = pd.read_csv(population_density_path)
    population_density_df["Year"] = population_density_df["Year"].astype(int)
    return population_density_df

# Get population and density for a given country and year
def get_population_density(country, year, population_density_df):
    country_data = population_density_df[population_density_df["Country Name"] == country]
    closest_year_data = country_data[country_data["Year"] <= year].sort_values(by="Year", ascending=False).head(1)
    if not closest_year_data.empty:
        population = closest_year_data["Population"].values[0]
        density = closest_year_data["Density (per km²)"].values[0]
        return population, density
    return None, None

# Preprocess data
def preprocess_data(df, population_density_df):
    df.columns = df.columns.str.strip()
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True)
    df["Year"] = df["Date"].dt.year

    # Add population and density
    population_list = []
    density_list = []
    for _, row in df.iterrows():
        population, density = get_population_density(row["Country Name"], row["Year"], population_density_df)
        population_list.append(population)
        density_list.append(density)
    df["Population"] = population_list
    df["Density (per km²)"] = density_list

    # Clean and calculate derived columns
    for col in ["Case", "Death", "Population", "Density (per km²)"]:
        df[col] = df[col].replace({',': ''}, regex=True).astype(float)

    df["Active Case"] = df["Case"] - df["Death"]
    df["Active Case"] = df["Active Case"].fillna(0).replace([np.inf, -np.inf], 0)

    df["Case Growth Rate"] = df.groupby("Country Name")["Case"].pct_change().fillna(0)
    df["Death Growth Rate"] = df.groupby("Country Name")["Death"].pct_change().fillna(0)

    # Replace infinity values with 0
    for col in ["Case Growth Rate", "Death Growth Rate"]:
        df[col] = df[col].replace([np.inf, -np.inf], 0)

    df["Death-to-Case Ratio"] = df["Death"] / df["Case"].replace(0, np.nan)
    df["Death-to-Case Ratio"] = df["Death-to-Case Ratio"].fillna(0).replace([np.inf, -np.inf], 0)

    return df

# Label the data based on conditions
def label_data(df, caused_by="None"):
    """
    Labels data into 'Epidemic', 'Endemic', 'Pandemic', or 'Normal' based on the caused_by parameter.
    
    Parameters:
        df (pd.DataFrame): The dataset to label.
        caused_by (str): The disease causing the outbreak.
        
    Returns:
        pd.DataFrame: The labeled dataset.
    """
    # Define labels
    labels = ["Epidemic", "Endemic", "Pandemic", "Normal"]

    # Define conditions based on the pathogen
    if caused_by == "Covid 19":
        conditions = [
            (df["Case"] > 100000) & (df["Death"] > 5000) & (df["Active Case"] > 20000) & (df["Death-to-Case Ratio"] > 0.03),
            (df["Case Growth Rate"] > 0.2) & (df["Death Growth Rate"] > 0.05),
            (df["Case"] > 500000),
        ]
    elif caused_by == "Cholera":
        conditions = [
            (df["Case"] > 5000) & (df["Death"] > 500) & (df["Active Case"] > 1000) & (df["Death-to-Case Ratio"] > 0.01),
            (df["Case Growth Rate"] > 0.08) & (df["Death Growth Rate"] > 0.02),
            (df["Case"] > 10000),
        ]
    elif caused_by == "Ebola":
        conditions = [
            (df["Case"] > 5000) & (df["Death"] > 300) & (df["Active Case"] > 100) & (df["Death-to-Case Ratio"] > 0.05),
            (df["Case Growth Rate"] > 0.1) & (df["Death Growth Rate"] > 0.02),
            (df["Case"] > 20000),
        ]
    elif caused_by == "SARS":
        conditions = [
            (df["Case"] > 8000) & (df["Death"] > 700) & (df["Active Case"] > 500) & (df["Death-to-Case Ratio"] > 0.09),
            (df["Case Growth Rate"] > 0.15) & (df["Death Growth Rate"] > 0.03),
            (df["Case"] > 30000),
        ]
    elif caused_by == "Swine flu":
        conditions = [
            (df["Case"] > 500000) & (df["Death"] > 20000) & (df["Active Case"] > 10000) & (df["Death-to-Case Ratio"] > 0.005),
            (df["Case Growth Rate"] > 0.05) & (df["Death Growth Rate"] > 0.005),
            (df["Case"] > 1000000),
        ]
    else:  # Universal case or unknown disease
        conditions = [
            (df["Case"] > 4000) & (df["Death"] > 1000) & (df["Active Case"] > 500) & (df["Death-to-Case Ratio"] > 0.05),
            (df["Case Growth Rate"] > 0.1) & (df["Death Growth Rate"] > 0.03),
            (df["Case"] > 10000),
        ]

    # Match conditions with labels
    label_cases = ["Epidemic", "Endemic", "Pandemic"]

    # Apply labels to DataFrame
    df["Label"] = np.select(conditions, label_cases, default="Normal")

    # Use np.select with the conditions and ensure "Normal" is the default.
    df["Label"] = np.select(conditions, labels[:-1], default="Normal")

    # Validate that no NaN remains in the Label column
    if df["Label"].isnull().sum() > 0:
        print(f"Warning: {df['Label'].isnull().sum()} rows could not be labeled.")
    return df

# Train the classifier and regressor
def train_model(data, graphs_dir):
    X = data[["Case", "Death", "Active Case", "Population", "Density (per km²)", "Case Growth Rate", "Death Growth Rate"]]
    y_classification = data["Label"]

    label_mapping = {label: idx for idx, label in enumerate(y_classification.unique())}
    y_classification = y_classification.map(label_mapping)

    # For regression: probabilities between 0 and 1
    y_regression = y_classification / (len(label_mapping) - 1)
    y_regression = y_regression.fillna(0)

    # Train-test split
    X = X.apply(pd.to_numeric, errors='coerce').fillna(0)
    X_train, X_test, y_train_class, y_test_class = train_test_split(X, y_classification, test_size=0.2, random_state=42)
    _, _, y_train_reg, y_test_reg = train_test_split(X, y_regression, test_size=0.2, random_state=42)

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    # Train classifier
    classifier = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
    classifier.fit(X_train, y_train_class)

    # Generate confusion matrix
    y_pred_class = classifier.predict(X_test)
    cm = confusion_matrix(y_test_class, y_pred_class)
    cm_display = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=list(label_mapping.keys()))
    cm_display.plot()

    # Save confusion matrix plot
    confusion_matrix_path = os.path.join(graphs_dir, "confusion_matrix.png")
    plt.savefig(confusion_matrix_path)
    plt.close()

    # Train regressor
    regressor = RandomForestRegressor(n_estimators=100, random_state=42)
    regressor.fit(X_train, y_train_reg)

    return classifier, regressor, label_mapping, scaler, confusion_matrix_path


# Predict using classifier and regressor
def predict(classifier, regressor, label_mapping, scaler, input_features, original_data):
    X = input_features[["Case", "Death", "Active Case", "Population", "Density (per km²)", "Case Growth Rate", "Death Growth Rate"]]
    X_scaled = scaler.transform(X)

    # Classification predictions
    class_predictions = classifier.predict(X_scaled)

    # Regression probabilities (scaled 0 to 100 for percentage representation)
    regressor_probs = regressor.predict(X_scaled) * 100

    # Map predicted labels back to their names
    reverse_label_mapping = {v: k for k, v in label_mapping.items()}
    predicted_labels = [reverse_label_mapping[label] for label in class_predictions]

    # Add predictions and probabilities to the original dataset
    original_data["Predicted Label"] = predicted_labels
    original_data["Prediction Probability"] = regressor_probs.round(2)  # Add probabilities as percentages

    return original_data


# Process data and generate results
def process_and_predict(input_file, caused_by="None"):
    population_density_df = load_population_density_data()
    data = pd.read_csv(input_file)
    data = preprocess_data(data, population_density_df)
    data = label_data(data, caused_by=caused_by)

    # Save prediction results
    BASE_DIR = Path(__file__).resolve().parent.parent
    media_dir = os.path.join(BASE_DIR, 'media')
    graphs_dir = os.path.join(media_dir, 'graphs')
    os.makedirs(graphs_dir, exist_ok=True)

    # Train models
    classifier, regressor, label_mapping, scaler, confusion_matrix_path = train_model(data, graphs_dir)

    # Predictions
    input_features = data[["Case", "Death", "Active Case", "Population", "Density (per km²)", "Case Growth Rate", "Death Growth Rate"]]
    predictions_df = predict(classifier, regressor, label_mapping, scaler, input_features, data)
    predictions_df = predictions_df.drop('Label', axis=1)


    # Save predictions to a CSV file
    output_file = os.path.join(media_dir, 'Epidemic_Predictions.csv')
    predictions_df.to_csv(output_file, index=False)

    # Generate graphs
    def save_graph(x, y, title, xlabel, ylabel, filename):
        plt.figure(figsize=(10, 6))
        plt.plot(x, y, marker='o')
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.grid()
        graph_path = os.path.join(graphs_dir, filename)
        plt.savefig(graph_path)
        plt.close()
        return graph_path

    graph_paths = [

        save_graph(data["Date"], data["Case"], "Cases Over Time", "Date", "Cases", "cases_over_time.png"),
        save_graph(data["Date"], data["Death"], "Deaths Over Time", "Date", "Deaths", "deaths_over_time.png"),
        save_graph(data["Date"], data["Case Growth Rate"], "Case Growth Rate Over Time", "Date", "Case Growth Rate", "case_growth_rate.png"),
        save_graph(data["Date"], data["Death Growth Rate"], "Death Growth Rate Over Time", "Date", "Death Growth Rate", "death_growth_rate.png"),
        save_graph(data["Date"], data["Prediction Probability"], "Epidemic Probability Over Time", "Date", "Epidemic Probability", "epidemic_probability_over_time.png")
    ]

    print(f"Predictions saved to {output_file}")
    print("Graphs saved:", graph_paths)
    print("confusion_matrix_file saved:", confusion_matrix_path)

    # Return paths
    return {"prediction_file": output_file, "graph_files": graph_paths}
