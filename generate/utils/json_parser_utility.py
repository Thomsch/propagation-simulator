# -*- coding: utf8 -*-
import re
import json

TAB = "    "
NEXT_LINE = '\n' + TAB

class json_parser_utility(object):
    """ Source: http://www.lifl.fr/~riquetd/parse-a-json-file-with-comments.html
    Permet d'identifier tous les commentaires d'un fichier JSON
    """
    no_comment_regex = re.compile(
        '(^)?[^\S\n]*/(?:\*(.*?)\*/[^\S\n]*|/[^\n]*)($)?',
        re.DOTALL | re.MULTILINE
    )

    def __init__(self, filename):
        self.current_content = {}
        self.next_content = ""
        self.filename = filename
        self.json_content = ""
        #
        # Traitement du fichier, création si il n'existe pas
        #
        try:
            with open(filename, 'r') as file_handler:
                self.current_content = self._decode_json(file_handler)
        except IOError:
            pass

    def _decode_json(self, file_handler):
        """ Ignore les commentaires du fichiers et le parse le json
        en dictionnaire."""
        # Enlever les commentaires du json
        json_content = self.json_content = ''.join(file_handler.readlines())
        match = self.no_comment_regex.search(json_content)
        while match:
            # suppression ligne par ligne
            json_content = json_content[:match.start()] + json_content[match.end():]
            match = self.no_comment_regex.search(json_content)
        return json.loads(json_content)

    def add_action_from_template(self, action_name, template):
        self.next_content = template

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        """ Ecrit les nouvelles actions dans le fichier, après la dernière accolade """
        try:
            if len(self.next_content) == 0:
                return

            close_tag = self.json_content.rfind('}')
            separator = ", " if len(self.current_content) > 0 else ""
            new_content = self.json_content[:close_tag].strip() + \
                          separator + NEXT_LINE + \
                          self.next_content + "\n}"

            with open(self.filename, 'w') as file_handler:
                file_handler.write(new_content)
        except IOError:
            pass
