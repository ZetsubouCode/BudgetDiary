from textblob import TextBlob
import emoji

class TextHandler:
    def get_emoji(emoji_name: str):
        try:
            if emoji_name:
                emoji_name = emoji_name.replace(":", "")
                emoji_name = f":{emoji_name}:"
                emoji_symbol = emoji.emojize(emoji_name, language="alias")

                # Check if the emoji contains only ASCII characters (not a real emoji)
                if emoji_symbol.encode("unicode_escape") == emoji_name.encode("unicode_escape"):
                    emoji_symbol = ""  # Set to empty string if no valid emoji found

            print(f"Emoji: {emoji_symbol}, Unicode: {emoji_symbol.encode('unicode_escape')}")
            return emoji_symbol
        except Exception as e:
            print(e)
            return None

    def get_emoji_decode(emoji_data):
        if isinstance(emoji_data, str):
            try:
                # Decode Unicode escape sequence into actual emoji
                emoji = emoji_data.encode().decode('unicode_escape')
            except Exception as e:
                print(f"Error decoding emoji: {e}")
                emoji = None
        else:
            emoji = None
        
        return emoji

    def convert_unicode_to_emoji(emoji_unicode: str) -> str:
        try:
            data = emoji_unicode.encode('utf-16', 'surrogatepass').decode('utf-16')
            print(data)
            if data == "":
                return None
            
            return data
        except UnicodeDecodeError:
            return emoji_unicode 
        
    def translate(text:str, to:str="en",from_lang:str="any") ->str:
        raw_text = TextBlob(text) 
        translated = raw_text.translate(from_lang=from_lang,to=to)
        return translated