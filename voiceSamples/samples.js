const fs = require('fs');
const path = require('path');
const { config, createAudioFromText } = require('tiktok-tts');

// Set API key and endpoint
config('16c3c2cd18f938d65543d7ed764b4156', 'https://api16-normal-useast5.us.tiktokv.com/media/api/text/speech/invoke');

// Fixed input text
const inputText = "皆さん、こんにちは！「知の探求」へようこそ。このチャンネルでは、私たちの世界の見方、考え方。";

// Voice options
const voiceOptions = [
    "jp_001", //0
    "jp_003", //1
    "jp_005", //2
    "jp_006", //3
    "jp_male_osada", //4
    "jp_male_matsuo", //5
    "jp_female_machikoriiita", //6
    "jp_male_matsudake", //7
    "jp_male_shuichiro", //8
    "jp_female_rei", //9
    "jp_male_hikakin", //10
    "jp_female_yagishaki" //11
];

// Create "voices" folder if it doesn't exist
const voicesDir = path.join(__dirname, 'voices');
if (!fs.existsSync(voicesDir)) {
    fs.mkdirSync(voicesDir);
}

// Generate audio for each voice
(async () => {
    for (const voice of voiceOptions) {
        const outputFilePath = path.join(voicesDir, `${voice}.mp3`);
        try {
            await createAudioFromText(inputText, outputFilePath, voice);
            console.log(`Generated: ${outputFilePath}`);
        } catch (err) {
            console.error(`Failed for ${voice}:`, err.message);
        }
    }
})();
