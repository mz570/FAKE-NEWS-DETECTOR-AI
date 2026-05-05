"""
Fake News Detector - CSV First, Web Second (with Real SerpApi)
"""

import streamlit as st
import pandas as pd
import os
import re
import requests
from datetime import datetime
import time

# Page config
st.set_page_config(
    page_title="Fake News Detector",
    page_icon="🔍",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 25px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 25px;
    }
    .true-result {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 30px;
        border-radius: 15px;
        color: white;
        text-align: center;
        animation: slideIn 0.5s;
    }
    .fake-result {
        background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
        padding: 30px;
        border-radius: 15px;
        color: white;
        text-align: center;
        animation: slideIn 0.5s;
    }
    .unclear-result {
        background: linear-gradient(135deg, #f2994a 0%, #f2c94c 100%);
        padding: 30px;
        border-radius: 15px;
        color: white;
        text-align: center;
        animation: slideIn 0.5s;
    }
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: bold;
        font-size: 18px;
        padding: 10px 30px;
        border-radius: 30px;
        width: 100%;
    }
    .stButton > button:hover {
        transform: scale(1.02);
        transition: 0.3s;
    }
    .info-box {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 4px solid #667eea;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# CSV DATABASE CLASS
# ============================================

class CSVDatabase:
    """Search for news in CSV files"""
    
    def __init__(self):
        self.true_df = None
        self.fake_df = None
        self.is_loaded = False
        self.load_csv_data()
    
    def load_csv_data(self):
        """Load CSV files into memory"""
        try:
            if os.path.exists('data/True.csv'):
                self.true_df = pd.read_csv('data/True.csv')
                self.is_loaded = True
            if os.path.exists('data/Fake.csv'):
                self.fake_df = pd.read_csv('data/Fake.csv')
                self.is_loaded = True
            return self.is_loaded
        except Exception as e:
            print(f"Error loading CSV: {e}")
            return False
    
    def search_in_csv(self, query):
        """
        Search for similar news in CSV files
        Returns: (found, result_type, confidence, matched_text)
        """
        if not self.is_loaded:
            return False, None, 0, None
        
        query_clean = query.lower().strip()
        best_match = None
        best_score = 0
        best_type = None
        
        # Search in True news
        if self.true_df is not None:
            for idx, row in self.true_df.iterrows():
                title = str(row.get('title', '')).lower()
                text = str(row.get('text', '')).lower()
                combined = title + " " + text
                
                # Calculate similarity
                score = self._calculate_similarity(query_clean, combined)
                
                if score > best_score and score > 30:  # 30% threshold
                    best_score = score
                    best_type = "TRUE"
                    best_match = title[:200]
        
        # Search in Fake news
        if self.fake_df is not None:
            for idx, row in self.fake_df.iterrows():
                title = str(row.get('title', '')).lower()
                text = str(row.get('text', '')).lower()
                combined = title + " " + text
                
                score = self._calculate_similarity(query_clean, combined)
                
                if score > best_score and score > 30:
                    best_score = score
                    best_type = "FAKE"
                    best_match = title[:200]
        
        if best_match:
            return True, best_type, best_score, best_match
        
        return False, None, 0, None
    
    def _calculate_similarity(self, text1, text2):
        """Calculate simple similarity score"""
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return (len(intersection) / len(union)) * 100
    
    def get_stats(self):
        """Get CSV statistics"""
        stats = {
            'true_count': len(self.true_df) if self.true_df is not None else 0,
            'fake_count': len(self.fake_df) if self.fake_df is not None else 0,
            'is_loaded': self.is_loaded
        }
        stats['total'] = stats['true_count'] + stats['fake_count']
        return stats


# ============================================
# REAL WEB SEARCH WITH SERPAPI
# ============================================

class RealWebSearch:
    """Real web search using SerpApi"""
    
    def __init__(self):
        self.api_key = self._load_api_key()
    
    def _load_api_key(self):
        """Load SerpApi key from file"""
        try:
            if os.path.exists('serpapi_key.txt'):
                with open('serpapi_key.txt', 'r') as f:
                    key = f.read().strip()
                    if key and len(key) > 10:
                        return key
        except:
            pass
        return None
    
    def search_google_news(self, query, num_results=10):
        """
        REAL Google News search using SerpApi
        Returns list of news articles
        """
        if not self.api_key:
            return None, "No SerpApi key found. Please add your key to serpapi_key.txt"
        
        try:
            # SerpApi endpoint
            url = "https://serpapi.com/search.json"
            
            params = {
                "q": f"{query} news",
                "api_key": self.api_key,
                "engine": "google_news",
                "gl": "us",
                "hl": "en",
                "num": num_results
            }
            
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                articles = []
                
                # Extract news results
                if "news_results" in data:
                    for item in data["news_results"][:num_results]:
                        articles.append({
                            "title": item.get("title", "No title"),
                            "link": item.get("link", "#"),
                            "source": item.get("source", {}).get("name", "Unknown") if isinstance(item.get("source"), dict) else item.get("source", "Unknown"),
                            "date": item.get("date", ""),
                            "snippet": item.get("snippet", ""),
                            "thumbnail": item.get("thumbnail", "")
                        })
                
                # Also check organic results
                if "organic_results" in data and len(articles) < num_results:
                    for item in data["organic_results"][:num_results - len(articles)]:
                        articles.append({
                            "title": item.get("title", "No title"),
                            "link": item.get("link", "#"),
                            "source": item.get("source", "Unknown"),
                            "date": "",
                            "snippet": item.get("snippet", ""),
                            "thumbnail": ""
                        })
                
                return articles, None
            else:
                return None, f"API Error: {response.status_code}"
                
        except requests.exceptions.Timeout:
            return None, "Request timeout. Please try again."
        except Exception as e:
            return None, f"Error: {str(e)}"
    
    def verify_claim(self, claim):
        """
        Verify claim using REAL web search
        Returns verdict with confidence
        """
        # Search the web
        articles, error = self.search_google_news(claim)
        
        if error:
            return {
                "verdict": "ERROR",
                "confidence": 0,
                "articles_found": 0,
                "credible_sources": 0,
                "articles": [],
                "error": error,
                "has_api": bool(self.api_key)
            }
        
        if not articles or len(articles) == 0:
            return {
                "verdict": "UNCLEAR",
                "confidence": 50,
                "articles_found": 0,
                "credible_sources": 0,
                "articles": [],
                "has_api": bool(self.api_key),
                "error": "No articles found"
            }
        
        # Credibility scoring
        credible_sources = [
            'reuters', 'apnews', 'associated press', 'bbc', 'npr', 
            'nytimes', 'new york times', 'washington post', 'cnn', 
            'the guardian', 'guardian', 'snopes', 'factcheck', 
            'politifact', 'abc news', 'nbc news', 'cbs news',
            'wall street journal', 'wsj', 'time', 'newsweek',
            'sciencedaily', 'nature', 'science', 'national geographic'
        ]
        
        score = 0
        credible_count = 0
        total_sources = len(articles)
        
        for article in articles:
            source = article['source'].lower()
            
            # Check if source is credible
            is_credible = any(cred in source for cred in credible_sources)
            if is_credible:
                score += 25
                credible_count += 1
            else:
                score += 10  # Still count non-credible sources but lower score
        
        # Calculate confidence (max 100)
        if total_sources > 0:
            base_confidence = (score / (total_sources * 25)) * 100
            # Boost confidence if multiple credible sources
            boost = min(credible_count * 5, 20)
            confidence = min(base_confidence + boost, 100)
        else:
            confidence = 50
        
        # Determine verdict
        if confidence >= 65:
            verdict = "TRUE"
        elif confidence >= 35:
            verdict = "UNCLEAR"
        else:
            verdict = "FAKE"
        
        return {
            "verdict": verdict,
            "confidence": confidence,
            "articles_found": total_sources,
            "credible_sources": credible_count,
            "articles": articles[:7],  # Top 7 articles
            "has_api": bool(self.api_key),
            "error": None
        }


# ============================================
# MAIN VERIFIER (CSV First, Web Second)
# ============================================

class NewsVerifier:
    def __init__(self):
        self.csv_db = CSVDatabase()
        self.web_search = RealWebSearch()
    
    def verify_news(self, text):
        """
        STEP 1: Search in CSV files
        STEP 2: If found → return CSV result (NO web search)
        STEP 3: If NOT found → search web and return web result
        """
        
        # STEP 1: Search in CSV database
        found_in_csv, result_type, confidence, matched_text = self.csv_db.search_in_csv(text)
        
        if found_in_csv:
            # Found in CSV - return CSV result (NO web search)
            return {
                "verdict": result_type,
                "confidence": confidence,
                "source_type": "CSV Database",
                "source_detail": "Found in local trained database",
                "web_used": False,
                "matched_article": matched_text,
                "explanation": f"This news was found in our {'TRUE' if result_type == 'TRUE' else 'FAKE'} news database with {confidence:.1f}% match confidence. No web search was performed."
            }
        else:
            # STEP 2: Not found in CSV - search web
            web_result = self.web_search.verify_claim(text)
            
            return {
                "verdict": web_result['verdict'],
                "confidence": web_result['confidence'],
                "source_type": "Web Search",
                "source_detail": "Not found in CSV database, searched the web",
                "web_used": True,
                "articles_found": web_result['articles_found'],
                "credible_sources": web_result['credible_sources'],
                "articles": web_result['articles'],
                "has_api": web_result['has_api'],
                "error": web_result['error'],
                "explanation": f"This news was NOT found in our CSV database. Web search found {web_result['articles_found']} related articles with {web_result['credible_sources']} from credible sources."
            }
    
    def refresh_csv(self):
        """Refresh CSV database"""
        self.csv_db.load_csv_data()
        return self.csv_db.get_stats()


# ============================================
# ADMIN TRAINING FUNCTIONS
# ============================================

def train_model_from_csv():
    """Train/Load CSV data into database"""
    try:
        # Create data directory if not exists
        os.makedirs('data', exist_ok=True)
        
        # Check if files exist
        true_exists = os.path.exists('data/True.csv')
        fake_exists = os.path.exists('data/Fake.csv')
        
        if not true_exists and not fake_exists:
            return False, "No CSV files found. Please upload True.csv and/or Fake.csv"
        
        # Load data into memory (database)
        csv_db = CSVDatabase()
        csv_db.load_csv_data()
        
        stats = csv_db.get_stats()
        
        if stats['total'] > 0:
            return True, f"Successfully loaded {stats['total']} articles ({stats['true_count']} true, {stats['fake_count']} fake)"
        else:
            return False, "CSV files loaded but no valid data found"
            
    except Exception as e:
        return False, f"Error training model: {str(e)}"


# ============================================
# MAIN APP
# ============================================

def main():
    # Initialize session state
    if 'verifier' not in st.session_state:
        st.session_state.verifier = NewsVerifier()
    if 'admin_auth' not in st.session_state:
        st.session_state.admin_auth = False
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "User"
    if 'training_status' not in st.session_state:
        st.session_state.training_status = None
    
    # Header
    st.markdown('<div class="header"><h1>🔍 Fake News Detector</h1><p>CSV First • Web Second • Real SerpApi Integration</p></div>', unsafe_allow_html=True)
    
    # Sidebar Navigation
    with st.sidebar:
        st.markdown("## 🧭 Navigation")
        
        if st.button("👤 User Panel", use_container_width=True):
            st.session_state.current_page = "User"
            st.rerun()
        
        if st.button("🔧 Admin Panel", use_container_width=True):
            st.session_state.current_page = "Admin"
            st.rerun()
        
        st.markdown("---")
        
        # Show stats
        stats = st.session_state.verifier.csv_db.get_stats()
        st.markdown("### 📊 Database Status")
        
        if stats['is_loaded'] and stats['total'] > 0:
            st.success(f"✅ Loaded: {stats['total']} articles")
            st.metric("True News", stats['true_count'])
            st.metric("Fake News", stats['fake_count'])
        else:
            st.warning("⚠️ No data loaded")
            st.info("Go to Admin Panel to load CSV files")
        
        st.markdown("---")
        st.markdown("### 💡 How It Works")
        st.info("""
        **For Users:**
        1. Enter news text
        2. System checks CSV first
        3. If found → CSV result
        4. If not found → Web search
        5. Get verdict with confidence
        
        **For Admins:**
        1. Upload CSV files
        2. Train/Load data
        3. System ready for users
        """)
    
    # ============================================
    # USER PANEL
    # ============================================
    
    if st.session_state.current_page == "User":
        st.markdown("## 📝 Verify News")
        st.markdown("Enter the news article or claim you want to verify:")
        
        # Search input
        search_text = st.text_area(
            "",
            height=150,
            placeholder="Example: 'Scientists discover cure for cancer' or 'Donald Trump wins 2024 election' or paste full news article here..."
        )
        
        # Verify button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            verify_btn = st.button("🔍 VERIFY NOW", use_container_width=True)
        
        # Results
        if verify_btn and search_text:
            with st.spinner("Verifying... Checking CSV database first..."):
                result = st.session_state.verifier.verify_news(search_text)
                
                st.markdown("---")
                st.markdown("## 📊 Verification Result")
                
                # Display result based on verdict
                if result['verdict'] == "TRUE":
                    st.markdown(f"""
                    <div class="true-result">
                        <h1>✅ TRUE NEWS</h1>
                        <h2>Confidence: {result['confidence']:.1f}%</h2>
                        <p>━━━━━━━━━━━━━━━━━━━━</p>
                        <p>📌 Source: {result['source_type']}</p>
                        <p>🎯 Method: {result['source_detail']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                elif result['verdict'] == "FAKE":
                    st.markdown(f"""
                    <div class="fake-result">
                        <h1>⚠️ FAKE NEWS</h1>
                        <h2>Confidence: {result['confidence']:.1f}%</h2>
                        <p>━━━━━━━━━━━━━━━━━━━━</p>
                        <p>📌 Source: {result['source_type']}</p>
                        <p>🎯 Method: {result['source_detail']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                else:
                    st.markdown(f"""
                    <div class="unclear-result">
                        <h1>❓ UNCLEAR</h1>
                        <h2>Confidence: {result['confidence']:.1f}%</h2>
                        <p>━━━━━━━━━━━━━━━━━━━━</p>
                        <p>📌 Source: {result['source_type']}</p>
                        <p>🎯 Method: {result['source_detail']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Confidence meter
                st.progress(result['confidence'] / 100)
                
                # Explanation
                st.markdown(f'<div class="info-box"><strong>📝 Explanation:</strong><br>{result["explanation"]}</div>', unsafe_allow_html=True)
                
                # Show matched article if found in CSV
                if result.get('matched_article'):
                    with st.expander("📖 Matched Article from CSV Database"):
                        st.markdown(f"**Matched text:** {result['matched_article']}")
                
                # Show web search results if web was used
                if result.get('web_used', False) and result.get('articles'):
                    with st.expander(f"🌐 Web Search Results ({result['articles_found']} articles found, {result['credible_sources']} from credible sources)"):
                        for i, article in enumerate(result['articles'][:5], 1):
                            st.markdown(f"""
                            **{i}. {article['title']}**  
                            📰 Source: {article['source']}  
                            📅 Date: {article['date'] if article['date'] else 'Recent'}  
                            📝 {article['snippet'][:200] if article['snippet'] else 'No snippet available'}  
                            🔗 [Read full article]({article['link']})
                            """)
                            st.markdown("---")
                
                # Show error if any
                if result.get('error'):
                    st.warning(f"⚠️ Web Search Note: {result['error']}")
                
                # Show API status
                if result.get('web_used', False) and not result.get('has_api', True):
                    st.error("🔴 SerpApi key not configured! Web search results are limited. Please add your SerpApi key to serpapi_key.txt")
                elif result.get('web_used', False) and result.get('has_api', False):
                    st.success("✅ Real web search performed using SerpApi")
                    
        elif verify_btn and not search_text:
            st.warning("⚠️ Please enter some text to verify")
        
        # Show CSV status
        if not st.session_state.verifier.csv_db.is_loaded or st.session_state.verifier.csv_db.get_stats()['total'] == 0:
            st.info("💡 No CSV data loaded. Contact admin to upload and train data for better results.")
    
    # ============================================
    # ADMIN PANEL
    # ============================================
    
    else:
        st.markdown("## 🔧 Admin Panel")
        st.markdown("Upload CSV files and train the model")
        
        # Simple login
        if not st.session_state.admin_auth:
            st.markdown("### 🔐 Admin Login")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                
                if st.button("Login", use_container_width=True):
                    if username == "admin" and password == "admin123":
                        st.session_state.admin_auth = True
                        st.success("✅ Login successful!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials (use admin/admin123)")
        else:
            st.success("✅ Admin Access Granted")
            
            # Logout button
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.admin_auth = False
                st.rerun()
            
            st.markdown("---")
            
            # ============================================
            # SECTION 1: Upload CSV Files
            # ============================================
            
            st.markdown("### 📁 Step 1: Upload CSV Files")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Upload True News CSV")
                true_file = st.file_uploader("Choose True.csv", type=['csv'], key="true_upload")
                if true_file:
                    os.makedirs('data', exist_ok=True)
                    true_df = pd.read_csv(true_file)
                    true_df.to_csv('data/True.csv', index=False)
                    st.success(f"✅ Uploaded {len(true_df)} true news articles")
            
            with col2:
                st.markdown("#### Upload Fake News CSV")
                fake_file = st.file_uploader("Choose Fake.csv", type=['csv'], key="fake_upload")
                if fake_file:
                    os.makedirs('data', exist_ok=True)
                    fake_df = pd.read_csv(fake_file)
                    fake_df.to_csv('data/Fake.csv', index=False)
                    st.success(f"✅ Uploaded {len(fake_df)} fake news articles")
            
            st.markdown("---")
            
            # ============================================
            # SECTION 2: Train/Load Model
            # ============================================
            
            st.markdown("### 🚀 Step 2: Train/Load Model")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🚀 TRAIN / LOAD DATA", use_container_width=True, type="primary"):
                    with st.spinner("Loading CSV data into database..."):
                        success, message = train_model_from_csv()
                        if success:
                            st.success(f"✅ {message}")
                            # Refresh verifier
                            st.session_state.verifier = NewsVerifier()
                            st.session_state.training_status = "success"
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
                            st.session_state.training_status = "error"
            
            # Show training status
            if st.session_state.training_status == "success":
                st.balloons()
            
            st.markdown("---")
            
            # ============================================
            # SECTION 3: Database Status
            # ============================================
            
            st.markdown("### 📊 Step 3: Database Status")
            
            stats = st.session_state.verifier.csv_db.get_stats()
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Status", "✅ Loaded" if stats['is_loaded'] and stats['total'] > 0 else "⚠️ Empty")
            with col2:
                st.metric("Total Articles", stats['total'])
            with col3:
                st.metric("True News", stats['true_count'])
            with col4:
                st.metric("Fake News", stats['fake_count'])
            
            if stats['total'] > 0:
                st.success(f"✅ Database ready! {stats['total']} articles loaded for searching.")
            else:
                st.warning("⚠️ No data loaded. Please upload CSV files and click 'Train/Load Data'")
            
            st.markdown("---")
            
            # ============================================
            # SECTION 4: SerpApi Configuration
            # ============================================
            
            st.markdown("### 🌐 Step 4: Web Search Configuration (SerpApi)")
            
            # Check current API key status
            api_key = None
            if os.path.exists('serpapi_key.txt'):
                with open('serpapi_key.txt', 'r') as f:
                    api_key = f.read().strip()
            
            if api_key and len(api_key) > 10:
                st.success("✅ SerpApi key configured! Web search will work.")
                st.info(f"Key: {api_key[:10]}...{api_key[-5:]}")
                
                if st.button("🗑️ Remove API Key"):
                    os.remove('serpapi_key.txt')
                    st.success("API key removed")
                    st.rerun()
            else:
                st.warning("⚠️ No SerpApi key found. Web search will be limited.")
                
                st.markdown("**To get a free SerpApi key:**")
                st.markdown("""
                1. Go to [https://serpapi.com/](https://serpapi.com/)
                2. Sign up for free account (100 free searches/month)
                3. Copy your API key
                4. Paste it below:
                """)
                
                new_key = st.text_input("Enter SerpApi Key:", type="password")
                
                if st.button("💾 Save API Key"):
                    if new_key and len(new_key) > 10:
                        with open('serpapi_key.txt', 'w') as f:
                            f.write(new_key.strip())
                        st.success("✅ API key saved! Web search is now enabled.")
                        st.rerun()
                    else:
                        st.error("Please enter a valid API key")
            
            st.markdown("---")
            
            # ============================================
            # SECTION 5: Test Instructions
            # ============================================
            
            with st.expander("📖 Test Instructions"):
                st.markdown("""
                **To test the system:**
                
                1. **Load CSV Data:**
                   - Upload True.csv and Fake.csv
                   - Click "Train/Load Data"
                
                2. **Switch to User Panel:**
                   - Click "User Panel" in sidebar
                   - Enter a news claim
                   - System will check CSV first, then web
                
                3. **Test Examples:**
                   - "Bangladesh got independence in 1971"
                   - "Donald Trump is president"
                   - "COVID-19 vaccine is safe"
                
                4. **Web Search:**
                   - Make sure SerpApi key is added
                   - System will search web for claims not in CSV
                """)

if __name__ == "__main__":
    main()