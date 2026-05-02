from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
#ensure data is ready
features = ['Pieces', 'Minifigures', 'Year', 'USD_MSRP']
target = 'ROI_Percent'
model_df = df_clean.dropna(subset=features + [target])
X = model_df[features]
y = model_df[target]

#split the data
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42)

#initialize and train
rf_model = RandomForestRegressor(
    n_estimators=100,
    random_state=42)
rf_model.fit(X_train, y_train)

#predict and evaluate
predictions = rf_model.predict(X_test)
print("Random Forest Results")
print("MAE:", mean_absolute_error(y_test, predictions))
print("R2 Score:", r2_score(y_test, predictions))
importance = rf_model.feature_importances_
for feature, score in zip(features, importance):
    print(f"{feature}: {score:.3f}")

# Test a custom LEGO set
new_set = [[1200, 6, 2022, 160]]
prediction = rf_model.predict(new_set)
print(f"Predicted ROI: {prediction[0]:.2f}%")

# Practice test set (from dataset)
test_set = X_test.iloc[[0]]
prediction = rf_model.predict(test_set)
print("Actual ROI:", y_test.iloc[0])
print("Predicted ROI:", prediction[0])

# Function to predict LEGO ROI
def predict_lego_roi(pieces, minifigs, year, msrp):
    new_data = [[pieces, minifigs, year, msrp]]
    prediction = rf_model.predict(new_data)
    return prediction[0]

# Use the function
roi = predict_lego_roi(1500, 8, 2023, 200)
print(f"Predicted ROI: {roi:.2f}%")
