import numpy as np
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE

class ClusterAnalyzer:
    
    def __init__(self, n_clusters=4):
        self.n_clusters = n_clusters
    
    def prepare_feature_vectors(self, emotion_series, energy_series):
        features = []
        
        for emotion, energy in zip(emotion_series, energy_series):
            vector = [
                emotion.get('neutral', 0),
                emotion.get('happy', 0),
                emotion.get('sad', 0),
                emotion.get('angry', 0),
                emotion.get('fearful', 0),
                energy / 100.0
            ]
            features.append(vector)
        
        return np.array(features)
    
    def perform_clustering(self, features):
        if len(features) < self.n_clusters:
            return np.zeros(len(features)), features[:, :2]
        
        kmeans = KMeans(n_clusters=self.n_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(features)
        
        if features.shape[1] > 2:
            tsne = TSNE(n_components=2, random_state=42, perplexity=min(30, len(features)-1))
            coordinates = tsne.fit_transform(features)
        else:
            coordinates = features
        
        return labels, coordinates
    
    def analyze(self, emotion_series, energy_series):
        features = self.prepare_feature_vectors(emotion_series, energy_series)
        labels, coordinates = self.perform_clustering(features)
        
        cluster_info = []
        for i in range(self.n_clusters):
            cluster_mask = labels == i
            cluster_size = np.sum(cluster_mask)
            
            if cluster_size > 0:
                cluster_info.append({
                    'cluster_id': int(i),
                    'size': int(cluster_size),
                    'percentage': float((cluster_size / len(labels)) * 100)
                })
        
        return {
            'labels': labels.tolist(),
            'coordinates': coordinates.tolist(),
            'cluster_info': cluster_info
        }
