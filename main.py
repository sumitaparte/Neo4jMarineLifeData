from typing import Dict, List
from util import *

from db import session

base_url = 'https://oceana.ca'


def get_animal_details(url: str) -> Dict:
    print("GET: {}{}".format(base_url, url))
    animal_soup = get_soup(url)
    animal = dict()
    name = animal_soup.find("div", class_="subpage-header-inner").find("h1").get_text().strip()
    habitat = animal_soup.find("h2", string="Ecosystem/Habitat").find_next('p').get_text().strip()
    feeding_habits = animal_soup.find("h2", string="Feeding Habits").find_next('p').get_text().strip()
    conservation_status = animal_soup.find("h2", string="Conservation Status")
    if conservation_status is not None:
        conservation_status = conservation_status.find_next('p').get_text().strip()
    if conservation_status is None:
        conservation_status = "NA"
    animal["name"] = name
    animal["habitat"] = habitat
    animal["feeding_habits"] = feeding_habits
    animal["conservation_status"] = conservation_status

    return animal


def get_all_animals() -> List[Dict]:
    animals = list()
    first_page = get_soup('{}/en/marine-life/canadian-marine-life-encyclopedia'.format(base_url))
    articles = first_page.find_all("article")
    for article in articles:
        article_url = article.find_next("a").get("href")
        animal = get_animal_details('{}{}'.format(base_url, article_url))
        animals.append(animal)
    return animals


def createAnimal(animal, n4j_session):
    create_qry = "CREATE (a: Animal{name: $name, habitat: $habitat, conservtnStatus:$conservation_status}) return a"
    return n4j_session.run(create_qry, name=animal['name'], habitat=animal['habitat'],
                           conservation_status=animal['conservation_status'])


def findAnimalByName(animal_name, n4j_session):
    return n4j_session.run("match (a) where a.name=$name return a", name=animal_name)


def createFeedingHabit(feeding_habits, n4j_session):
    cql = "MERGE (fh:feeding_habits{name: $feeding_habits})"
    return n4j_session.run(cql, feeding_habits=feeding_habits)
    pass


def createRelationship(animal, n4j_session):
    cql = """MATCH (a:Animal),(b:feeding_habits) WHERE a.name = $animal_name and b.name = $r_name 
            CREATE (a)-[:Identical_Feeding_habits]->(b)"""
    return n4j_session.run(cql, animal_name=animal['name'], r_name=animal['feeding_habits'])


# ################## MAIN #######################

# Get all Animals
marine_animals = get_all_animals()
# Process all Animals
for m_animal in marine_animals:

    if session is None:
        continue

    x = findAnimalByName(m_animal["name"], session)
    if x.single() is not None:
        continue

    # Create Animal node
    createAnimal(m_animal, session)

    # Create feeding habit node
    createFeedingHabit(m_animal["feeding_habits"], session)

    # Create relationship with animal node and feeding habit node
    createRelationship(m_animal, session)


# Relationship with animal nodes with same habitats and delete self relationships
session.run("MATCH (a:Animal),(b:Animal) WHERE a.habitat = b.habitat and  NOT (a.name = b.name) "
            "create (a)-[r:neighbor]->(b)")

# Remove one edge from two way neighbor relationship
session.run("match (a)-[r1:neighbor]->(b)-[r2:neighbor]->(a)  where ID(r1)>ID(r2) delete r1 return a")

session.close()
print("done")
