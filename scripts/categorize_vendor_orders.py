"""Bulk-categorize uncategorized Amazon and Henry Schein orders in amazon_orders.

Usage:
    python scripts/categorize_vendor_orders.py                # dry run (default)
    python scripts/categorize_vendor_orders.py --apply         # write to DB

    # Production:
    fly ssh console -a ledger-oak -C 'python3 /app/scripts/categorize_vendor_orders.py'
    fly ssh console -a ledger-oak -C 'python3 /app/scripts/categorize_vendor_orders.py --apply'
"""
from __future__ import annotations

import os
import sys
from collections import defaultdict
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATA_DIR = os.environ.get("DATA_DIR", "./local_state")
os.makedirs(DATA_DIR, exist_ok=True)

from core.db import get_connection, init_db

# ── Personal keyword rules ──────────────────────────────────────────────────
# (keywords, category, subcategory)
# Order matters: more specific rules first, first match wins.

_PERSONAL_RULES: list[tuple[list[str], str, str]] = [
    # ── Childcare (before Home so "baby" doesn't match Home/General) ──────
    (["diaper", "huggies", "pampers", "diaper pail", "baby gate", "baby monitor",
      "nursery", "baby wipe", "baby bottle", "pacifier", "sippy cup", "teether",
      "infant", "newborn", "crib", "bassinet", "baby seat", "car seat",
      "stroller", "baby carrier", "swaddle", "onesie", "bib", "cradle cap",
      "baby shampoo", "baby lotion", "baby powder",
      "baby proof", "child proof", "childproof", "baby safety",
      "potty", "potty train", "floor potty",
      "babyganics", "baby sanitizer", "baby soap"],
     "Childcare", "General"),

    # ── LL Expense (before Shopping so resale items go here) ──────────────
    (["poshmark", "resale", "purse display", "handbag display", "bubble mailer",
      "shipping supplies", "mailing box", "shipping envelope", "holographic mailer",
      "poly mailer", "tissue paper wrap", "thank you card pack",
      "jewelry display", "garment bag",
      "purse chain", "chain strap", "crossbody strap", "shoulder strap",
      "seavilia", "leather luster", "patent leather finish",
      "wool dauber"],
     "LL Expense", "General"),

    # ── Food/Coffee (before Food/Groceries so coffee doesn't become generic food)
    (["coffee pod", "k-cup", "k cup", "kcup", "creamer", "coffee maker",
      "keurig", "nespresso", "coffee filter", "coffee bean", "ground coffee",
      "coffee capsule", "coffee machine", "espresso"],
     "Food", "Coffee"),

    # ── Food/Groceries ───────────────────────────────────────────────────
    (["snack", "food", "cereal", "candy", "chips", "crackers", "cookies",
      "waffles", "waffle", "drink mix", "seasoning", "sauce", "spice",
      "pantry", "grocery", "granola", "protein bar", "kind bar", "cliff bar",
      "clif bar", "popcorn", "pretzel", "jerky", "fruit snack", "gummy",
      "chocolate", "peanut butter", "jelly", "jam", "honey", "maple syrup",
      "olive oil", "cooking spray", "vinegar", "ketchup", "mustard",
      "mayonnaise", "ranch", "bbq sauce", "hot sauce", "salsa",
      "nut", "almond", "cashew", "walnut", "mixed nuts",
      "tea bag", "tea box", "green tea", "herbal tea",
      "frito-lay", "frito lay", "variety pack", "fun times mix",
      "sweet'n low", "sweetener", "sugar packet",
      "coffee stirrer", "stir stick", "margaritaville",
      "concoction maker", "frozen drink"],
     "Food", "Groceries"),

    # ── Entertainment/Toys (before Entertainment/General so toys win) ─────
    (["toy", "toys", "lego", "hot wheels", "nerf", "playset", "play set",
      "playground", "trampoline", "puzzle", "stuffed animal", "plush",
      "plushie", "doll", "action figure", "walkie talkie", "coloring book",
      "craft kit", "sticker", "play-doh", "play doh", "playdough",
      "figurine", "building blocks", "remote control car", "rc car",
      "water gun", "squirt gun", "foam dart", "pretend play",
      "bluey", "vtech", "wacky waving", "inflatable tube",
      "construction paper", "crayola"],
     "Entertainment", "Toys"),

    # ── Entertainment/Books ──────────────────────────────────────────────
    (["book", "kindle", "paperback", "hardcover", "novel", "edition",
      "reading", "workbook", "textbook", "coloring"],
     "Entertainment", "Books"),

    # ── Entertainment/Games ──────────────────────────────────────────────
    (["board game", "card game", "video game", "nintendo", "xbox",
      "playstation", "gaming", "game console", "switch game",
      "uno", "monopoly", "dice"],
     "Entertainment", "Games"),

    # ── Entertainment/Kids (tablets/devices for kids) ─────────────────────
    (["kids tablet", "fire tablet", "fire hd", "kids pro", "fire 7 kids",
      "fire 8 kids", "fire 10 kids", "kids edition", "kids case"],
     "Entertainment", "Kids"),

    # ── Entertainment/General (party supplies, misc) ─────────────────────
    (["party supplies", "balloon", "party decoration", "birthday banner",
      "tablecloth", "streamers", "confetti", "party favor", "party plate",
      "party cup", "party hat", "pinata", "piñata", "sprinkles",
      "birthday candle", "cake topper",
      "party blower", "noisemaker", "noise maker", "blowout"],
     "Entertainment", "General"),

    # ── Clothing/Kids (before generic Clothing) ──────────────────────────
    (["kids clothes", "boys ", "girls ", "toddler clothing", "children's",
      "kids shoes", "kids boots", "kids jacket", "kids dress", "kids shirt",
      "kids pants", "kids shorts", "kids pajama", "kids costume",
      "kids hat", "kids glove", "kids sock", "baby clothes", "baby outfit",
      "girls dress", "girls shirt", "boys shirt", "boys pants",
      "girls pants", "girls shorts", "boys shorts", "girls jacket",
      "boys jacket", "children dress", "children shirt",
      "toddler shoes", "toddler dress", "toddler shirt",
      # Specific kids brands/items
      "crocs kids", "crocs unisex-child", "kid's original ride",
      "rocky kid", "little kid", "big kid",
      "kids flexible glasses", "kids prescription glasses",
      "kids travel suitcase", "toddler luggage",
      "kids water bottle", "kids lunch"],
     "Clothing", "Kids"),

    # ── Clothing/Men ─────────────────────────────────────────────────────
    (["men's", "mens ", "tactical pants", "vertx", "men shirt",
      "men shorts", "men jacket", "men shoes", "men boots"],
     "Clothing", "Men"),

    # ── Clothing/Women ───────────────────────────────────────────────────
    (["women's", "womens ", "dress", "gown", "tearaway pants",
      "women shirt", "women shorts", "women jacket", "women shoes",
      "legging", "yoga pants", "maternity"],
     "Clothing", "Women"),

    # ── Clothing/General (catch-all clothing) ────────────────────────────
    (["shirt", "pants", "shoes", "socks", "jacket", "clothing",
      "shorts", "underwear", "hat ", "gloves", "boots", "sneaker",
      "sandal", "hoodie", "sweater", "coat", "vest",
      "pajama", "costume", "t-shirt", "jeans", "belt", "beanie",
      "scarf", "tie ", "polo", "blazer"],
     "Clothing", "General"),

    # ── Pets/Food (before Pets/General) ──────────────────────────────────
    (["dog food", "cat food", "royal canin", "pet food", "purina",
      "blue buffalo", "iams", "pedigree", "meow mix", "fancy feast",
      "dog treat", "cat treat", "pet treat", "kibble", "wet food",
      "dry food"],
     "Pets", "Food"),

    # ── Pets/Toys ────────────────────────────────────────────────────────
    (["dog toy", "cat toy", "pet toy", "chew toy", "fetch toy",
      "squeaky toy", "rope toy", "catnip"],
     "Pets", "Toys"),

    # ── Pets/Health ──────────────────────────────────────────────────────
    (["pet health", "flea", "tick collar", "tick prevention", "heartworm",
      "pet medicine", "pet supplement", "pet vitamin", "pet shampoo",
      "pet wipe", "pet ear", "pet dental"],
     "Pets", "Health"),

    # ── Pets/General ─────────────────────────────────────────────────────
    (["pet ", "dog ", "cat ", "aquarium", "reptile", "fish tank",
      "pet bed", "pet mat", "pet crate", "pet tracker", "tractive",
      "leash", "collar", "puppy", "kitten", "bird", "hamster",
      "pet carrier", "pet bowl", "pet feeder", "pet gate",
      "litter", "litter box", "scratching post"],
     "Pets", "General"),

    # ── Health & Beauty/Skincare (before generic Health) ──────────────────
    (["skincare", "sunscreen", "moisturizer", "dermalogica", "supergoop",
      "crest", "mouthwash", "toothbrush", "toothpaste", "oral care",
      "deodorant", "lotion", "soap", "body wash", "face wash",
      "hand soap", "face cream", "anti-aging", "serum", "toner",
      "cleanser", "exfoliat", "lip balm", "chapstick",
      "makeup", "cosmetic", "nail polish", "foundation", "mascara",
      "eyeliner", "lipstick", "blush", "concealer", "bronzer",
      "setting spray", "brush set", "beauty blender",
      "razor", "shaving cream", "aftershave", "cologne", "perfume",
      "floss", "colgate",
      "tweezerman", "brow shaping", "eyebrow",
      "eyeglass", "nose pad", "gecko grip", "nerdwax", "glasses wax",
      "anti slip eyeglass"],
     "Health & Beauty", "Skincare"),

    # ── Health & Beauty/Haircare ─────────────────────────────────────────
    (["shampoo", "conditioner", "hair dryer", "hair straightener",
      "hair brush", "hair clip", "hair tie", "hair spray",
      "hair gel", "hair wax", "hair color", "hair dye",
      "curling iron", "flat iron", "blow dryer"],
     "Health & Beauty", "Haircare"),

    # ── Health & Beauty/Fitness ──────────────────────────────────────────
    (["fitness", "exercise", "workout", "yoga mat", "resistance band",
      "dumbbell", "kettlebell", "jump rope", "exercise ball",
      "foam roller", "pull up bar", "weight", "treadmill",
      "exercise bike", "gym"],
     "Health & Beauty", "Fitness"),

    # ── Healthcare/General ───────────────────────────────────────────────
    (["medicine", "first aid", "thermometer", "medical", "tick remover",
      "health", "vitamin", "supplement", "bandage", "allergy",
      "ibuprofen", "tylenol", "advil", "acetaminophen", "aspirin",
      "cough", "cold medicine", "inhaler", "pulse oximeter",
      "blood pressure", "heating pad", "ice pack", "brace",
      "glucometer", "test strip",
      "monistat", "yeast infection", "miconazole",
      "walking cane", "cane ", "foldable cane", "walking stick"],
     "Healthcare", "General"),

    # ── Home/Kitchen (before Home/General) ────────────────────────────────
    (["kitchen", "trash can", "simplehuman", "paper plate", "dixie",
      "plates", "cups", "pan", "skillet", "cookware", "blender",
      "ninja", "air fryer", "waffle maker", "cooking", "utensil",
      "silicone turner", "spatula", "cutting board", "knife set",
      "silverware", "dinnerware", "fork", "spoon", "pot ",
      "baking", "mixing bowl", "colander", "strainer", "peeler",
      "can opener", "bottle opener", "corkscrew", "measuring cup",
      "measuring spoon", "whisk", "tong", "ladle", "rolling pin",
      "dish rack", "dish drying", "paper towel holder",
      "oxo", "flexible turner", "good grips"],
     "Home", "Kitchen"),

    # ── Home/Cleaning ────────────────────────────────────────────────────
    (["cleaning", "mrs meyer", "lysol", "swiffer", "mop", "vacuum",
      "broom", "cleaner", "clorox", "windex", "disinfectant",
      "dish soap", "dawn ", "trash bags", "trash bag", "garbage bag",
      "glad ", "hand soap", "scrub", "sponge", "duster",
      "spray bottle", "microfiber cloth", "mop pad", "cleaning wipe",
      "stain remover", "oxy clean", "oxiclean", "magic eraser",
      "pledge", "pine sol", "fabuloso", "air freshener", "febreze"],
     "Home", "Cleaning"),

    # ── Home/Decor ───────────────────────────────────────────────────────
    (["decor", "picture frame", "aura", "wall art", "candle", "rug",
      "curtain", "pillow", "blanket", "throw", "tapestry",
      "vase", "decorative", "wall decal", "photo frame",
      "artificial plant", "fake plant", "led strip", "string light",
      "accent light", "table lamp", "floor lamp"],
     "Home", "Decor"),

    # ── Home/Improvement ─────────────────────────────────────────────────
    (["led", "light bulb", "cree", "handrail", "grab bar", "mount",
      "mounting", "bracket", "hardware", "screw", "bolt", "nut ",
      "washer", "hinge", "clamp", "beam clamp", "drywall", "caulk",
      "putty", "stud finder", "wire nut", "outlet", "switch plate",
      "wall plate", "electrical", "flood light", "paint",
      "sandpaper", "primer", "tape measure", "level",
      "nail", "lag ", "anchor", "wall anchor", "toggle bolt",
      "door knob", "door handle", "cabinet hardware", "drawer pull"],
     "Home", "Improvement"),

    # ── Home/Laundry ─────────────────────────────────────────────────────
    (["laundry", "detergent", "dryer sheet", "fabric softener",
      "charmin", "toilet paper", "cottonelle", "paper towel",
      "bounty", "scott ", "tissue", "kleenex", "napkin",
      "laundry basket", "hamper", "ironing board", "iron ",
      "starch", "wrinkle release", "downy"],
     "Home", "Laundry"),

    # ── Home/Storage ─────────────────────────────────────────────────────
    (["storage", "container", "organizer", "rubbermaid", "bin",
      "box", "shelf", "shelving", "closet", "rack",
      "basket", "drawer", "cabinet", "stackable",
      "plastic tote", "storage bag", "vacuum bag", "space bag"],
     "Home", "Storage"),

    # ── Home/Tools ───────────────────────────────────────────────────────
    (["tool", "drill", "dewalt", "workbench", "wrench", "screwdriver",
      "pliers", "saw", "hammer", "socket", "ratchet",
      "tool box", "tool bag", "tool set", "power tool",
      "impact driver", "drill bit", "sander", "grinder",
      "level", "utility knife", "box cutter",
      "ldm", "laser distance", "laser measure", "tape measure"],
     "Home", "Tools"),

    # ── Home/Security ────────────────────────────────────────────────────
    (["camera", "security", "axis", "vaultek", "safe", "gun safe",
      "security camera", "doorbell camera", "ring doorbell",
      "motion sensor", "alarm", "lock", "deadbolt", "padlock",
      "trail cam", "trail camera", "game camera",
      "holster", "gun cloth", "gun cleaning", "otis technology",
      "firearm", "magazine pouch", "ammo"],
     "Home", "Security"),

    # ── Home/General ─────────────────────────────────────────────────────
    (["home", "household", "mattress", "bed", "box spring", "furniture",
      "dehumidifier", "air conditioner", "fan", "humidifier",
      "hanger", "hook", "mat", "door mat", "welcome mat",
      "shower curtain", "bath mat", "towel", "bath towel",
      "sheet", "comforter", "duvet", "pillow case", "bedding",
      "air filter", "filtrete", "hvac", "hepa",
      "extension cord", "power strip", "surge protector",
      "smoke detector", "carbon monoxide", "fire extinguisher",
      "aluminum foil", "plastic wrap", "ziploc", "zip lock",
      "packing tape", "scotch tape", "duct tape"],
     "Home", "General"),

    # ── Ranch/Equipment ──────────────────────────────────────────────────
    (["sprayer", "petratools", "hose", "garden", "weed killer",
      "fence", "outdoor", "grill", "weber", "lawn", "yard",
      "wheelbarrow", "garden tool", "garden hose", "mower",
      "trimmer", "chainsaw", "hedge trimmer", "leaf blower",
      "weed eater", "pressure washer", "irrigation", "sprinkler",
      "fire pit", "patio", "deck", "landscape", "mulch",
      "soil", "fertilizer", "seed", "plant", "pot ", "planter",
      "shovel", "rake", "hoe", "garden glove", "tiller",
      "post hole", "auger",
      "insecticide", "permethrin", "durvet", "pour-on",
      "natural armor", "weed and grass", "herbicide",
      "diesel exhaust fluid", "bluedef", "def ",
      "geocel", "sealant", "gutter seal"],
     "Ranch", "Equipment"),

    # ── Ranch/Supplies ───────────────────────────────────────────────────
    (["livestock", "feed", "trough", "float valve", "stock tank",
      "barn", "hay", "straw", "feed bucket", "water tank",
      "cattle", "horse", "chicken", "goat", "saddle"],
     "Ranch", "Supplies"),

    # ── Gifts/General ────────────────────────────────────────────────────
    (["gift", "gift set", "gift card", "gift wrap", "wrapping paper",
      "gift bag", "gift box", "gift tag", "present"],
     "Gifts", "General"),

    # ── Transportation/General ───────────────────────────────────────────
    (["car", "vehicle", "auto", "automotive", "car seat cover",
      "car mat", "car charger", "car phone mount", "car wash",
      "windshield", "wiper", "tire", "motor oil", "car freshener",
      "dash cam", "car vacuum", "car cover", "trunk organizer",
      "car jack", "jumper cable"],
     "Transportation", "General"),

    # ── Shopping/Kids ────────────────────────────────────────────────────
    (["kids gift", "kids backpack", "kids suitcase", "kids luggage",
      "kids water bottle", "kids lunch", "kids umbrella"],
     "Shopping", "Kids"),

    # ── Abuelitos/General ────────────────────────────────────────────────
    (["abuelitos"],
     "Abuelitos", "General"),

    # ── Electronics (catch-all, near bottom) ─────────────────────────────
    (["cable", "charger", "adapter", "hub", "usb", "hdmi",
      "phone case", "screen protector", "earbuds", "headphone",
      "speaker", "battery pack", "bluetooth", "mouse", "keyboard",
      "monitor", "laptop", "tablet", "apple tv", "remote",
      "roku", "fire stick", "sd card", "flash drive", "hard drive",
      "ssd", "echo ", "alexa", "smart plug", "smart home",
      "ring ", "doorbell", "power bank", "surge protector",
      "rayovac", "energizer", "duracell", "alkaline", "lithium",
      "aa battery", "aaa battery", "lr44", "cr2",
      "isoacoustic", "iso-puck", "acoustic isolator"],
     "Electronics", "General"),

    # ── Home/General (last-resort catch for misc home items) ─────────────
    (["silicone boot", "stanley", "brasso", "metal polish",
      "light switch guard", "switch cover"],
     "Home", "General"),
]


