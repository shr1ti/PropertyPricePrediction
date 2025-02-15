import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Data Preprocessing
def processed_data(df):
    features = ['total_opex', 'CP/ Room', 'GrossMargin', 'avg_rent', 
                'occupancy_ratio', 'months_of_stay']
    df_work = df[features].copy()
    
    for col in df_work.columns:
        df_work[col] = pd.to_numeric(df_work[col], errors='coerce')
    
    df_work = df_work.dropna(subset=['total_opex', 'CP/ Room', 'GrossMargin', 'avg_rent'], how='all')
    df_work = df_work.fillna(df_work.median())
    
    return df_work

# Clustering & Price Recommendation Model
class PropertyPriceRecommender:
    def __init__(self, n_clusters=5):
        self.n_clusters = n_clusters
        self.scaler = StandardScaler()
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        self.isolation_forest = IsolationForest(random_state=42, contamination=0.1)
        self.pca = PCA(n_components=2)
        
    def fit(self, data):
        self.features_scaled = self.scaler.fit_transform(data)
        self.clusters = self.kmeans.fit_predict(self.features_scaled)
        self.anomalies = self.isolation_forest.fit_predict(self.features_scaled)
        
        self.cluster_stats = {}
        for i in range(self.n_clusters):
            cluster_mask = self.clusters == i
            cluster_data = data[cluster_mask]
            
            self.cluster_stats[i] = {
                'median_price': cluster_data['avg_rent'].median(),
                'price_std': cluster_data['avg_rent'].std(),
                'opex_median': cluster_data['total_opex'].median(),
                'cp_room_median': cluster_data['CP/ Room'].median(),
                'margin_median': cluster_data['GrossMargin'].median(),
                'rent_median': cluster_data['avg_rent'].median()
            }

    def recommend_price(self, features):
        features_scaled = self.scaler.transform(features)
        cluster = self.kmeans.predict(features_scaled)[0]
        stats = self.cluster_stats[cluster]
        
        recommended_price = stats['median_price']
        
        if features['total_opex'].iloc[0] > stats['opex_median']:
            recommended_price *= 0.95
        if features['CP/ Room'].iloc[0] > stats['cp_room_median']:
            recommended_price *= 1.05
        if features['GrossMargin'].iloc[0] > stats['margin_median']:
            recommended_price *= 1.03
        if features['avg_rent'].iloc[0] > stats['rent_median']:
            recommended_price *= 1.02
            
        gross_margin = features['GrossMargin'].iloc[0]

        # Properties with GrossMargin < 40% get two pricing options (15% and 10% profit)
        if gross_margin < 40:
            price_15_profit = int(recommended_price * 1.15)  
            price_10_profit = int(recommended_price * 1.10)  
            pricing_options = [price_15_profit, price_10_profit]
        else:
            # Properties with GrossMargin > 40% get three pricing options (15%, 10%, and 5% profit)
            price_15_profit = int(recommended_price * 1.15) 
            price_10_profit = int(recommended_price * 1.10)  
            price_5_profit = int(recommended_price * 1.05)   
            pricing_options = [price_15_profit, price_10_profit, price_5_profit]

        return recommended_price, cluster, pricing_options

# Visualization Function
def visualize_clusters(df_processed, recommender):
    features_pca = recommender.pca.fit_transform(recommender.features_scaled)
    
    viz_df = pd.DataFrame({
        'PCA1': features_pca[:, 0],
        'PCA2': features_pca[:, 1],
        'Cluster': recommender.clusters
    })

    plt.figure(figsize=(14, 5))

    # PCA Scatter Plot
    plt.subplot(1, 2, 1)
    sns.scatterplot(x='PCA1', y='PCA2', hue='Cluster', palette='viridis', data=viz_df)
    plt.title('PCA Visualization of Clusters')
    plt.xlabel('First Principal Component')
    plt.ylabel('Second Principal Component')
    plt.legend(title='Cluster')

    # Box Plot for Price Distribution
    plt.subplot(1, 2, 2)
    df_processed['Cluster'] = recommender.clusters
    sns.boxplot(x='Cluster', y='avg_rent', data=df_processed, palette='viridis')
    plt.title('Price Distribution by Cluster')
    plt.xlabel('Cluster')
    plt.ylabel('Average Rent')

    plt.tight_layout()
    plt.show()

# Main Execution Function
def main(data_path):
    df = pd.read_csv(data_path)
    df_processed = processed_data(df)
    
    recommender = PropertyPriceRecommender(n_clusters=5)
    recommender.fit(df_processed)
    
    results = []
    for idx, row in df_processed.iterrows():
        property_features = df_processed.iloc[[idx]]
        recommended_price, cluster, pricing_options = recommender.recommend_price(property_features)
        
        results.append({
            'property_id': df.loc[idx, 'property_id'],
            'cluster': cluster,
            'recommended_price': round(recommended_price, 2),
            'pricing_options': pricing_options,
            'furnished_price': round(df.loc[idx, 'Furnished Price'], 2),
            'semi_furnished_price': round(df.loc[idx, 'Semi-Furnished Price'], 2),
            'unfurnished_price': round(df.loc[idx, 'Unfurnished Price'], 2)
        })
    
    results_df = pd.DataFrame(results)
    
    # Save output to CSV
    results_df.to_csv('price_recommendations.csv', index=False)
    print("\nPrice Recommendations saved to 'price_recommendations.csv'")

    # Generate Visualizations
    visualize_clusters(df_processed, recommender)

    return results_df, recommender

if __name__ == "__main__":
    results_df, recommender = main('final_clustered_data.csv')
    
    print("\nPrice Recommendations Summary:")
    print(results_df.head())
    print("\nNumber of Properties Analyzed:", len(results_df))
