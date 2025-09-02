from flask import Flask, render_template, request, send_file, flash, redirect, url_for
import yt_dlp
import os
import tempfile
import shutil
import validators
import logging

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "supersecretkey")

logging.basicConfig(level=logging.INFO)

def fetch_formats(url):
    ydl_opts = {'quiet': True, 'no_warnings': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        formats = []
        for f in info_dict.get("formats", []):
            if f.get("vcodec") != "none" and f.get("acodec") != "none":
                size = f.get("filesize")
                size_str = f"{round(size/(1024*1024),1)} MB" if size else "Unknown size"
                formats.append({
                    "format_id": f["format_id"],
                    "ext": f["ext"],
                    "resolution": f.get("format_note") or f.get("height", "N/A"),
                    "filesize": size_str
                })
        return formats

def download_media(url, chosen_format=None, audio_only=False):
    temp_dir = tempfile.mkdtemp()
    try:
        ydl_opts = {
            'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
        }

        if audio_only:
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                }],
            })
        else:
            ydl_opts['format'] = chosen_format or 'bestvideo[height<=720]+bestaudio/best'

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info_dict)
            if audio_only:
                filename = os.path.splitext(filename)[0] + ".mp3"
        return filename, temp_dir
    except Exception as e:
        shutil.rmtree(temp_dir)
        raise e

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("url")
        chosen_format = request.form.get("format_id")
        audio_only = request.form.get("audio_only") == "on"

        if not url or not validators.url(url):
            flash("Please enter a valid YouTube URL.", "error")
            return redirect(url_for('index'))

        if not chosen_format and not audio_only:
            try:
                formats = fetch_formats(url)
                if not formats:
                    flash("No downloadable formats found.", "error")
                    return redirect(url_for('index'))
                return render_template("index.html", url=url, formats=formats)
            except Exception as e:
                logging.error(f"Error fetching formats: {e}")
                flash("Failed to fetch video formats. Please check the URL and try again.", "error")
                return redirect(url_for('index'))

        else:
            try:
                filename, temp_dir = download_media(url, chosen_format, audio_only)
                response = send_file(filename, as_attachment=True)
                @response.call_on_close
                def cleanup():
                    shutil.rmtree(temp_dir, ignore_errors=True)
                return response
            except Exception as e:
                logging.error(f"Download error: {e}")
                flash(f"Download Error: {str(e)}", "error")
                return redirect(url_for('index'))

    return render_template("index.html", formats=None)
    
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug_mode = False if os.environ.get("PORT") else True
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
