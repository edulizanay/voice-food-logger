import os
import tempfile
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
from transcription import transcribe_file
from processing import process_food_text
from storage import store_food_data, get_today_entries

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Allowed audio file extensions
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'mp4', 'm4a', 'ogg', 'webm'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Main page with recording interface and today's entries"""
    today_entries = get_today_entries()
    return render_template('index.html', entries=today_entries)

@app.route('/upload_audio', methods=['POST'])
def upload_audio():
    """Handle audio file upload and process through the pipeline"""
    try:
        # Check if audio file was uploaded
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        file = request.files['audio']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file format. Allowed: ' + ', '.join(ALLOWED_EXTENSIONS)}), 400
        
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, filename)
        file.save(temp_path)
        
        try:
            # Step 1: Transcribe audio
            print("Starting transcription...")
            transcription = transcribe_file(temp_path)
            if not transcription:
                return jsonify({'error': 'Failed to transcribe audio'}), 500
            
            print(f"Transcription: {transcription}")
            
            # Step 2: Process food description
            print("Processing food description...")
            parsed_data = process_food_text(transcription)
            if not parsed_data or 'items' not in parsed_data:
                return jsonify({'error': 'Failed to parse food description'}), 500
            
            print(f"Parsed data: {parsed_data}")
            
            # Step 3: Store food data
            print("Storing food data...")
            success = store_food_data(parsed_data['items'])
            if not success:
                return jsonify({'error': 'Failed to store food data'}), 500
            
            # Return success response
            response_data = {
                'success': True,
                'transcription': transcription,
                'items': parsed_data['items'],
                'timestamp': datetime.now().isoformat()
            }
            
            print("Pipeline completed successfully")
            return jsonify(response_data)
            
        finally:
            # Clean up temporary file
            try:
                os.remove(temp_path)
                os.rmdir(temp_dir)
            except:
                pass  # Ignore cleanup errors
    
    except Exception as e:
        print(f"Error processing audio: {e}")
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

@app.route('/entries')
def get_entries():
    """API endpoint to get today's entries"""
    entries = get_today_entries()
    return jsonify(entries)

@app.route('/test_pipeline')
def test_pipeline():
    """Test endpoint to verify the pipeline works"""
    test_audio = "test_data/sample_food_recording.wav"
    
    if not os.path.exists(test_audio):
        return jsonify({
            'error': 'Test audio file not found',
            'message': 'Please add a sample audio file at test_data/sample_food_recording.wav'
        }), 404
    
    try:
        # Test transcription
        transcription = transcribe_file(test_audio)
        if not transcription:
            return jsonify({'error': 'Transcription failed'}), 500
        
        # Test processing
        parsed_data = process_food_text(transcription)
        if not parsed_data:
            return jsonify({'error': 'Food processing failed'}), 500
        
        return jsonify({
            'success': True,
            'transcription': transcription,
            'parsed_data': parsed_data,
            'message': 'Pipeline test successful'
        })
        
    except Exception as e:
        return jsonify({'error': f'Pipeline test failed: {str(e)}'}), 500

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    return jsonify({'error': 'File too large. Maximum size is 16MB.'}), 413

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Check if GROQ_API_KEY is set
    if not os.getenv('GROQ_API_KEY'):
        print("ERROR: GROQ_API_KEY environment variable not set!")
        print("Please set your API key in the .env file")
        exit(1)
    
    print("Voice Food Logger starting...")
    print("Access the app at: http://localhost:5000")
    print("Test pipeline at: http://localhost:5000/test_pipeline")
    
    # Create necessary directories
    os.makedirs('logs', exist_ok=True)
    os.makedirs('test_data', exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000)