# ── BFM keyword rules ───────────────────────────────────────────────────────

_BFM_RULES: list[tuple[list[str], str, str]] = [
    # ── IT/Hardware (before generic Electronics) ─────────────────────────
    (["computer", "pc ", "ssd", "keyboard", "mouse", "monitor",
      "cable", "adapter", "usb", "hdmi", "ram", "printer",
      "toner", "brother", "beelink", "corsair", "samsung",
      "hard drive", "flash drive", "ethernet", "router", "switch",
      "docking station", "hub", "webcam", "headset",
      "laptop stand", "monitor arm", "kvm", "ups battery",
      "surge protector", "power strip", "label maker",
      "cable management", "velcro", "zip tie",
      "thermal paste", "cpu", "gpu", "motherboard", "fan ",
      "heatsink", "pc case", "power supply", "psu",
      # IT tools & infrastructure
      "pliers", "wire stripper", "klein tools", "knipex", "conduit",
      "tweezers", "crimper", "multimeter", "soldering",
      "cable tester", "punch down", "fish tape", "wire puller",
      "raceway", "wire loom", "cable tray", "patch panel",
      "keystone jack", "wall mount", "tv mount", "tv wall",
      "bracket", "shelf bracket", "corner bracket",
      # Cameras & AV
      "axis", "camera mount", "security camera", "ip camera",
      "smart tv", "lg ", "samsung tv", "apple tv",
      "twelve south", "hoverbar", "ipad stand",
      "macbook", "laptop case", "laptop sleeve",
      # Storage media
      "sd card", "microsd", "pny", "sandisk",
      # LED/wiring infrastructure
      "led channel", "led diffuser", "led strip", "muzata",
      "aluminum channel", "conduit connector", "wire connector",
      "wire splitter", "low voltage",
      # Misc IT
      "pelican case", "pelican 1400", "range bag",
      "backpack", "vertx", "briggs", "maxpedition",
      "organizer pouch", "pocket organizer",
      "magnifying glass", "magnifier", "loupe",
      "polycom", "voip", "phone handset",
      "screw", "bolt", "nut ", "seam sealer"],
     "IT", "Hardware"),

    # ── Supplies/Printer (before Supplies/General) ───────────────────────
    (["printer paper", "toner", "brother toner", "ink cartridge",
      "labels", "label tape", "dymo", "thermal label",
      "copy paper", "cardstock"],
     "Supplies", "Printer"),

    # ── Supplies/General ─────────────────────────────────────────────────
    (["office supplies", "staples", "paper", "folder", "pen ",
      "pencil", "envelope", "tape", "label", "binder",
      "post-it", "sticky note", "rubber band", "paper clip",
      "scissors", "ruler", "highlighter", "marker", "sharpie",
      "stamp", "stamp pad", "desk organizer", "file cabinet",
      "whiteboard", "dry erase",
      # Storage & misc supplies
      "storage box", "plastic storage", "iris usa", "iris ",
      "storage bin", "storage container", "tote",
      "wd-40", "wd40", "lubricant",
      "eye wash", "physiciancare", "first aid kit",
      "embroidery", "name patch", "custom patch",
      "decal", "sticker", "business prime", "membership fee",
      "hook and loop", "adhesive strip"],
     "Supplies", "General"),

    # ── Kitchen/General ──────────────────────────────────────────────────
    (["kitchen", "coffee", "keurig", "k-cup", "k cup", "kcup",
      "snack", "food", "water", "cup ", "plate", "napkin",
      "paper towel", "trash can", "trash bag", "simplehuman",
      "dixie", "creamer", "sugar", "sweetener", "stir stick",
      "paper plate", "plastic fork", "plastic spoon",
      "disposable", "styrofoam", "paper bowl", "solo cup"],
     "Kitchen", "General"),

    # ── Bathroom/General ─────────────────────────────────────────────────
    (["toilet paper", "charmin", "cottonelle", "hand soap",
      "soap dispenser", "tissue", "kleenex", "purell",
      "sanitizer", "air freshener", "paper towel dispenser",
      "urinal cake", "bathroom", "toilet"],
     "Bathroom", "General"),

    # ── Medical Supplies (Henry Schein subcategories — specific first) ───
    (["syringe", "needle", "safety needle", "luer lock",
      "injection needle", "hypodermic", "insulin syringe"],
     "Medical Supplies", "Needles & Syringes"),

    (["test kit", "xpert", "cepheid", "diagnostic", "rapid test",
      "covid test", "flu test", "rsv test", "strep", "hemocue",
      "glucose test", "ekg", "electrode", "a1c"],
     "Medical Supplies", "Diagnostics"),

    (["glove", "mask", "ppe", "sani-cloth", "sani cloth",
      "sharps", "sharps container", "gown", "face shield",
      "n95", "surgical mask", "exam glove", "nitrile",
      "biohazard", "red bag", "disinfectant wipe"],
     "Medical Supplies", "PPE"),

    (["exam table", "thermometer", "curette", "electrode",
      "otoscope", "ophthalmoscope", "stethoscope",
      "blood pressure cuff", "pulse ox", "tongue depressor",
      "reflex hammer", "speculum", "exam paper", "table paper",
      "headlamp", "penlight"],
     "Medical Supplies", "Exam Supplies"),

    (["injection", "medication", "rx ", "drug", "pharmaceutical",
      "injectable", "vial", "ampoule", "vaccine"],
     "Medical Supplies", "Rx"),

    (["bandage", "wound", "gauze", "adhesive bandage",
      "wound care", "steri-strip", "butterfly closure",
      "wound dressing", "hemostatic"],
     "Medical Supplies", "Wound Care"),

    (["medical", "medical supply", "clinical", "patient",
      "specimen", "lab supply", "cotton ball", "cotton swab",
      "alcohol prep", "alcohol pad", "betadine", "iodine",
      "first aid", "nar ", "north american rescue", "burntec",
      "burn dressing", "trauma", "tourniquet", "hemostatic",
      "pulse oximeter", "innovo"],
     "Medical Supplies", "General"),

    # ── Facilities/General ───────────────────────────────────────────────
    (["facility", "building", "maintenance", "light bulb",
      "hvac", "air filter", "filtrete", "fluorescent",
      "exit sign", "fire extinguisher", "smoke detector",
      "ceiling tile", "floor mat", "door stop"],
     "Facilities", "General"),

    # ── Home/General (cleaning supplies for office) ──────────────────────
    (["household", "cleaning", "lysol", "wipes", "disinfectant",
      "broom", "mop", "vacuum", "clorox", "windex",
      "spray bottle", "microfiber", "duster", "sponge",
      "trash bag", "garbage bag"],
     "Home", "General"),

    # ── Staff Gifts/General ──────────────────────────────────────────────
    (["gift", "holiday", "party", "decoration", "birthday",
      "gift card", "gift basket", "celebration", "congratulation",
      "thank you gift", "appreciation"],
     "Staff Gifts", "General"),

    # ── Office Environment/General ───────────────────────────────────────
    (["office decor", "wall art", "picture frame", "plant",
      "rug", "clock", "wall clock", "desk plant", "succulent",
      "artificial plant", "door sign", "name plate",
      "welcome sign", "wall calendar"],
     "Office Environment", "General"),

    # ── Electronics/General ──────────────────────────────────────────────
    (["electronics", "battery", "duracell", "charger",
      "power bank", "extension cord", "outlet",
      "energizer", "aa battery", "aaa battery", "9v battery",
      "rechargeable", "smart plug"],
     "Electronics", "General"),

    # ── Marketing/General ────────────────────────────────────────────────
    (["marketing", "promotional", "signage", "banner",
      "business card", "flyer", "brochure", "poster",
      "pen with logo", "branded", "custom print"],
     "Marketing", "General"),
]


