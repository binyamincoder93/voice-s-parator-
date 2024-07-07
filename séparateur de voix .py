print("Hello, World!")
from flask import Flask, render_template, request, jsonify
import os
import subprocess
from spleeter.separator import Separator

app = Flask(__name__)

# Fonction pour télécharger un fichier audio à partir d'une URL YouTube
def download_audio(url, download_path='downloads'):
    os.makedirs(download_path, exist_ok=True)
    command = [
        'yt-dlp', '-x', '--audio-format', 'mp3', '-o', f'{download_path}/%(title)s.%(ext)s', url
    ]
    subprocess.run(command)

# Fonction pour séparer l'audio en voix et musique
def separate_audio(input_audio, output_directory):
    separator = Separator('spleeter:2stems')
    separator.separate_to_file(input_audio, output_directory)

# Route pour traiter les requêtes de séparation d'audio
@app.route('/separate', methods=['POST'])
def separate():
    if 'url' in request.form:
        youtube_url = request.form['url']
        download_path = 'downloads'
        try:
            download_audio(youtube_url, download_path)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

        for file in os.listdir(download_path):
            if file.endswith('.mp3'):
                input_audio = os.path.join(download_path, file)
                break
        else:
            return jsonify({'error': 'No MP3 file downloaded'}), 400

    elif 'file' in request.files:
        file = request.files['file']
        input_path = os.path.join('uploads', file.filename)
        os.makedirs('uploads', exist_ok=True)
        file.save(input_path)
        input_audio = input_path
    else:
        return jsonify({'error': 'No file or URL provided'}), 400

    output_directory = os.path.join('output', os.path.splitext(os.path.basename(input_audio))[0])
    os.makedirs(output_directory, exist_ok=True)
    separate_audio(input_audio, output_directory)

    return jsonify({'message': 'File processed successfully'}), 200

# Route principale pour la page d'accueil
@app.route('/')
def index():
    return render_template('index.html')

# Route pour la page "À propos"
@app.route('/about')
def about():
    return render_template('about.html')

# Route avec un paramètre pour afficher le profil utilisateur
@app.route('/user/<username>')
def show_user_profile(username):
    return f'Utilisateur {username}'

# Exécution de l'application Flask
if __name__ == '__main__':
    app.run(debug=True)
