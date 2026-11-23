"""
Pantry and diet rules of the recommender (own decisions, documented for the thesis).

This file only contains *decisions*, no algorithm:
  1. GROUPS            - which canonical ingredients a user "has" when they tick a pantry item
                         (e.g. ticking "lemon" covers lemon, lemon juice and lemon zest)
  2. STAPLE_ITEMS      - basic items assumed to be in every kitchen
  3. CATEGORY_*        - the shop-style category of each pantry item (used to group the pantry screen)
  4. MEAT_RX / NOT_MEAT_RX - which ingredients make a recipe non-vegetarian

recommender.ipynb applies these rules and writes the result to pantry_items.csv and meat_ingredients.csv,
where every single decision can be checked (and edited) in Excel.
"""

# ---- 1-2. Pantry items --------------------------------------------------------------------------------------
# ---- Pantry items: which recipe ingredients does a user "have" when they tick one pantry item? -------------
STAPLE_ITEMS = {"salt", "black pepper", "water", "vegetable oil"}   # assumed to be in every kitchen

# Explicit groups (own decision, reviewed by hand): pantry item -> canonical ingredient names it covers.
# Names that do not occur in the data are simply ignored.
GROUPS = {
    "salt": ["salt", "kosher salt", "sea salt", "coarse salt", "salt and pepper", "salt & ground black pepper",
             "salt & pepper", "salt and black pepper", "table salt"],
    "black pepper": ["pepper", "black pepper", "fresh ground black pepper", "ground black pepper", "fresh ground pepper",
                     "ground pepper", "cracked black pepper", "fresh coarse ground black pepper", "white pepper",
                     "black peppercorn", "peppercorn"],
    "water": ["water", "boiling water", "cold water", "hot water", "warm water", "ice cube", "ice", "ice water",
              "lukewarm water"],
    "vegetable oil": ["vegetable oil", "canola oil", "cooking spray", "peanut oil", "corn oil", "light olive oil"],
    "bell pepper": ["green pepper", "green bell pepper", "red bell pepper", "red pepper", "bell pepper",
                    "sweet red pepper", "yellow bell pepper", "orange bell pepper", "red capsicum", "capsicum"],
    "chili pepper": ["chile", "green chili", "jalapeno pepper", "jalapeno", "serrano pepper", "green chile",
                     "red chili", "chipotle chile in adobo", "chili", "hot pepper", "green chilies", "fresh jalapeno pepper",
                     "red chile", "serrano chile", "chipotle pepper", "habanero pepper"],
    "red pepper flakes": ["red pepper flake", "crushed red pepper flake", "crushed red pepper", "dried red pepper flake"],
    "cayenne pepper": ["cayenne pepper", "cayenne", "ground red pepper"],
    "powdered sugar": ["powdered sugar", "confectioners' sugar", "icing sugar"],
    "brown sugar": ["brown sugar", "light brown sugar", "dark brown sugar", "packed brown sugar"],
    "sugar": ["sugar", "caster sugar", "superfine sugar", "granulated sugar"],
    "cocoa powder": ["cocoa", "cocoa powder", "unsweetened cocoa powder", "unsweetened cocoa"],
    "oats": ["oat", "rolled oat", "oatmeal", "quick oat", "old fashioned oat", "quick-cooking oat"],
    "ketchup": ["ketchup", "catsup"],
    "half-and-half": ["half-and-half", "half-and-half cream"],
    "cream": ["heavy cream", "light cream", "whipping cream", "double cream", "single cream"],
    "whipped topping": ["cool whip", "whipped topping", "whipped cream"],
    "tomato": ["tomato", "plum tomato", "roma tomato", "cherry tomato", "chopped tomato", "grape tomato",
               "ripe tomato", "large tomato", "beefsteak tomato"],
    "canned tomato": ["diced tomato", "crushed tomato", "stewed tomato", "whole tomato", "canned tomato",
                      "canned diced tomato", "tomatoes with juice", "rotel tomato", "diced tomatoes with green chilies"],
    "tomato sauce": ["tomato sauce", "tomato puree", "spaghetti sauce", "marinara sauce", "pasta sauce"],
    "onion": ["onion", "yellow onion", "sweet onion", "white onion", "spanish onion", "vidalia onion", "large onion"],
    "scallion": ["scallion", "green onion", "spring onion"],
    "garlic": ["garlic", "minced garlic clove", "garlic clove", "minced garlic", "fresh garlic"],
    "ginger": ["ginger", "gingerroot", "fresh ginger", "ground ginger", "fresh gingerroot"],
    "chicken": ["chicken", "chicken breast", "chicken breast half", "chicken thigh", "cooked chicken",
                "cooked chicken breast", "boneless skinless chicken breast", "chicken tender", "chicken wing",
                "chicken drumstick", "whole chicken", "chicken piece", "boneless chicken breast",
                "skinless chicken breast", "chicken leg", "chicken breast fillet", "boneless skinless chicken thigh"],
    "ground beef": ["ground beef", "lean ground beef", "extra lean ground beef", "ground chuck", "hamburger"],
    "ham": ["ham", "cooked ham", "ham steak", "deli ham"],
    "bacon": ["bacon", "bacon strip", "turkey bacon", "bacon bit"],
    "shrimp": ["shrimp", "large shrimp", "medium shrimp", "cooked shrimp", "prawn"],
    "egg": ["egg", "large egg", "hard-boiled egg", "egg white", "egg yolk", "beaten egg", "extra large egg"],
    "egg substitute": ["egg substitute", "egg beater"],
    "milk": ["milk", "whole milk", "skim milk", "low-fat milk", "2% low-fat milk", "1% low-fat milk", "nonfat milk", "2% milk"],
    "cheddar": ["cheddar", "sharp cheddar cheese", "cheddar cheese", "mild cheddar cheese", "low-fat cheddar cheese"],
    "parmesan": ["parmesan cheese", "parmigiano-reggiano cheese", "fresh parmesan cheese", "grated parmesan cheese"],
    "mozzarella": ["mozzarella", "mozzarella cheese", "part-skim mozzarella cheese", "fresh mozzarella cheese"],
    "lemon": ["lemon", "lemon juice", "lemon zest", "lemon rind", "lemon peel", "lemon wedge", "lemon, juice of",
              "lemon, zest of", "fresh lemon juice", "lemon, rind of", "lemon slice"],
    "lime": ["lime", "lime juice", "lime zest", "lime wedge", "lime, juice of", "lime, zest of", "fresh lime juice",
             "lime rind", "lime peel"],
    "orange": ["orange", "orange zest", "orange rind", "orange peel", "orange, zest of", "orange, juice of",
               "orange, rind of", "navel orange"],
    "apple": ["apple", "granny smith apple", "tart apple", "red apple", "golden delicious apple", "green apple"],
    "potato": ["potato", "red potato", "russet potato", "baking potato", "new potato", "yukon gold potato",
               "small red potato", "idaho potato"],
    "carrot": ["carrot", "baby carrot", "large carrot", "shredded carrot"],
    "celery": ["celery", "celery rib", "celery stalk", "celery stick"],
    "mushroom": ["mushroom", "sliced mushroom", "button mushroom", "fresh mushroom", "white mushroom", "baby portabella mushroom",
                 "cremini mushroom", "portabella mushroom"],
    "spinach": ["spinach", "baby spinach", "frozen chopped spinach", "frozen spinach", "fresh spinach", "spinach leaf"],
    "broccoli": ["broccoli", "broccoli floret", "frozen broccoli"],
    "corn": ["corn", "frozen corn", "whole kernel corn", "corn kernel", "creamed corn", "cream-style corn"],
    "pea": ["pea", "frozen pea", "green pea"],
    "rice": ["rice", "long grain rice", "white rice", "brown rice", "cooked rice", "basmati rice",
             "jasmine rice", "long-grain rice", "instant rice", "arborio rice", "cooked brown rice"],
    "pasta": ["pasta", "spaghetti", "elbow macaroni", "penne pasta", "linguine", "fettuccine", "egg noodle",
              "macaroni", "penne", "rotini pasta", "angel hair pasta", "lasagna noodle", "spaghetti pasta",
              "bow tie pasta", "noodle", "fettuccine pasta", "orzo pasta", "rigatoni pasta", "small shell pasta"],
    "bread": ["bread", "white bread", "french bread", "italian bread", "sourdough bread", "whole wheat bread",
              "bread slice", "baguette"],
    "breadcrumbs": ["breadcrumb", "dry breadcrumb", "fresh breadcrumb", "panko breadcrumb", "italian seasoned breadcrumb",
                    "seasoned breadcrumb", "plain breadcrumb"],
    "flour": ["flour", "unbleached flour", "bread flour", "self-rising flour", "cake flour", "plain flour"],
    "cornmeal": ["cornmeal", "yellow cornmeal"],
    "corn syrup": ["corn syrup", "light corn syrup", "dark corn syrup"],
    "peanut butter": ["peanut butter", "creamy peanut butter", "chunky peanut butter", "smooth peanut butter"],
    "mustard": ["mustard", "yellow mustard", "prepared mustard"],
    "vinegar": ["vinegar", "white vinegar", "distilled white vinegar"],
    "cider vinegar": ["cider vinegar", "apple cider vinegar"],
    "rice vinegar": ["rice vinegar", "rice wine vinegar", "seasoned rice vinegar"],
    "white wine": ["white wine", "dry white wine"],
    "red wine": ["red wine", "dry red wine"],
    "sherry": ["dry sherry", "sherry wine", "sherry"],
    "chicken broth": ["chicken broth", "chicken stock", "chicken bouillon cube", "low sodium chicken broth",
                      "chicken bouillon", "chicken bouillon granule", "fat free chicken broth"],
    "beef broth": ["beef broth", "beef stock", "beef bouillon cube", "beef bouillon", "beef consomme"],
    "vegetable broth": ["vegetable broth", "vegetable stock"],
    "coconut": ["coconut", "flaked coconut", "shredded coconut", "sweetened flaked coconut", "unsweetened coconut",
                "desiccated coconut"],
    "almond": ["almond", "sliced almond", "slivered almond", "blanched almond"],
    "walnut": ["walnut", "chopped walnut", "walnut piece"],
    "pecan": ["pecan", "chopped pecan", "pecan half", "pecan piece"],
    "chocolate chips": ["chocolate chip", "semi-sweet chocolate chip", "milk chocolate chip", "white chocolate chip",
                        "mini chocolate chip", "semisweet chocolate chip"],
    "chocolate": ["chocolate", "semisweet chocolate", "bittersweet chocolate", "unsweetened chocolate",
                  "dark chocolate", "white chocolate", "unsweetened baking chocolate", "semi-sweet chocolate"],
    "raisin": ["raisin", "golden raisin"],
    "pineapple": ["pineapple", "crushed pineapple", "pineapple chunk", "pineapple tidbit"],
    "applesauce": ["applesauce", "unsweetened applesauce"],
    "yogurt": ["yogurt", "plain yogurt", "greek yogurt", "plain greek yogurt", "low-fat plain yogurt", "nonfat yogurt",
               "vanilla yogurt", "plain nonfat yogurt", "fat-free plain yogurt"],
    "sour cream": ["sour cream", "light sour cream", "low-fat sour cream", "fat-free sour cream"],
    "cream cheese": ["cream cheese", "light cream cheese", "fat-free cream cheese", "neufchatel cheese"],
    "mayonnaise": ["mayonnaise", "light mayonnaise", "low-fat mayonnaise", "miracle whip", "fat-free mayonnaise"],
    "butter": ["butter", "salted butter", "melted butter", "cold butter", "softened butter"],
    "margarine": ["margarine", "light margarine", "butter flavored crisco"],
    "tortilla": ["tortilla", "flour tortilla", "corn tortilla", "tortilla chip", "whole wheat tortilla"],
    "beans": ["black bean", "kidney bean", "pinto bean", "refried bean", "cannellini bean", "great northern bean",
              "navy bean", "red kidney bean", "white bean", "baked bean"],
    "chickpea": ["chickpea", "garbanzo bean"],
    "olive": ["black olive", "kalamata olive", "green olive", "olive", "pitted black olive"],
    "vanilla": ["vanilla", "vanilla extract", "pure vanilla extract", "vanilla bean"],
    "hot sauce": ["hot sauce", "tabasco sauce", "hot pepper sauce", "sriracha sauce"],
    "nut": ["nut", "chopped nut", "mixed nut"],
    "mint": ["of fresh mint", "mint leaf", "mint", "fresh mint"],
    "cilantro": ["cilantro", "cilantro leaf", "fresh cilantro", "coriander leaf"],
    "parsley": ["parsley", "flat leaf parsley", "italian parsley", "fresh parsley", "dried parsley", "parsley flake"],
    "basil": ["basil", "basil leaf", "dried basil", "fresh basil", "fresh basil leaf"],
    "oregano": ["oregano", "dried oregano", "fresh oregano", "oregano leaf"],
    "thyme": ["thyme", "dried thyme", "fresh thyme", "thyme leaf", "dried thyme leaf"],
    "rosemary": ["rosemary", "dried rosemary", "fresh rosemary"],
    "dill": ["dill", "dill weed", "fresh dill", "dried dill", "dried dill weed"],
    "sage": ["sage", "dried sage", "fresh sage", "rubbed sage", "ground sage"],
    "chives": ["chive", "fresh chive"],
    "cinnamon": ["cinnamon", "ground cinnamon", "cinnamon stick"],
    "nutmeg": ["nutmeg", "ground nutmeg"],
    "cumin": ["cumin", "ground cumin", "cumin seed"],
    "coriander": ["coriander", "ground coriander", "coriander seed"],
    "cloves": ["clove", "ground clove", "whole clove"],
    "allspice": ["allspice", "ground allspice"],
    "turmeric": ["turmeric", "ground turmeric"],
    "cardamom": ["cardamom", "ground cardamom", "cardamom pod"],
    "mustard powder": ["dry mustard", "mustard powder", "ground mustard"],
    "dried onion": ["dried onion flake", "onion flake", "dried minced onion", "minced onion"],
    "tofu": ["firm tofu", "tofu", "extra firm tofu", "silken tofu"],
    "pie crust": ["pie crust", "pie shell", "unbaked pie shell", "refrigerated pie crust", "baked pie shell",
                  "deep dish pie shell", "graham cracker pie crust"],
    "graham crackers": ["graham cracker crumb", "graham cracker"],
    "squash": ["butternut squash", "squash", "yellow squash", "acorn squash", "summer squash"],
    "cabbage": ["cabbage", "red cabbage", "green cabbage", "coleslaw mix"],
    "lettuce": ["lettuce", "romaine lettuce", "iceberg lettuce", "lettuce leaf", "mixed greens", "salad green"],
    "cranberry": ["cranberry", "fresh cranberry", "frozen cranberry"],
    "mandarin orange": ["mandarin orange", "mandarin orange segment"],
    "pork": ["pork chop", "pork tenderloin", "pork loin", "pork shoulder", "boneless pork chop", "pork roast",
             "boneless pork loin", "pork butt", "pork rib"],
    "salmon": ["salmon fillet", "salmon", "smoked salmon"],
    "white fish": ["white fish fillet", "tilapia fillet", "cod fillet", "fish fillet", "halibut fillet", "cod"],
    "crab": ["crabmeat", "crab meat", "imitation crabmeat"],
    "tuna": ["tuna", "tuna in water", "canned tuna", "solid white tuna"],
    "beef steak/roast": ["beef", "stewing beef", "beef chuck roast", "flank steak", "sirloin steak", "beef stew meat",
                         "round steak", "chuck roast", "beef tenderloin", "steak", "skirt steak"],
    "sausage": ["sausage", "italian sausage", "smoked sausage", "pork sausage", "kielbasa", "andouille sausage",
                "breakfast sausage", "chorizo sausage", "hot italian sausage", "polish sausage", "sweet italian sausage"],
    "coconut milk": ["coconut milk", "light coconut milk", "unsweetened coconut milk"],
    "cottage cheese": ["cottage cheese", "low-fat cottage cheese", "small curd cottage cheese"],
    "ricotta": ["ricotta cheese", "part-skim ricotta cheese"],
    "swiss cheese": ["swiss cheese", "gruyere cheese"],
    "feta": ["feta cheese", "crumbled feta cheese"],
    "blue cheese": ["blue cheese", "gorgonzola"],
    "artificial sweetener": ["artificial sweetener", "splenda granular", "splenda sugar substitute", "stevia", "sugar substitute"],
    "honey": ["honey"],
}

