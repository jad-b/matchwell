import networkx as nx


TEST_EDGES = (
    ('A', 'B'),
    ('A', 'C'),
    ('A', 'D'),
    ('B', 'E'),
    ('B', 'F'),
    ('D', 'G'),
    ('D', 'H'),
    ('D', 'I'),
)

TEST_TREE = nx.DiGraph(TEST_EDGES)
