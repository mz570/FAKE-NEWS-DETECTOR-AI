import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.preprocess import preprocess_dataframe

def train_model():
    """Train the ML model"""
    print("Loading data...")
    true_df = pd.read_csv('data/True.csv')
    fake_df = pd.read_csv('data/Fake.csv')
    
    true_df['label'] = 1
    fake_df['label'] = 0
    
    df = pd.concat([true_df, fake_df], ignore_index=True)
    df['text'] = df['title'] + " " + df['text']
    df = preprocess_dataframe(df, 'text')
    
    X = df['processed_text']
    y = df['label']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)
    
    model = LogisticRegression(max_iter=1000)
    model.fit(X_train_tfidf, y_train)
    
    y_pred = model.predict(X_test_tfidf)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"Model Accuracy: {accuracy:.4f}")
    
    os.makedirs('model', exist_ok=True)
    joblib.dump(model, 'model/model.pkl')
    joblib.dump(vectorizer, 'model/vectorizer.pkl')
    
    with open('model/accuracy.txt', 'w') as f:
        f.write(str(accuracy))
    
    return model, vectorizer, accuracy

if __name__ == "__main__":
    train_model()