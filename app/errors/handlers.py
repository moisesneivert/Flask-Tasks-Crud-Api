from flask import jsonify

def register_error_handlers(app):

    @app.errorhandler(ValueError)
    def handle_validation_error(error):
        return jsonify({"error": str(error)}), 400
