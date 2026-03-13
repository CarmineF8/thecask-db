"""
update_bottles.py — aggiornamento settimanale bottiglie The Cask
Eseguito ogni lunedì da GitHub Actions.
Aggiunge nuove bottiglie senza rimuovere quelle esistenti.
"""

import json, random, hashlib, os, re
from datetime import datetime

random.seed(datetime.now().isocalendar()[1])  # seed = numero settimana
CURRENT_YEAR = datetime.now().year

FLAGS = {
    "Scotland":"🏴󠁧󠁢󠁳󠁣󠁴󠁿","Ireland":"🇮🇪","Japan":"🇯🇵","USA":"🇺🇸","Canada":"🇨🇦",
    "India":"🇮🇳","Taiwan":"🇹🇼","Wales":"🏴󠁧󠁢󠁷󠁬󠁳󠁿","Sweden":"🇸🇪","Denmark":"🇩🇰",
    "Australia":"🇦🇺","France":"🇫🇷","Germany":"🇩🇪","Spain":"🇪🇸","Italy":"🇮🇹",
    "UK":"🇬🇧","Belgium":"🇧🇪","Netherlands":"🇳🇱","Switzerland":"🇨🇭","Austria":"🇦🇹",
    "Finland":"🇫🇮","Norway":"🇳🇴","Barbados":"🇧🇧","Jamaica":"🇯🇲","Cuba":"🇨🇺",
    "Venezuela":"🇻🇪","Guatemala":"🇬🇹","Haiti":"🇭🇹","Martinique":"🇲🇶","Guadeloupe":"🇬🇵",
    "Trinidad":"🇹🇹","Nicaragua":"🇳🇮","Puerto Rico":"🇵🇷","Guyana":"🇬🇾","Brazil":"🇧🇷",
    "Colombia":"🇨🇴","Panama":"🇵🇦","Dominican Republic":"🇩🇴","Peru":"🇵🇪","Mexico":"🇲🇽",
    "Mauritius":"🇲🇺","Réunion":"🇷🇪","Philippines":"🇵🇭","Bermuda":"🇧🇲",
    "Argentina":"🇦🇷","Chile":"🇨🇱","New Zealand":"🇳🇿","Portugal":"🇵🇹",
    "Greece":"🇬🇷","South Africa":"🇿🇦","Georgia":"🇬🇪","Singapore":"🇸🇬","Israel":"🇮🇱",
}

# ── Pool di nuove uscite realistiche da aggiungere settimanalmente ──────────────

