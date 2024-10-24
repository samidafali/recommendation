from flask import Flask, request, jsonify
from pymongo import MongoClient
from flask_cors import CORS
import os
import logging
from dotenv import load_dotenv
from bson import ObjectId

# Charger les variables d'environnement
load_dotenv()

# Initialiser le logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
# Autoriser toutes les origines pour toutes les routes
CORS(app)

# Configuration MongoDB
client = MongoClient(os.getenv("MONGO_URI"))
db = client['test']  # Remplacez par le nom de votre base de données
courses_collection = db['courses']

@app.route('/recommend', methods=['POST'])
def recommend_course():
    logging.debug("Received request for course recommendation.")
    
    data = request.json
    logging.debug(f"Request data: {data}")

    category = data.get('category')
    difficulty = data.get('difficulty')

    # Log des catégories et de la difficulté reçues
    logging.debug(f"Received category: {category}, difficulty: {difficulty}")

    # Validation des entrées
    if not category or not difficulty:
        logging.warning("Category or difficulty not provided.")
        return jsonify({"error": "Category and difficulty are required"}), 400

    # Trouver le cours le plus pertinent basé sur la catégorie et la difficulté
    recommended_course = courses_collection.find_one({
        "category": category,
        "difficulty": difficulty,
        "isapproved": True  # Seulement les cours approuvés
    })

    if not recommended_course:
        logging.info(f"No recommended course found for category: {category}, difficulty: {difficulty}.")
        return jsonify({"message": "No recommended course found."}), 404

    logging.debug(f"Recommended course found: {recommended_course}")

    # Convertir les ObjectId en chaînes de caractères
    recommended_course['_id'] = str(recommended_course['_id'])
    for i in range(len(recommended_course['enrolledUsers'])):
        recommended_course['enrolledUsers'][i] = str(recommended_course['enrolledUsers'][i])
    
    # Convertir tous les ObjectId dans les vidéos
    for video in recommended_course.get('videos', []):
        video['_id'] = str(video['_id'])  # Convertir chaque ObjectId en chaîne de caractères

    # Loguer la réponse avant de la retourner
    logging.debug(f"Response being sent: {recommended_course}")

    # Retourner le cours recommandé
    return jsonify({"recommended_course": recommended_course}), 200

    logging.debug("Received request for course categories.")
@app.route('/categories', methods=['GET'])
def get_categories():
    logging.debug("Received request for course categories.")
    
    # Récupérer toutes les catégories uniques des cours
    categories = courses_collection.distinct("category")

    if not categories:
        logging.info("No categories found.")
        return jsonify({"message": "No categories found."}), 404

    # Supprimer les doublons (si nécessaire)
    unique_categories = list(set(categories))

    logging.debug(f"Categories found: {unique_categories}")
    return jsonify({"categories": unique_categories}), 200


if __name__ == '__main__':
    app.run(debug=True)
