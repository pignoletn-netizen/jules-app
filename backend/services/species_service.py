import requests
import re
import os
from typing import Dict, Any, List

TAXREF_DATASET_KEY = "7ddf754f-d193-4cc9-b351-99906754a03b"

# Ecology traits reference database for major spider families and common species
FAMILY_ECOLOGY = {
    "Agelenidae": {
        "general": "Araignées constructrices de toiles en entonnoir à la surface du sol, dans les creux de rochers, les murets de pierres sèches ou les buissons bas.",
        "habitat": "Murets de pierres, lisières de forêts, grottes, jardins et bâtiments.",
        "lifestyle": "Prédatrices nocturnes et diurnes guettant leurs proies à la sortie du tube de leur toile."
    },
    "Lycosidae": {
        "general": "Araignées-loups actives à la surface du sol, ne construisant pas de toile de capture mais chassant à l'affût ou à la course.",
        "habitat": "Pelouses sèches, prairies, forêts, grèves de cours d'eau et zones ouvertes.",
        "lifestyle": "Chasseurs terrestres véloces. Les femelles transportent leur cocon fixé aux filières puis les jeunes sur leur abdomen."
    },
    "Salticidae": {
        "general": "Araignées sauteuses dotées d'une vue très développée, chassant à la vue durant la journée.",
        "habitat": "Troncs d'arbres, murs ensoleillés, rochers, végétation basse et feuillages.",
        "lifestyle": "Chasseurs diurnes très agiles effectuant des sauts précis pour capturer leurs proies."
    },
    "Thomisidae": {
        "general": "Araignées-crabes se déplaçant latéralement, chassant à l'affût sans toile sur la végétation ou les fleurs.",
        "habitat": "Fleurs, inflorescences, feuillages, écorces et strate herbacée.",
        "lifestyle": "Chasseurs à l'affût capables de capturer des insectes pollinisateurs plus gros qu'elles."
    },
    "Araneidae": {
        "general": "Araignées orbitèles tissant de grandes toiles géométriques circulaires dans la végétation.",
        "habitat": "Haies, lisières forestières, jardins, prairies et arbustes.",
        "lifestyle": "Chasseurs suspendus au centre de leur toile ou dissimulés dans une loge de soie attenante."
    },
    "Gnaphosidae": {
        "general": "Araignées nocturnes du sol, se cachant le jour sous les pierres ou dans la matière organique dans un logis de soie.",
        "habitat": "Milieux ouverts et secs, garrigues, pelouses chaudes, sous-bois secs et litières.",
        "lifestyle": "Chasseurs terrestres nocturnes neutralisant leurs proies avec des fils de soie solides."
    },
    "Linyphiidae": {
        "general": "Petites araignées très abondantes tissant des toiles en nappe horizontales sous lesquelles elles se suspendent.",
        "habitat": "Litière de feuilles, strate herbacée basse, pelouses, forêts et cultures.",
        "lifestyle": "Prédatrices discrètes de la litière et de la basse végétation, se déplaçant parfois par 'ballooning' (fil de la Vierge)."
    },
    "Clubionidae": {
        "general": "Araignées nocturnes vivant dans la végétation, construisant des loges de soie entre deux feuilles repliées.",
        "habitat": "Feuillages d'arbres, herbes hautes, roselières et buissons.",
        "lifestyle": "Chasseuses nocturnes très actives sur les tiges et les feuilles."
    },
    "Theridiidae": {
        "general": "Araignées tissant des toiles tridimensionnelles irrégulières en réseau de fils enchevêtrés.",
        "habitat": "Sous les pierres, crevasses, végétation, cavités et habitations.",
        "lifestyle": "Prédatrices immobilisant rapidement les proies engluées grâce à leur soie adhésive."
    }
}

ARA_DEPARTMENTS = [
    "Ain", "Allier", "Ardèche", "Cantal", "Drôme", "Isère", "Loire", "Haute-Loire", "Puy-de-Dôme", "Rhône", "Savoie", "Haute-Savoie"
]

