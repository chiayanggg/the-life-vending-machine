import asyncio
import math
import os
import subprocess
import wave
import struct
import edge_tts
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

WORKSPACE = r"c:\Users\User\Desktop\AI Video"
KEYFRAMES_DIR = os.path.join(WORKSPACE, "assets", "keyframes")
AUDIO_DIR = os.path.join(WORKSPACE, "assets", "audio_temp")
SEGMENTS_DIR = os.path.join(WORKSPACE, "assets", "segments_temp")
OUTPUT_MP4 = os.path.join(WORKSPACE, "The_Life_Vending_Machine_Animatic.mp4")
ARTIFACT_MP4 = r"C:\Users\User\.gemini\antigravity\brain\9b243d93-dfd4-4c84-ad2f-0b408c2ac463\The_Life_Vending_Machine_Animatic.mp4"

os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(SEGMENTS_DIR, exist_ok=True)

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()

# Voices (Southeast Asian English Neural Voices)
VOICE_RYAN = "en-SG-WayneNeural"
VOICE_MUM = "en-SG-LunaNeural"
VOICE_NURSE = "en-HK-YanNeural"
VOICE_NARRATOR = "en-SG-WayneNeural"

BEATS = [
    {
        "id": "01_prologue_1",
        "scene_tag": "PROLOGUE — THE ORDINARY TABLE",
        "image": "01_prologue_terrace_house.jpg",
        "speaker": "RYAN",
        "voice": VOICE_RYAN,
        "rate": "+0%",
        "pitch": "+0Hz",
        "text": "Ma, everything is going up lah. Why are you still paying for that old policy every month? Keep the cash better.",
        "sub_en": "RYAN: \"Ma, everything's going up lah. Why still pay for that old policy every month?\"",
        "sub_zh": "Ryan：“妈，现在什么都起价了，干嘛每个月还交那份旧保单？留着现金更好啦。”",
        "zoom": (1.0, 1.08),
        "sfx": "rain_warm",
        "pad_sec": 1.2,
    },
    {
        "id": "02_prologue_2",
        "scene_tag": "PROLOGUE — THE ORDINARY TABLE",
        "image": "01_prologue_terrace_house.jpg",
        "speaker": "MUM",
        "voice": VOICE_MUM,
        "rate": "-8%",
        "pitch": "-4Hz",
        "text": "Just a little bit only. Drink your soup first, before it gets cold.",
        "sub_en": "MUM: \"Just a little bit only. Drink first, before it gets cold.\"",
        "sub_zh": "妈妈：“一点点钱而已。先喝汤吧，别等凉了。”",
        "zoom": (1.08, 1.14),
        "sfx": "rain_warm",
        "pad_sec": 1.0,
    },
    {
        "id": "03_prologue_3",
        "scene_tag": "PROLOGUE — THE ORDINARY TABLE",
        "image": "01_prologue_terrace_house.jpg",
        "speaker": "RYAN",
        "voice": VOICE_RYAN,
        "rate": "+6%",
        "pitch": "+0Hz",
        "text": "No time, Ma. Client wants revisions by midnight.",
        "sub_en": "RYAN: \"No time, Ma. Client wants revisions by midnight.\"",
        "sub_zh": "Ryan：“来不及了妈，客户半夜前要改稿。”",
        "zoom": (1.14, 1.18),
        "sfx": "rain_warm",
        "pad_sec": 1.2,
    },
    {
        "id": "04_scene1_discover",
        "scene_tag": "SCENE 1 — THE FIRST TRADE (KL UNDERPASS, 1:15 AM)",
        "image": "02_scene1_vending_machine.jpg",
        "speaker": "MACHINE / V.O.",
        "voice": VOICE_NARRATOR,
        "rate": "-10%",
        "pitch": "-8Hz",
        "text": "What would you buy? Wealth. Health. Time. Rule: Everything has a price.",
        "sub_en": "[VENDING MACHINE]: \"WHAT WOULD YOU BUY? WEALTH · HEALTH · TIME — EVERYTHING HAS A PRICE.\"",
        "sub_zh": "【神秘贩卖机】：“你想购买什么？财富 · 健康 · 时间 —— 所有东西都有代价。”",
        "zoom": (1.0, 1.10),
        "sfx": "crt_hum",
        "pad_sec": 1.5,
    },
    {
        "id": "05_scene1_confirm",
        "scene_tag": "SCENE 1 — THE FIRST TRADE",
        "image": "03_scene1_confirm_trade.jpg",
        "speaker": "RYAN (V.O.)",
        "voice": VOICE_RYAN,
        "rate": "-4%",
        "pitch": "-2Hz",
        "text": "Selection: Career Breakthrough. Price: Twenty percent of your health. I'm twenty-six. I'm healthy. What's a little exhaustion if we finally make it?",
        "sub_en": "RYAN (V.O.): \"Price: 20% of your health... I'm 26. What's a little exhaustion if we finally make it?\"",
        "sub_zh": "Ryan（内心）：“代价：20%的健康……我还年轻，牺牲一点健康换事业成功算什么？”",
        "zoom": (1.0, 1.12),
        "sfx": "heartbeat_confirm",
        "pad_sec": 1.5,
    },
    {
        "id": "06_scene2_success",
        "scene_tag": "SCENE 2 — THE COST OF WINNING",
        "image": "04_scene2_corporate_success.jpg",
        "speaker": "RYAN (V.O.)",
        "voice": VOICE_RYAN,
        "rate": "+2%",
        "pitch": "+0Hz",
        "text": "Your opportunity has arrived. Within months, the deals closed, the titles came, and every door in Kuala Lumpur opened.",
        "sub_en": "Within months, deals closed, promotions came, and every door in KL opened.",
        "sub_zh": "几个月内，重要项目接踵而来、升职加薪，事业大门彻底敞开。",
        "zoom": (1.08, 1.0),
        "sfx": "success_chord",
        "pad_sec": 1.2,
    },
    {
        "id": "07_scene2_vertigo",
        "scene_tag": "SCENE 2 — THE COST OF WINNING",
        "image": "05_scene2_vertigo_washroom.jpg",
        "speaker": "MUM (VOICE NOTE)",
        "voice": VOICE_MUM,
        "rate": "-8%",
        "pitch": "-4Hz",
        "text": "Ryan ah, Ma left lotus root soup in the fridge. Earning money is important, but don't forget to take care of your body, okay? Rest early.",
        "sub_en": "MUM (Voice Note): \"Earning money is important, but don't forget to take care of your body, okay?\"",
        "sub_zh": "妈妈（语音留言）：“Ryan啊，赚钱重要，身体也要顾好，早点休息啊。”",
        "zoom": (1.0, 1.10),
        "sfx": "tinnitus_vertigo",
        "pad_sec": 0.8,
    },
    {
        "id": "08_scene2_reply",
        "scene_tag": "SCENE 2 — THE COST OF WINNING",
        "image": "05_scene2_vertigo_washroom.jpg",
        "speaker": "RYAN",
        "voice": VOICE_RYAN,
        "rate": "-6%",
        "pitch": "-3Hz",
        "text": "Yeah, yeah... I know, Ma. Soon.",
        "sub_en": "RYAN: \"Yeah, yeah... I know, Ma. Soon.\"",
        "sub_zh": "Ryan：“知道啦，妈……再忙完这一阵子。”",
        "zoom": (1.10, 1.15),
        "sfx": "tinnitus_vertigo",
        "pad_sec": 1.2,
    },
    {
        "id": "09_scene3_hospital",
        "scene_tag": "SCENE 3 — THE SUDDEN CRISIS",
        "image": "06_scene3_hospital_crisis.jpg",
        "speaker": "RYAN (V.O.)",
        "voice": VOICE_RYAN,
        "rate": "-5%",
        "pitch": "-3Hz",
        "text": "Then the hospital call came. Estimated surgical deposit: thirty-eight thousand Ringgit. I thought climbing faster meant I was ready. I wasn't ready for anything.",
        "sub_en": "RYAN (V.O.): \"Surgical deposit: RM 38,000. I thought success meant I was ready. I wasn't.\"",
        "sub_zh": "Ryan（内心）：“手术押金：RM 38,000。我以为事业有起色就代表准备好了，原来我根本毫无防备。”",
        "zoom": (1.0, 1.10),
        "sfx": "hospital_beep",
        "pad_sec": 1.5,
    },
    {
        "id": "10_scene4_cancel",
        "scene_tag": "SCENE 4 — THE SECOND TRADE & THE TWIST",
        "image": "07_scene4_slam_cancel.jpg",
        "speaker": "RYAN (V.O.)",
        "voice": VOICE_RYAN,
        "rate": "-2%",
        "pitch": "-2Hz",
        "text": "Price: All of your remaining health. I tried pressing Health and Time for my mother, but the machine flashed: Error. This machine only takes. It cannot protect. Remembering Ma's words, I slammed Cancel.",
        "sub_en": "[MACHINE]: \"ERROR: THIS MACHINE ONLY TAKES. IT CANNOT PROTECT.\" — Ryan slams [ CANCEL ].",
        "sub_zh": "【贩卖机】：“错误：本机器只索取，无法提供保障。” —— Ryan想起妈妈的话，含泪按下【取消】。",
        "zoom": (1.0, 1.12),
        "sfx": "cancel_slam",
        "pad_sec": 1.5,
    },
    {
        "id": "11_scene5_nurse",
        "scene_tag": "SCENE 5 — TRUE PROTECTION",
        "image": "08_scene5_hospital_payoff.jpg",
        "speaker": "NURSE",
        "voice": VOICE_NURSE,
        "rate": "+0%",
        "pitch": "+2Hz",
        "text": "Mister Tan, no need to worry about the deposit. The Guarantee Letter just came through from your mum's medical policy. We are wheeling her in now.",
        "sub_en": "NURSE: \"Mr. Tan, no need to worry about the deposit. Guarantee Letter just came through from your mum's policy.\"",
        "sub_zh": "护士：“陈先生，不用担心押金了，你妈妈医疗保单的担保信（GL）已经批下来了。”",
        "zoom": (1.08, 1.02),
        "sfx": "warm_piano",
        "pad_sec": 1.0,
    },
    {
        "id": "12_scene5_mum_payoff",
        "scene_tag": "SCENE 5 — TRUE PROTECTION",
        "image": "08_scene5_hospital_payoff.jpg",
        "speaker": "MUM",
        "voice": VOICE_MUM,
        "rate": "-10%",
        "pitch": "-4Hz",
        "text": "I hoped we would never need to use it... But I never wanted my son to trade his health just to save mine.",
        "sub_en": "MUM: \"I hoped we'd never need it... But I never wanted my son to trade his health just to save mine.\"",
        "sub_zh": "妈妈：“我也希望永远用不到……但我绝不想让儿子为了救我，拿自己的健康去交换。”",
        "zoom": (1.02, 1.10),
        "sfx": "warm_piano",
        "pad_sec": 1.8,
    },
    {
        "id": "13_scene6_morning",
        "scene_tag": "SCENE 6 — THE LAST CHOICE",
        "image": "09_scene6_morning_soup.jpg",
        "speaker": "RYAN (V.O.)",
        "voice": VOICE_RYAN,
        "rate": "-6%",
        "pitch": "+0Hz",
        "text": "True protection isn't a desperate trade when crisis hits. It is a quiet promise prepared long before the storm arrives.",
        "sub_en": "RYAN (V.O.): \"True protection isn't a desperate trade in a crisis. It's a promise prepared before the storm.\"",
        "sub_zh": "Ryan（内心）：“真正的保障，不是危机降临时绝望的交换，而是风雨来临前早就准备好的守护。”",
        "zoom": (1.0, 1.08),
        "sfx": "warm_piano",
        "pad_sec": 1.5,
    },
    {
        "id": "14_scene6_walkaway",
        "scene_tag": "FINALE — THE PRICE OF TOMORROW",
        "image": "10_scene6_walk_away.jpg",
        "speaker": "TITLE CARD",
        "voice": VOICE_NARRATOR,
        "rate": "-12%",
        "pitch": "-4Hz",
        "text": "Not every price has to be paid with your life. Life is unpredictable. Be prepared.",
        "sub_en": "\"NOT EVERY PRICE HAS TO BE PAID WITH YOUR LIFE. — LIFE IS UNPREDICTABLE. BE PREPARED.\"",
        "sub_zh": "“并不是人生中的每一份代价，都需要用生命去交换。人生无法预测，但保障可以提前准备。”",
        "zoom": (1.0, 1.08),
        "sfx": "warm_piano",
        "pad_sec": 2.5,
    },
]


