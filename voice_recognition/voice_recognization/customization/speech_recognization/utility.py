import frappe
import re
from fuzzywuzzy import process
from gtts import gTTS
import pygame
import random

@frappe.whitelist()
def identify_voice(speech_text, url):
    response = random.choice(['got it', 'ok', 'sure'])
    speak_text(response, 'en')
    
    get_url_original = url.split('/')[4]
    get_doctype = frappe.db.get_list('DocType', {}, pluck='name')
    if contains_create_new_keyword(speech_text):
        get_url = find_best_match(get_url_original, get_doctype)
        return 'create new', get_url
    elif check_doctype_keyword(speech_text):
        word = check_specific_doctype(speech_text, get_doctype)
        if word:
            formatted_response = word[0].replace(" ", "-")
            return '/app/' + formatted_response
        else:
            speak_text('doctype not found. Pronounce Correctly', 'en')
            return None
        
    elif check_entry_keyword(speech_text):
        index = get_url_original.find('?')
        if index != -1:
            get_url_original = get_url_original[:index]
        get_url = find_best_match(get_url_original, get_doctype)
        if get_url:
            title_field = get_title_field(get_url)
            if not title_field:
                title_field = 'name'
            get_title_list = frappe.db.get_list(get_url, {}, pluck= title_field)
        else:
            return None
        word = check_specific_doctype(speech_text, get_title_list)
        if word:
            get_name = frappe.db.get_value(get_url, {title_field:word[0]}, 'name')
            formatted_response = get_name
            return '/app/' + get_url_original + '/' + formatted_response
        else:
            speak_text('Entry not found. Pronounce Correctly', 'en')
            return None
    
    elif check_change_keyword(speech_text):
        get_url_original = find_best_match(get_url_original, get_doctype)
        doctype_meta = frappe.get_meta(get_url_original)
        fieldname, value = parse_speech_text(speech_text)
        if fieldname and value:
            check_fieldname = [field.fieldname for field in doctype_meta.fields if field.label and fieldname == field.label.lower()]
            link_field = [ ' '.join(word.capitalize() for word in value.split()) for field in doctype_meta.fields if field.fieldtype == 'Select' and field.label and fieldname == field.label.lower()]
            if check_fieldname:
                return check_fieldname[0], value if not link_field else link_field
            else:
                return None, None
        else:
            speak_text('Field not found. Pronounce Correctly', 'en')
            return None, None
    elif contains_save_keyword(speech_text):
        return 'save'
    else:
        pass

def parse_speech_text(speech_text):
    match = re.search(r"change ([\w\s]+) value to ([\w\s]+)", speech_text.lower())
    if match:
        fieldname = match.group(1).strip()
        new_value = match.group(2).strip()        
        return fieldname, new_value
    return None, None

def check_specific_doctype(text, doctype_list):
    pattern = r'\b(?:' + '|'.join(re.escape(word.lower()) for word in doctype_list) + r')\b'
    
    matches = re.findall(pattern, text.lower())

    return matches

def check_entry_keyword(text):
    keywords = ["entry"]

    pattern = r'\b(?:' + '|'.join(re.escape(keyword) for keyword in keywords) + r')\b'

    matches = re.findall(pattern, text, re.IGNORECASE)
    if matches:
        return True
    else:
        return False
    
def find_best_match(input_string, doctype_list):
    normalized_input = input_string.lower().replace("-", " ")
    
    normalized_doctypes = [doctype.lower() for doctype in doctype_list]
    
    best_match = process.extractOne(normalized_input, normalized_doctypes)
    
    if best_match:
        matched_doctype = doctype_list[normalized_doctypes.index(best_match[0])]
        return matched_doctype
    return None

def get_title_field(doctype):
    doctype_meta = frappe.get_meta(doctype)
    return doctype_meta.title_field

def check_change_keyword(text):
    keywords = ["change"]

    pattern = r'\b(?:' + '|'.join(re.escape(keyword) for keyword in keywords) + r')\b'

    matches = re.findall(pattern, text, re.IGNORECASE)
    if matches:
        return True
    else:
        return False

def contains_save_keyword(text):
    return re.search(r'\bsave\b', text, re.IGNORECASE) is not None

def contains_create_new_keyword(text):
    return re.search(r'\bcreate new\b', text, re.IGNORECASE) is not None

def speak_text(text, sound):
    tts = gTTS(text,lang=sound)
    tts.save("output.mp3")
    play_audio("output.mp3")

def play_audio(file_path):
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    
    # Event loop to check if the audio has finished playing
    clock = pygame.time.Clock()
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        clock.tick(5) 

def contains_child_keyword(text):
    return re.search(r'\bchild\b', text, re.IGNORECASE) is not None

def check_childtable(speech_text):
    match = re.search(r"new ([\w\s]+) child table", speech_text.lower())
    if match:
        table_name = match.group(1).strip()
        return table_name
    return None

def check_doctype_keyword(text):
    pattern = r'\b(d(?:o|0)(?:c|g)?(?:\s*type|t(?:y)?pe)?)\b'
    pattern = re.sub(pattern, 'doctype', text.lower())
    
    if re.search(pattern, text, re.IGNORECASE):
        return True
    else:
        return False
