import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.model_selection import train_test_split
import joblib


def train_and_serialize_model(
    data_path: str = "outputs/membrane_doe.csv", model_path: str = "surrogate_rf.joblib"
):
    """Trains a multi-output Random Forest to predict Reactor Performance and serializes it."""
    print(f"Loading data from {data_path}...")
    df = pd.read_csv(data_path)

    features = ["T_in_K", "P_in_bar", "h2_co2_ratio", "flow_mol_s"]
    targets = ["co2_conversion", "meoh_yield"]

    X = df[features]
    y = df[targets]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.15, random_state=42
    )

    print("Training Multi-Output Random Forest Regressor...")
    # Base estimator optimized for speed and accuracy
    base_rf = RandomForestRegressor(
        n_estimators=100, max_depth=10, random_state=42, n_jobs=-1
    )
    model = MultiOutputRegressor(base_rf)

    model.fit(X_train, y_train)

    # Evaluate
    score = model.score(X_test, y_test)
    print(f"Model trained successfully. Test R^2 Score: {score:.4f}")

    # Serialize
    joblib.dump(model, model_path)
    print(f"Model serialized and saved to {model_path}")


if __name__ == "__main__":
    train_and_serialize_model()
