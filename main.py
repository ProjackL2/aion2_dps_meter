import configparser
import os
from dps_meter import DPSMeter
from localize import lang

def config_startup(path):
    config = configparser.ConfigParser()
    try:
        with open(path, 'r', encoding='utf-8') as f:
            config.read_file(f)
    except UnicodeDecodeError as e:
        print(f"[Warning] UTF-8 decoding failed: {e}. Trying cp949 encoding.")
        with open(path, 'r', encoding='cp949') as f:
            config.read_file(f)
            
    firstrun = config.get('language', 'firstrun') == "1"
    if firstrun:
        print("Please select your AION2 client language from the following options:")
        print(", ".join(list(lang.keys())))
        selected_lang = input("Enter language code: ").strip()
        if selected_lang not in lang:
            print(f"[Warning] Language '{selected_lang}' not supported. Defaulting to English ('en').")
            selected_lang = 'en'
        config.set('language', 'lang', selected_lang)
        config.set('language', 'firstrun', "0")
        with open(path, 'w', encoding='utf-8') as f:
            config.write(f)
    return config

def main():
    ini_path = os.path.join(os.getcwd(),'config.ini')
    config = config_startup(ini_path)
    dps_meter = DPSMeter(config)
    dps_meter.run()


if __name__ == '__main__':
    main()