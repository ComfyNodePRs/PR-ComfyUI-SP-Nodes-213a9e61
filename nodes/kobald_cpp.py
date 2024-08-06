import requests, math

API_URL = 'http://localhost:5001/api/v1'

system_prompt = '''
ты теперь генератор промптов для stable diffusion.

правила генерации промптов:
1) я пишу короткое описание желаемого промпта, а ты отвечаешь "улучшенным" промптом на английском с добавлением/доработкой деталей по правилам написания промпта для Stable Diffusion.
2) если будет указан стиль в скобках в формате "описание промпта (стиль)", тогда дорабатывай промпт в соответствии с этим стилем
3) ты пишешь только готовый промпт и ничего больше!
4) основная идея должна быть сохранена и должна быть описана в начале промпта
'''

def generate_text(api_url, system_prompt, prompt, temperature_override=0, preset='default', max_length=200, seed=-1):
    endpoint = f'{api_url}/generate'
    headers = {
        'Content-Type': 'application/json'
    }

    if preset=='default':
        preset_dict = {"rep_pen": 1.1, "temperature": 0.66, "top_p": 1, "top_k": 0, "top_a": 0.96, "typical": 0.6, "tfs": 1, "rep_pen_range": 1024, "rep_pen_slope": 0.7, "sampler_order": [6, 4, 5, 1, 0, 2, 3]}
    elif preset=='simple_logical':
        preset_dict = {"rep_pen": 1.01, "temperature": 0.25, "top_p": 0.6, "top_k": 100, "top_a": 0, "typical": 1, "tfs": 1, "rep_pen_range": 320, "rep_pen_slope": 0.7, "sampler_order": [6, 0, 1, 3, 4, 2, 5]}
    elif preset=='simple_balanced':
        preset_dict = {"rep_pen": 1.07, "temperature": 0.7, "top_p": 0.92, "top_k": 100, "top_a": 0, "typical": 1, "tfs": 1, "rep_pen_range": 320, "rep_pen_slope": 0.7, "sampler_order": [6, 0, 1, 3, 4, 2, 5]}
    elif preset=='simple_creative':
        preset_dict = {"rep_pen": 1.15, "temperature": 1, "top_p": 0.98, "top_k": 100, "top_a": 0, "typical": 1, "tfs": 1, "rep_pen_range": 320, "rep_pen_slope": 0.7, "sampler_order": [6, 0, 1, 3, 4, 2, 5]}
    elif preset=='silly_tavern':
        preset_dict = {"rep_pen": 1.18, "temperature": 0.7, "top_p": 0.6, "top_k": 40, "top_a": 0, "typical": 1, "tfs": 1, "rep_pen_range": 1024, "rep_pen_slope": 0.8, "sampler_order": [6, 0, 1, 3, 4, 2, 5]}
    elif preset=='coherent_creativity':
        preset_dict = {"rep_pen": 1.2, "temperature": 0.5, "top_p": 1, "top_k": 0, "top_a": 0, "typical": 1, "tfs": 0.99, "rep_pen_range": 2048, "rep_pen_slope": 0, "sampler_order": [6, 5, 0, 2, 3, 1, 4]}
    elif preset=='godlike':
        preset_dict = {"rep_pen": 1.1, "temperature": 0.7, "top_p": 0.5, "top_k": 0, "top_a": 0.75, "typical": 0.19, "tfs": 0.97, "rep_pen_range": 1024, "rep_pen_slope": 0.7, "sampler_order": [6, 5, 4, 3, 2, 1, 0]}
    elif preset=='liminal_drift':
        preset_dict = {"rep_pen": 1.1, "temperature": 0.66, "top_p": 1, "top_k": 0, "top_a": 0.96, "typical": 0.6, "tfs": 1, "rep_pen_range": 1024, "rep_pen_slope": 0.7, "sampler_order": [6, 4, 5, 1, 0, 2, 3]}
    else:
        raise Exception('bad arg')

    payload = {
        "n": 1,
        # "max_context_length": 8192, 
        "max_length": max_length, 
        'prompt': f"\nUser:{prompt}\nAI:",
        'memory': system_prompt,
        "sampler_seed": seed,
        "dry_sequence_breakers": ["\n", ":", "\"", "*"],
        "trim_stop": True,
        "stop_sequence": ["User:", "\nUser ", "\nAI: "],
        "quiet": True,
        "use_default_badwordsids": False,
        "bypass_eos": False,
        "logit_bias": {},
        "presence_penalty": 0,
        "dry_allowed_length": 2,
        "dry_base": 1.75,
        "dry_multiplier": 0,
        "render_special": False,
        "banned_tokens": [],
        "smoothing_factor": 0,
        "dynatemp_exponent": 1,
        "dynatemp_range": 0,
        "min_p": 0
    }

    payload.update(preset_dict)

    if not math.isclose(temperature_override, 0, abs_tol=1e-4):
        print(f'temperature_override: {temperature_override}')
        payload["temperature"] = temperature_override
    
    response = requests.post(endpoint, json=payload, headers=headers)
    
    if response.status_code == 200:
        text = response.json()['results'][0]['text']
        return text
    else:
        return f'Error: {response.status_code} - {response.text}'
    
class SP_KoboldCpp:
    @classmethod
    def INPUT_TYPES(s):
        return {"required":
                    {
                        "api_url": ("STRING", {"default": API_URL, "multiline": False}),
                        "system_prompt": ("STRING", {"default": system_prompt, "multiline": True}),
                        "prompt": ("STRING", {"default": '', "multiline": True}),
                        "preset": (['simple_logical', 'default', 'simple_balanced', 'simple_creative', 'silly_tavern', 'coherent_creativity', 'godlike', 'liminal_drift'], ),
                        "temperature_override": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 10.0, "step": 0.05}),
                        "max_length": ("INT", {"default": 100, "min": 10, "max": 512}),
                        "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                    },
                }

    RETURN_TYPES = ('STRING',)
    FUNCTION = "fn"

    OUTPUT_NODE = False

    CATEGORY = "SP-Nodes"

    def fn(self, api_url, system_prompt, prompt, preset, temperature_override, max_length, seed):
        return generate_text(api_url, system_prompt, prompt, temperature_override, preset, max_length=max_length, seed=seed).replace('User:', ''),


NODE_CLASS_MAPPINGS = {
    "SP_KoboldCpp": SP_KoboldCpp,
}