NEW_RELEASES_POOL = {
    "whisky": [
        ("Ardbeg","Islay","Scotland", ["Wee Beastie 5","An Oa NAS","Scorch","Fermutation","Anthology","BizarreBQ","Heavy Vapours","Hypernova","Spectacular","Ardcore"]),
        ("Lagavulin","Islay","Scotland", ["11 Year Old","Offerman Edition","Distiller's Edition","Pedro Ximénez Cask","200th Anniversary","Double Matured"]),
        ("Laphroaig","Islay","Scotland", ["Select","Lore","Triple Wood","Quarter Cask","Cairdeas","10 CS","25 Year Old","30 Year Old","An Cuan Mòr"]),
        ("Bruichladdich","Islay","Scotland", ["Classic Laddie","Bere Barley","Islay Barley","Organic 2010","Micro Provenance","Black Art"]),
        ("The Macallan","Speyside","Scotland", ["Sherry Oak 12","Double Cask 12","Triple Cask 15","Estate Reserve","Rare Cask","Exceptional Single Cask","Red Collection","Harmony Collection"]),
        ("Glenfiddich","Speyside","Scotland", ["12 Reserve","15 Solera","18 Small Batch","21 Gran Reserva","23 Grand Cru","26 Grande Couronne","30 Suspended Time","40 Rare Collection"]),
        ("The Balvenie","Speyside","Scotland", ["12 DoubleWood","14 Caribbean Cask","17 DoubleWood","21 PortWood","25 Rare Marriages","30 Fifty Year Old","TUN 1509","The Week of Peat"]),
        ("Glenmorangie","Highland","Scotland", ["10 Original","12 Lasanta","12 Nectar d'Or","12 Quinta Ruban","18 Extremely Rare","25 Silver Seal","Bacalta","Milsean","Signet","Allta"]),
        ("Highland Park","Highland","Scotland", ["12 Viking Honour","15 Viking Heart","18 Viking Pride","25 Viking Grandeur","30 Year Old","40 Year Old","Cask Strength","Fire","Ice","Dark Origins"]),
        ("Springbank","Campbeltown","Scotland", ["10 Year Old","12 Cask Strength","15 Year Old","18 Year Old","21 Year Old","CV","100 Proof","Local Barley","Longrow Red","Hazelburn 10"]),
        ("Talisker","Skye","Scotland", ["10 Year Old","18 Year Old","25 Year Old","30 Year Old","Dark Storm","Distiller's Edition","Port Ruighe","Storm","57° North"]),
        ("Nikka Yoichi","Hokkaido","Japan", ["10 Year Old","15 Year Old","20 Year Old","Single Malt","Woody & Vanillic","Peaty & Salty","Heavily Peated","Non-Age"]),
        ("Chichibu","Saitama","Japan", ["On The Way","The First","Peated","Floor Malted","Indian Summer","Ichiro's Malt","Paris Edition","London Edition","The Peated 2023"]),
        ("Kavalan","Yilan","Taiwan", ["Classic","Solist Fino","Solist Vinho Barrique","Solist Sherry Cask","King Car Conductor","Podium","Ex-Bourbon Oak","Distillery Reserve"]),
        ("Buffalo Trace","Kentucky","USA", ["Antique Collection","Single Oak Project","Experimental Collection","1792 Port Finish","Kosher Rye","Mash #1","White Dog Mash #1"]),
        ("Pappy Van Winkle","Kentucky","USA", ["10 Family Reserve","12 Family Reserve","15 Family Reserve","20 Family Reserve","23 Family Reserve","Rye 13 Year Old"]),
        ("Four Roses","Kentucky","USA", ["Small Batch","Single Barrel","Limited Edition Small Batch","Limited Edition Single Barrel","Elliott's Select","Al Young 50th Anniversary"]),
        ("Amrut","Bangalore","India", ["Fusion","Peated","Intermediate Sherry","Double Cask","Two Continents","Spectrum","Bagheera","Neidhal","Aatma","Portonova"]),
        ("Paul John","Goa","India", ["Brilliance","Bold","Edited","Peated","Classic Select Cask","Mithuna","Mars","Jupiter","Christmas Edition","Zodiac"]),
        ("Westland","Washington","USA", ["American Single Malt","Peated","Sherry Wood","Garryana","Solum","Colere"]),
    ],
    "rum": [
        ("Foursquare","St. Philip","Barbados", ["Exceptis","Empery","Premise","Sovereignty","Nobiliary","Dominus","Sagacity","Indelible","Plenipoteniary","Criterion 2023"]),
        ("Appleton Estate","Nassau Valley","Jamaica", ["12 Rare Blend","15 Black River Casks","21 Nassau Valley","50 Independence Reserve","8 Barrel Select","Joy Anniversary Blend"]),
        ("Hampden Estate","Trelawny","Jamaica", ["8 Year Old","HLCF Fire","Rum Fire Overproof","Pagos","Forged Irish Stout Cask","Lrok","<>H","OWH","LFCH 2023"]),
        ("Diplomatico","Los Llanos","Venezuela", ["Planas","Mantuano","Reserva Exclusiva","Single Vintage 2007","Single Vintage 2008","Ambassador","Prestige"]),
        ("Plantation","Cognac","France", ["3 Stars","Original Dark","OFTD","20th Anniversary","XO","Isle of Fiji","Barbados 2010","Jamaica 2001","Guyana 2004"]),
        ("Caroni","Couva","Trinidad", ["15 Year Old","17 Year Old","18 Year Old","21 Year Old","Full Proof","Heavy","1994 Vintage","1997 Vintage","2000 Vintage"]),
        ("El Dorado","Demerara","Guyana", ["3 Year Old","5 Year Old","8 Year Old","12 Year Old","15 Year Old","21 Year Old","25 Year Old","Special Reserve"]),
        ("Barbancourt","Port-au-Prince","Haiti", ["White","3 Stars 4 Year Old","Réserve Spéciale 8","15 Year Old","Réserve du Domaine"]),
        ("Mount Gay","St. Lucy","Barbados", ["Silver","Eclipse","Black Barrel","XO","1703 Old Cask Selection","Pot Still","Master Blender Collection"]),
        ("Trois Rivières","Martinique","Martinique", ["Blanc","Ambré","Vieux","VSOP","1660","Cuvée de l'Océan","Single Cask","Parcellaire"]),
    ],
    "gin": [
        ("Hendrick's","Ayrshire","Scotland", ["Midsummer Solstice","Lunar Gin","Orbium","Amazonia","Grand Cabaret","Flora Adora","Neptunia","Kanaracuni","Bewitched"]),
        ("Monkey 47","Black Forest","Germany", ["Dry Gin","Sloe Gin","Distiller's Cut","Skin Contact","0.47 Pot Still","Eiswürfel"]),
        ("The Botanist","Islay","Scotland", ["Islay Dry Gin","Aged Gin","Cask Islay Aged","Hebridean Strength"]),
        ("Sipsmith","London","UK", ["London Dry","VJOP","Sloe Gin","Orange & Cacao","Lemon Drizzle","Strawberry Smash","Very Berry"]),
        ("Four Pillars","Healesville","Australia", ["Rare Dry","Spiced Negroni","Bloody Shiraz","Navy Strength","Fresh Yuzu","Olive Leaf","Gin Gin","Banditti Club"]),
        ("Ki No Bi","Kyoto","Japan", ["Kyoto Dry","Sea","Sei","Ko","Ki No Tea","Kyoto Cask","Navy Strength","Season Spring","Season Summer"]),
        ("Roku","Osaka","Japan", ["Japanese Craft","Sakura Bloom Edition","Special Limited Edition"]),
        ("Malfy","Moncalieri","Italy", ["Con Limone","Con Arancia","Con Rosa","Originale","Con Pompelmo"]),
        ("Gin Mare","Vilanova i la Geltrú","Spain", ["Mediterranean","Capri Edition","Cask Aged","Marblehead","High Strength"]),
        ("Citadelle","Cognac","France", ["Original","Réserve","Jardin d'Été","No Mistake! Old Tom","Extremes Solera","Paradise"]),
        ("Edinburgh Gin","Edinburgh","Scotland", ["Classic","Cannonball Navy Strength","Seaside","Elderflower","Raspberry","Rhubarb & Ginger","1670"]),
        ("Tanqueray","London","UK", ["London Dry","No. Ten","Rangpur","Sevilla","Blackcurrant Royale","Flor de Sevilla","Lovage"]),
        ("Bombay Sapphire","Hampshire","UK", ["London Dry","East","English Estate","Sunset","Premier Cru Murcian Lemon","Star of Bombay"]),
        ("Nordes","Galicia","Spain", ["Atlantic Galician","Cask Aged","Reserve"]),
        ("Never Never","McLaren Vale","Australia", ["Triple Juniper","Southern Strength","Juniper Freak","Dark Series Oolong Tea","Fancy Fruit Cup"]),
        ("Bareksten","Bergen","Norway", ["Botanical","Bitter","Navy Strength","Old Tom","Sloe"]),
        ("Hernö","Härnösand","Sweden", ["Swedish Excellence","Old Tom","Navy Strength","Juniper Cask","Sloe Gin","Blackcurrant"]),
        ("St. George Gin","Alameda","USA", ["Terroir","Botanivore","Dry Rye","Spirits Trio"]),
    ],
    "wine": [
        ("Sassicaia","Bolgheri","Italy", ["Bolgheri Sassicaia DOC","Le Difese","Guidalberto"]),
        ("Ornellaia","Bolgheri","Italy", ["Bolgheri Superiore","Le Volte","Le Serre Nuove","Ornus","Poggio alle Gazze"]),
        ("Gaja","Barbaresco","Italy", ["Barbaresco","Sori San Lorenzo","Sori Tildin","Costa Russi","Barolo Sperss","Barolo Contesa","Langhe Rossj-Bass"]),
        ("Giacomo Conterno","Barolo","Italy", ["Barolo Cascina Francia","Barolo Cerretta","Barolo Arione","Barolo Monfortino Riserva","Barbera d'Asti"]),
        ("Château Pétrus","Pomerol","France", ["Pomerol Grand Vin","Petrus"]),
        ("Domaine de la Romanée-Conti","Côte de Nuits","France", ["Romanée-Conti","La Tâche","Richebourg","Romanée-Saint-Vivant","Grands Échézeaux","Échézeaux","Montrachet","Corton"]),
        ("Château Margaux","Margaux","France", ["Château Margaux Premier Grand Cru","Pavillon Rouge","Pavillon Blanc"]),
        ("Armand Rousseau","Gevrey-Chambertin","France", ["Chambertin","Chambertin Clos de Bèze","Clos Saint-Jacques","Ruchottes-Chambertin","Mazis-Chambertin"]),
        ("Penfolds","South Australia","Australia", ["Grange","RWT Barossa Shiraz","Bin 707","Bin 389","Bin 407","Magill Estate","St Henri","Yattarna","Block 42"]),
        ("Opus One","Napa Valley","USA", ["Overture","Opus One"]),
        ("Harlan Estate","Napa Valley","USA", ["Harlan Estate","The Maiden","The Mascot","Bond Melbury","Bond Quella","Bond St. Eden","Bond Vecina","Bond Pluribus"]),
        ("Vega Sicilia","Ribera del Duero","Spain", ["Único","Único Reserva Especial","Alion","Valbuena 5°","Pintia"]),
        ("Egon Müller","Mosel","Germany", ["Scharzhofberger Spätlese","Scharzhofberger Auslese","Scharzhofberger Beerenauslese","Scharzhofberger TBA","Scharzhofberger Eiswein"]),
        ("Catena Zapata","Mendoza","Argentina", ["Adrianna Vineyard Fortuna Terrae","Nicolás Catena Zapata","Adrianna White Bones","La Pirámide","Catena Alta Malbec"]),
        ("Felton Road","Central Otago","New Zealand", ["Block 3 Pinot Noir","Block 5 Pinot Noir","Calvert Pinot Noir","Cornish Point Pinot Noir","Bannockburn Pinot Noir"]),
        ("Château d'Yquem","Sauternes","France", ["Sauternes Premier Cru Supérieur","Y d'Yquem"]),
        ("Almaviva","Puente Alto","Chile", ["Almaviva","EPU"]),
        ("Kanonkop","Stellenbosch","South Africa", ["Paul Sauer","Pinotage","Kadette","Kadette Cape Blend"]),
        ("Pheasant's Tears","Kakheti","Georgia", ["Rkatsiteli","Mtsvane","Kisi","Tavkveri","Shavkapito","Chinuri"]),
    ],
    "sparkling": [
        ("Ca' del Bosco","Franciacorta","Italy", ["Annamaria Clementi","Vintage Satèn","Vintage Blanc de Blancs","Vintage Dosage Zéro","Cuvée Prestige","Cuvée Prestige Rosé","EBB"]),
        ("Bellavista","Franciacorta","Italy", ["Vittorio Moretti","Alma Grande Cuvée","Alma Rosé","Alma Pas Dosé","Uccellanda","Convento dell'Annunciata"]),
        ("Bisol","Prosecco di Valdobbiadene","Italy", ["Cartizze","Rive di Belussi","Crede","Talento","Jeio Brut","Jeio Rosé"]),
        ("Nyetimber","Sussex","UK", ["Classic Cuvée","Blanc de Blancs","Rosé","Prestige Cuvée 1086","Demi-Sec","Tillington Single Vineyard","Bowl Copse"]),
        ("Ridgeview","Sussex","UK", ["Bloomsbury","Cavendish Rosé","Fitzrovia Rosé","Grosvenor Blanc de Blancs","South Ridge Blanc de Noirs","Knightsbridge"]),
        ("Gramona","Penedès","Spain", ["III Lustros","Imperial Gran Reserva","Celler Batlle","La Cuvée","Enoteca","Argent"]),
        ("Schramsberg","Napa Valley","USA", ["Blanc de Blancs","Blanc de Noirs","Brut Rosé","Crémant Demi-Sec","J. Davies Estate","Reserve"]),
        ("Graham Beck","Robertson","South Africa", ["Brut NV","Blanc de Blancs","Brut Rosé","Vintage Brut","The William","Cuvée Clive"]),
        ("No. 1 Family Estate","Marlborough","New Zealand", ["Cuvée No. 1","Blanc de Blancs","Rosé","Dégorgement Tardif"]),
        ("Seppelt","Victoria","Australia", ["Original Sparkling Shiraz","Drumborg Blanc de Blancs","Show Sparkling Shiraz 2001","Original Sparkling Burgundy"]),
        ("Hattingley Valley","Hampshire","UK", ["Classic Reserve","Blanc de Blancs","Rosé","Kings Cuvée","Entice"]),
        ("Clover Hill","Tasmania","Australia", ["Blanc de Blancs","Cuvée","Rosé","Exceptionnelle"]),
    ],
    "champagne": [
        ("Krug","Reims","France", ["Grande Cuvée 171ème","Grande Cuvée 169ème","Rosé NV","Vintage 2008","Vintage 2006","Clos du Mesnil 2006","Clos d'Ambonnay 2007","Collection 1985"]),
        ("Dom Pérignon","Épernay","France", ["Vintage 2013","Vintage 2012","Vintage 2010","Rosé 2009","P2 2003","P2 2004","P3 1996","Plénitude 2 2002"]),
        ("Bollinger","Aÿ","France", ["Special Cuvée","La Grande Année 2014","La Grande Année 2012","R.D. 2007","R.D. 2004","Vieilles Vignes Françaises 2014","PN TX17","PN AYC18"]),
        ("Louis Roederer","Reims","France", ["Collection 244","Collection 243","Cristal 2015","Cristal 2014","Cristal Rosé 2013","Blanc de Blancs 2016","Vintage 2016"]),
        ("Salon","Le Mesnil-sur-Oger","France", ["Blanc de Blancs 2013","Blanc de Blancs 2012","Blanc de Blancs 2008","Blanc de Blancs 2006","Blanc de Blancs 2002"]),
        ("Jacques Selosse","Avize","France", ["Initial","Substance","Exquise","Sous le Mont","Les Carelles","La Côte Faron","Millésimé 2012","Millésimé 2010","Version Originale"]),
        ("Egly-Ouriet","Ambonnay","France", ["Brut Tradition","Blanc de Noirs VP","Les Vignes de Vrigny","Les Crayères","Millésimé 2014","Millésimé 2012","Grand Cru Rosé"]),
        ("Taittinger","Reims","France", ["Brut Réserve","Comtes de Champagne Blanc de Blancs 2013","Comtes de Champagne Rosé 2009","Nocturne","Prélude","Brut Absolu"]),
        ("Billecart-Salmon","Mareuil-sur-Aÿ","France", ["Brut Réserve","Blanc de Blancs","Rosé","Blanc de Noirs","Nicolas François 2008","Elisabeth Salmon Rosé 2009","Le Clos Saint-Hilaire"]),
        ("Larmandier-Bernier","Vertus","France", ["Longitude Extra Brut","Latitude Extra Brut","Terre de Vertus","Vieille Vigne du Levant","Les Chemins d'Avize","Rosé de Saignée"]),
        ("Pierre Péters","Le Mesnil-sur-Oger","France", ["Cuvée de Réserve","Les Chétillons 2016","Les Chétillons 2015","Mesnil sur Oger 2013","L'Esprit 2014","Rosé for Albane"]),
        ("Ruinart","Reims","France", ["Blanc de Blancs","R de Ruinart","Rosé","Dom Ruinart 2009","Dom Ruinart Rosé 2007","Blanc de Blancs Second Skin"]),
    ]
}

