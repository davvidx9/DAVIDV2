fx_version 'cerulean'
game 'gta5'

author 'Pulse Scripts'
description 'Loading Screen V2'
version '1.0.0'

lua54 'yes'

loadscreen 'web/index.html'

shared_script 'config.lua'
server_script 'server.lua'
client_script 'client.lua'

files {
    'web/index.html',
    'web/style.css',
    'web/script.js',
    'web/config.js',
    'web/assets/avatars/*.jfif',
    'web/assets/logo.png',
    'web/assets/background.mp4',
    'web/assets/music/*.mp3',
    'web/assets/music/*.png',
}

loadscreen_manual_shutdown 'yes'

loadscreen_cursor 'yes'

escrow_ignore {
    'web/*',
    'client.lua',
    'config.lua',
    --'server.lua'
}


dependency '/assetpacks'