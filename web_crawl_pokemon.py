import pandas as pd
import requests
import io
import pprint

pp = pprint.PrettyPrinter(indent=4)

MY_PARTY = [
    'Pichu',
    'Buizel',
    'Ralts',
    'Clodsire',
    'Oricorio',
    'Crocalor',
]

URL = "https://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_by_Paldea_Pok%C3%A9dex_number"
BULBA = "https://bulbapedia.bulbagarden.net/"
LOOK_FOR = "decoding=\"async\" width=\"60\" height=\"60\""
NUMBER_OF_POKEMONS = 400

DAMAGE_START = "<th width=\"100px\">Damaged<br />normally by:"
DAMAGE_END = "<h3><span class=\"mw-headline\" id=\"Learnset\">Learnset</span></h3>"
DAMAGE_SEARCH_FOR_START = "style=\"display:"
DAMAGE_SEARCH_FOR = "display:inline-block;"

NORMAL_TO = "<th width=\"100px\">Damaged<br />normally by:"
WEAK_TO = "<th width=\"100px\">Weak to:"
IMMUNE_TO = "<th width=\"100px\">Immune to:"
RESISTANT_TO = "<th width=\"100px\">Resistant to:"
ENDING = "<td><b>None</b>"


POKEMON_TYPES = {
    'Normal': None,
    'Fighting': None,
    'Flying': None,
    'Poison': None,
    'Ground': None,
    'Rock': None,
    'Bug': None,
    'Ghost': None,
    'Steel': None,
    'Fire': None,
    'Water': None,
    'Grass': None,
    'Electric': None,
    'Psychic': None,
    'Ice': None,
    'Dragon': None,
    'Dark': None,
    'Fairy': None,
}

NUM_TYPES = len(list(POKEMON_TYPES))

def craw_for_links():
    resp = requests.get(URL)

    if resp.status_code == 200:
        csvtext = resp.text
        csvbuffer = io.StringIO(csvtext)
        links = []
        names = []
        types = []
        pdexes = []
        count = 0
        unique_names = set()
        
        for line in csvbuffer:
            line = line.strip()
            
            # look for pokemon
            if LOOK_FOR in line and count < NUMBER_OF_POKEMONS:
                line_front, _, line_end = line.partition('\" title=\"')
                name, _, line = line_end.partition('\">')
                if name in unique_names:
                    continue
                unique_names.add(name)
                # add to list of names
                names.append(name)
                _, _, line = line_front.partition('href=\"')
                link, _, line = line.partition('\" ')
                # add to list of links
                links.append(link)
                count += 1
                pdexes.append(count)
                
    return pd.DataFrame({
        "Pdex": pdexes,
        "names": names,
        "links": links},index=names)




class Pokedex:
    def __init__(self):
        self._pokemon_data = craw_for_links()

    def get_data(self):
        return self._pokemon_data

    def fetch_pokemon(self, pokemon_name: str):
        return BULBA + self.get_data().loc[pokemon_name]['links']
    
    def find_type(self, pokemon_name: str):
        resp = requests.get(self.fetch_pokemon(pokemon_name))
        normal_damage = POKEMON_TYPES.copy()
        weak_to = POKEMON_TYPES.copy()
        immune_to = POKEMON_TYPES.copy()
        resistant_to = POKEMON_TYPES.copy()
        effective = {
            "noraml to: ": normal_damage, 
            "weak to: ": weak_to, 
            "immune to: ": immune_to, 
            "resistant to: ": resistant_to
        }
        type_index = POKEMON_TYPES.copy()

        if resp.status_code == 200:
            csvtext = resp.text
            csvbuffer = io.StringIO(csvtext)
            lines = [line.strip() for line in csvbuffer if not line.strip() == '']
            pokemon_types = '<tbody><tr>'
            pokemon_types_lines = lines[lines.index(DAMAGE_START) + 2 :lines.index(DAMAGE_END)]
            normal_damage_lines = lines[lines.index(NORMAL_TO) + 2 :lines.index(ENDING)]
            weak_to_lines = lines[lines.index(WEAK_TO) + 2 :]
            weak_to_lines = weak_to_lines[:weak_to_lines.index(ENDING)]
            immune_to_lines = lines[lines.index(IMMUNE_TO) + 2 :]
            immune_to_lines = immune_to_lines[:immune_to_lines.index(ENDING)]
            resistant_to_lines = lines[lines.index(RESISTANT_TO) + 2 :]
            resistant_to_lines = resistant_to_lines[:resistant_to_lines.index(ENDING)]

            type_count = 0
            effectiveness_count = 0
            
            for line in normal_damage_lines:
                if DAMAGE_SEARCH_FOR_START in line:
                    if "inline-block" in line:
                        effective["noraml to: "][list(POKEMON_TYPES)[type_count]] = True
                    else:
                        effective["noraml to: "][list(POKEMON_TYPES)[type_count]] = False

                    type_count = type_count + 1
                    if type_count == NUM_TYPES:
                        break

            type_count = 0
            for line in weak_to_lines:
                if DAMAGE_SEARCH_FOR_START in line:
                    if "inline-block" in line:
                        effective["weak to: "][list(POKEMON_TYPES)[type_count]] = True
                    else:
                        effective["weak to: "][list(POKEMON_TYPES)[type_count]] = False

                    type_count = type_count + 1
                    if type_count == NUM_TYPES:
                        break
            
            type_count = 0
            for line in immune_to_lines:
                if DAMAGE_SEARCH_FOR_START in line:
                    if "inline-block" in line:
                        effective["immune to: "][list(POKEMON_TYPES)[type_count]] = True
                    else:
                        effective["immune to: "][list(POKEMON_TYPES)[type_count]] = False

                    type_count = type_count + 1
                    if type_count == NUM_TYPES:
                        break

            type_count = 0
            for line in resistant_to_lines:
                if DAMAGE_SEARCH_FOR_START in line:
                    if "inline-block" in line:
                        effective["resistant to: "][list(POKEMON_TYPES)[type_count]] = True
                    else:
                        effective["resistant to: "][list(POKEMON_TYPES)[type_count]] = False

                    type_count = type_count + 1
                    if type_count == NUM_TYPES:
                        break

            return effective

        else:
            return f"Pokemon {pokemon_name} not found"
    
def main():
    pokedex = Pokedex()
    data = pokedex.get_data()
    #print(data)
    party = []
    while True:
        pokemon_name = input("what pokemon would you like to know about? ")
        # print(pokedex.find_type('Sprigatito'))
        print(pokedex.find_type(pokemon_name))
        
    
if __name__ == "__main__":
    main()
