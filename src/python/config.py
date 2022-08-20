# Cog Configuration
cogs = ["cog_manager", "moderation", "applications", "welcomes", "coins", "badges", "guild", "logs", "miscellaneous"]
formal_cogs = {"cog_manager": "Cog Manager", "moderation": "Moderation", "applications": "Applications", "welcomes": "Welcomes", "coins": "Coins", "badges": "Badges", "guild": "Guild", "logs": "Logs", "miscellaneous": "Miscellaneous"}  # How the cogs will appear when listed
cog_aliases = {"cog_manager": ["CogManager", "Cog Manager"], "moderation": ["punish"], "applications": [], "welcomes": [], "coins": ["points", "xp"], "badges": [], "guild": [], "logs": [], "miscellaneous": ["misc"]}
constant_cogs = ["cog_manager"]  # Impossible to disable

help_categories = ["cog_manager", "moderation", "applications", "welcomes", "coins", "badges", "miscellaneous"]
formal_help_categories = {"cog_manager": "Cog Manager", "moderation": "Moderation", "applications": "Applications", "welcomes": "Welcomes", "coins": "Coins", "badges": "Badges", "guild": "Guild", "miscellaneous": "Miscellaneous"}

# ID Configuration
category_ids = {
    "bots": 809161725538467870,
    "ingame": 923658068917649478
}

channel_ids = {
    "welcomes": 736217931423285268,
    "apply": 994681865204158534,
    "applications": 738402536909701161,
    "staff_announcements": 707609210665566299,
    "moderation_logs": 808827126517858325,
    "message_logs": 808832171133370459,
    "application_logs": 957436399546695711,
    "miscellaneous_logs": 743952311168008312,
    "join_leave_logs": 808826688212303872,
    "voice_logs": 809566972140322816,
    "transaction_logs": 1000661999597916190
}

message_ids = {
    "apply": 995352030732374197
}

role_ids = {
    "muted": 714919830272081941,
    "member": 707624818090049627,
    "waiting": 707645200540893284,
    "guild": 707620276178780311,
    "inactive": 1000705935133638697,
    "booster": 628595835298381834,
    "booster_colors": [854748729064292413, 718861417947725846, 815409129924722698, 718861575473201182, 718861722416316450, 718861642372481055, 718861510801358858],
    "staff": 722936225409007646,
    "override": 707600610945663016
}

emoji_ids = {
    "yes": 790681118562451547,
    "no": 790681118390222890,
    "out": 833489666585919488,
    "hypixel": 829068788053573672,
    "coin": 810360620927025154,
    "rank": 802731703273521152
}

badge_ids = {
    "event_3": 930628019964510319, "event_2": 930628019989643294, "event_1": 930628019905777684,
    "messages_3": 930628159035047947, "messages_2": 930628019863818251, "messages_1": 930628121714126899,
    "chatgames_3": 930628019582799973, "chatgames_2": 930628019926736896, "chatgames_1": 930628182116294698,
    "ranktier_1": 930612832926584922, "ranktier_2": 930612832876240956, "ranktier_3": 930612832880443462, "ranktier_4": 930612832796545045,
    "launchcat": 912419839321178182,
    "outop": 930612832876241016,
    "cookiebadge": 930612832897212436,
    "sphealteam6": 930612832855277598
}

# Embed Configuration
embed_success_color = 0x2ecc71
embed_info_color = 0xff8d00
embed_error_color = 0xf44336

