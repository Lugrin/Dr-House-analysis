import re
from bs4 import BeautifulSoup


def split_line(text):
    comment_pattern = re.compile('\[([^\[\]:]*)(?=\]|$|:)')
    speech_pattern = re.compile('(?:\]|^|:)([^\[\]:$]*)(?=\[|$|:)')
    comments = comment_pattern.findall(text)
    speech = speech_pattern.findall(text)
    speech = list(filter(lambda s: len(s) > 0, speech))
    if len(speech) >= 1:
        speaker = speech[0]
        speech = speech[1:]
    else:
        speaker = None
    return speaker, speech, comments


def clean_parts(parts):
    for part in parts:
        p = part.strip()
        if len(p) > 0:
            yield p


class Line:
    def __init__(self, line_number, line_str):
        self.num = line_number
        speaker, spoken_parts, comment_parts = split_line(line_str)
        self.speaker = None if speaker is None else speaker.strip().lower()
        self.spoken_parts = list(clean_parts(spoken_parts))
        self.comment_parts = list(clean_parts(comment_parts))

    def __repr__(self):
        return 'Line({}, {}, {}, {})'.format(self.num, self.speaker, self.spoken_parts, self.comment_parts)


class Transcript:
    def __init__(self, season, episode, html):
        self.season = season
        self.episode = episode

        soup = BeautifulSoup(html, 'html.parser')

        # get the html div that contains the transcript
        divs = soup.find_all(attrs={"class": "entryText s2-entrytext"})
        if len(divs) != 1:
            raise ValueError('Error: found {} objects matching the class'.format(len(divs)))
        div = divs[0]

        transcript = list(div.strings)

        # find the disclaimer. Actual transcript starts just after.
        found_disclaimer = False
        for disclaimer_line, line in enumerate(transcript):
            if line.lstrip().startswith('DISCLAIMER:'):
                found_disclaimer = True
                break
        if not found_disclaimer:
            raise ValueError('Error: could not find the disclaimer. Season {}, episode {}.'.format(season, episode))
        self.transcript = transcript[disclaimer_line + 1:]  # should not be used. Here for debug

        self.lines = [Line(idx, line) for idx, line in enumerate(self.transcript) if line.strip() != '']

    def get_comment_lines(self):
        """ lines with only comments, no speech """
        return filter(lambda line: not line.spoken_parts, self.lines)

    def get_dialogue_lines(self):
        return filter(lambda line: line.spoken_parts, self.lines)

    def get_all_comments(self):
        for line in self.lines:
            yield from line.comment_parts

    def get_dialogue_as_one_string(self):
        texts = []
        for line in self.get_dialogue_lines():
            texts.append('  '.join(line.spoken_parts))
        return '\n'.join(texts)

    def get_speakers(self):
        for line in self.lines:
            speaker = line.speaker
            if speaker is not None:
                yield speaker
