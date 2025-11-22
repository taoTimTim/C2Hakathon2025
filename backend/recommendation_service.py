import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import os

app = Flask(__name__)
CORS(app)

tfidf_vectorizer = None
tfidf_matrix = None
all_data_df = None

def load_and_train_model():
    """
    Loads clubs.csv, events.csv, AND groups.csv.
    Merges them all and trains the model.
    """
    global tfidf_vectorizer, tfidf_matrix, all_data_df

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
            df = pd.read_csv('events.csv', keep_default_na=False)
            if 'contact' not in df.columns: df['contact'] = "" # Account for missing column data
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
        all_data_df = all_data_df.fillna("") # Safety net
    else:
        print("No CSV files found. Using DUMMY data.")
        # Dummy data fallback
        data = {
            'id': [101, 801, 901],
            'name': ['Robotics Club', 'Winter Formal', 'Freshman Group'],
            'category': ['Tech', 'Event', 'Group'],
            'contact': ['robotics@uni.edu', '', 'discord.gg/freshman'],
            'description': [
                'Building robots.',
                'Dance party.',
                'For 1st year students to connect.'
            ]
        }
        all_data_df = pd.DataFrame(data)

    # --- AI Model Training ---
    # Create the "keyword soup"
    all_data_df['soup'] = all_data_df['name'] + " " + all_data_df['category'] + " " + all_data_df['description']
    
    # Vectorize
    tfidf_vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf_vectorizer.fit_transform(all_data_df['soup'])
    
    print(f"🤖 Model trained on {len(all_data_df)} total spaces.")

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.json
    
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
    app.run(debug=True, port=5000)