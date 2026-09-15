from flask import Flask, render_template, request, jsonify
from gam_copy import copiar_configuracao

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/copiar", methods=["POST"])
def copiar():

    try:

        source_id = int(
            request.form["source_id"]
        )

        target_id = int(
            request.form["target_id"]
        )

        resultado = copiar_configuracao(
            source_id,
            target_id
        )

        return jsonify({
            "success": True,
            "message": resultado
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        })

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )