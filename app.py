from flask import Flask, request, jsonify
from nominatim import NominatimFeature
from extract import ExtractFeature
from render import RenderFeature

app = Flask(__name__)

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

@app.route("/")
def index():
    return jsonify({"status": "EyeOnDev API is running."})

if __name__ == "__main__":
    app.run(debug=True)
