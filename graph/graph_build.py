import networkx as nx
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import joblib
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.preprocess import preprocess_dataframe

class NewsGraph:
    def __init__(self, similarity_threshold=0.5):
        self.graph = nx.Graph()
        self.similarity_threshold = similarity_threshold
        self.tfidf_matrix = None
        
    def build_graph(self, df, vectorizer):
        """Build graph from dataframe using TF-IDF vectors"""
        print("Building news graph...")
        
        # Add nodes with labels
        for idx, row in df.iterrows():
            self.graph.add_node(
                idx, 
                label=row['label'],
                title=row['title'][:100],
                text=row['text'][:200]
            )
        
        # Get TF-IDF vectors
        processed_texts = df['processed_text'].tolist()
        self.tfidf_matrix = vectorizer.transform(processed_texts)
        
        # Compute cosine similarity and add edges
        print("Computing similarities...")
        n_samples = self.tfidf_matrix.shape[0]
        batch_size = 50
        
        for i in range(0, n_samples, batch_size):
            batch_end = min(i + batch_size, n_samples)
            batch_matrix = self.tfidf_matrix[i:batch_end]
            similarities = cosine_similarity(batch_matrix, self.tfidf_matrix)
            
            for row_idx in range(similarities.shape[0]):
                global_idx = i + row_idx
                for col_idx in range(global_idx + 1, n_samples):
                    similarity = similarities[row_idx, col_idx]
                    if similarity >= self.similarity_threshold:
                        self.graph.add_edge(global_idx, col_idx, weight=similarity)
            
            print(f"Processed {batch_end}/{n_samples} nodes...")
        
        print(f"✅ Graph built: {self.graph.number_of_nodes()} nodes, {self.graph.number_of_edges()} edges")
        return self.graph
    
    def save_graph(self, path='graph/news_graph.gpickle'):
        os.makedirs('graph', exist_ok=True)
        nx.write_gpickle(self.graph, path)
        print(f"Graph saved to {path}")
    
    def load_graph(self, path='graph/news_graph.gpickle'):
        self.graph = nx.read_gpickle(path)
        print(f"Graph loaded: {self.graph.number_of_nodes()} nodes, {self.graph.number_of_edges()} edges")
        return self.graph

def build_graph_from_data():
    """Build graph from the dataset"""
    true_df = pd.read_csv('data/True.csv')
    fake_df = pd.read_csv('data/Fake.csv')
    
    true_df['label'] = 1
    fake_df['label'] = 0
    
    df = pd.concat([true_df, fake_df], ignore_index=True)
    df['text'] = df['title'] + " " + df['text']
    df = preprocess_dataframe(df, 'text')
    
    vectorizer = joblib.load('model/vectorizer.pkl')
    
    news_graph = NewsGraph(similarity_threshold=0.5)
    graph = news_graph.build_graph(df, vectorizer)
    news_graph.save_graph()
    
    return news_graph