async def generate_tts():
    for beat in BEATS:
        mp3_path = os.path.join(AUDIO_DIR, f"{beat['id']}.mp3")
        wav_path = os.path.join(AUDIO_DIR, f"{beat['id']}_voice.wav")
        communicate = edge_tts.Communicate(
            beat["text"],
            beat["voice"],
            rate=beat["rate"],
            pitch=beat["pitch"],
        )
        await communicate.save(mp3_path)
        subprocess.run(
            [
                FFMPEG_EXE,
                "-y",
                "-i",
                mp3_path,
                "-ar",
                "44100",
                "-ac",
                "1",
                wav_path,
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


def mix_sfx_and_pad(voice_wav, out_wav, sfx_type, pad_sec):
    with wave.open(voice_wav, "rb") as wf:
        sr = wf.getframerate()
        n_frames = wf.getnframes()
        raw = wf.readframes(n_frames)
        voice_samples = list(struct.unpack(f"<{n_frames}h", raw))

    pre_pad = int(0.4 * sr)
    post_pad = int(pad_sec * sr)
    total_samples = pre_pad + len(voice_samples) + post_pad

    mixed = []
    import random
    random.seed(42)
    rain_state = 0.0

    for i in range(total_samples):
        t = i / sr
        v = 0.0
        if pre_pad <= i < pre_pad + len(voice_samples):
            v = voice_samples[i - pre_pad] / 32768.0

        # Procedural background ambience per scene mood
        bg = 0.0
        if sfx_type == "rain_warm":
            noise = random.uniform(-1, 1)
            rain_state = 0.92 * rain_state + 0.08 * noise
            bg = rain_state * 0.06 + 0.02 * math.sin(2 * math.pi * 220 * t)
        elif sfx_type == "crt_hum":
            bg = (
                0.04 * math.sin(2 * math.pi * 60 * t)
                + 0.02 * math.sin(2 * math.pi * 120 * t)
                + 0.015 * math.sin(2 * math.pi * 432 * t)
            )
        elif sfx_type == "heartbeat_confirm":
            beat_phase = (t * 1.3) % 1.0
            hb = math.exp(-beat_phase * 12) * math.sin(2 * math.pi * 55 * t) * 0.18
            bg = hb + 0.03 * math.sin(2 * math.pi * 110 * t)
        elif sfx_type == "success_chord":
            bg = (
                0.03 * math.sin(2 * math.pi * 261.63 * t)
                + 0.025 * math.sin(2 * math.pi * 329.63 * t)
                + 0.025 * math.sin(2 * math.pi * 392.00 * t)
            )
        elif sfx_type == "tinnitus_vertigo":
            # Subtle high-frequency tinnitus ring + low throb
            bg = 0.035 * math.sin(2 * math.pi * 3100 * t) * (0.6 + 0.4 * math.sin(2 * math.pi * 0.8 * t)) + 0.04 * math.sin(2 * math.pi * 65 * t)
        elif sfx_type == "hospital_beep":
            beep = 0.06 * math.sin(2 * math.pi * 1046.5 * t) if (t % 1.2) < 0.12 else 0.0
            bg = beep + 0.03 * math.sin(2 * math.pi * 146.8 * t)
        elif sfx_type == "cancel_slam":
            noise = random.uniform(-1, 1)
            rain_state = 0.90 * rain_state + 0.10 * noise
            bg = rain_state * 0.07 + 0.03 * math.sin(2 * math.pi * 98 * t)
        elif sfx_type == "warm_piano":
            # Warm Fmaj7 / Cmaj7 ambient pad
            env = 0.7 + 0.3 * math.sin(2 * math.pi * 0.25 * t)
            bg = env * (
                0.035 * math.sin(2 * math.pi * 174.61 * t)
                + 0.03 * math.sin(2 * math.pi * 220.00 * t)
                + 0.03 * math.sin(2 * math.pi * 261.63 * t)
                + 0.025 * math.sin(2 * math.pi * 329.63 * t)
            )

        # Fade in / out envelope on background
        duration = total_samples / sr
        if t < 0.3:
            bg *= t / 0.3
        elif t > duration - 0.4:
            bg *= max(0.0, (duration - t) / 0.4)

        sample = max(-0.98, min(0.98, v * 0.92 + bg))
        mixed.append(int(sample * 32767))

    with wave.open(out_wav, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(struct.pack(f"<{len(mixed)}h", *mixed))

    return total_samples / sr


def get_font(size, bold=False):
    candidates = [
        r"C:\Windows\Fonts\msyhbd.ttc" if bold else r"C:\Windows\Fonts\msyh.ttc",
        r"C:\Windows\Fonts\simhei.ttf",
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def create_subtitled_overlay_image(img_path, scene_tag, sub_en, sub_zh, out_png):
    base = Image.open(img_path).convert("RGB").resize((1920, 1080), Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(base, "RGBA")

    # Cinematic top & bottom letterbox bars with subtle gradient overlay
    draw.rectangle([(0, 0), (1920, 82)], fill=(8, 10, 15, 215))
    draw.rectangle([(0, 905), (1920, 1080)], fill=(8, 10, 15, 225))

    font_tag = get_font(24, bold=True)
    font_en = get_font(29, bold=True)
    font_zh = get_font(28, bold=False)

    # Top left scene tag & top right film title
    draw.text((48, 26), f"🎬  {scene_tag}", fill=(255, 205, 110, 255), font=font_tag)
    draw.text((1380, 26), "THE LIFE VENDING MACHINE 《人生贩卖机》", fill=(180, 210, 230, 220), font=font_tag)

    # Centered subtitles at bottom
    bbox_en = draw.textbbox((0, 0), sub_en, font=font_en)
    w_en = bbox_en[2] - bbox_en[0]
    draw.text(((1920 - w_en) // 2, 932), sub_en, fill=(255, 255, 255, 255), font=font_en)

    bbox_zh = draw.textbbox((0, 0), sub_zh, font=font_zh)
    w_zh = bbox_zh[2] - bbox_zh[0]
    draw.text(((1920 - w_zh) // 2, 988), sub_zh, fill=(255, 215, 130, 255), font=font_zh)

    base.save(out_png, quality=95)


def build_video():
    print("1/3 Generating Southeast Asian English Neural Voiceovers...")
    asyncio.run(generate_tts())

    segment_files = []
    print("2/3 Rendering 14 Cinematic Animatic Segments with Subtitles & Sound Design...")
    for idx, beat in enumerate(BEATS, 1):
        voice_wav = os.path.join(AUDIO_DIR, f"{beat['id']}_voice.wav")
        mixed_wav = os.path.join(AUDIO_DIR, f"{beat['id']}_mixed.wav")
        duration = mix_sfx_and_pad(voice_wav, mixed_wav, beat["sfx"], beat["pad_sec"])

        img_src = os.path.join(KEYFRAMES_DIR, beat["image"])
        styled_png = os.path.join(SEGMENTS_DIR, f"{beat['id']}_frame.png")
        create_subtitled_overlay_image(
            img_src,
            beat["scene_tag"],
            beat["sub_en"],
            beat["sub_zh"],
            styled_png,
        )

        seg_mp4 = os.path.join(SEGMENTS_DIR, f"seg_{idx:02d}.mp4")
        # Render smooth 1080p segment with fade-in/out
        fade_out_start = max(0.5, duration - 0.35)
        vf = f"scale=1920:1080,fade=t=in:st=0:d=0.3,fade=t=out:st={fade_out_start:.2f}:d=0.35,format=yuv420p"
        cmd = [
            FFMPEG_EXE,
            "-y",
            "-loop",
            "1",
            "-i",
            styled_png,
            "-i",
            mixed_wav,
            "-t",
            f"{duration:.2f}",
            "-vf",
            vf,
            "-c:v",
            "libx264",
            "-preset",
            "ultrafast",
            "-tune",
            "stillimage",
            "-r",
            "24",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-shortest",
            seg_mp4,
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        segment_files.append(seg_mp4)
        print(f"   [OK] Segment {idx:02d}/14 ({duration:.1f}s) - {beat['id']}")

    print("3/3 Concatenating Final MP4 Video Animatic...")
    concat_list = os.path.join(SEGMENTS_DIR, "concat_list.txt")
    with open(concat_list, "w", encoding="utf-8") as f:
        for seg in segment_files:
            f.write(f"file '{seg.replace(os.sep, '/')}'\n")

    subprocess.run(
        [
            FFMPEG_EXE,
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            concat_list,
            "-c",
            "copy",
            OUTPUT_MP4,
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    import shutil
    shutil.copyfile(OUTPUT_MP4, ARTIFACT_MP4)
    print(f"DONE! Saved to: {OUTPUT_MP4}")


if __name__ == "__main__":
    build_video()
