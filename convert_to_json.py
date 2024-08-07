import json

# Step 1: Load and Prepare the Dataset
data = [
    {
        "sentence": "Can you play the next song",
        "labels": [
            "O",
            "O",
            "COMMAND",
            "O",
            "O",
            "O"
        ]
    },
    {
        "sentence": "Please pause the music",
        "labels": [
            "O",
            "COMMAND",
            "O",
            "O"
        ]
    },
    {
        "sentence": "Skip to the next track",
        "labels": [
            "COMMAND",
            "O",
            "O",
            "O",
            "O"
        ]
    },
    {
        "sentence": "Unpause the song",
        "labels": [
            "COMMAND",
            "O",
            "O"
        ]
    },
    {
        "sentence": "Can you pause this",
        "labels": [
            "O",
            "O",
            "COMMAND",
            "O"
        ]
    },
    {
        "sentence": "Play that track",
        "labels": [
            "COMMAND",
            "O",
            "O"
        ]
    },
    {
        "sentence": "Skip this track",
        "labels": [
            "COMMAND",
            "O",
            "O"
        ]
    },
    {
        "sentence": "Pause the song please",
        "labels": [
            "COMMAND",
            "O",
            "O",
            "O"
        ]
    },
    {
        "sentence": "Play the next song",
        "labels": [
            "COMMAND",
            "O",
            "O",
            "O"
        ]
    },
    {
        "sentence": "Skip this song",
        "labels": [
            "COMMAND",
            "O",
            "O"
        ]
    },
    {
        "sentence": "Pause the track now",
        "labels": [
            "COMMAND",
            "O",
            "O",
            "O"
        ]
    },
    {
        "sentence": "Play the current song",
        "labels": [
            "COMMAND",
            "O",
            "O",
            "O"
        ]
    },
    {
        "sentence": "Pause music",
        "labels": [
            "COMMAND",
            "O"
        ]
    },
    {
        "sentence": "Play music",
        "labels": [
            "COMMAND",
            "O"
        ]
    },
    {
        "sentence": "Skip track",
        "labels": [
            "COMMAND",
            "O"
        ]
    },
    {
        "sentence": "Can you play a song",
        "labels": [
            "O",
            "O",
            "COMMAND",
            "O",
            "O"
        ]
    },
    {
        "sentence": "Pause this track",
        "labels": [
            "COMMAND",
            "O",
            "O"
        ]
    },
    {
        "sentence": "Skip the song",
        "labels": [
            "COMMAND",
            "O",
            "O"
        ]
    },
    {
        "sentence": "Play a track",
        "labels": [
            "COMMAND",
            "O",
            "O"
        ]
    },
    {
        "sentence": "Unpause this song",
        "labels": [
            "COMMAND",
            "O",
            "O"
        ]
    },
    {
        "sentence": "Pause it",
        "labels": [
            "COMMAND",
            "O"
        ]
    },
    {
        "sentence": "Play it",
        "labels": [
            "COMMAND",
            "O"
        ]
    },
    {
        "sentence": "Skip it",
        "labels": [
            "COMMAND",
            "O"
        ]
    },
    {
        "sentence": "Can you skip this",
        "labels": [
            "O",
            "O",
            "COMMAND",
            "O"
        ]
    },
    {
        "sentence": "Please play that",
        "labels": [
            "O",
            "COMMAND",
            "O"
        ]
    },
    {
        "sentence": "Pause the current track",
        "labels": [
            "COMMAND",
            "O",
            "O",
            "O"
        ]
    },
    {
        "sentence": "Skip to another song",
        "labels": [
            "COMMAND",
            "O",
            "O",
            "O"
        ]
    },
    {
        "sentence": "Play this music",
        "labels": [
            "COMMAND",
            "O",
            "O"
        ]
    },
    {
        "sentence": "Pause this music",
        "labels": [
            "COMMAND",
            "O",
            "O"
        ]
    },
    {
        "sentence": "Unpause the track",
        "labels": [
            "COMMAND",
            "O",
            "O"
        ]
    },
    {
        "sentence": "Play another song",
        "labels": [
            "COMMAND",
            "O",
            "O"
        ]
    },
    {
        "sentence": "Pause another track",
        "labels": [
            "COMMAND",
            "O",
            "O"
        ]
    },
    {
        "sentence": "Skip this music",
        "labels": [
            "COMMAND",
            "O",
            "O"
        ]
    },
    {
        "sentence": "Play a different track",
        "labels": [
            "COMMAND",
            "O",
            "O",
            "O"
        ]
    },
    {
        "sentence": "Pause a different song",
        "labels": [
            "COMMAND",
            "O",
            "O",
            "O"
        ]
    },
    {
        "sentence": "Skip to a different track",
        "labels": [
            "COMMAND",
            "O",
            "O",
            "O",
            "O"
        ]
    },
    {
        "sentence": "Can you play the next track",
        "labels": [
            "O",
            "O",
            "COMMAND",
            "O",
            "O",
            "O"
        ]
    },
    {
        "sentence": "Pause this current song",
        "labels": [
            "COMMAND",
            "O",
            "O",
            "O"
        ]
    },
    {
        "sentence": "Skip this current track",
        "labels": [
            "COMMAND",
            "O",
            "O",
            "O"
        ]
    },
    {
        "sentence": "Play the previous song",
        "labels": [
            "COMMAND",
            "O",
            "O",
            "O"
        ]
    },
    {
        "sentence": "Pause the previous track",
        "labels": [
            "COMMAND",
            "O",
            "O",
            "O"
        ]
    },
    {
        "sentence": "Skip the previous song",
        "labels": [
            "COMMAND",
            "O",
            "O",
            "O"
        ]
    },
    {
        "sentence": "Can you play another track",
        "labels": [
            "O",
            "O",
            "COMMAND",
            "O",
            "O",
            "O"
        ]
    },
    {
        "sentence": "Pause another song",
        "labels": [
            "COMMAND",
            "O",
            "O"
        ]
    },
    {
        "sentence": "Skip another track",
        "labels": [
            "COMMAND",
            "O",
            "O"
        ]
    },
    {
        "sentence": "Play the current track",
        "labels": [
            "COMMAND",
            "O",
            "O",
            "O"
        ]
    },
    {
        "sentence": "Unpause the current song",
        "labels": [
            "COMMAND",
            "O",
            "O",
            "O"
        ]
    },
    {
        "sentence": "Pause the music now",
        "labels": [
            "COMMAND",
            "O",
            "O",
            "O"
        ]
    },
    {
        "sentence": "Play the music now",
        "labels": [
            "COMMAND",
            "O",
            "O",
            "O"
        ]
    },
    {
        "sentence": "Skip the music now",
        "labels": [
            "COMMAND",
            "O",
            "O",
            "O"
        ]
    },
    {
        "sentence": "Can you unpause the song",
        "labels": [
            "O",
            "O",
            "COMMAND",
            "O",
            "O"
        ]
    },
    {
        "sentence": "Pause this song now",
        "labels": [
            "COMMAND",
            "O",
            "O",
            "O"
        ]
    },
    {
        "sentence": "Play this song now",
        "labels": [
            "COMMAND",
            "O",
            "O",
            "O"
        ]
    },
    {
        "sentence": "Skip this song now",
        "labels": [
            "COMMAND",
            "O",
            "O",
            "O"
        ]
    },
    {
        "sentence": "Pause a song",
        "labels": [
            "COMMAND",
            "O",
            "O"
        ]
    },
    {
        "sentence": "Play a song",
        "labels": [
            "COMMAND",
            "O",
            "O"
        ]
    },
    {
        "sentence": "Skip a song",
        "labels": [
            "COMMAND",
            "O",
            "O"
        ]
    }
]

with open('spotify_dataset.json', 'w') as f:
    json.dump(data, f, indent=4)