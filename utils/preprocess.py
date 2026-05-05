import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

def preprocess_text(text):
    """Preprocess text: lowercase, remove special characters, stopwords, stemming"""
    if not isinstance(text, str):
        text = str(text)
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove special characters and digits
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    
    # Remove extra whitespaces
    text = ' '.join(text.split())
    
    # Tokenize
    tokens = text.split()
    
    # Remove stopwords and apply stemming
    stop_words = set(stopwords.words('english'))
    stemmer = PorterStemmer()
    
    tokens = [stemmer.stem(token) for token in tokens if token not in stop_words]
    
    return ' '.join(tokens)

def preprocess_dataframe(df, text_column='text'):
    """Preprocess entire dataframe column"""
    df['processed_text'] = df[text_column].apply(preprocess_text)
    return df