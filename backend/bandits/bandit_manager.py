# === bandit_manager.py ===
import random
from collections import defaultdict

class MultiArmedBandit:
    def __init__(self, epsilon=0.1):
        self.q_values = defaultdict(lambda: defaultdict(float))
        self.counts = defaultdict(lambda: defaultdict(int))
        self.epsilon = epsilon

    def choose(self, emotion, options):
        if not options:
            return None

        q_vals = self.q_values[emotion]

        if random.random() < self.epsilon:
            return random.choice(options)

        return max(options, key=lambda item: q_vals[item["id"]])

    def choose_multiple(self, emotion, options, k=6):
        if not options:
            return []

        q_vals = self.q_values[emotion]
        sorted_items = sorted(options, key=lambda item: q_vals.get(item["id"], 0.0), reverse=True)

        selected = set()
        results = []
        tries = 0

        while len(results) < min(k, len(options)) and tries < 50:
            if random.random() < self.epsilon:
                candidate = random.choice(options)
            else:
                candidate = sorted_items[len(results)]

            if candidate["id"] not in selected:
                selected.add(candidate["id"])
                results.append(candidate)

            tries += 1

        return results

    def update(self, emotion, item_id, reward):
        count = self.counts[emotion][item_id]
        q = self.q_values[emotion][item_id]
        self.counts[emotion][item_id] += 1
        self.q_values[emotion][item_id] += (reward - q) / (count + 1)
