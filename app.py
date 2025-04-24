from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

@app.route("/run", methods=["POST"])
def trigger_engine():
    data = request.json
    restaurant = data.get("restaurant", "xtreme_pizza")  # default to xtreme_pizza

    try:
        result = subprocess.run(
            ["python3", "run.py", restaurant],
            capture_output=True,
            text=True,
            timeout=30
        )
        return jsonify({
            "status": "success",
            "output": result.stdout,
            "error": result.stderr
        })

    except subprocess.TimeoutExpired:
        return jsonify({"status": "error", "message": "Timeout: the engine took too long."}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
