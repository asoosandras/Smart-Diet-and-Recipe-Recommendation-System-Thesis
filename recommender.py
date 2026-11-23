"""
Smart Diet recipe recommender: the two-stage filtering algorithm (Chapter 3.4).

Used by recommender.ipynb (evaluation) and app.py (Streamlit prototype). The data files it reads are
produced by recommender.ipynb into the folder app_data/.

    Stage 1  diet filters (hard constraints)   calorie limit, vegetarian, high-protein
    Stage 2  pantry matching                   which recipe ingredients does the user have?
             + substitution network            a missing ingredient counts as covered if the user has a
                                               substitute that at least 5 reviewers used (Chapter 3.3)
    Ranking                                    fewest missing -> fewest swaps -> uses most of the pantry
                                               -> best weighted rating
"""
from pathlib import Path

import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).parent / "app_data"
HIGH_PROTEIN_G = 25          # decision: "high-protein" = at least 25 g protein per serving
MAX_SWAPS = 2                # decision: a recipe with more than 2 swaps is no longer the same dish
                             # decision: an ingredient named in the recipe title is never swapped


class Recommender:
    def __init__(self, data_dir=DATA_DIR):
        d = Path(data_dir)
        self.recipes = pd.read_parquet(d / "recipes.parquet").reset_index(drop=True)
        items = pd.read_csv(d / "pantry_items.csv", sep=";", encoding="utf-8-sig")
        subs = pd.read_csv(d / "substitutions.csv", sep=";", encoding="utf-8-sig")
        names = pd.read_csv(d / "ingredient_names.csv", sep=";", encoding="utf-8-sig")

        self.name = dict(zip(names["ingredient_id"], names["name"]))
        self.is_meat = np.zeros(int(names["ingredient_id"].max()) + 1, dtype=bool)
        self.is_meat[names.loc[names["meat"], "ingredient_id"].to_numpy()] = True

        # pantry item -> canonical ingredient ids it covers; category of each item; staples
        self.item_ids = items.groupby("pantry_item")["ingredient_id"].apply(list).to_dict()
        first = items.drop_duplicates("pantry_item").set_index("pantry_item")
        self.item_category = first["category"].to_dict()
        self.staple_items = sorted(first.index[first["staple"]].tolist())
        self.staple_ids = items.loc[items["staple"], "ingredient_id"].to_numpy()
        self.item_of_id = dict(zip(items["ingredient_id"], items["pantry_item"]))

        # long format (one row per recipe-ingredient pair) for fast counting with np.bincount
        lens = self.recipes["ingredient_ids"].str.len().to_numpy()
        self.pair_recipe = np.repeat(np.arange(len(self.recipes)), lens)
        self.pair_ing = np.concatenate(self.recipes["ingredient_ids"].to_numpy()).astype(int)
        self.n_ids = max(int(self.pair_ing.max()), int(names["ingredient_id"].max())) + 1

        # main ingredients: an ingredient named in the recipe title (e.g. "potato" in "potato stew") is never swapped,
        # because replacing it would change the dish itself
        name_arr = np.array([self.name.get(i, "") for i in range(self.n_ids)], dtype=object)
        titles = self.recipes["name"].str.lower().to_numpy()[self.pair_recipe]
        self.pair_in_title = np.fromiter((bool(n) and n in t for n, t in zip(name_arr[self.pair_ing], titles)),
                                         dtype=bool, count=len(titles))

        # substitution edges a -> b, strongest first
        # fully specified order (ties broken by rating, then by id) so the chosen tip is the same on every machine
        self.subs = subs.sort_values(["support", "mean_rating", "a_id", "b_id"],
                                     ascending=[False, False, True, True], kind="mergesort")
        self.subs_by_a = {a: g for a, g in self.subs.groupby("a_id")}

    # ------------------------------------------------------------------ helpers
    def pantry_ids(self, pantry_items, assume_staples=True):
        """Canonical ingredient ids the user has (the pantry items expanded to their ingredient groups)."""
        have = np.zeros(self.n_ids, dtype=bool)
        for item in pantry_items:
            have[self.item_ids.get(item, [])] = True
        if assume_staples:
            have[self.staple_ids] = True
        return have

    def _substitutable(self, have, vegetarian):
        """For every ingredient the user does NOT have: is there a network substitute the user DOES have?"""
        ok = np.zeros(self.n_ids, dtype=bool)
        e = self.subs
        usable = have[e["b_id"].to_numpy()] & ~have[e["a_id"].to_numpy()]
        if vegetarian:                                  # never suggest meat as a substitute
            usable &= ~self.is_meat[e["b_id"].to_numpy()]
        ok[e.loc[usable, "a_id"].to_numpy()] = True
        return ok

    # ------------------------------------------------------------------ stage 1
    def diet_mask(self, max_calories=None, vegetarian=False, high_protein=False):
        r = self.recipes
        m = np.ones(len(r), dtype=bool)
        if max_calories:
            m &= (r["calories"] <= max_calories).to_numpy()
        if vegetarian:
            m &= r["vegetarian"].to_numpy()
        if high_protein:
            m &= (r["protein_g"] >= HIGH_PROTEIN_G).to_numpy()
        return m

    # ------------------------------------------------------------------ stage 2
    def match_counts(self, pantry_items, use_substitutions=True, assume_staples=True, vegetarian=False):
        """Per recipe: number of (non-staple) ingredients the user has / can swap / is missing."""
        have = self.pantry_ids(pantry_items, assume_staples)
        staple = np.zeros(self.n_ids, dtype=bool)
        staple[self.staple_ids] = True
        counted = ~staple[self.pair_ing]                 # staples are not counted in the coverage
        n = len(self.recipes)
        n_ing = np.bincount(self.pair_recipe, weights=counted, minlength=n)
        n_have = np.bincount(self.pair_recipe, weights=counted & have[self.pair_ing], minlength=n)
        if use_substitutions:
            sub = self._substitutable(have, vegetarian)
            n_swap = np.bincount(self.pair_recipe, weights=counted & sub[self.pair_ing] & ~self.pair_in_title,
                                 minlength=n)
        else:
            n_swap = np.zeros(n)
        n_missing = n_ing - n_have - n_swap
        if not assume_staples:                           # then staples the user lacks are missing too
            n_missing += np.bincount(self.pair_recipe, weights=~counted & ~have[self.pair_ing], minlength=n)
        return n_ing.astype(int), n_have.astype(int), n_swap.astype(int), n_missing.astype(int)

    def explain(self, recipe_row, have, vegetarian=False, use_substitutions=True):
        """Swap tips and missing ingredients of one recipe (for display)."""
        swaps, missing = [], []
        title = str(recipe_row["name"]).lower()
        for i in recipe_row["ingredient_ids"]:
            if have[i]:
                continue
            tip = None
            main = self.name.get(i, "") and self.name.get(i, "") in title     # main ingredient: never swapped
            g = self.subs_by_a.get(i) if use_substitutions and not main else None
            if g is not None:
                g = g[have[g["b_id"].to_numpy()]]
                if vegetarian:
                    g = g[~self.is_meat[g["b_id"].to_numpy()]]
                if len(g):
                    b = g.iloc[0]
                    tip = {"missing": self.name.get(i, str(i)), "use": self.name.get(int(b["b_id"])),
                           "reviews": int(b["support"]), "rating": round(float(b["mean_rating"]), 2)}
            if tip:
                swaps.append(tip)
            else:
                missing.append(self.name.get(i, str(i)))
        return swaps, missing

    # ------------------------------------------------------------------ full pipeline
    def recommend(self, pantry_items, max_calories=None, vegetarian=False, high_protein=False,
                  max_missing=0, use_substitutions=True, assume_staples=True, top_n=10, min_have=1,
                  max_swaps=MAX_SWAPS, min_swaps=0):
        diet = self.diet_mask(max_calories, vegetarian, high_protein)
        n_ing, n_have, n_swap, n_missing = self.match_counts(pantry_items, use_substitutions,
                                                             assume_staples, vegetarian)
        ok = (diet & (n_ing > 0) & (n_missing <= max_missing) & (n_have >= min_have)
              & (n_swap <= max_swaps) & (n_swap >= min_swaps))
        cand = self.recipes.loc[ok, ["id", "name", "minutes", "calories", "protein_g", "vegetarian",
                                     "weighted_rating", "n_ratings", "ingredient_ids"]].copy()
        cand["n_ingredients"] = n_ing[ok]
        cand["n_have"] = n_have[ok]
        cand["n_swaps"] = n_swap[ok]
        cand["n_missing"] = n_missing[ok]
        cand["coverage"] = (cand["n_have"] / cand["n_ingredients"]).round(2)
        # the recipe id is the last tie-breaker, so equal scores always come out in the same order
        cand = cand.sort_values(["n_missing", "n_swaps", "n_have", "weighted_rating", "n_ratings", "id"],
                                ascending=[True, True, False, False, False, True], kind="mergesort")
        top = cand.head(top_n).copy()
        have = self.pantry_ids(pantry_items, assume_staples)
        expl = [self.explain(r, have, vegetarian, use_substitutions) for _, r in top.iterrows()]
        top["swap_tips"] = [e[0] for e in expl]
        top["missing"] = [e[1] for e in expl]
        return top.drop(columns="ingredient_ids").reset_index(drop=True), len(cand)

    def cookable(self, pantry_items, max_calories=None, vegetarian=False, high_protein=False,
                 assume_staples=True, max_swaps=MAX_SWAPS, min_have=1):
        """Boolean masks used by the evaluation: diet ok, cookable with exact matching, cookable with swaps."""
        diet = self.diet_mask(max_calories, vegetarian, high_protein)
        n_ing, have_e, _, miss_e = self.match_counts(pantry_items, False, assume_staples, vegetarian)
        _, have_s, swap_s, miss_s = self.match_counts(pantry_items, True, assume_staples, vegetarian)
        valid = (n_ing > 0) & (have_e >= min_have)
        return {"valid": valid, "diet": diet, "missing_exact": miss_e,
                "exact": valid & diet & (miss_e == 0),
                "with_subs": valid & diet & (miss_s == 0) & (swap_s <= max_swaps)}

    def funnel(self, pantry_items, near_missing=2, **diet):
        """How many recipes survive each step (for the funnel figure)."""
        c = self.cookable(pantry_items, **diet)
        return {
            "All recipes": int((self.recipes["ingredient_ids"].str.len() > 0).sum()),
            "Diet filters passed": int(c["diet"].sum()),
            f"At most {near_missing} ingredients missing": int((c["valid"] & c["diet"]
                                                                 & (c["missing_exact"] <= near_missing)).sum()),
            "Cookable now (exact match)": int(c["exact"].sum()),
            "Cookable now (with substitutions)": int(c["with_subs"].sum()),
        }
