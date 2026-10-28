import os
import shutil
import subprocess
from pathlib import Path
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
import imageio_ffmpeg
from gradio_client import Client, handle_file

load_dotenv(".env.local")

WORKSPACE = Path(r"c:\Users\User\Desktop\AI Video")
KEYFRAMES_DIR = WORKSPACE / "assets" / "keyframes"
REAL_CLIPS_DIR = WORKSPACE / "assets" / "real_clips"
REAL_VOICES_DIR = WORKSPACE / "assets" / "real_voices"
OUTPUT_10S = WORKSPACE / "Opening_10s_Real_AI_Film.mp4"
ARTIFACT_10S = Path(r"C:\Users\User\.gemini\antigravity\brain\9b243d93-dfd4-4c84-ad2f-0b408c2ac463\Opening_10s_Real_AI_Film.mp4")

REAL_CLIPS_DIR.mkdir(parents=True, exist_ok=True)
REAL_VOICES_DIR.mkdir(parents=True, exist_ok=True)

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
eleven_client = ElevenLabs()


def generate_elevenlabs_audio():
    dialogue_out = REAL_VOICES_DIR / "opening_10s_dialogue.mp3"
    sfx_out = REAL_VOICES_DIR / "opening_10s_sfx.mp3"

    if not dialogue_out.exists():
        print("Generating ElevenLabs v3 Emotional Multi-Speaker Dialogue...")
        audio_stream = eleven_client.text_to_dialogue.convert(
            model_id="eleven_v3",
            inputs=[
                {
                    "text": "[sighs heavily, exhausted] Ma... everything is going up lah. Why are you still paying for that old policy every month? Keep the cash better.",
                    "voice_id": "bIHbv24MWmeRgasZH58o",
                },
                {
                    "text": "[warm, gentle motherly tone, soft chuckle] Just a little bit only... Drink your soup first, before it gets cold.",
                    "voice_id": "hpp4J3VqNfWAUOO0d1Us",
                },
                {
                    "text": "[hurried, stressed sigh] No time, Ma. Client wants revisions by midnight.",
                    "voice_id": "bIHbv24MWmeRgasZH58o",
                },
            ],
        )
        dialogue_out.write_bytes(b"".join(audio_stream))

    if not sfx_out.exists():
        print("Generating ElevenLabs Tropical Rain & Soup Bowl SFX...")
        sfx_stream = eleven_client.text_to_sound_effects.convert(
            text="Heavy tropical night rain pattering against glass louvre windows with a warm ceramic soup bowl and spoon gently placed on a wooden dining table",
            duration_seconds=11.0,
            prompt_influence=0.5,
        )
        sfx_out.write_bytes(b"".join(sfx_stream))

    return dialogue_out, sfx_out


def generate_real_video_clips():
    print("Connecting to Lightricks/ltx-video-distilled for real Image-to-Video generation...")
    client = Client("Lightricks/ltx-video-distilled")

    clip1_path = REAL_CLIPS_DIR / "clip_01.mp4"
    if not clip1_path.exists():
        res1, _ = client.predict(
            prompt="Cinematic live-action film shot. The Malaysian mother gently pours hot steaming herbal soup from the stainless steel thermal flask into the porcelain bowl with a warm smile, while her exhausted son Ryan rubs his forehead stressed at his laptop. Rain falls outside the windows.",
            negative_prompt="worst quality, inconsistent motion, blurry, jittery, distorted, morphing",
            input_image_filepath=handle_file(str(KEYFRAMES_DIR / "01_prologue_terrace_house.jpg")),
            input_video_filepath=None,
            height_ui=512,
            width_ui=768,
            mode="image-to-video",
            duration_ui=5,
            ui_frames_to_use=9,
            seed_ui=42,
            randomize_seed=False,
            ui_guidance_scale=1.0,
            improve_texture_flag=True,
            api_name="/image_to_video",
        )
        shutil.copyfile(res1["video"], clip1_path)

    clip2_path = REAL_CLIPS_DIR / "clip_02.mp4"
    if not clip2_path.exists():
        res2, _ = client.predict(
            prompt="Cinematic tabletop close-up shot. The older woman's gentle hands carefully slide a payment receipt into the worn transparent plastic zip-folder labeled MEDICAL POLICY on the wooden dining table while white steam rises from the hot soup bowl beside her.",
            negative_prompt="worst quality, inconsistent motion, blurry, jittery, distorted, morphing",
            input_image_filepath=handle_file(str(KEYFRAMES_DIR / "01b_prologue_folder.jpg")),
            input_video_filepath=None,
            height_ui=512,
            width_ui=768,
            mode="image-to-video",
            duration_ui=5,
            ui_frames_to_use=9,
            seed_ui=108,
            randomize_seed=False,
            ui_guidance_scale=1.0,
            improve_texture_flag=True,
            api_name="/image_to_video",
        )
        shutil.copyfile(res2["video"], clip2_path)

    return clip1_path, clip2_path


def merge_10s_film(clip1, clip2, dialogue_mp3, sfx_mp3):
    concat_txt = REAL_CLIPS_DIR / "concat_10s.txt"
    concat_txt.write_text(
        f"file '{str(clip1).replace(os.sep, '/')}'\nfile '{str(clip2).replace(os.sep, '/')}'\n",
        encoding="utf-8",
    )

    joined_vid = REAL_CLIPS_DIR / "joined_10s_raw.mp4"
    subprocess.run(
        [
            FFMPEG_EXE,
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_txt),
            "-vf",
            "scale=1920:1080:flags=lanczos,fps=24,format=yuv420p",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "18",
            "-an",
            str(joined_vid),
        ],
        check=True,
    )

    subprocess.run(
        [
            FFMPEG_EXE,
            "-y",
            "-stream_loop",
            "-1",
            "-i",
            str(joined_vid),
            "-i",
            str(dialogue_mp3),
            "-stream_loop",
            "-1",
            "-i",
            str(sfx_mp3),
            "-filter_complex",
            "[1:a]volume=1.0[a_vo];[2:a]volume=0.30[a_sfx];[a_vo][a_sfx]amix=inputs=2:duration=first:dropout_transition=2[a_out]",
            "-map",
            "0:v:0",
            "-map",
            "[a_out]",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-shortest",
            str(OUTPUT_10S),
        ],
        check=True,
    )
    shutil.copyfile(OUTPUT_10S, ARTIFACT_10S)


if __name__ == "__main__":
    d_mp3, s_mp3 = generate_elevenlabs_audio()
    c1, c2 = generate_real_video_clips()
    merge_10s_film(c1, c2, d_mp3, s_mp3)
