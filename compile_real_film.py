"""
Auto-Compiler for 'The Life Vending Machine' Real AI Film Clips + Emotional Voices
----------------------------------------------------------------------------------
How it works:
1. Drop your generated Image-to-Video MP4 clips (from Kling / Hailuo / Vidu) into:
   c:\\Users\\User\\Desktop\\AI Video\\assets\\real_clips\\
   Named: clip_01.mp4, clip_02.mp4 ... clip_11.mp4

2. Drop your emotional voice recordings / ElevenLabs MP3s into:
   c:\\Users\\User\\Desktop\\AI Video\\assets\\real_voices\\
   Named: voice_01.mp3 ... voice_08.mp3

3. Run:
   python compile_real_film.py
   (Any missing clips or voices will automatically fall back to our high-res motion keyframes so it never crashes!)
"""

import os
import subprocess
import imageio_ffmpeg

WORKSPACE = r"c:\Users\User\Desktop\AI Video"
REAL_CLIPS_DIR = os.path.join(WORKSPACE, "assets", "real_clips")
REAL_VOICES_DIR = os.path.join(WORKSPACE, "assets", "real_voices")
FALLBACK_SEGMENTS_DIR = os.path.join(WORKSPACE, "assets", "segments_film")
COMPILED_TEMP_DIR = os.path.join(WORKSPACE, "assets", "compiled_real_temp")
FINAL_OUTPUT = os.path.join(WORKSPACE, "The_Life_Vending_Machine_FINAL_COMPETITION.mp4")

os.makedirs(COMPILED_TEMP_DIR, exist_ok=True)
FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()

SCENE_PLAN = [
    {"clip": "clip_01.mp4", "voice": "voice_01.mp3", "fallback": "shot_02.mp4", "title": "Prologue A - Dining Table"},
    {"clip": "clip_02.mp4", "voice": "voice_02.mp3", "fallback": "shot_03.mp4", "title": "Prologue B - Insurance Folder"},
    {"clip": "clip_03.mp4", "voice": None,           "fallback": "shot_06.mp4", "title": "Scene 1A - Discovering the Machine"},
    {"clip": "clip_04.mp4", "voice": "voice_03.mp3", "fallback": "shot_08.mp4", "title": "Scene 1B - Pressing Confirm"},
    {"clip": "clip_05.mp4", "voice": None,           "fallback": "shot_09.mp4", "title": "Scene 2A - Corporate Boardroom"},
    {"clip": "clip_06.mp4", "voice": "voice_04.mp3", "fallback": "shot_10.mp4", "title": "Scene 2B - Washroom Vertigo"},
    {"clip": "clip_07.mp4", "voice": "voice_05.mp3", "fallback": "shot_12.mp4", "title": "Scene 3 - Hospital Deposit Crisis"},
    {"clip": "clip_08.mp4", "voice": "voice_06.mp3", "fallback": "shot_15.mp4", "title": "Scene 4 - Slamming Cancel"},
    {"clip": "clip_09.mp4", "voice": "voice_07.mp3", "fallback": "shot_16.mp4", "title": "Scene 5 - Hospital Ward Payoff"},
    {"clip": "clip_10.mp4", "voice": None,           "fallback": "shot_18.mp4", "title": "Scene 6A - Morning Soup"},
    {"clip": "clip_11.mp4", "voice": "voice_08.mp3", "fallback": "shot_19.mp4", "title": "Scene 6B - Walking Past Machine"},
]


def main():
    print("=================================================================")
    print("  THE LIFE VENDING MACHINE — REAL AI FILM COMPILER")
    print("=================================================================")

    found_clips = [f for f in os.listdir(REAL_CLIPS_DIR) if f.lower().endswith((".mp4", ".mov", ".webm"))]
    found_voices = [f for f in os.listdir(REAL_VOICES_DIR) if f.lower().endswith((".mp3", ".wav", ".m4a"))]
    print(f"Found {len(found_clips)}/11 real AI video clips in assets/real_clips/")
    print(f"Found {len(found_voices)}/8 emotional voice tracks in assets/real_voices/\n")

    output_segments = []
    for idx, item in enumerate(SCENE_PLAN, 1):
        clip_path = os.path.join(REAL_CLIPS_DIR, item["clip"])
        voice_path = os.path.join(REAL_VOICES_DIR, item["voice"]) if item["voice"] else None
        fallback_path = os.path.join(FALLBACK_SEGMENTS_DIR, item["fallback"])
        out_seg = os.path.join(COMPILED_TEMP_DIR, f"final_seg_{idx:02d}.mp4")

        v_src = clip_path if os.path.exists(clip_path) else fallback_path
        has_custom_voice = voice_path and os.path.exists(voice_path)

        status_v = "REAL AI VIDEO" if os.path.exists(clip_path) else "Fallback Keyframe"
        status_a = "REAL EMOTIONAL VOICE" if has_custom_voice else "Default Audio"
        print(f" [{idx:02d}/11] {item['title']} -> Video: [{status_v}] | Audio: [{status_a}]")

        if has_custom_voice:
            # Loop/stretch video to match custom emotional voice duration and normalize to 1920x1080 24fps
            cmd = [
                FFMPEG_EXE, "-y",
                "-stream_loop", "-1", "-i", v_src,
                "-i", voice_path,
                "-map", "0:v:0", "-map", "1:a:0",
                "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,fps=24,format=yuv420p",
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "19",
                "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
                "-shortest",
                out_seg
            ]
        else:
            cmd = [
                FFMPEG_EXE, "-y",
                "-i", v_src,
                "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,fps=24,format=yuv420p",
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "19",
                "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
                out_seg
            ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        output_segments.append(out_seg)

    concat_file = os.path.join(COMPILED_TEMP_DIR, "concat_final.txt")
    with open(concat_file, "w", encoding="utf-8") as f:
        for seg in output_segments:
            f.write(f"file '{seg.replace(os.sep, '/')}'\n")

    subprocess.run(
        [FFMPEG_EXE, "-y", "-f", "concat", "-safe", "0", "-i", concat_file, "-c", "copy", FINAL_OUTPUT],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    print("\n=================================================================")
    print(f"DONE! Compiled film saved to:\n{FINAL_OUTPUT}")
    print("=================================================================")


if __name__ == "__main__":
    main()
