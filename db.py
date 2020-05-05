from neo4j import GraphDatabase, basic_auth

session = None
dbUrl = 'bolt://localhost'
dbUsername = 'neo4j'
dbPassword = 'root'

try:
    driver = GraphDatabase.driver(dbUrl, auth=basic_auth(dbUsername, dbPassword))
    session = driver.session()
except Exception as e:
    print(e)
    print("DB Connection Failed")