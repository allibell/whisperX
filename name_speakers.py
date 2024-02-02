import re
import spacy
import argparse

# Load the spacy model for named entity recognition
nlp = spacy.load("en_core_web_sm")

def replace_speaker_with_name(input_file_path, output_file_path):
    with open(input_file_path, 'r') as file:
        lines = file.readlines()

    speaker_names = {}
    prev_speaker_to_addressed_speaker = tuple()
    for i in range(len(lines)):
        line = lines[i]
        match = re.match(r'\[(SPEAKER_\d+)\]: (.*)', line)
        if match:
            speaker, text = match.groups()
            # print(f"Speaker: {speaker}, Text: {text}")
            # print(f"Speaker names: {speaker_names}")
            if speaker in speaker_names:
                continue
            # TODO: This is a hack to handle the case where the speaker is addressing someone else
            # If we saved a name that didn't belong to the previous speaker, give it to this speaker
            if len(prev_speaker_to_addressed_speaker) > 0 and speaker != prev_speaker_to_addressed_speaker[0]:
                speaker_names[speaker] = prev_speaker_to_addressed_speaker[1]
                prev_speaker_to_addressed_speaker = tuple()
            doc = nlp(text)
            names = [ent for ent in doc.ents if ent.label_ == 'PERSON']
            if names:
                # Check the grammatical role of the name in the sentence
                for name in names:
                    if name.root.dep_ in ['nsubj', 'nsubjpass']:
                        # If the name is the subject of the sentence, it's likely the speaker's name
                        speaker_names[speaker] = name.text
                        break
                    else:
                        prev_speaker_to_addressed_speaker = (speaker, name.text)

    with open(output_file_path, 'w') as file:
        for line in lines:
            for speaker, name in speaker_names.items():
                line = line.replace(speaker, name)
            file.write(line)


def main():
    parser = argparse.ArgumentParser(description="Determine speaker names given a subtitle file.")
    parser.add_argument("subtitles_file", help="Path to the subtitles file (.vtt)")
    parser.add_argument("--output_file", help="Path to the output subtitles file (.vtt), defaults to overwriting", default=None)

    args = parser.parse_args()
    if not args.output_file:
        args.output_file = args.subtitles_file
    replace_speaker_with_name(args.subtitles_file, args.output_file)

if __name__ == "__main__":
    main()
