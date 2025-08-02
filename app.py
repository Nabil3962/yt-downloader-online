from flask import Flask, render_template, request, send_file
import yt_dlp
import os
import tempfile

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("url")
        quality = request.form.get("quality", "720p")
        audio_only = request.form.get("audio_only") == "on"
        browser = request.form.get("browser", "chrome")

        if not url:
            return "Please enter a YouTube URL", 400

        temp_dir = tempfile.mkdtemp()
        outtmpl = os.path.join(temp_dir, "%(title)s.%(ext)s")

        ydl_opts = {
            'outtmpl': outtmpl,
            'noplaylist': False,
            'cookiesfrombrowser': (browser,),
        }

        if audio_only:
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

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

        filename = ydl.prepare_filename(info)
        if audio_only:
            filename = os.path.splitext(filename)[0] + ".mp3"

        return send_file(filename, as_attachment=True)

    return render_template("index.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