GROUPS["flour"] += ["self raising flour", "self-raising flour"]
GROUPS["vanilla"] += ["vanilla essence"]
GROUPS["marshmallow"] = ["marshmallow", "ature marshmallow", "miniature marshmallow"]   # 'ature' = stemming artefact of 'miniature'
GROUPS["lemongrass"] = ["lemongras", "lemongrass"]
GROUPS["cornstarch"] = ["cornstarch", "cornflmy", "corn starch"]                       # cornflour (UK) = cornstarch
GROUPS["cream of mushroom soup"] = ["cream of mushroom soup", "condensed cream of mushroom soup"]
GROUPS["cream of chicken soup"] = ["cream of chicken soup", "condensed cream of chicken soup"]
GROUPS["monterey jack cheese"] = ["monterey jack cheese", "monterey jack pepper cheese", "pepper jack cheese"]
GROUPS["whipped topping"] += ["frozen whipped topping"]
GROUPS["breadcrumbs"] += ["seasoned bread crumb", "bread crumb"]
GROUPS["pie crust"] += ["graham cracker crust", "pizza crust"]
GROUPS["parsley"] += ["fresh parsley leaf", "dried parsley flake", "fresh flat-leaf parsley"]
GROUPS["marjoram"] = ["marjoram", "dried marjoram"]
GROUPS["tarragon"] = ["tarragon", "dried tarragon"]
GROUPS["paprika"] = ["paprika", "sweet paprika", "smoked paprika", "hungarian paprika"]
GROUPS["cayenne pepper"] += ["ground cayenne pepper"]
GROUPS["onion soup mix"] = ["onion soup mix", "dry onion soup mix"]
GROUPS["bacon"] += ["cooked bacon"]
GROUPS["turkey"] = ["cooked turkey", "turkey breast", "turkey"]
GROUPS["pork"] += ["pork loin chop"]
GROUPS["shrimp"] += ["raw shrimp"]
GROUPS["sesame seed"] = ["sesame seed", "toasted sesame seed"]
GROUPS["sesame oil"] = ["sesame oil", "dark sesame oil", "toasted sesame oil"]
GROUPS["vegetable oil"] += ["salad oil"]
GROUPS["shortening"] = ["shortening", "vegetable shortening"]
GROUPS["lemon"] += ["lemons, juice of"]
GROUPS["chili pepper"] += ["diced green chili", "green chili pepper"]
GROUPS["spinach"] += ["baby spinach leaf"]
GROUPS["onion"] += ["diced onion"]
GROUPS["bell pepper"] += ["yellow pepper"]
GROUPS["asparagus"] = ["asparagus", "asparagus spear"]
GROUPS["baking mix"] = ["bisquick", "bisquick baking mix"]
GROUPS["salt"] += ["salt & fresh ground pepper"]
GROUPS["mushroom"] += ["shiitake mushroom"]
GROUPS["cucumber"] = ["cucumber", "english cucumber"]
GROUPS["soy milk"] = ["soymilk", "soy milk"]

