from collections import deque
from typing import List, Tuple, Dict, Set
import numpy as np

class GraphAlgorithms:
    """Implementation of BFS, DFS, and Union-Find for news graph"""
    
    def __init__(self, graph):
        self.graph = graph
        self.union_find = None
    
    # ============ BFS (Breadth-First Search) ============
    def bfs_find_similar(self, start_node: int, max_depth: int = 3, max_results: int = 10) -> List[Tuple[int, float]]:
        """
        BFS to find similar news articles
        Returns list of (node_id, similarity_weight)
        """
        if self.graph is None or self.graph.number_of_nodes() == 0:
            return []
        
        visited = set()
        queue = deque([(start_node, 0, 1.0)])  # (node, depth, similarity)
        similar_articles = []
        
        while queue and len(similar_articles) < max_results:
            node, depth, similarity = queue.popleft()
            
            if node in visited:
                continue
            
            visited.add(node)
            
            if node != start_node:
                similar_articles.append((node, similarity))
            
            if depth < max_depth:
                for neighbor in self.graph.neighbors(node):
                    if neighbor not in visited:
                        edge_weight = self.graph[node][neighbor].get('weight', 0.5)
                        new_similarity = similarity * edge_weight
                        queue.append((neighbor, depth + 1, new_similarity))
        
        similar_articles.sort(key=lambda x: x[1], reverse=True)
        return similar_articles
    
    # ============ DFS (Depth-First Search) ============
    def dfs_explore_cluster(self, start_node: int, max_nodes: int = 50) -> List[int]:
        """
        DFS to explore entire connected component/cluster
        Returns list of all nodes in the cluster
        """
        if self.graph is None or self.graph.number_of_nodes() == 0:
            return []
        
        visited = set()
        cluster = []
        
        def dfs(node):
            if node in visited or len(cluster) >= max_nodes:
                return
            visited.add(node)
            cluster.append(node)
            
            for neighbor in self.graph.neighbors(node):
                if neighbor not in visited:
                    dfs(neighbor)
        
        dfs(start_node)
        return cluster
    
    def dfs_find_path(self, start_node: int, end_node: int) -> List[int]:
        """
        DFS to find path between two articles
        Returns list of nodes representing the path
        """
        if self.graph is None:
            return []
        
        visited = set()
        path = []
        
        def dfs_path(current, target, path_so_far):
            if current in visited:
                return False
            visited.add(current)
            path_so_far.append(current)
            
            if current == target:
                path.extend(path_so_far)
                return True
            
            for neighbor in self.graph.neighbors(current):
                if dfs_path(neighbor, target, path_so_far):
                    return True
            
            path_so_far.pop()
            return False
        
        dfs_path(start_node, end_node, [])
        return path
    
    # ============ UNION-FIND (Disjoint Set Union) ============
    class UnionFind:
        """Union-Find data structure for connected components"""
        def __init__(self, n):
            self.parent = list(range(n))
            self.rank = [0] * n
            self.size = [1] * n
        
        def find(self, x):
            if self.parent[x] != x:
                self.parent[x] = self.find(self.parent[x])
            return self.parent[x]
        
        def union(self, x, y):
            root_x = self.find(x)
            root_y = self.find(y)
            
            if root_x != root_y:
                if self.rank[root_x] < self.rank[root_y]:
                    self.parent[root_x] = root_y
                    self.size[root_y] += self.size[root_x]
                elif self.rank[root_x] > self.rank[root_y]:
                    self.parent[root_y] = root_x
                    self.size[root_x] += self.size[root_y]
                else:
                    self.parent[root_y] = root_x
                    self.rank[root_x] += 1
                    self.size[root_x] += self.size[root_y]
        
        def get_component_size(self, x):
            return self.size[self.find(x)]
        
        def get_all_components(self):
            components = {}
            for i in range(len(self.parent)):
                root = self.find(i)
                if root not in components:
                    components[root] = []
                components[root].append(i)
            return components
    
    def build_union_find(self):
        """Build Union-Find structure from graph edges"""
        if self.graph is None or self.graph.number_of_nodes() == 0:
            return None
        
        n = self.graph.number_of_nodes()
        self.union_find = self.UnionFind(n)
        
        for edge in self.graph.edges():
            self.union_find.union(edge[0], edge[1])
        
        return self.union_find
    
    def find_connected_components(self) -> Dict[int, List[int]]:
        """Find all connected components using Union-Find"""
        if self.union_find is None:
            self.build_union_find()
        
        return self.union_find.get_all_components()
    
    # ============ HYBRID PREDICTION WITH GRAPH ============
    def predict_with_graph_voting(self, article_id: int, depth: int = 2) -> Tuple[int, float]:
        """
        Use graph voting to predict if article is fake or true
        Uses BFS to find neighbors and votes based on their labels
        """
        similar = self.bfs_find_similar(article_id, max_depth=depth)
        
        if not similar:
            return None, 0.0
        
        votes = {0: 0, 1: 0}  # 0: Fake, 1: True
        total_weight = 0
        
        for node_id, similarity in similar:
            if node_id in self.graph.nodes and 'label' in self.graph.nodes[node_id]:
                label = self.graph.nodes[node_id]['label']
                votes[label] += similarity
                total_weight += similarity
        
        if total_weight == 0:
            return None, 0.0
        
        if votes[1] > votes[0]:
            confidence = votes[1] / total_weight
            return 1, confidence
        else:
            confidence = votes[0] / total_weight
            return 0, confidence
    
    def get_cluster_stats(self, node_id: int) -> Dict:
        """Get statistics about the cluster containing the node"""
        cluster = self.dfs_explore_cluster(node_id, max_nodes=1000)
        
        true_count = 0
        fake_count = 0
        
        for n in cluster:
            if n in self.graph.nodes and 'label' in self.graph.nodes[n]:
                if self.graph.nodes[n]['label'] == 1:
                    true_count += 1
                else:
                    fake_count += 1
        
        return {
            "cluster_size": len(cluster),
            "true_articles": true_count,
            "fake_articles": fake_count,
            "true_percentage": (true_count / len(cluster) * 100) if cluster else 0
        }