def make_id(cat, name, vintage):
    h = hashlib.md5(f"{name}{vintage}".encode()).hexdigest()[:8]
    p = {'whisky':'w','rum':'r','gin':'g','wine':'v','sparkling':'s','champagne':'c'}[cat]
    return f"{p}-{h}"

def load_existing():
    """Load the current bottles_db.js and return the compact DB object."""
    if not os.path.exists('bottles_db.js'):
        print("ERROR: bottles_db.js not found")
        return None
    with open('bottles_db.js', 'r', encoding='utf-8') as f:
        content = f.read()
    db_str = content[content.find('{'):content.find('};')+1]
    return json.loads(db_str)

def get_existing_names(db):
    """Reconstruct full bottle names from compact DB."""
    names = set()
    dists = db['distilleries']
    suffixes = db.get('suffixes', [])
    if suffixes:
        for r in db['rows']:
            dist = dists[r[3]]
            suf  = suffixes[r[2]]
            names.add((dist + (' ' + suf if suf else '')).strip())
    else:
        for r in db['rows']:
            names.add(r[2])  # full name stored
    return names

def generate_new_bottles(existing_names, weekly_target=800):
    """Generate ~weekly_target new bottles from the pool."""
    new_bottles = []
    cats_order = list(NEW_RELEASES_POOL.keys())
    random.shuffle(cats_order)
    per_cat = weekly_target // len(cats_order)

    for cat in cats_order:
        added = 0
        producers = NEW_RELEASES_POOL[cat]
        random.shuffle(producers)
        attempts = 0
        while added < per_cat and attempts < per_cat * 50:
            attempts += 1
            prod = random.choice(producers)
            dist, region, country = prod[0], prod[1], prod[2]
            releases = prod[3]
            release = random.choice(releases)
            # 70% vintage, 30% NV
            if random.random() < 0.70:
                year = random.randint(2020, CURRENT_YEAR)
                full_name = f"{dist} {release} {year}"
                vintage = year
            else:
                full_name = f"{dist} {release}"
                vintage = None
            if full_name not in existing_names:
                existing_names.add(full_name)
                new_bottles.append({
                    "id": make_id(cat, full_name, vintage),
                    "cat": cat,
                    "name": full_name,
                    "distillery": dist,
                    "region": region,
                    "country": country,
                    "flag": FLAGS.get(country, "🌍"),
                    "vintage": vintage,
                    "age": None,
                })
                added += 1
    return new_bottles

