from flask import Flask, render_template, request, send_file
import yt_dlp
import os
import tempfile
import shutil

app = Flask(__name__)

# Global error handler
@app.errorhandler(Exception)
def handle_error(e):
    return f"System Error: {str(e)}", 500

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("url")
        if not url or "youtube.com" not in url and "youtu.be" not in url:
            return "Invalid YouTube URL", 400

        temp_dir = tempfile.mkdtemp()
        try:
            ydl_opts = {
                'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
                'force_ipv4': True,
                'cookiefile': None,  # COMPLETELY DISABLES COOKIES
                'ignoreerrors': True,
                'nocheckcertificate': True,
                'default_search': 'auto',
                'source_address': '0.0.0.0',
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
                    'format': f'bestvideo[height<={request.form.get("quality", "720")}]+bestaudio/best',
                    'merge_output_format': 'mp4',
                })

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                if request.form.get("audio_only"):
                    filename = filename.replace('.webm', '.mp3').replace('.mp4', '.mp3')

            return send_file(filename, as_attachment=True)

        except Exception as e:
            shutil.rmtree(temp_dir, ignore_errors=True)
            return f"Download Error: {str(e)}", 500

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
