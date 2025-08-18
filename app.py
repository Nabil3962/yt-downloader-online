from flask import Flask, render_template, request, send_file
import yt_dlp
import os
import tempfile

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("url")
        chosen_format = request.form.get("format_id")
        audio_only = request.form.get("audio_only")

        if not url:
            return "Please enter a YouTube URL", 400

        # Step 1: If no format chosen, show available formats
        if not chosen_format and not audio_only:
            with yt_dlp.YoutubeDL({'quiet': True, 'no_warnings': True}) as ydl:
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
            return render_template("index.html", url=url, formats=formats)

        # Step 2: Download the chosen format or audio
        else:
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

                return send_file(filename, as_attachment=True)

            except Exception as e:
                return f"Download Error: {str(e)}", 500

    return render_template("index.html", formats=None)


if __name__ == "__main__":
    # For local testing only
    port = int(os.environ.get("PORT", 5000))
    debug_mode = False if os.environ.get("PORT") else True
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