# ── Henry Schein-specific rules (all BFM Medical Supplies) ───────────────────

_HENRY_SCHEIN_RULES: list[tuple[list[str], str, str]] = [
    (["syringe", "needle", "safety needle", "luer lock",
      "hypodermic", "insulin syringe"],
     "Medical Supplies", "Needles & Syringes"),

    (["test kit", "xpert", "cepheid", "diagnostic", "rapid test",
      "covid", "flu test", "rsv", "strep", "hemocue",
      "glucose", "ekg", "electrode", "a1c", "hba1c"],
     "Medical Supplies", "Diagnostics"),

    (["glove", "mask", "ppe", "sani-cloth", "sani cloth", "wipe",
      "sharps", "gown", "face shield", "n95", "nitrile",
      "biohazard", "red bag"],
     "Medical Supplies", "PPE"),

    (["exam table", "thermometer", "curette", "otoscope",
      "ophthalmoscope", "stethoscope", "blood pressure",
      "pulse ox", "tongue depressor", "reflex hammer",
      "speculum", "table paper", "exam paper", "penlight",
      "headlamp"],
     "Medical Supplies", "Exam Supplies"),

    (["injection", "medication", "rx", "drug", "pharmaceutical",
      "injectable", "vial", "ampoule", "vaccine", "lidocaine",
      "epinephrine", "saline"],
     "Medical Supplies", "Rx"),

    (["bandage", "wound", "gauze", "adhesive bandage",
      "steri-strip", "wound dressing", "hemostatic"],
     "Medical Supplies", "Wound Care"),
]


