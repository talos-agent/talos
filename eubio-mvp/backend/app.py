from flask import Flask, render_template, request, jsonify
import joblib
import numpy as np

app = Flask(__name__, template_folder='templates', static_folder='static')

# ---------- load placeholder model ----------
try:
    model = joblib.load('model/placeholder_model.pkl')
except FileNotFoundError:
    # first run: train and save
    from sklearn.datasets import load_iris
    from sklearn.linear_model import LogisticRegression
    X, y = load_iris(return_X_y=True)
    model = LogisticRegression(max_iter=200)
    model.fit(X, y)
    joblib.dump(model, 'model/placeholder_model.pkl')

# ---------- routes ----------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()          # list of 4 floats
        X = np.array(data['features']).reshape(1, -1)
        proba = model.predict_proba(X)[0].tolist()
        pred = int(model.predict(X)[0])
        return jsonify({'prediction': pred, 'probabilities': proba})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)