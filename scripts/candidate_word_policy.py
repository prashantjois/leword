"""Reviewed lexical types; answer eligibility is in candidate-word-review.json."""

# Nationalities, regional demonyms, and people/nation names are eligible even
# when normally capitalized. This does not admit unrelated names or places.
ALLOWED_DEMONYMS = set('''
    aleut anglo arabs asian aztec bantu boers brits cajun carib celts croat
    cuban czech danes dutch finns goths greek haida hakka hausa hmong inuit
    iowan iraqi irish khmer kiowa kurds malay maori mayan nazca norse olmec
    omani oriya osage punic roman sakha saudi saxon scots serbs serer sioux
    slavs swazi swede swiss tamil tatar texan thais turks tutsi utahn uzbek
    welsh xhosa yakut yaqui zulus
'''.split())

# Sexual medical terms remain excluded under the requested gameplay policy.
SEXUAL_MEDICAL_TERMS = set('''
    sperm semen penis vulva glans gonad hymen pubis labia pubic uteri ovary
    ovule groin loins mamma tubal teats sexed
'''.split())

# Medical vocabulary is allowed except for the explicit sexual vocabulary above.
ALLOWED_MEDICAL_TERMS = set('''
    lupus edema polyp lymph renal aorta cecum ileum ilium ulnar ulnae vagus
    talus bursa carpi uteri sacra septa tarsi villi velum axons cilia glans
    gonad hymen pubis labia penis vulva pubic sperm semen urine fecal feces
    enema tumor ulcer cysts stent graft organ nerve blood brain skull spine
    bones veins cells gland fetus fetal tibia femur bowel colon groin loins
    navel mamma tooth teeth tonic serum medic doses detox viral virus covid
    ebola staph strep sulfa bolus phage prion cocci nevus ictus lobar basal
    natal ovule ovary tubal atria fossa scurf wheal phial cecal chyme codon
    exons sebum mucus mumps rabid mania manic panic comas apnea lumps pores
    scars scabs sinus nasal aural optic pupil
'''.split()) - SEXUAL_MEDICAL_TERMS

# Recognizable historical vocabulary is eligible. Age alone is not a reason
# to exclude a word; individual names and unfamiliar variants remain reviewed.
ALLOWED_HISTORICAL_TERMS = set('''
    reich pasha sepoy sahib fakir hajji magus sibyl nabob helot groat burgh
    swain troth wroth wight quoth twixt neath whoso whigs tudor grail oakum
    navvy milch poesy
'''.split())

# Type information is descriptive. It never automatically excludes a word.
TYPE_OVERRIDES = {}
for label, words in {
    'regular noun': '''
        kiddo rehab pappy turbo cutie biker creme femme carbs lovey poppa doozy
        pinup bicep remix manga login satay inbox kanji wurst karts baler barre
        paver rebar bento bindi caver copay emoji panko ramen snark taiga isles
        islet gouda ahold aitch ankhs bevvy bhaji bloop boing carer carny cutey
        cutup dater favas fests fifer flyby footy gazer gunge hazer hider jiffs
        joeys kendo korma logon loris mages moggy moper noirs ollie prier ragas
        ragga rater rotis stims tabla tikka tuque tween updos vlogs welly wikis
        zines afros druid ficus hosta lilos noels pekes seder senor shahs soave
        burbs celeb coeds faves hydro nitro perps synth veeps vocab sicko fiche
        clonk codec
    ''',
    'adjective': '''
        legit daffy girly dorky hyper hunky mopey porky pouty saggy geeky nerdy
        artsy bendy piney jokey ditsy gunky lippy linty unmet zingy malty lardy
        buzzy cyber dilly dippy duper finny folic gutty hench jammy kicky oared
        paleo samey sarky tarty nodal
    ''',
    'verb': '''
        roger roust flied kneed meted wised doled eking uncap unset doxed doxes
        faffs frack frags gussy juked maced maxed miked phish rebid redye relit
        remap resat resit resow tromp unfix vaped vapes clonk
    ''',
    'adverb': 'natch wetly yonks',
    'interjection': 'achoo avast golly humph voila yikes pshaw',
}.items():
    for word in words.split():
        TYPE_OVERRIDES.setdefault(word, []).append(label)