# ── Amazon category fallback maps ────────────────────────────────────────────
# Used when keyword rules don't match but Amazon's own category is available.
# Maps Amazon internal category -> (our_category, our_subcategory).

_PERSONAL_AMAZON_CAT_MAP: dict[str, tuple[str, str]] = {
    "grocery": ("Food", "Groceries"),
    "health and beauty": ("Health & Beauty", "Skincare"),
    "beauty": ("Health & Beauty", "Skincare"),
    "office product": ("Home", "General"),
    "home improvement": ("Home", "Improvement"),
    "home": ("Home", "General"),
    "kitchen": ("Home", "Kitchen"),
    "lighting": ("Home", "Improvement"),
    "ce": ("Electronics", "General"),
    "personal computer": ("Electronics", "General"),
    "speakers": ("Electronics", "General"),
    "wireless": ("Electronics", "General"),
    "video games": ("Entertainment", "Games"),
    "baby product": ("Childcare", "General"),
    "toys": ("Entertainment", "Toys"),
    "apparel": ("Clothing", "General"),
    "shoes": ("Clothing", "General"),
    "pet supplies": ("Pets", "General"),
    "lawn & garden": ("Ranch", "Equipment"),
    "automotive": ("Transportation", "General"),
    "sports": ("Entertainment", "General"),
    "books": ("Entertainment", "Books"),
    "home theater": ("Electronics", "General"),
    "luggage": ("Home", "General"),
    "photography": ("Electronics", "General"),
}

