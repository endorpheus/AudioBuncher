# tag_definitions.py
from mutagen.id3 import (ID3, TIT2, TPE1, TALB, TDRC, TRCK, APIC, 
                        TCON, COMM, TCOM, TPE2, TPUB, TBPM, TKEY)

class TagDefinitions:
    TAG_FRAMES = {
        'Title': ('TIT2', TIT2),
        'Artist': ('TPE1', TPE1),
        'Album': ('TALB', TALB),
        'Year': ('TDRC', TDRC),
        'Track': ('TRCK', TRCK),
        'Genre': ('TCON', TCON),
        'Comment': ('COMM', COMM),
        'Composer': ('TCOM', TCOM),
        'Album Artist': ('TPE2', TPE2),
        'Publisher': ('TPUB', TPUB),
        'BPM': ('TBPM', TBPM),
        'Key': ('TKEY', TKEY)
    }

    # Tags that need special handling
    SPECIAL_TAGS = ['Album Art', 'Comment']

    @staticmethod
    def create_tag(tag_name, value):
        """Create a tag with the given value"""
        if tag_name not in TagDefinitions.TAG_FRAMES:
            return None
            
        frame_id, frame_class = TagDefinitions.TAG_FRAMES[tag_name]
        
        if frame_id == 'COMM':
            return frame_class(encoding=3, lang='eng', desc='', text=value)
        else:
            return frame_class(text=value)

    @staticmethod
    def get_tag_value(tags, tag_name):
        """Extract tag value in a standardized way"""
        if tag_name not in TagDefinitions.TAG_FRAMES:
            return ""
            
        frame_id = TagDefinitions.TAG_FRAMES[tag_name][0]
        
        if frame_id == 'COMM':
            # Get first comment frame
            for frame in tags.getall('COMM'):
                return str(frame)
        else:
            return str(tags.get(frame_id, ""))

    @staticmethod
    def get_display_name(tag_name):
        """Get user-friendly display name for a tag"""
        return tag_name.replace('_', ' ').title()
