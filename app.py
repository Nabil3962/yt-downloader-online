from flask import Flask, render_template, request, send_file
import yt_dlp
import os
import tempfile
import shutil

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("url")
        if not url:
            return "Please enter a YouTube URL", 400

        temp_dir = tempfile.mkdtemp()
        try:
            ydl_opts = {
                'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,  # FIXES 'NoneType' ERROR
                'force_ipv4': True,
                'ignoreerrors': False,
                'noplaylist': False,
            }

            if request.form.get("audio_only"):
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                    }],
                })
            else:
                ydl_opts.update({
                    'format': 'bestvideo[height<=720]+bestaudio/best',
                    'merge_output_format': 'mp4',
                })

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info_dict)

            return send_file(filename, as_attachment=True)

        except Exception as e:
            return f"Download Error: {str(e)}", 500
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