def search_species_data(species_name: str) -> Dict[str, Any]:
    """
    Search TAXREF / GBIF for species information, taxonomy, CDnom, ecology,
    and geographic distribution in France and Auvergne-Rhône-Alpes.
    """
    clean_name = species_name.strip()

    # 1. Match species via GBIF
    gbif_match_url = "https://api.gbif.org/v1/species/match"
    gbif_res = requests.get(gbif_match_url, params={"name": clean_name}, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
    match_data = gbif_res.json() if gbif_res.status_code == 200 else {}

    species_key = match_data.get("speciesKey") or match_data.get("usageKey")
    scientific_name = match_data.get("scientificName", clean_name)
    canonical_name = match_data.get("canonicalName", clean_name)
    authorship = match_data.get("authorship", "")

    taxonomy = {
        "kingdom": match_data.get("kingdom", "Animalia"),
        "phylum": match_data.get("phylum", "Arthropoda"),
        "class": match_data.get("class", "Arachnida"),
        "order": match_data.get("order", "Araneae"),
        "family": match_data.get("family", "Inconnue"),
        "genus": match_data.get("genus", canonical_name.split()[0] if canonical_name else ""),
        "species": match_data.get("species", canonical_name)
    }

    # 2. Search TAXREF dataset on GBIF for official INPN Taxref ID (CDnom)
    cd_nom = "Non trouvé"
    taxref_url = "https://api.gbif.org/v1/species/search"
    taxref_res = requests.get(taxref_url, params={"datasetKey": TAXREF_DATASET_KEY, "q": canonical_name}, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)

    vernacular_names = []
    if taxref_res.status_code == 200:
        taxref_json = taxref_res.json()
        results = taxref_json.get("results", [])
        if results:
            first_match = results[0]
            cd_nom = first_match.get("taxonID", str(first_match.get("key", "Inconnu")))
            v_list = first_match.get("vernacularNames", [])
            for v in v_list:
                v_name = v.get("vernacularName")
                v_lang = v.get("language", "")
                if v_name and v_name not in vernacular_names:
                    vernacular_names.append(f"{v_name} ({v_lang})" if v_lang else v_name)

    if cd_nom == "Non trouvé" and species_key:
        cd_nom = f"GBIF:{species_key}"

    # 3. Retrieve occurrences in France and Auvergne-Rhône-Alpes
    total_fr_occ = 0
    ara_occ = 0
    dep_counts = {}

    if species_key:
        occ_url = "https://api.gbif.org/v1/occurrence/search"
        occ_res = requests.get(occ_url, params={"taxonKey": species_key, "country": "FR", "limit": 300}, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)

        if occ_res.status_code == 200:
            occ_data = occ_res.json()
            total_fr_occ = occ_data.get("count", 0)

            for o in occ_data.get("results", []):
                state_prov = str(o.get("stateProvince", ""))
                locality = str(o.get("locality", ""))
                combined_loc = f"{state_prov} {locality}".lower()

                is_ara = False
                for dep in ARA_DEPARTMENTS:
                    if dep.lower() in combined_loc:
                        dep_counts[dep] = dep_counts.get(dep, 0) + 1
                        is_ara = True

                if not is_ara and ("rhône-alpes" in combined_loc or "rhone-alpes" in combined_loc or "auvergne" in combined_loc):
                    dep_counts["Auvergne-Rhône-Alpes (général)"] = dep_counts.get("Auvergne-Rhône-Alpes (général)", 0) + 1
                    is_ara = True

                if is_ara:
                    ara_occ += 1

    # 4. Synthesize Ecology and Habitat Info
    family_name = taxonomy.get("family")
    fam_info = FAMILY_ECOLOGY.get(family_name, {
        "general": "Espèce d'araignée prédatrice d'invertebrés, jouant un rôle écologique clé dans la régulation des populations d'insectes.",
        "habitat": "Strate herbacée, litière forestière, murets de pierre et habitats terrestres variés.",
        "lifestyle": "Chasseur actif ou à la toile selon le mode de prédation propre à la famille."
    })

    # Specific ecological facts for known species
    specific_facts = ""
    if "Textrix denticulata" in canonical_name or "textrix denticulata" in canonical_name.lower():
        specific_facts = "Textrix denticulata est une agélénide saxicole et corticole. Elle affectionne particulièrement les murets de pierres sèches, les fentes de rochers, les écorces d'arbres et les bâtiments. Sa toile en entonnoir comporte un tube de retraite distinctif."
    elif "Agelena labyrinthica" in canonical_name:
        specific_facts = "Agelena labyrinthica construit de très larges toiles en nappe prolongées d'un entonnoir dans les buissons bas et les hautes herbes bien ensoleillées."
    elif "Pardosa" in canonical_name:
        specific_facts = "Les espèces du genre Pardosa sont des araignées-loups héliophiles très actives au sol durant les journées ensoleillées."

    general_ecology = f"{fam_info['general']} {specific_facts}".strip()
    habitat_type = fam_info['habitat']
    lifestyle = fam_info['lifestyle']

    # 5. Build synthetic report summary text
    summary_text = (
        f"La fiche écologique pour l'espèce **{canonical_name}** ({scientific_name}) indique une appartenance à la famille des "
        f"**{taxonomy['family']}** (Ordre : {taxonomy['order']}).\n\n"
        f"**Identifiant Taxref / INPN (CDnom) :** `{cd_nom}`\n\n"
        f"**Écologie générale & Habitat :** {general_ecology}\n"
        f"Type d'habitat privilégié : {habitat_type}.\n\n"
        f"**Répartition géographique :**\n"
        f"- En France métropolitaine : {total_fr_occ} occurrences répertoriées dans la base GBIF/INPN.\n"
        f"- En Auvergne-Rhône-Alpes : {ara_occ} occurrences observées (Départements clés : {', '.join([f'{k} ({v})' for k, v in dep_counts.items()]) if dep_counts else 'Présence régionale attestée'})."
    )

    return {
        "query": clean_name,
        "cd_nom": cd_nom,
        "scientific_name": scientific_name,
        "canonical_name": canonical_name,
        "authorship": authorship,
        "taxonomy": taxonomy,
        "vernacular_names": vernacular_names,
        "ecology": {
            "general_ecology": general_ecology,
            "habitat_type": habitat_type,
            "lifestyle": lifestyle
        },
        "distribution": {
            "total_france_occurrences": total_fr_occ,
            "auvergne_rhone_alpes_occurrences": ara_occ,
            "departments_breakdown": dep_counts
        },
        "summary_text": summary_text
    }