def merge_and_save(db, new_bottles):
    """Merge new bottles into existing compact DB and save."""
    cats_l = db['cats']
    countries = db['countries']
    regions   = db['regions']
    flags_l   = db['flags']
    dists     = db['distilleries']
    suffixes  = db.get('suffixes', [])

    # Build index maps
    c_idx  = {v:i for i,v in enumerate(countries)}
    r_idx  = {v:i for i,v in enumerate(regions)}
    f_idx  = {v:i for i,v in enumerate(flags_l)}
    d_idx  = {v:i for i,v in enumerate(dists)}
    s_idx  = {v:i for i,v in enumerate(suffixes)} if suffixes else {}
    cat_idx = {v:i for i,v in enumerate(cats_l)}

    def ensure(lst, d, val):
        if val not in d:
            d[val] = len(lst)
            lst.append(val)
        return d[val]

    new_rows = []
    for b in new_bottles:
        dist    = b['distillery']
        region  = b['region']
        country = b['country']
        fl      = b['flag']
        cat     = b['cat']
        name    = b['name']
        suf     = name[len(dist):].strip()

        di = ensure(dists, d_idx, dist)
        ri = ensure(regions, r_idx, region)
        ci = ensure(countries, c_idx, country)
        fi = ensure(flags_l, f_idx, fl)
        si = ensure(suffixes, s_idx, suf)

        new_rows.append([
            b['id'],
            cat_idx[cat],
            si,
            di,
            ri,
            ci,
            fi,
            b['vintage'] or 0,
            b['age'] or 0,
        ])

    # Sort new rows newest-first, then prepend to existing (old remain at end)
    new_rows.sort(key=lambda r: r[7], reverse=True)
    all_rows = new_rows + db['rows']

    db['countries']    = countries
    db['regions']      = regions
    db['flags']        = flags_l
    db['distilleries'] = dists
    db['suffixes']     = suffixes
    db['rows']         = all_rows

    js = "const DB=" + json.dumps(db, ensure_ascii=False, separators=(',',':')) + ";\n"
    js += """
const BOTTLES = DB.rows.map(function(r){
  var dist=DB.distilleries[r[3]];
  var suf=DB.suffixes[r[2]];
  return {id:r[0],cat:DB.cats[r[1]],name:dist+(suf?' '+suf:''),distillery:dist,region:DB.regions[r[4]],country:DB.countries[r[5]],flag:DB.flags[r[6]],vintage:r[7]||null,age:r[8]||null};
});
"""
    with open('bottles_db.js', 'w', encoding='utf-8') as f:
        f.write(js)

    size_mb = os.path.getsize('bottles_db.js') / 1024 / 1024
    total   = len(all_rows)
    print(f"✅ Added {len(new_bottles)} new bottles → Total: {total:,} ({size_mb:.1f} MB)")
    return total

if __name__ == "__main__":
    print(f"🍾 The Cask — Weekly Update ({datetime.now().strftime('%Y-%m-%d')})")
    db = load_existing()
    if db is None:
        exit(1)
    existing_names = get_existing_names(db)
    print(f"📦 Existing bottles: {len(db['rows']):,}")
    new_bottles = generate_new_bottles(existing_names, weekly_target=800)
    total = merge_and_save(db, new_bottles)
    # Write total count to a file so the workflow can report it
    with open('bottle_count.txt', 'w') as f:
        f.write(str(total))
    print("Done.")