# ---- Categories of the pantry items (manual overrides are checked first, then the first matching rule wins) ----
CATEGORY_OVERRIDE = {
    "salt": "Staples", "black pepper": "Staples", "water": "Staples", "vegetable oil": "Staples",
    "tomato": "Vegetables", "bell pepper": "Vegetables", "chili pepper": "Vegetables", "eggplant": "Vegetables",
    "garlic": "Vegetables", "corn": "Vegetables", "pea": "Vegetables", "sweet potato": "Vegetables",
    "pumpkin": "Vegetables", "roasted red pepper": "Vegetables", "sun-dried tomato": "Vegetables",
    "egg substitute": "Eggs & dairy", "butter": "Eggs & dairy", "cream cheese": "Eggs & dairy",
    "whipped topping": "Eggs & dairy", "evaporated milk": "Eggs & dairy", "sweetened condensed milk": "Eggs & dairy",
    "vanilla ice cream": "Eggs & dairy", "soy milk": "Eggs & dairy", "powdered milk": "Eggs & dairy",
    "peanut butter": "Nuts & seeds", "coconut": "Nuts & seeds", "nut": "Nuts & seeds", "peanut": "Nuts & seeds",
    "tahini": "Nuts & seeds",
    "garlic powder": "Herbs & spices", "onion powder": "Herbs & spices", "chili powder": "Herbs & spices",
    "red pepper flakes": "Herbs & spices", "cayenne pepper": "Herbs & spices", "ginger": "Herbs & spices",
    "mustard powder": "Herbs & spices", "nutmeg": "Herbs & spices", "lemon pepper": "Herbs & spices",
    "celery seed": "Herbs & spices", "caraway seed": "Herbs & spices", "mustard seed": "Herbs & spices",
    "fennel seed": "Herbs & spices", "poppy seed": "Herbs & spices", "onion salt": "Herbs & spices",
    "lemongrass": "Herbs & spices", "onion soup mix": "Herbs & spices",
    "pie crust": "Grains, pasta & bread", "graham crackers": "Grains, pasta & bread",
    "hamburger bun": "Grains, pasta & bread", "wheat germ": "Grains, pasta & bread", "cornbread": "Grains, pasta & bread",
    "margarine": "Oils & fats", "shortening": "Oils & fats", "olive oil": "Oils & fats",
    "cream of tartar": "Baking", "baking powder": "Baking", "baking soda": "Baking", "cocoa powder": "Baking",
    "chocolate chips": "Baking", "chocolate": "Baking", "almond extract": "Baking", "butterscotch chip": "Baking",
    "baking mix": "Baking", "candy bar": "Baking", "cornstarch": "Baking",
    "lemon": "Fruits", "lime": "Fruits", "orange": "Fruits", "orange juice": "Fruits", "fruit": "Fruits",
    "cherry pie filling": "Fruits", "dried cranberry": "Fruits", "dried apricot": "Fruits",
    "artificial sweetener": "Sweeteners", "apricot preserve": "Sweeteners", "orange marmalade": "Sweeteners",
    "fish sauce": "Sauces & condiments", "oyster sauce": "Sauces & condiments", "olive": "Sauces & condiments",
    "salsa": "Sauces & condiments", "worcestershire sauce": "Sauces & condiments", "pizza sauce": "Sauces & condiments",
    "coconut milk": "Canned goods & broths", "canned tomato": "Canned goods & broths",
    "tomato sauce": "Canned goods & broths", "tomato paste": "Canned goods & broths",
    "canned pumpkin": "Canned goods & broths", "pumpkin puree": "Canned goods & broths",
    "kahlua": "Drinks & alcohol", "apple cider": "Drinks & alcohol",
    "mandarin orange": "Fruits", "dried onion": "Herbs & spices",
}
CATEGORY_RULES = [  # (category, regex on the pantry item name)
    ("Sauces & condiments", r"\bvinegar\b"),          # before the drinks rule ("red wine vinegar")
    ("Canned goods & broths", r"\b(broth|stock|bouillon|consomme|soup)\b"),
    ("Drinks & alcohol", r"\b(wine|sherry|beer|rum|vodka|brandy|liqueur|bourbon|whiskey|tequila|juice|coffee|tea|"
                         r"cola|soda|lemonade)\b"),
    ("Meat & fish", r"\b(chicken|beef|pork|bacon|ham|sausage|turkey|lamb|veal|steak|shrimp|prawn|salmon|tuna|fish|"
                    r"cod|tilapia|crab|clam|scallop|anchov|pepperoni|salami|prosciutto|chorizo|kielbasa|hot dog|"
                    r"meat|liver|duck|lobster|mussel|oyster|halibut|trout)"),
    ("Eggs & dairy", r"\b(egg|milk|cream|cheese|cheddar|parmesan|mozzarella|ricotta|feta|yogurt|buttermilk|"
                     r"half-and-half|sour cream|ghee|velveeta|mascarpone|cottage)"),
    ("Oils & fats", r"\b(oil|shortening|lard)\b"),
    ("Grains, pasta & bread", r"\b(rice|pasta|spaghetti|macaroni|noodle|bread|breadcrumbs|tortilla|oats|cornmeal|"
                              r"couscous|quinoa|barley|cracker|crust|biscuit|bun|roll|pita|bagel|cereal|corn flake|"
                              r"krisp|crouton|puff pastry|phyllo|wonton|granola|lasagna)"),
    ("Baking", r"\b(flour|baking|yeast|cornstarch|cocoa|chocolate|vanilla|extract|cake mix|gelatin|tartar|"
               r"marshmallow|sprinkle|pudding|frosting|food coloring)"),
    ("Sweeteners", r"\b(sugar|honey|syrup|molasses|sweetener|agave|stevia|jam|jelly|preserve|marmalade)"),
    ("Herbs & spices", r"\b(basil|oregano|thyme|rosemary|parsley|cilantro|dill|sage|mint|chives|tarragon|marjoram|"
                       r"bay leaf|cinnamon|cumin|coriander|cloves|allspice|turmeric|cardamom|paprika|curry|"
                       r"seasoning|spice|garam masala|powder|saffron|herb|salt)"),
    ("Nuts & seeds", r"\b(nut|almond|walnut|pecan|peanut|cashew|pistachio|hazelnut|seed|pine nut)"),
    ("Sauces & condiments", r"\b(sauce|ketchup|mustard|mayonnaise|vinegar|salsa|dressing|pickle|caper|relish|"
                            r"paste|pesto|hummus|horseradish|smoke)"),
    ("Legumes & tofu", r"\b(bean|chickpea|lentil|tofu|edamame|snow pea)"),
    ("Fruits", r"\b(apple|banana|berry|strawberr|blueberr|raspberr|cranberr|cherr|peach|pear|pineapple|mango|"
               r"grape|raisin|date|apricot|plum|prune|melon|kiwi|fig|pomegranate|rhubarb|avocado|applesauce|"
               r"currant|papaya|nectarine)"),
    ("Vegetables", r"."),   # everything that is left (onion, carrot, potato, ...); reviewed by hand
]


