/**
 * ============================================================
 *  Loading Screen — Configuration
 *  Edit everything here. No changes needed in other files.
 * ============================================================
 */

const CONFIG = {

  /* ----------------------------------------------------------
   *  SERVER IDENTITY
   * ---------------------------------------------------------- */
  server: {
    name:     'Pulse ROLEPLAY',
    tagline:  'Where Stories Come Alive',
    subtitle: 'Premium Serious Roleplay Experience',
    logo:     'assets/logo.png',      // Set to '' to hide
  },

  /* ----------------------------------------------------------
   *  BACKGROUND VIDEO
   * ---------------------------------------------------------- */
  background: {
    video:          'assets/background.mp4',   // MP4 or WebM path
    fallbackColor:  '#080c14',                 // Shown if video fails
    overlayOpacity: 0.68,                      // 0 = transparent, 1 = black
  },

  /* ----------------------------------------------------------
   *  THEME COLORS
   *  All UI elements derive from these values automatically.
   * ---------------------------------------------------------- */
  theme: {
    primary:        '#c8a96e',          // Gold accent — buttons, bar, glows
    accent:         '#e8c87a',          // Lighter gold — gradients, highlights
    background:     '#080c14',          // Deep dark fallback
    textHighlight:  '#c8a96e',          // Inline highlighted text color
    overlayTint:    'rgba(5,8,18,0.55)',// Extra darkening gradient layer
  },

  /* ----------------------------------------------------------
   *  MUSIC PLAYER
   * ---------------------------------------------------------- */
  music: {
    autoplay:      true,
    defaultVolume: 0.25,         // 0.0 – 1.0
    playlist: [
      {
        title:     'Fearless Funk',
        artist:    'DR MØB, Chris Linton',
        src:       'assets/music/music1.mp3',
        thumbnail: 'assets/music/music1.png',            // Optional cover image path
      },
      {
        title:     'Vandali',
        artist:    'Aditya Sharma',
        src:       'assets/music/music2.mp3',
        thumbnail: 'assets/music/music2.png',
      },
    ],
  },

  /* ----------------------------------------------------------
   *  STAFF PANEL
   * ---------------------------------------------------------- */
  staff: {
    enabled: true,
    title:   'SERVER TEAM',
    members: [
      { name: 'CommanderX',   role: 'Server Owner',       avatar: 'assets/avatars/avatar1.jfif'  },
      { name: 'NightWatch',   role: 'Head Administrator', avatar: 'assets/avatars/avatar2.jfif'  },
      { name: 'SilentByte',   role: 'Lead Developer',     avatar: 'assets/avatars/avatar3.jfif'    },
      { name: 'Aurora',       role: 'Community Manager',  avatar: 'assets/avatars/avatar4.jfif'     },
    ],
  },

  /* ----------------------------------------------------------
   *  SOCIAL LINKS
   *  platform: 'discord' | 'youtube' | 'instagram' | 'twitter'
   * ---------------------------------------------------------- */
  social: {
    links: [
      { platform: 'discord',   label: 'Discord',   url: 'https://discord.gg/c6gXmtEf3H'         },
      { platform: 'youtube',   label: 'YouTube',   url: 'https://www.youtube.com/@pulsescripts'       },
      { platform: 'instagram', label: 'Instagram', url: 'https://www.instagram.com/pulsescripts'      },
      { platform: 'twitter',   label: 'X / Twitter', url: 'https://x.com/PulseScripts'           },
    ],
  },

  /* ----------------------------------------------------------
   *  LOADING BAR
   * ---------------------------------------------------------- */
  loading: {
    text:         'Establishing connection…',
    completeText: 'Welcome to Pulse Roleplay',
    showPercent:  true,
  },

  /* ----------------------------------------------------------
   *  SECTION TOGGLES
   *  Set false to completely hide a section.
   * ---------------------------------------------------------- */
  sections: {
    showLogo:     true,
    showStaff:    true,
    showMusic:    true,
    showSocial:   true,
    showControls: true,   // Set false to hide the Show Controls button entirely
  },

  /* ----------------------------------------------------------
   *  SERVER KEYBINDS
   *  Displayed in the controls panel when the player clicks
   *  "Show Controls". Add, remove, or reorder freely.
   * ---------------------------------------------------------- */
  controls: [
    { key: 'F2',  label: 'Inventory'   },
    { key: 'M',   label: 'Phone'       },
    { key: '~',   label: 'Hands Up'    },
    { key: 'F3',  label: 'Emote Menu'  },
    { key: 'F8',  label: 'Scoreboard'  },
    { key: 'R',   label: 'Reload'      },
    { key: 'G',   label: 'Trunk'       },
  ],

};
