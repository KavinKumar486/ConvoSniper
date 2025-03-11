from flask import Flask, render_template, request, redirect, url_for
import time
import logging
import os
# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='static', template_folder='templates')

@app.route('/')
def index():
    logger.debug("Rendering index page")
    return render_template('index.html', show_insights=False)

@app.route('/find_interests', methods=['GET', 'POST'])
def find_interests():
    content = request.args.get('content', '') if request.method == 'GET' else request.form.get('content', '')
    if not content:
        content = 'Python'  # Default to 'Python' if no content provided
    logger.debug(f"Received content: {content}")

    # Simulate loading for 10 seconds
    logger.debug("Simulating loading for 10 seconds")
    time.sleep(10)
    logger.debug("Loading complete, redirecting to results")

    # Redirect to results page with content as a query parameter
    return redirect(url_for('results', content=content))

@app.route('/results')
def results():
    content = request.args.get('content', 'Python')
    logger.debug(f"Rendering results for content: {content}")
    return render_template('results.html')

@app.route('/accept_reject/<action>')
def accept_reject(action):
    logger.debug(f"Received {action} action")
    if action.lower() == 'accept':
        # Redirect to insights.html for "Accept"
        return redirect(url_for('insights'))
    else:  # 'reject'
        # Redirect to index for "Reject"
        return redirect(url_for('index', show_insights=False))

@app.route('/insights')
def insights():
    logger.debug("Rendering insights page with initial 'Show Insights' button")
    return render_template('insights.html', show_visuals=False)

@app.route('/show_insights')
def show_insights():
    try:
        logger.debug("Rendering insights page with visualizations")
        # Assuming visualize_engagement.py saves images, but we'll use static files for now
        image_paths = [
            "static/engagement_metrics_by_platform.png",
            "static/likes_vs_comments.png",
            "static/engagement_over_time.png"
        ]
        existing_images = [path for path in image_paths if os.path.exists(path)]
        if not existing_images:
            logger.debug("No visualization images found")
            return "No visualization images found", 500
        
        logger.debug(f"Rendering insights with images: {existing_images}")
        return render_template('insights.html', show_visuals=True, image_paths=existing_images)
    except Exception as e:
        logger.error(f"Error in show_insights: {e}")
        return "Error loading insights", 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)  # Keep port 5001 as per your previous URL