import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer

# ✅ Step 1: Load Data
df = pd.read_csv('final_merged_data.csv')

# ✅ Step 2: Remove Low Occupancy Properties
df = df[df['occupancy_ratio'] >= 20]

# ✅ Step 3: Define Numerical and Categorical Columns
numerical_cols = [
    'total_opex', 'CP/ Room', 'GrossMargin', 'avg_rent', 'occupancy_ratio', 'months_of_stay',
    'Furnished Price', 'Semi-Furnished Price', 'Unfurnished Price'
]
categorical_cols = ['locality', 'city']

# ✅ Step 4: Handle Missing Values in Numerical Columns
df_numerical = df[numerical_cols].copy()
imputer = SimpleImputer(strategy='median')
df_numerical_imputed = pd.DataFrame(
    imputer.fit_transform(df_numerical),
    columns=df_numerical.columns,
    index=df_numerical.index
)

# ✅ Step 5: Remove Outliers using IQR
def remove_outliers_iqr(df, columns):
    df_clean = df.copy()
    for column in columns:
        Q1 = df_clean[column].quantile(0.25)
        Q3 = df_clean[column].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        df_clean = df_clean[
            (df_clean[column] >= lower_bound) & 
            (df_clean[column] <= upper_bound)
        ]
    return df_clean

df_no_outliers = remove_outliers_iqr(df_numerical_imputed, numerical_cols)

# ✅ Step 6: Handle Categorical Data
df_categorical = df.loc[df_no_outliers.index, categorical_cols].copy()
df_categorical = df_categorical.fillna('Unknown')

# One-hot encoding for categorical variables
df_categorical_encoded = pd.get_dummies(
    df_categorical, 
    columns=categorical_cols,
    prefix=categorical_cols,
    drop_first=True
)

# ✅ Step 7: Scale Numerical Features
scaler = StandardScaler()
df_numerical_scaled = pd.DataFrame(
    scaler.fit_transform(df_no_outliers),
    columns=df_no_outliers.columns,
    index=df_no_outliers.index
)

# ✅ Step 8: Combine Processed Data
df_preprocessed = pd.concat([df_numerical_scaled, df_categorical_encoded], axis=1)

# ✅ Step 9: Save Preprocessed Data
df_preprocessed.to_csv('processed_data.csv', index=False)

# ✅ Step 10: Display Summary
print("\nOriginal dataset shape:", df.shape)
print("Preprocessed dataset shape:", df_preprocessed.shape)
print("\nColumns in preprocessed dataset:", df_preprocessed.columns.tolist())

print("\nPreprocessed numerical features statistics:")
print(df_preprocessed.describe())

preprocessing_objects = {
    'scaler': scaler,
    'imputer': imputer
}

print("\nPreprocessing complete. Data is ready for modeling! 🚀")
