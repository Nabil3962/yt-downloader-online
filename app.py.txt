from flask import Flask, render_template, request
import yt_dlp

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    message = ""
    if request.method == 'POST':
        url = request.form['url']
        quality = request.form['quality']
        audio = request.form.get('audio')

        ydl_opts = {
            'outtmpl': '%(title)s.%(ext)s',
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
            message = "✅ Download complete!"
        except Exception as e:
            message = f"❌ Error: {str(e)}"

    return render_template('index.html', message=message)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
