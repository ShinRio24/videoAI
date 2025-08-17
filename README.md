## Additional Requirements
## What This Project Does

This project generates and posts a YouTube Shorts video (about one minute long, in Japanese) based on a topic you provide after the `main` command. It automates image selection, narration, video creation, and uploading.

## Features

- **Image grabbing**: Finds and selects the most relevant images for your topic.
- **Audio narration**: Generates Japanese audio narration for the video.
- **Video compiling**: Assembles images and narration into a short video (around one minute).
- **Auto uploading**: Automatically uploads the generated video to YouTube and other supported platforms.

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/videoAI.git
    cd videoAI
    ```
2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3. Add required secrets and configuration files as described below.

## Additional Requirements

- **YouTube API credentials**: Create a `secrets/youtube_api.json` file with your YouTube API keys.
- **OAuth tokens and client secrets**: If your workflow requires OAuth authentication (e.g., for YouTube or other platforms), add the relevant token and client secret files (such as `secrets/client_secret.json` or `secrets/oauth_token.json`) to the `secrets/` directory.
- **Platform-specific configs**: Add any necessary configuration files for other platforms you wish to auto-upload to.