# ---- 4. Vegetarian rule --------------------------------------------------------------------------------------
# An ingredient is non-vegetarian if its name contains a meat / fish / seafood word (or gelatin / lard / suet) ...
MEAT_RX = (r"\b(chicken|beef|pork|bacon|ham|hams|sausage|turkey|lamb|veal|steak|shrimp|prawn|salmon|tuna|fish|"
           r"cod|tilapia|crab|crabmeat|clam|scallop|anchov\w*|pepperoni|salami|prosciutto|pancett\w*|chorizo|"
           r"kielbasa|bratwurst|hot dog|frankfurter|wiener|meat|meatball|liver|duck|goose|venison|lobster|mussel|"
           r"oyster|halibut|trout|sardine|catfish|snapper|swordfish|mahi|haddock|flounder|brisket|rib|ribs|"
           r"roast beef|corned beef|pastrami|gelatin|lard|suet|bouillon|giblet|squid|octop\w*|caviar)\b")
# "pancett\w*" and "octop\w*" also cover the dataset's own singular forms ("pancettum", "octopu").
# The rule is applied to the canonical names AND to the original ingredient text of each recipe, because the
# canonical mapping sometimes drops the meat word ("beef rump" -> "rum", "tuna in olive oil" -> "olive oil").
# ... unless it is one of these known vegetarian exceptions (plural forms included, for the original text).
NOT_MEAT_RX = (r"\b(?:vegetarian|veggie|meatless|vegan|soy|imitation bacon|vegetable bouillon|"
               r"oyster mushroom|hamburger bun|hot dog bun|steak sauce|steak seasoning|meat tenderizer|"
               r"celery rib|beefsteak tomato|pork and bean|steak.style)s?\b")
