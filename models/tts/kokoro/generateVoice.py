from kokoro import KPipeline
import soundfile as sf

pipeline = KPipeline(lang_code="a")

text = "Hi ! This is my first Kokoro TTS test."

generator = pipeline(text, voice="af_bella")

for i, (gs, ps, audio) in enumerate(generator):
    sf.write(f"output_{i}.wav", audio, 24000)

print("Done!")


"""Language code: 'a'

Female voices (af_*):

    af_heart: ❤️ Premium quality voice (Grade A)
    af_alloy: Clear and professional (Grade C)
    af_aoede: Smooth and melodic (Grade C+)
    af_bella: 🔥 Warm and friendly (Grade A-)
    af_jessica: Natural and engaging (Grade D)
    af_kore: Bright and energetic (Grade C+)
    af_nicole: 🎧 Professional and articulate (Grade B-)
    af_nova: Modern and dynamic (Grade C)
    af_river: Soft and flowing (Grade D)
    af_sarah: Casual and approachable (Grade C+)
    af_sky: Light and airy (Grade C-)

Male voices (am_*):

    am_adam: Strong and confident (Grade F+)
    am_echo: Resonant and clear (Grade D)
    am_eric: Professional and authoritative (Grade D)
    am_fenrir: Deep and powerful (Grade C+)
    am_liam: Friendly and conversational (Grade D)
    am_michael: Warm and trustworthy (Grade C+)
    am_onyx: Rich and sophisticated (Grade D)
    am_puck: Playful and energetic (Grade C+)
    am_santa: Holiday-themed voice (Grade D-)

🇬🇧 British English (8 voices)

Language code: 'b'

Female voices (bf_*):

    bf_alice: Refined and elegant (Grade D)
    bf_emma: Warm and professional (Grade B-)
    bf_isabella: Sophisticated and clear (Grade C)
    bf_lily: Sweet and gentle (Grade D)

Male voices (bm_*):

    bm_daniel: Polished and professional (Grade D)
    bm_fable: Storytelling and engaging (Grade C)
    bm_george: Classic British accent (Grade C)
    bm_lewis: Modern British accent (Grade D+)

🇯🇵 Japanese (5 voices)

Language code: 'j'

Female voices (jf_*):

    jf_alpha: Standard Japanese female (Grade C+)
    jf_gongitsune: Based on classic tale (Grade C)
    jf_nezumi: Mouse bride tale voice (Grade C-)
    jf_tebukuro: Glove story voice (Grade C)

Male voices (jm_*):

    jm_kumo: Spider thread tale voice (Grade C-)
"""