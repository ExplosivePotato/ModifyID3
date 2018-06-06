import re
import sys
import os.path
from mutagen import easyid3, id3, File
import argparse

TAG_VALUES = ['album', 'artist', 'title', 'tracknumber']
FILE_NAME_REGEX = re.compile('(?P<artist>[^-]+)-(?P<title>.*).mp3')

def get_tag(args):
    abs_path = os.path.abspath(args.path)
    try:
        id3_tag = easyid3.EasyID3(abs_path)
    except id3.ID3NoHeaderError:
        id3_tag = File(abs_path, easy=True)
        id3_tag.add_tags()
        id3_tag.save()

    return id3_tag

def get_artist_and_title(args):
    abs_path = os.path.abspath(args.path)
    file_name = os.path.basename(abs_path)

    d = {}
    re_result = FILE_NAME_REGEX.match(file_name)
    if re_result:
        d = re_result.groupdict()
    else:
        return

    if not args.artist:
        args.artist = d['artist'].strip()
    if not args.title:
        args.title = d['title'].strip()


def combin_tag_to_args(args, tag):
    for value in TAG_VALUES:
        if not args.__dict__[value] and value in tag:
            args.__dict__[value] = tag[value][0]


def get_value_from_user(args, value_name):
    print '\n'
    if value_name in args.__dict__ and args.__dict__[value_name]:
        print '{name} - {value}'.format(name=value_name.upper(), value=args.__dict__[value_name])
        user_choise = raw_input('Change it? y/[n]:')
        if user_choise != 'y':
            return
    user_choise = raw_input('Please enter value for {name}: '.format(name=value_name))
    args.__dict__[value_name] = user_choise


def get_args_in_interactive_mode(args):
    for value in TAG_VALUES:
        get_value_from_user(args, value)


def save_args_to_tag(args, tag):
    for value in TAG_VALUES:
        tag[value] = args.__dict__[value]


def main(args):
    id3_tag = get_tag(args)
    get_artist_and_title(args)
    combin_tag_to_args(args, id3_tag)
    
    if args.interactive:
        get_args_in_interactive_mode(args)

    id3_tag.delete()
    save_args_to_tag(args, id3_tag)
    id3_tag.save()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.description = "Edits the id3 header of an mp3 file,\nIf the file's name matches the format '{{artist}} - {{title}}' the details will be taken from the name"
    parser.formatter_class = argparse.RawTextHelpFormatter
    parser.add_argument("-p", '--path', help="The path of the file, can be ethier relative or absolute", action='store', dest='path', required=True)
    parser.add_argument("-i", "--interactive", help="Whether to use the interactive mode", action='store_true')
    parser.add_argument("--title", help="The title of the song", action='store', dest='title', default='')
    parser.add_argument("--album", help="The song's album", action='store', dest='album', default='')
    parser.add_argument("--artist", help="The song's artist", action='store', dest='artist', default='')
    parser.add_argument("--tracknumber", help="The song's tracknumber", action='store', dest='tracknumber', default='')
    args = parser.parse_args()
    sys.exit(main(args))