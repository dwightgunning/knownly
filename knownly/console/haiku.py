import random


def haiku():
	# from: https://gist.github.com/hasenj/3205543
    # originally from: https://gist.github.com/1266756
    # with some changes
    # example output:
    # "falling-late-violet-forest-d27b3"
    adjs = [ "autumn", "hidden", "bitter", "misty", "silent", "empty", "dry", "dark",
          "summer", "icy", "delicate", "quiet", "white", "cool", "spring", "winter",
          "patient", "twilight", "dawn", "crimson", "wispy", "weathered", "blue",
          "billowing", "broken", "cold", "damp", "falling", "frosty", "green",
          "long", "late", "lingering", "bold", "little", "morning", "muddy", "old",
          "red", "rough", "still", "small", "sparkling", "throbbing", "shy",
          "wandering", "withered", "wild", "black", "young", "holy", "solitary",
          "fragrant", "aged", "snowy", "proud", "floral", "restless", "divine",
          "polished", "ancient", "purple", "lively", "nameless"
      ]
    nouns = [ "waterfall", "river", "breeze", "moon", "rain", "wind", "sea", "morning",
          "snow", "lake", "sunset", "pine", "shadow", "leaf", "dawn", "glitter",
          "forest", "hill", "cloud", "meadow", "sun", "glade", "bird", "brook",
          "butterfly", "bush", "dew", "dust", "field", "fire", "flower", "firefly",
          "feather", "grass", "haze", "mountain", "night", "pond", "darkness",
          "snowflake", "silence", "sound", "sky", "shape", "surf", "thunder",
          "violet", "water", "wildflower", "wave", "water", "resonance", "sun",
          "wood", "dream", "cherry", "tree", "fog", "frost", "voice", "paper",
          "frog", "smoke", "star"
      ]
    hex = "0123456789abcdef"
    return (random.choice(adjs) + "-" + random.choice(adjs) + "-" + random.choice(nouns) + "-" + random.choice(nouns) + "-" + 
              random.choice(hex) + random.choice(hex) + random.choice(hex) + random.choice(hex) + random.choice(hex))