# Moderation Configuration
allowed_regex = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789`~!@#$%^&*()-_=+[{]}\|;:,<.>/?/*-+’‘“€£¿¡” \n¯ツ" + "'" + '"'

# Application Configuration
application_questions = [
    "**Question 1/7**\nWhat is your Minecraft Username?",
    "**Question 2/7**\nDo you know/understand English?",
    "**Question 3/7**\nHow much time do you play on Hypixel weekly? Specify (i.e. if you play less while school is in session)",
    "**Question 4/7**\nWhich guilds were you previously in, and why did you decide to leave them?",
    "**Question 5/7**\nWhy do you want to join OUT?",
    "**Question 6/7**\nWhy should we accept you?",
    "**Question 7/7**\nHere you can say anything else about you:"
]

gamemode_emojis = {
            "🌳": "Skyblock",
            "🛏️": "Bedwars",
            "☁️": "Skywars",
            "⚔️": "Duels",
            "🏹": "Murder Mystery",
            "🕳️": "Pit",
            "🍎": "UHC",
            "🧨": "TNT Games",
            "🎮": "Arcade",
            "🔔": "Classic Games",
            "🐑": "Wool Wars",
            "🛠️": "Build Battle",
            "🥕": "SpeedUHC",
            "🌟": "Blitz",
            "🪓": "Warlords",
            "🥊": "Smash Heroes",
            "🏰": "Mega Walls",
            "🔫": "Cops and Crims",
            "✅": "Finished"
        }

# Points Configuration
member_randomizer = (1, 3)
guild_randomizer = (1, 5)
booster_randomizer = (3, 5)

support_rate = 0.02

shop_categories = ["roles", "pets", "badges", "hypixel", "misc"]
formal_shop_categories = {"roles": "Discord Roles", "pets": "OUT Pets", "badges": "Profile Badges", "hypixel": "Hypixel Ranks", "misc": "Miscellaneous"}

category_items = {
    "roles": [
        {
            "type": "role",
            "name": "Asteroid",
            "description": "An Asteroid straight from Pluto, Lectro's home.",
            "price": 100,
            "role_id": 680823950401732719
        }, {
            "type": "role",
            "name": "Planet",
            "description": "PLUTOOOOO, most likely the best planet according to Lectro.",
            "price": 5000,
            "role_id": 680824305713414168
        }, {
            "type": "role",
            "name": "Eclipse",
            "description": "I'm so bright that the sun shines through the moon. If you wanna be bright too, buy me!",
            "price": 10000,
            "role_id": 910677332228984912
        }, {
            "type": "role",
            "name": "Star",
            "description": "Hey now, you're an all star, get your game on, go play. You might know where this is from...",
            "price": 20000,
            "role_id": 745375702647308429
        }, {
            "type": "role",
            "name": "#WHALE",
            "description": "THE KING OF ALL WHALES!",
            "price": 35069,
            "role_id": 702785602512224356,
        }, {
            "type": "role",
            "name": "Nebula",
            "description": "Just like a nebula, this makes you so cool :D",
            "price": 50000,
            "role_id": 910677012497186816
        }, {
            "type": "role",
            "name": "Orange Supergiant",
            "description": "You are a literal giant orange, now deal with it.",
            "price": 65000,
            "role_id": 723955285277802526
        }, {
            "type": "role",
            "name": "SuperNova",
            "description": "The king of all stars, clearly way better than Star.",
            "price": 100000,
            "role_id": 723955427666034719
        }
    ], "pets": [
        {
            "type": "role",
            "name": "Pet Kitty",
            "description": "meow.",
            "price": 10000,
            "role_id": 910677567940472854
        }, {
            "type": "role",
            "name": "Pet Doggo",
            "description": "DOGGO!",
            "price": 10000,
            "role_id": 910677726300610590
        }, {
            "type": "role",
            "name": "Pet Axolotl",
            "description": "The cutest predator!",
            "price": 20000,
            "role_id": 910677743023300638
        }, {
            "type": "role",
            "name": "Pet Ditto",
            "description": "blOb",
            "price": 20000,
            "role_id": 910677767501283359
        }, {
            "type": "role",
            "name": "Pet Parrot",
            "description": "I dance 24/7",
            "price": 30000,
            "role_id": 910677786644086855
        }, {
            "type": "role",
            "name": "Pet Spheal",
            "description": "SPHEALLLLLLLLLLLLLLLLL",
            "price": 30000,
            "role_id": 910677804658606171,
        }, {
            "type": "role",
            "name": "Pet Dragon",
            "description": "Is this the Ender Dragon?",
            "price": 50000,
            "role_id": 910677819359653898
        }
    ], "badges": [
        {
            "type": "badge",
            "name": "OUT OP Badge",
            "description": "Everyone knows that **OUT** is OP but this makes YOU more op too!",
            "price": 500,
            "badge_id": "outop"
        }, {
            "type": "badge",
            "name": "Cookie Badge",
            "description": "Who doesn't love a good cookie?",
            "price": 2000,
            "badge_id": "cookiebadge"
        }, {
            "type": "badge",
            "name": "Spheal Team 6 Badge",
            "description": "Although Spheal > all, this badge represents the hard work of all Spheal Team 6 members!",
            "price": 10000,
            "badge_id": "sphealteam6"
        }, {
            "type": "rank_badge_transaction",
            "name": "Rank Badge Upgrade",
            "description": "__Tier 1:__\n+ 1 Giveaway Entry\n\n__Tier 2:__\n+ `!giftcoins` command\n+ Early Announcement Leak Channel\n\n__Tier 3:__\n+ Exclusive Giveaways Channel\n\n__Tier 4:__\n+ Private VC\n+ Private Threads Perms",
            "price": 15000,
            "badge_identifier": "ranktier",
            "badge_tiers": 4,
            "transaction": "{member.name} ({member.mention}) has purchased the {tier}{suffix} of the Rank Badge.",
            "staff_id": 348602127654060035
        }, {
            "type": "badge",
            "name": "LaunchCat Badge",
            "description": "Honor your proud warrior, LaunchCat, the sacred hero of OUT.",
            "price": 65000,
            "badge_id": "launchcat"
        }
    ], "hypixel": [
        {
            "type": "transaction",
            "name": "VIP Rank",
            "description": "A rank upgrade to VIP on Hypixel.\nOnly one purchasable per month.",
            "price": 45500,
            "transaction": "{member.name} ({member.mention}) has purchased a Hypixel Rank Upgrade to VIP.",
            "staff_id": 756296123538210837
        }, {
            "type": "transaction",
            "name": "VIP+ Rank",
            "description": "A rank upgrade to VIP+ on Hypixel.\nOnly one purchasable per month.",
            "price": 52000,
            "transaction": "{member.name} ({member.mention}) has purchased a Hypixel Rank Upgrade to VIP+.",
            "staff_id": 756296123538210837
        }, {
            "type": "transaction",
            "name": "MVP Rank",
            "description": "A rank upgrade to MVP on Hypixel.\nOnly one purchasable per month.",
            "price": 97500,
            "transaction": "{member.name} ({member.mention}) has purchased a Hypixel Rank Upgrade to MVP.",
            "staff_id": 756296123538210837
        }, {
            "type": "transaction",
            "name": "MVP+ Rank",
            "description": "A rank upgrade to MVP+ on Hypixel.\nOnly one purchasable per month.",
            "price": 130000,
            "transaction": "{member.name} ({member.mention}) has purchased a Hypixel Rank Upgrade to MVP+.",
            "staff_id": 756296123538210837
        }, {
            "type": "transaction",
            "name": "MVP++ Rank",
            "description": "A rank upgrade to MVP++ on Hypixel.\nOnly one purchasable per month.",
            "price": 52000,
            "transaction": "{member.name} ({member.mention}) has purchased a Hypixel Rank Upgrade to MVP++.",
            "staff_id": 756296123538210837
        }
    ], "misc": [
        {
            "type": "transaction",
            "name": "Custom Sprite",
            "description": "A custom graphic, designed by only the best graphic designer there ever was, CRIS EL PERRO!",
            "price": 30000,
            "transaction": "{member.name} ({member.mention}) has purchased a Custom Sprite Design.",
            "staff_id": 639925069447168031
        }, {
            "type": "transaction",
            "name": "Custom Program/Script",
            "description": "A custom program/script, designed by only the best developer there ever was, STARBUCK BARISTA!",
            "price": 45000,
            "transaction": "{member.name} ({member.mention}) has purchased a Custom Program/Script.",
            "staff_id": 348311499946721282
        }, {
            "type": "transaction",
            "name": "Custom Emoji",
            "description": "Your own personal emoji!!!",
            "price": 50000,
            "transaction": "{member.name} ({member.mention}) has purchased a Custom Emoji.",
            "staff_id": 348602127654060035
        }, {
            "type": "transaction",
            "name": "Discord Nitro",
            "description": "A month's worth of Discord Nitro.\nOnly one purchasable per month.",
            "price": 65000,
            "transaction": "{member.name} ({member.mention}) has purchased Discord Nitro.",
            "staff_id": 756296123538210837
        }, {
            "type": "transaction",
            "name": "Custom Role Icon",
            "description": "Want to have a clean looking image beside your name like Lectro and Vibes? Buy this custom role icon!",
            "price": 100000,
            "transaction": "{member.name} ({member.mention}) has purchased a Custom Role Icon.",
            "staff_id": 348602127654060035
        }
    ]
}