_BFM_AMAZON_CAT_MAP: dict[str, tuple[str, str]] = {
    "grocery": ("Kitchen", "General"),
    "health and beauty": ("Bathroom", "General"),
    "beauty": ("Bathroom", "General"),
    "office product": ("Supplies", "General"),
    "home improvement": ("Facilities", "General"),
    "home": ("Supplies", "General"),
    "kitchen": ("Kitchen", "General"),
    "lighting": ("Facilities", "General"),
    "ce": ("IT", "Hardware"),
    "personal computer": ("IT", "Hardware"),
    "speakers": ("IT", "Hardware"),
    "wireless": ("IT", "Hardware"),
    "video games": ("Electronics", "General"),
    "business, industrial, & scientific supplies basic": ("Supplies", "General"),
    "baby product": ("Supplies", "General"),
    "toys": ("Staff Gifts", "General"),
    "apparel": ("Supplies", "General"),
    "shoes": ("Supplies", "General"),
    "pet supplies": ("Supplies", "General"),
    "lawn & garden": ("Facilities", "General"),
    "automotive": ("Supplies", "General"),
    "sports": ("Supplies", "General"),
    "books": ("Supplies", "General"),
    "home theater": ("IT", "Hardware"),
    "luggage": ("Supplies", "General"),
    "photography": ("IT", "Hardware"),
}


