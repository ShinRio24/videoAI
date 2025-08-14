const { config, createAudioFromText } = require('tiktok-tts');
//https://github.com/VRCWizard/TTS-Voice-Wizard/wiki/TikTok-TTS
//https://api16-normal-useast5.us.tiktokv.com/media/api/text/speech/invoke
config('79ecb82e9416b5e1c28d23ebbe8adfd9', "https://api16-normal-useast5.us.tiktokv.com/media/api/text/speech/invoke");


const outputFileName = process.argv[2];  // Output file
const inpText = process.argv.slice(3).join(" ");  // Input text (from 3rd argument onward)


//speaker options
//https://github.com/oscie57/tiktok-voice/wiki/Voice-Codes
voiceOptions  = ["jp_001", //0
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
    "jp_female_yagishaki", //11
    "jp_female_sakura"
]
//0
usingVoice = 12

createAudioFromText(inpText, 
    outputFileName,
     voiceOptions[usingVoice]
    );
console.log(voiceOptions[usingVoice]);

console.log("typeof outputFileName:", typeof outputFileName);
