import unittest

import os

from main.transcript import split_line, Transcript


class TranscriptTest(unittest.TestCase):

    def test_split_line(self):
        tests = [
            {'text': '', 'speaker': None, 'spoken_parts': [], 'comment_parts': []},
            {'text': 'Bob: Hello!', 'speaker': 'Bob', 'spoken_parts': [' Hello!'], 'comment_parts': []},
            {'text': 'xxx:aaa[bbb]ccc[ddd]eee[fff]ggg',
             'speaker': 'xxx',
             'spoken_parts': ['aaa', 'ccc', 'eee', 'ggg'],
             'comment_parts': ['bbb', 'ddd', 'fff']},
            {'text': 'Bob:Hello![aaa]', 'speaker': 'Bob', 'spoken_parts': ['Hello!'], 'comment_parts': ['aaa']},
            {'text': 'xx:[aa]bb[cc]', 'speaker': 'xx', 'spoken_parts': ['bb'], 'comment_parts': ['aa', 'cc']},
            {'text': 'xx:aa[bb', 'speaker': 'xx', 'spoken_parts': ['aa'], 'comment_parts': ['bb']},
            {'text': 'xx:aa[bb][cc]dd', 'speaker': 'xx', 'spoken_parts': ['aa', 'dd'], 'comment_parts': ['bb', 'cc']},
        ]

        for test in tests:
            speaker, s, c = split_line(test['text'])
            self.assertEqual(speaker, test['speaker'])
            self.assertEqual(s, test['spoken_parts'])
            self.assertEqual(c, test['comment_parts'])

    def test_transcript(self):
        this_dir = os.path.dirname(os.path.abspath(__file__))
        transcript_file = os.path.join(this_dir, 'resources', 'short_transcript.html')

        with open(transcript_file) as f:
            transcript = Transcript(1, 4, f.read())

        for l in transcript.lines:
            print(l)

        self.assertEqual(len(transcript.lines), 5)


if __name__ == '__main__':
    unittest.main()
