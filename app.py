from flask import Flask, request, jsonify
from flask_cors import CORS
from nominatim import NominatimFeature
from extract import ExtractFeature
from render import RenderFeature
from eye import EyeOnDev

app = Flask(__name__)

CORS(app)  # This will handle OPTIONS and add CORS headers automatically

nominatim = NominatimFeature()
extractor = ExtractFeature()
renderer = RenderFeature()

@app.route("/search")
def nominatim_search():
    #data = request.args.get("data", "")
    result = nominatim.geocode_all()
    return jsonify(result)

@app.route("/extract")
def extract():
    #data = request.args.get("data", "")
    result = extractor.extract()
    return jsonify(result)

@app.route("/render")
def render():
    #content = request.args.get("content", "")
    result = renderer.render()
    return jsonify(result)

@app.route("/eye", methods=["GET", "POST"])
def eye_on_dev():
    # Allow a POST here
    if request.method == 'POST':
        data = request.get_json()
        url = data.get("source_url", "https://www.lowersalfordtownship.org/departments/building-zoning/eye-on-development/")
        corrections = data.get("corrections", {})
    
    eod = EyeOnDev()
    result = eod.run_all(url, corrections)
    return jsonify(result)

@app.route("/")
def index():
    return jsonify({"status": "EyeOnDev API is running."})

if __name__ == "__main__":
    app.run(debug=True)
