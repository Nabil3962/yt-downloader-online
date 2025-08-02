from flask import Flask, render_template, request
import yt_dlp
import os

app = Flask(__name__)

DOWNLOAD_FOLDER = os.path.join(os.getcwd(), "downloads")
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    message = ""
    if request.method == 'POST':
        url = request.form.get('url', '').strip()
        quality = request.form.get('quality', '720p')
        audio = request.form.get('audio') == 'on'  # checkbox returns 'on' if checked

        if not url:
            message = "❌ Please enter a YouTube video or playlist URL."
            return render_template('index.html', message=message)

        ydl_opts = {
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'noplaylist': False,
        }

        if audio:
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            })
        else:
            ydl_opts.update({
                'format': f'bestvideo[height<={quality[:-1]}]+bestaudio/best',
                'merge_output_format': 'mp4',
            })

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            message = "✅ Download completed successfully!"
        except Exception as e:
            message = f"❌ Error: {str(e)}"

    return render_template('index.html', message=message)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)
