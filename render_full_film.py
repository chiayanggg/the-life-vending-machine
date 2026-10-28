import asyncio
import math
import os
import random
import shutil
import struct
import subprocess
import wave
import edge_tts
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

WORKSPACE = r"c:\Users\User\Desktop\AI Video"
KEYFRAMES_DIR = os.path.join(WORKSPACE, "assets", "keyframes")
REFS_DIR = os.path.join(WORKSPACE, "assets", "references")
AUDIO_DIR = os.path.join(WORKSPACE, "assets", "audio_film")
SEGMENTS_DIR = os.path.join(WORKSPACE, "assets", "segments_film")
OUTPUT_MP4 = os.path.join(WORKSPACE, "The_Life_Vending_Machine_Full_Film.mp4")
ARTIFACT_MP4 = r"C:\Users\User\.gemini\antigravity\brain\9b243d93-dfd4-4c84-ad2f-0b408c2ac463\The_Life_Vending_Machine_Full_Film.mp4"

os.makedirs(KEYFRAMES_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(SEGMENTS_DIR, exist_ok=True)

# Copy the newly generated folder close-up if present
folder_src = r"C:\Users\User\.gemini\antigravity\brain\9b243d93-dfd4-4c84-ad2f-0b408c2ac463\shot_prologue_folder_1793028962058.jpg"
folder_dst = os.path.join(KEYFRAMES_DIR, "01b_prologue_folder.jpg")
if os.path.exists(folder_src):
    shutil.copyfile(folder_src, folder_dst)

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()

VOICE_RYAN = "en-SG-WayneNeural"
VOICE_MUM = "en-SG-LunaNeural"
VOICE_NURSE = "en-HK-YanNeural"
VOICE_MACHINE = "en-SG-WayneNeural"


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


def generate_special_keyframes():
    """Create cinematic close-up crops and CRT screen inserts so the film cuts dynamically across 20+ shots."""
    # 1. Opening Title Card
    bg = Image.open(os.path.join(KEYFRAMES_DIR, "02_scene1_vending_machine.jpg")).convert("RGB").resize((1920, 1080))
    bg = bg.filter(ImageFilter.GaussianBlur(radius=6))
    bg = ImageEnhance.Brightness(bg).enhance(0.38)
    draw = ImageDraw.Draw(bg)
    f_title = get_font(74, bold=True)
    f_sub = get_font(36, bold=False)
    f_zh = get_font(54, bold=True)
    draw.text((960, 410), "THE LIFE VENDING MACHINE", fill=(255, 215, 130), font=f_title, anchor="mm")
    draw.text((960, 505), "《 人 生 贩 卖 机 》", fill=(255, 255, 255), font=f_zh, anchor="mm")
    draw.text((960, 595), "THE PRICE OF TOMORROW  ·  A MALAYSIAN SHORT FILM", fill=(160, 215, 235), font=f_sub, anchor="mm")
    bg.save(os.path.join(KEYFRAMES_DIR, "00_title_card.jpg"), quality=95)

    # 2. Close-up crop of Mum's warm face from mum_reference.jpg (right panel)
    mum_ref = Image.open(os.path.join(REFS_DIR, "mum_reference.jpg")).convert("RGB")
    w, h = mum_ref.size
    # Crop right-side medium warm shot and scale to 16:9
    crop_mum = mum_ref.crop((int(w * 0.58), int(h * 0.05), int(w * 0.99), int(h * 0.80))).resize((1920, 1080), Image.Resampling.LANCZOS)
    crop_mum.save(os.path.join(KEYFRAMES_DIR, "01c_mum_closeup.jpg"), quality=95)

    # 3. Close-up crop of the 3 glowing canisters (WEALTH, HEALTH, TIME) from vending machine scene
    vm = Image.open(os.path.join(KEYFRAMES_DIR, "02_scene1_vending_machine.jpg")).convert("RGB")
    w, h = vm.size
    crop_canisters = vm.crop((int(w * 0.22), int(h * 0.16), int(w * 0.78), int(h * 0.72))).resize((1920, 1080), Image.Resampling.LANCZOS)
    crop_canisters.save(os.path.join(KEYFRAMES_DIR, "02b_canisters_closeup.jpg"), quality=95)

    # 4. Close-up CRT Screen: ERROR THIS MACHINE ONLY TAKES
    err_img = Image.open(os.path.join(KEYFRAMES_DIR, "07_scene4_slam_cancel.jpg")).convert("RGB").resize((1920, 1080))
    err_crop = err_img.crop((320, 120, 1680, 885)).resize((1920, 1080), Image.Resampling.LANCZOS)
    err_crop.save(os.path.join(KEYFRAMES_DIR, "07a_machine_error_closeup.jpg"), quality=95)

    # 5. End Credits / Brand Closing Card
    end_bg = Image.open(os.path.join(KEYFRAMES_DIR, "10_scene6_walk_away.jpg")).convert("RGB").resize((1920, 1080))
    end_bg = end_bg.filter(ImageFilter.GaussianBlur(radius=8))
    end_bg = ImageEnhance.Brightness(end_bg).enhance(0.32)
    d_end = ImageDraw.Draw(end_bg)
    f_quote = get_font(48, bold=True)
    f_q_zh = get_font(38, bold=False)
    f_tag = get_font(34, bold=True)
    d_end.text((960, 390), "“NOT EVERY PRICE HAS TO BE PAID WITH YOUR LIFE.”", fill=(255, 220, 140), font=f_quote, anchor="mm")
    d_end.text((960, 460), "并不是人生中的每一份代价，都需要用生命去交换。", fill=(240, 240, 240), font=f_q_zh, anchor="mm")
    d_end.line([(660, 535), (1260, 535)], fill=(255, 205, 110), width=2)
    d_end.text((960, 595), "LIFE IS UNPREDICTABLE. BE PREPARED.", fill=(165, 225, 245), font=f_tag, anchor="mm")
    d_end.text((960, 650), "人生无法预测，但保障可以提前准备。", fill=(200, 220, 230), font=f_q_zh, anchor="mm")
    end_bg.save(os.path.join(KEYFRAMES_DIR, "11_end_card.jpg"), quality=95)


SHOTS = [
    {
        "id": "00_intro",
        "scene": "THE LIFE VENDING MACHINE 《人生贩卖机》",
        "image": "00_title_card.jpg",
        "voice": VOICE_MACHINE,
        "rate": "-10%",
        "pitch": "-6Hz",
        "text": "The Life Vending Machine. The Price of Tomorrow.",
        "sub_en": "THE LIFE VENDING MACHINE — The Price of Tomorrow",
        "sub_zh": "《人生贩卖机》—— 明日的代价",
        "motion": "zoom_in_center",
        "vfx": "rain_neon",
        "sfx": "crt_hum",
        "pad_sec": 1.0,
    },
    {
        "id": "01_prologue_table",
        "scene": "PROLOGUE — KUALA LUMPUR, TERRACE HOUSE",
        "image": "01_prologue_terrace_house.jpg",
        "voice": VOICE_RYAN,
        "rate": "+0%",
        "pitch": "+0Hz",
        "text": "Late at night in Kuala Lumpur. Ryan is chasing career success, exhausted by rejected pitches and a bank balance barely holding on.",
        "sub_en": "Ryan is fighting for his career in KL, exhausted by bills and rejected pitches.",
        "sub_zh": "深夜的吉隆坡，处于事业奋斗期的 Ryan 疲惫不堪，渴望早日成功。",
        "motion": "pan_left_to_right",
        "vfx": "warm_rain",
        "sfx": "rain_warm",
        "pad_sec": 0.6,
    },
    {
        "id": "02_prologue_folder",
        "scene": "PROLOGUE — THE OLD INSURANCE FOLDER",
        "image": "01b_prologue_folder.jpg",
        "voice": VOICE_RYAN,
        "rate": "+2%",
        "pitch": "+0Hz",
        "text": "Ma, everything is going up lah. Why are you still paying for that old medical policy every month? Keep the cash better.",
        "sub_en": "RYAN: \"Ma, everything's going up lah. Why still pay for that old policy every month?\"",
        "sub_zh": "Ryan：“妈，现在什么都起价了，干嘛每个月还交那份旧保单？留着现金更好啦。”",
        "motion": "zoom_in_slow",
        "vfx": "warm_rain",
        "sfx": "rain_warm",
        "pad_sec": 0.6,
    },
    {
        "id": "03_prologue_mum",
        "scene": "PROLOGUE — A MOTHER'S WARMTH",
        "image": "01c_mum_closeup.jpg",
        "voice": VOICE_MUM,
        "rate": "-8%",
        "pitch": "-4Hz",
        "text": "Just a little bit only. Drink your soup first, before it gets cold.",
        "sub_en": "MUM: \"Just a little bit only. Drink your soup first, before it gets cold.\"",
        "sub_zh": "妈妈：“一点点钱而已。先喝汤吧，别等凉了。”",
        "motion": "zoom_in_center",
        "vfx": "warm_dust",
        "sfx": "rain_warm",
        "pad_sec": 0.5,
    },
    {
        "id": "04_prologue_leave",
        "scene": "PROLOGUE — NO TIME TO REST",
        "image": "01_prologue_terrace_house.jpg",
        "voice": VOICE_RYAN,
        "rate": "+6%",
        "pitch": "+0Hz",
        "text": "No time, Ma. Client wants revisions by midnight.",
        "sub_en": "RYAN: \"No time, Ma. Client wants revisions by midnight.\"",
        "sub_zh": "Ryan：“来不及了妈，客户半夜前要改稿。”",
        "motion": "zoom_out_slow",
        "vfx": "warm_rain",
        "sfx": "rain_warm",
        "pad_sec": 0.8,
    },
    {
        "id": "05_scene1_underpass",
        "scene": "SCENE 1 — THE MYSTERIOUS VENDING MACHINE (1:15 AM)",
        "image": "02_scene1_vending_machine.jpg",
        "voice": VOICE_MACHINE,
        "rate": "-10%",
        "pitch": "-8Hz",
        "text": "Walking through a quiet underpass at 1 AM, Ryan discovers a mysterious machine: What would you buy?",
        "sub_en": "In a deserted KL underpass at 1 AM, a glowing machine asks: \"WHAT WOULD YOU BUY?\"",
        "sub_zh": "凌晨一点的地下通道，Ryan 意外发现一台神秘贩卖机：“你想购买什么？”",
        "motion": "zoom_in_slow",
        "vfx": "rain_neon",
        "sfx": "crt_hum",
        "pad_sec": 0.7,
    },
    {
        "id": "06_scene1_canisters",
        "scene": "SCENE 1 — WEALTH · HEALTH · TIME",
        "image": "02b_canisters_closeup.jpg",
        "voice": VOICE_MACHINE,
        "rate": "-12%",
        "pitch": "-10Hz",
        "text": "Inside are the three most precious things in life: Wealth. Health. Time. Rule: Everything has a price.",
        "sub_en": "WEALTH · HEALTH · TIME — \"RULE: EVERYTHING HAS A PRICE.\"",
        "sub_zh": "它出售人生中最珍贵的三样东西：财富 · 健康 · 时间 ——“所有东西都有代价。”",
        "motion": "pan_left_to_right",
        "vfx": "crt_scanlines",
        "sfx": "crt_hum",
        "pad_sec": 0.8,
    },
    {
        "id": "07_scene1_confirm",
        "scene": "SCENE 1 — THE FIRST TRADE",
        "image": "03_scene1_confirm_trade.jpg",
        "voice": VOICE_RYAN,
        "rate": "-4%",
        "pitch": "-2Hz",
        "text": "Ryan selects Wealth: Career Success. The screen flashes: Price, your health. Thinking he is still young and strong, he presses Confirm.",
        "sub_en": "PRICE: YOUR HEALTH — Thinking he's still young, Ryan presses [ CONFIRM ].",
        "sub_zh": "代价：你的健康 —— Ryan 觉得自己还年轻，犹豫片刻后按下了【确认】。",
        "motion": "zoom_in_center",
        "vfx": "red_pulse_crt",
        "sfx": "heartbeat_confirm",
        "pad_sec": 1.0,
    },
    {
        "id": "08_scene2_success",
        "scene": "SCENE 2 — THE PRICE OF SUCCESS",
        "image": "04_scene2_corporate_success.jpg",
        "voice": VOICE_RYAN,
        "rate": "+2%",
        "pitch": "+0Hz",
        "text": "Your opportunity has arrived. Soon, Ryan lands major contracts, wins recognition, and his career takes off.",
        "sub_en": "\"YOUR OPPORTUNITY HAS ARRIVED.\" Soon, Ryan signs major contracts and rises fast.",
        "sub_zh": "“你的机会到了。” 不久后，Ryan 事业突飞猛进，不断签下重要合同。",
        "motion": "pan_right_to_left",
        "vfx": "warm_dust",
        "sfx": "success_chord",
        "pad_sec": 0.8,
    },
    {
        "id": "09_scene2_vertigo",
        "scene": "SCENE 2 — FAILING HEALTH",
        "image": "05_scene2_vertigo_washroom.jpg",
        "voice": VOICE_MUM,
        "rate": "-8%",
        "pitch": "-4Hz",
        "text": "Ryan ah, earning money is important, but your body must be taken care of too.",
        "sub_en": "As his health quietly deteriorates, Mum reminds him: \"Money is important, but take care of your body.\"",
        "sub_zh": "与此同时，他的身体越来越差，常感头晕疲惫。妈妈总叮嘱：“赚钱重要，身体也要顾好。”",
        "motion": "vertigo_shake",
        "vfx": "vertigo_wave",
        "sfx": "tinnitus_vertigo",
        "pad_sec": 0.5,
    },
    {
        "id": "10_scene2_ignore",
        "scene": "SCENE 2 — BRUSHING IT OFF",
        "image": "05_scene2_vertigo_washroom.jpg",
        "voice": VOICE_RYAN,
        "rate": "-4%",
        "pitch": "-2Hz",
        "text": "I know lah, Ma. I'm just a little tired from work.",
        "sub_en": "RYAN: \"I know lah, Ma. Just a bit tired from work.\"",
        "sub_zh": "Ryan：“知道啦，妈，只是工作太累而已。” 他依然把所有精力投入事业。",
        "motion": "zoom_in_slow",
        "vfx": "vertigo_wave",
        "sfx": "tinnitus_vertigo",
        "pad_sec": 0.8,
    },
    {
        "id": "11_scene3_hospital",
        "scene": "SCENE 3 — THE SUDDEN CRISIS",
        "image": "06_scene3_hospital_crisis.jpg",
        "voice": VOICE_RYAN,
        "rate": "-4%",
        "pitch": "-3Hz",
        "text": "Right in the middle of celebrating a major breakthrough, an urgent call comes from the hospital. His mother has collapsed and needs immediate treatment.",
        "sub_en": "At the height of his celebration, the hospital calls: Mum is admitted and needs urgent surgery.",
        "sub_zh": "就在庆祝重大成功时，医院打来电话：妈妈突发疾病住院，急需进一步治疗。",
        "motion": "zoom_in_center",
        "vfx": "hospital_cold",
        "sfx": "hospital_beep",
        "pad_sec": 0.6,
    },
    {
        "id": "12_scene3_bill",
        "scene": "SCENE 3 — UNPREPARED FOR THE COST",
        "image": "06_scene3_hospital_crisis.jpg",
        "voice": VOICE_RYAN,
        "rate": "-6%",
        "pitch": "-4Hz",
        "text": "Looking at the thirty-eight thousand Ringgit medical deposit, Ryan realizes for the first time: career success does not mean being financially prepared for a crisis.",
        "sub_en": "Deposit: RM 38,000. Ryan realizes career success doesn't equal financial preparedness.",
        "sub_zh": "看着高昂的医疗押金，Ryan 第一次意识到：事业成功，并不代表已经做好财务准备。",
        "motion": "zoom_out_slow",
        "vfx": "hospital_cold",
        "sfx": "hospital_beep",
        "pad_sec": 0.9,
    },
    {
        "id": "13_scene4_return",
        "scene": "SCENE 4 — THE SECOND TRADE",
        "image": "07a_machine_error_closeup.jpg",
        "voice": VOICE_MACHINE,
        "rate": "-10%",
        "pitch": "-8Hz",
        "text": "Desperate for funds, Ryan runs back to the machine. Selection: Additional Funds. Price: All of your remaining health.",
        "sub_en": "Desperate, Ryan returns to the machine. The screen warns: \"PRICE: YOUR REMAINING HEALTH.\"",
        "sub_zh": "为了筹集医药费，Ryan 再次跑回贩卖机前。屏幕却显示：“代价：你剩余的健康。”",
        "motion": "zoom_in_center",
        "vfx": "red_pulse_crt",
        "sfx": "heartbeat_confirm",
        "pad_sec": 0.7,
    },
    {
        "id": "14_scene4_cancel",
        "scene": "SCENE 4 — REFUSING TO SACRIFICE LIFE",
        "image": "07_scene4_slam_cancel.jpg",
        "voice": VOICE_RYAN,
        "rate": "-3%",
        "pitch": "-2Hz",
        "text": "As his trembling hand reaches for Confirm, he hears his mother's voice: Don't just chase money, take care of your body. Tears falling, Ryan slams Cancel.",
        "sub_en": "Remembering Mum's words, Ryan stops—and slams [ CANCEL ].",
        "sub_zh": "伸手欲按确认的最后一刻，他想起妈妈的话，最终挣扎着按下了【取消】。",
        "motion": "zoom_out_slow",
        "vfx": "rain_neon",
        "sfx": "cancel_slam",
        "pad_sec": 1.0,
    },
    {
        "id": "15_scene5_ward",
        "scene": "SCENE 5 — TRUE PROTECTION",
        "image": "08_scene5_hospital_payoff.jpg",
        "voice": VOICE_NURSE,
        "rate": "+0%",
        "pitch": "+2Hz",
        "text": "Back at the hospital, his mother hands him the worn folder she kept for years. The nurse smiles: Mister Tan, the Guarantee Letter from your mother's medical policy has cleared the eligible hospital expenses.",
        "sub_en": "NURSE: \"Mr. Tan, your mum's medical policy Guarantee Letter cleared the eligible expenses.\"",
        "sub_zh": "妈妈拿出坚持维持多年的医疗保单。经核实，合资格的医疗费用获得了保障与理赔。",
        "motion": "pan_left_to_right",
        "vfx": "warm_dust",
        "sfx": "warm_piano",
        "pad_sec": 0.8,
    },
    {
        "id": "16_scene5_mum_words",
        "scene": "SCENE 5 — A MOTHER'S FORESIGHT",
        "image": "08_scene5_hospital_payoff.jpg",
        "voice": VOICE_MUM,
        "rate": "-10%",
        "pitch": "-4Hz",
        "text": "I also hoped we would never need to use it. But when we truly need it, at least we have a preparation.",
        "sub_en": "MUM: \"I hoped we'd never need it. But when we do, at least we are prepared.\"",
        "sub_zh": "妈妈：“我也希望永远用不到。不过真的需要的时候，至少我们还有一份准备。”",
        "motion": "zoom_in_center",
        "vfx": "warm_dust",
        "sfx": "warm_piano",
        "pad_sec": 1.2,
    },
    {
        "id": "17_scene6_morning",
        "scene": "SCENE 6 — CHERISHING WHAT MATTERS",
        "image": "09_scene6_morning_soup.jpg",
        "voice": VOICE_RYAN,
        "rate": "-6%",
        "pitch": "+0Hz",
        "text": "Insurance cannot promise we will never fall ill. But when unexpected risks arrive, it protects our family from paying the price alone.",
        "sub_en": "Insurance can't stop illness, but it keeps a family from bearing the financial burden alone.",
        "sub_zh": "保险不能保证人永远不生病，但当风险发生时，它能帮家庭减轻沉重的财务负担。",
        "motion": "pan_right_to_left",
        "vfx": "warm_dust",
        "sfx": "warm_piano",
        "pad_sec": 1.0,
    },
    {
        "id": "18_scene6_walkaway",
        "scene": "SCENE 6 — THE FINAL CHOICE",
        "image": "10_scene6_walk_away.jpg",
        "voice": VOICE_RYAN,
        "rate": "-8%",
        "pitch": "+0Hz",
        "text": "Passing the mysterious vending machine one last time, Ryan looks at Wealth, Health, and Time. Without pressing a single button, he smiles and walks away as the machine's lights fade out.",
        "sub_en": "Ryan smiles and walks past the machine without pressing a button. Its lights fade to black.",
        "sub_zh": "Ryan 再次经过贩卖机，这一次他没有按下任何按钮，只是微笑着转身离开，机器灯光渐渐熄灭。",
        "motion": "zoom_out_slow",
        "vfx": "rain_neon",
        "sfx": "warm_piano",
        "pad_sec": 1.2,
    },
    {
        "id": "19_end_credits",
        "scene": "FINALE — BE PREPARED",
        "image": "11_end_card.jpg",
        "voice": VOICE_MACHINE,
        "rate": "-12%",
        "pitch": "-4Hz",
        "text": "Not every price has to be paid alone. Life is unpredictable. Be prepared.",
        "sub_en": "\"NOT EVERY PRICE HAS TO BE PAID ALONE. — LIFE IS UNPREDICTABLE. BE PREPARED.\"",
        "sub_zh": "“并不是人生中的每一份代价，都需要独自承担。人生无法预测，但保障可以提前准备。”",
        "motion": "zoom_in_slow",
        "vfx": "warm_dust",
        "sfx": "warm_piano",
        "pad_sec": 2.2,
    },
]


async def generate_all_tts():
    for shot in SHOTS:
        mp3_path = os.path.join(AUDIO_DIR, f"{shot['id']}.mp3")
        wav_path = os.path.join(AUDIO_DIR, f"{shot['id']}_voice.wav")
        comm = edge_tts.Communicate(
            shot["text"],
            shot["voice"],
            rate=shot["rate"],
            pitch=shot["pitch"],
        )
        await comm.save(mp3_path)
        subprocess.run(
            [FFMPEG_EXE, "-y", "-i", mp3_path, "-ar", "44100", "-ac", "1", wav_path],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


def mix_audio(voice_wav, out_wav, sfx_type, pad_sec):
    with wave.open(voice_wav, "rb") as wf:
        sr = wf.getframerate()
        n = wf.getnframes()
        voice_samples = list(struct.unpack(f"<{n}h", wf.readframes(n)))

    pre = int(0.3 * sr)
    post = int(pad_sec * sr)
    total = pre + len(voice_samples) + post
    duration = total / sr

    random.seed(101)
    rain_state = 0.0
    mixed = []

    for i in range(total):
        t = i / sr
        v = voice_samples[i - pre] / 32768.0 if pre <= i < pre + len(voice_samples) else 0.0

        bg = 0.0
        if sfx_type == "rain_warm":
            rain_state = 0.92 * rain_state + 0.08 * random.uniform(-1, 1)
            bg = rain_state * 0.055 + 0.02 * math.sin(2 * math.pi * 196.0 * t) + 0.015 * math.sin(2 * math.pi * 246.94 * t)
        elif sfx_type == "crt_hum":
            bg = 0.04 * math.sin(2 * math.pi * 60 * t) + 0.025 * math.sin(2 * math.pi * 120 * t) + 0.02 * math.sin(2 * math.pi * 392 * t)
        elif sfx_type == "heartbeat_confirm":
            beat_phase = (t * 1.35) % 1.0
            hb = math.exp(-beat_phase * 11) * math.sin(2 * math.pi * 55 * t) * 0.20
            bg = hb + 0.03 * math.sin(2 * math.pi * 110 * t)
        elif sfx_type == "success_chord":
            bg = 0.03 * math.sin(2 * math.pi * 261.63 * t) + 0.025 * math.sin(2 * math.pi * 329.63 * t) + 0.025 * math.sin(2 * math.pi * 392.0 * t)
        elif sfx_type == "tinnitus_vertigo":
            bg = 0.038 * math.sin(2 * math.pi * 3150 * t) * (0.6 + 0.4 * math.sin(2 * math.pi * 1.1 * t)) + 0.045 * math.sin(2 * math.pi * 62 * t)
        elif sfx_type == "hospital_beep":
            beep = 0.065 * math.sin(2 * math.pi * 1046.5 * t) if (t % 1.1) < 0.12 else 0.0
            bg = beep + 0.03 * math.sin(2 * math.pi * 146.8 * t)
        elif sfx_type == "cancel_slam":
            rain_state = 0.90 * rain_state + 0.10 * random.uniform(-1, 1)
            slam = 0.25 * math.exp(-max(0, t - (duration - 1.2)) * 18) if t > (duration - 1.2) else 0.0
            bg = rain_state * 0.06 + slam + 0.025 * math.sin(2 * math.pi * 130.8 * t)
        elif sfx_type == "warm_piano":
            env = 0.75 + 0.25 * math.sin(2 * math.pi * 0.25 * t)
            bg = env * (
                0.038 * math.sin(2 * math.pi * 174.61 * t)
                + 0.032 * math.sin(2 * math.pi * 220.00 * t)
                + 0.030 * math.sin(2 * math.pi * 261.63 * t)
                + 0.025 * math.sin(2 * math.pi * 329.63 * t)
            )

        if t < 0.25:
            bg *= t / 0.25
        elif t > duration - 0.35:
            bg *= max(0.0, (duration - t) / 0.35)

        val = max(-0.98, min(0.98, v * 0.92 + bg))
        mixed.append(int(val * 32767))

    with wave.open(out_wav, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(struct.pack(f"<{len(mixed)}h", *mixed))

    return duration


def render_animated_segment(shot, idx, duration):
    """Render a 24fps animated MP4 segment with real camera movement (zoom/pan/shake), particle/CRT VFX, and subtitles."""
    fps = 24
    total_frames = max(12, int(duration * fps))
    src_path = os.path.join(KEYFRAMES_DIR, shot["image"])
    base_img = Image.open(src_path).convert("RGB").resize((2240, 1260), Image.Resampling.LANCZOS)

    font_tag = get_font(22, bold=True)
    font_en = get_font(28, bold=True)
    font_zh = get_font(27, bold=False)

    seg_mp4 = os.path.join(SEGMENTS_DIR, f"shot_{idx:02d}.mp4")
    audio_wav = os.path.join(AUDIO_DIR, f"{shot['id']}_mixed.wav")

    # Pipe raw RGB24 frames directly to FFmpeg for fast, high-quality 24fps encoding
    cmd = [
        FFMPEG_EXE,
        "-y",
        "-f",
        "rawvideo",
        "-vcodec",
        "rawvideo",
        "-s",
        "1920x1080",
        "-pix_fmt",
        "rgb24",
        "-r",
        str(fps),
        "-i",
        "-",
        "-i",
        audio_wav,
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "20",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-shortest",
        seg_mp4,
    ]

    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    random.seed(idx * 77)
    rain_drops = [(random.randint(0, 1920), random.randint(0, 1080), random.randint(18, 36)) for _ in range(95)]
    dust_motes = [(random.randint(0, 1920), random.randint(100, 880), random.randint(3, 7)) for _ in range(40)]

    for f in range(total_frames):
        p = f / max(1, total_frames - 1)  # 0.0 -> 1.0 progress
        t = f / fps

        # Camera movement math on the 2240x1260 canvas -> cropped to 1920x1080
        motion = shot["motion"]
        if motion == "zoom_in_center":
            crop_w = int(2240 - 300 * p)
            crop_h = int(1260 - 168 * p)
            x0 = (2240 - crop_w) // 2
            y0 = (1260 - crop_h) // 2
        elif motion == "zoom_in_slow":
            crop_w = int(2200 - 220 * p)
            crop_h = int(1237 - 123 * p)
            x0 = (2240 - crop_w) // 2
            y0 = (1260 - crop_h) // 2
        elif motion == "zoom_out_slow":
            crop_w = int(1940 + 260 * p)
            crop_h = int(1091 + 146 * p)
            x0 = (2240 - crop_w) // 2
            y0 = (1260 - crop_h) // 2
        elif motion == "pan_left_to_right":
            crop_w, crop_h = 1960, 1102
            x0 = int(20 + 240 * p)
            y0 = (1260 - crop_h) // 2
        elif motion == "pan_right_to_left":
            crop_w, crop_h = 1960, 1102
            x0 = int(260 - 240 * p)
            y0 = (1260 - crop_h) // 2
        elif motion == "vertigo_shake":
            crop_w = int(2060 - 100 * math.sin(2 * math.pi * 0.9 * t))
            crop_h = int(crop_w * 9 / 16)
            shake_x = int(18 * math.sin(2 * math.pi * 3.2 * t))
            shake_y = int(12 * math.cos(2 * math.pi * 2.7 * t))
            x0 = max(0, min(2240 - crop_w, (2240 - crop_w) // 2 + shake_x))
            y0 = max(0, min(1260 - crop_h, (1260 - crop_h) // 2 + shake_y))
        else:
            crop_w, crop_h = 1920, 1080
            x0, y0 = 160, 90

        frame = base_img.crop((x0, y0, x0 + crop_w, y0 + crop_h)).resize((1920, 1080), Image.Resampling.BILINEAR)
        draw = ImageDraw.Draw(frame, "RGBA")

        # Dynamic Visual Effects (VFX)
        vfx = shot["vfx"]
        if vfx in ("rain_neon", "warm_rain"):
            col = (180, 220, 255, 85) if vfx == "rain_neon" else (255, 230, 195, 60)
            for rx, ry, rlen in rain_drops:
                cur_y = (ry + int(f * 34)) % 920
                cur_x = (rx - int(f * 6)) % 1920
                draw.line([(cur_x, cur_y), (cur_x - 5, cur_y + rlen)], fill=col, width=2)
        elif vfx == "crt_scanlines":
            for sy in range(85, 900, 6):
                draw.line([(0, sy), (1920, sy)], fill=(0, 255, 200, 22), width=1)
            bar_y = int(85 + ((f * 18) % 815))
            draw.rectangle([(0, bar_y), (1920, bar_y + 18)], fill=(120, 255, 220, 25))
        elif vfx == "red_pulse_crt":
            pulse_alpha = int(35 + 30 * math.sin(2 * math.pi * 1.4 * t))
            draw.rectangle([(0, 82), (1920, 905)], fill=(220, 20, 30, pulse_alpha))
            for sy in range(85, 900, 6):
                draw.line([(0, sy), (1920, sy)], fill=(255, 50, 50, 24), width=1)
        elif vfx == "vertigo_wave":
            pulse = int(40 + 35 * abs(math.sin(2 * math.pi * 1.2 * t)))
            draw.rectangle([(0, 82), (1920, 905)], fill=(20, 50, 70, pulse))
        elif vfx == "warm_dust":
            for dx, dy, dr in dust_motes:
                cx = (dx + int(f * 1.8)) % 1920
                cy = dy + int(12 * math.sin(t + dx))
                draw.ellipse([(cx - dr, cy - dr), (cx + dr, cy + dr)], fill=(255, 230, 160, 75))
        elif vfx == "hospital_cold":
            pulse = int(20 + 20 * math.sin(2 * math.pi * 1.1 * t))
            draw.rectangle([(0, 82), (1920, 905)], fill=(200, 235, 255, pulse))

        # Top & Bottom Cinema Letterbox Bars
        draw.rectangle([(0, 0), (1920, 78)], fill=(6, 8, 12, 230))
        draw.rectangle([(0, 908), (1920, 1080)], fill=(6, 8, 12, 235))

        # Header & Dual Subtitles
        draw.text((44, 24), f"🎬  {shot['scene']}", fill=(255, 208, 115, 255), font=font_tag)
        draw.text((1390, 24), "THE LIFE VENDING MACHINE 《人生贩卖机》", fill=(175, 210, 235, 215), font=font_tag)

        bbox_en = draw.textbbox((0, 0), shot["sub_en"], font=font_en)
        w_en = bbox_en[2] - bbox_en[0]
        draw.text(((1920 - w_en) // 2, 934), shot["sub_en"], fill=(255, 255, 255, 255), font=font_en)

        bbox_zh = draw.textbbox((0, 0), shot["sub_zh"], font=font_zh)
        w_zh = bbox_zh[2] - bbox_zh[0]
        draw.text(((1920 - w_zh) // 2, 990), shot["sub_zh"], fill=(255, 215, 130, 255), font=font_zh)

        # Smooth fade-in and fade-out at shot boundaries
        fade_alpha = 0
        if t < 0.25:
            fade_alpha = int(255 * (1.0 - t / 0.25))
        elif t > duration - 0.25:
            fade_alpha = int(255 * (1.0 - max(0.0, (duration - t) / 0.25)))
        if fade_alpha > 0:
            draw.rectangle([(0, 0), (1920, 1080)], fill=(0, 0, 0, fade_alpha))

        proc.stdin.write(frame.tobytes())

    proc.stdin.close()
    proc.wait()
    return seg_mp4


def main():
    print("Step 1/4: Preparing 20 Multi-Angle Shot Keyframes & Inserts...")
    generate_special_keyframes()

    print("Step 2/4: Generating Southeast Asian English Voiceovers...")
    asyncio.run(generate_all_tts())

    print("Step 3/4: Rendering 20 Animated 24fps Film Shots (Camera Motion + VFX + Subtitles)...")
    seg_list = []
    total_dur = 0.0
    for idx, shot in enumerate(SHOTS, 1):
        v_wav = os.path.join(AUDIO_DIR, f"{shot['id']}_voice.wav")
        m_wav = os.path.join(AUDIO_DIR, f"{shot['id']}_mixed.wav")
        dur = mix_audio(v_wav, m_wav, shot["sfx"], shot["pad_sec"])
        total_dur += dur
        seg_mp4 = render_animated_segment(shot, idx, dur)
        seg_list.append(seg_mp4)
        print(f"   [Rendered] Shot {idx:02d}/20 ({dur:.1f}s | {shot['motion']} + {shot['vfx']}) -> {shot['id']}")

    print(f"Step 4/4: Assembling Final Motion Film ({total_dur:.1f}s total)...")
    concat_txt = os.path.join(SEGMENTS_DIR, "concat_film.txt")
    with open(concat_txt, "w", encoding="utf-8") as f:
        for s in seg_list:
            f.write(f"file '{s.replace(os.sep, '/')}'\n")

    subprocess.run(
        [FFMPEG_EXE, "-y", "-f", "concat", "-safe", "0", "-i", concat_txt, "-c", "copy", OUTPUT_MP4],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    shutil.copyfile(OUTPUT_MP4, ARTIFACT_MP4)
    print(f"SUCCESS! Full motion film saved to: {OUTPUT_MP4}")


if __name__ == "__main__":
    main()
