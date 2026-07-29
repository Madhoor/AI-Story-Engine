ahgg


1 python pakage for ollama or rest api  
rest api as we can change the llm latter 

so python -> API -> ollama -> story     MCP latter ? :)
for MCP integration all the llm outpts to be JSON 


changed the word limit from 220 - 260  {given by gpt by estimating the length of voice over ~60 secs }
it felt short to tell the complete story so new limit is 300 - 360 


instead of the rewrite method 
we are doing the ranking method 
as the rewrite did not neccesaryliy make the story better even with more context 


ok it does not ask which to save froom between stories wioth the same score and i dont think thats bad or good but smth we can improve on latter by checking what the critic says 
eg.if score > best_score:
    best_story = story

elif score == best_score:
    # compare originality
    # compare hook
    # compare confidence

currently the stories do kinda feel like the coreect type but maybe having larger words limit maybe a bit of a hinderance as 
the reader/viewer mayb scroll before it makes sense for them 





working on kokoro 





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

