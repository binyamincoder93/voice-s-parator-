from flask import Flask, render_template, request, send_file
import os
import librosa

app = Flask(__name__)

# Chemin vers le dossier où les fichiers seront sauvegardés
UPLOAD_FOLDER = './uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            # Sauvegarde du fichier uploadé dans le dossier UPLOAD_FOLDER
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            
            # Charger le fichier audio
            y, sr = librosa.load(file_path)
            
            # Séparer la voix et la musique
            y_harmonic, y_percussive = librosa.effects.hpss(y)
            
            # Enregistrer les résultats
            output_harmonic_path = os.path.join(app.config['UPLOAD_FOLDER'], 'output_harmonic.wav')
            output_percussive_path = os.path.join(app.config['UPLOAD_FOLDER'], 'output_percussive.wav')
            
            librosa.output.write_wav(output_harmonic_path, y_harmonic, sr)
            librosa.output.write_wav(output_percussive_path, y_percussive, sr)
            
            # Retourner les chemins des fichiers générés
            return render_template('result.html', harmonic_file=output_harmonic_path, percussive_file=output_percussive_path)

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
