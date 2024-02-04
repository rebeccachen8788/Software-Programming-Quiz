from application import create_app
import os

app = create_app()

# Listener
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 12118))
    app.run(port=port, debug=True)