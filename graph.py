from utils import *
import networkx as nx
from db import session


# not to use this
try:
    result = session.run("MATCH (a:Animal) WHERE a.conservtnStatus =~ '.*Endangered.*' return a")

    graph = result.get_graph()
    plt.figure(figsize=(6,4));
    nx.draw(g)
except Exception as e:
    print(e)
    print("DB Connection Failed")