def _match_rules(
    text: str,
    rules: list[tuple[list[str], str, str]],
) -> tuple[Optional[str], Optional[str]]:
    """Match text against keyword rules. Returns (category, subcategory) or (None, None)."""
    lower = text.lower()
    for keywords, category, subcategory in rules:
        if any(kw in lower for kw in keywords):
            return category, subcategory
    return None, None


def categorize_orders(entity_key: str, apply: bool = False) -> dict:
    """Categorize uncategorized vendor orders for an entity.

    Returns stats dict with counts and breakdown.
    """
    conn = get_connection(entity_key)
    try:
        rows = conn.execute(
            "SELECT id, product_summary, amazon_category, vendor "
            "FROM amazon_orders "
            "WHERE category IS NULL OR category = ''"
        ).fetchall()

        if not rows:
            return {"total": 0, "categorized": 0, "remaining": 0, "breakdown": {}}

        updates = []
        breakdown = defaultdict(int)

        for row in rows:
            order_id = row["id"]
            product_summary = row["product_summary"] or ""
            amazon_cat = row["amazon_category"] or ""
            vendor = row["vendor"] or "amazon"

            category, subcategory = None, None

            # Henry Schein orders: try HS-specific rules first, then BFM rules
            if vendor == "henry_schein":
                category, subcategory = _match_rules(product_summary, _HENRY_SCHEIN_RULES)
                if not category:
                    category, subcategory = _match_rules(product_summary, _BFM_RULES)
                # Default all Henry Schein to Medical Supplies/General
                if not category:
                    category, subcategory = "Medical Supplies", "General"

            # Amazon orders: use entity-appropriate rules
            elif entity_key == "company":
                category, subcategory = _match_rules(product_summary, _BFM_RULES)
            else:
                category, subcategory = _match_rules(product_summary, _PERSONAL_RULES)

            # If still no match and we have an Amazon category, try the category map
            if not category and amazon_cat:
                cat_map = _BFM_AMAZON_CAT_MAP if entity_key == "company" else _PERSONAL_AMAZON_CAT_MAP
                key = amazon_cat.strip().lower()
                if key in cat_map:
                    category, subcategory = cat_map[key]

            if category:
                updates.append((category, subcategory or "General", order_id))
                cat_label = f"{category}/{subcategory or 'General'}"
                breakdown[cat_label] += 1

        if apply and updates:
            conn.executemany(
                "UPDATE amazon_orders SET category = ?, subcategory = ? WHERE id = ?",
                updates,
            )
            conn.commit()

        return {
            "total": len(rows),
            "categorized": len(updates),
            "remaining": len(rows) - len(updates),
            "breakdown": dict(sorted(breakdown.items())),
        }
    finally:
        conn.close()


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Bulk-categorize uncategorized vendor orders in amazon_orders."
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        default=False,
        help="Write changes to DB (default is dry run).",
    )
    args = parser.parse_args()

    mode = "APPLY" if args.apply else "DRY RUN"
    print(f"=== Categorize Vendor Orders ({mode}) ===\n")

    entities = [
        ("Personal", "personal"),
        ("BFM", "company"),
        ("Luxe Legacy", "luxelegacy"),
    ]

    grand_total = 0
    grand_categorized = 0
    grand_remaining = 0

    for display_name, entity_key in entities:
        # Initialize DB (ensures tables exist)
        try:
            init_db(entity_key)
        except Exception:
            pass

        stats = categorize_orders(entity_key, apply=args.apply)

        if stats["total"] == 0:
            print(f"  {display_name}: no uncategorized orders")
            continue

        print(f"  {display_name}:")
        print(f"    Uncategorized orders found: {stats['total']}")
        print(f"    Categorized:                {stats['categorized']}")
        print(f"    Still uncategorized:         {stats['remaining']}")

        if stats["breakdown"]:
            print(f"    Breakdown:")
            for cat, count in stats["breakdown"].items():
                print(f"      {cat}: {count}")

        print()

        grand_total += stats["total"]
        grand_categorized += stats["categorized"]
        grand_remaining += stats["remaining"]

    print(f"  --- Grand Total ---")
    print(f"    Total uncategorized:  {grand_total}")
    print(f"    Categorized:          {grand_categorized}")
    print(f"    Still uncategorized:  {grand_remaining}")

    if not args.apply and grand_categorized > 0:
        print(f"\n  (Dry run -- no changes written. Use --apply to write.)")


if __name__ == "__main__":
    main()
