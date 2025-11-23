import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import os

app = Flask(__name__)

# --- CRITICAL FIX: Allow all origins explicitly ---
CORS(app, resources={r"/*": {"origins": "*"}})

# Global variables
tfidf_vectorizer = None
tfidf_matrix = None
all_data_df = None

def load_and_train_model():
    """
    Loads clubs.csv, events.csv, AND groups.csv.
    Merges them all and trains the model.
    """
    global tfidf_vectorizer, tfidf_matrix, all_data_df

    # Initialize empty dataframes
    dfs = [] 
    
    # 1. Load Clubs
    if os.path.exists('clubs.csv'):
        try:
            df = pd.read_csv('clubs.csv', keep_default_na=False)
            print(f"Loaded {len(df)} clubs.")
            dfs.append(df)
        except Exception as e:
            print(f"Error loading clubs.csv: {e}")

    # 2. Load Events
    if os.path.exists('events.csv'):
        try:
            # Added error_bad_lines=False logic (via on_bad_lines for newer pandas) to skip broken rows
            df = pd.read_csv('events.csv', keep_default_na=False)
            if 'contact' not in df.columns: df['contact'] = "" 
            print(f"Loaded {len(df)} events.")
            dfs.append(df)
        except Exception as e:
            print(f"Error loading events.csv: {e}")

    # 3. Load Groups
    if os.path.exists('groups.csv'):
        try:
            df = pd.read_csv('groups.csv', keep_default_na=False)
            if 'contact' not in df.columns: df['contact'] = "" 
            print(f"Loaded {len(df)} groups.")
            dfs.append(df)
        except Exception as e:
            print(f"Error loading groups.csv: {e}")

    # 4. Merge or Fallback
    if len(dfs) > 0:
        all_data_df = pd.concat(dfs, ignore_index=True)
        all_data_df = all_data_df.fillna("") 
    else:
        print("No CSV files found. Using DUMMY data.")
        data = {'id': [1], 'name': ['Test Club'], 'category': ['Test'], 'contact': [''], 'description': ['Test']}
        all_data_df = pd.DataFrame(data)

    # --- AI Training ---
    all_data_df['soup'] = all_data_df['name'] + " " + all_data_df['category'] + " " + all_data_df['description']
    tfidf_vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf_vectorizer.fit_transform(all_data_df['soup'])
    
    print(f"Model trained on {len(all_data_df)} total spaces.")

@app.route('/items', methods=['GET'])
def get_all_items():
    try:
        items = all_data_df.to_dict(orient='records')
        return jsonify(items)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/recommend', methods=['POST', 'OPTIONS'])
def recommend():
    # Handle preflight request manually if CORS fails (Safety Net)
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200

    data = request.json
    print(f"Received Request: {data}") # Debug print
    
    user_year = data.get('year', '')
    user_classes = " ".join(data.get('classes', []))
    user_interests = data.get('interests', '')
    user_profile_text = f"{user_year} {user_classes} {user_interests}"
    
    try:
        user_tfidf = tfidf_vectorizer.transform([user_profile_text])
        cosine_sim = linear_kernel(user_tfidf, tfidf_matrix)
        
        sim_scores = list(enumerate(cosine_sim[0]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        top_indices = [i[0] for i in sim_scores[:5]]
        
        results = []
        for i in top_indices:
            score = sim_scores[top_indices.index(i)][1]
            if score > 0.0:
                results.append({
                    "id": int(all_data_df.iloc[i]['id']),
                    "name": all_data_df.iloc[i]['name'],
                    "category": all_data_df.iloc[i]['category'],
                    "contact": all_data_df.iloc[i]['contact'],
                    "description": all_data_df.iloc[i]['description'],
                    "match_score": round(score, 2)
                })
        return jsonify(results)
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify([])

if __name__ == '__main__':
    load_and_train_model()
    # Host on 0.0.0.0 to ensure it listens on all interfaces
    app.run(debug=True, port=5001, host='0.0.0.0')