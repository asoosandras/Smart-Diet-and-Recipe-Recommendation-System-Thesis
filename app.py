"""
Smart Diet: Streamlit pilot of the recommender (Chapter 3.4.3).

Start:   venv/Scripts/streamlit run app.py
Needs:   the folder app_data/ (created by recommender.ipynb) and recommender.py
"""
import pandas as pd
import streamlit as st

from recommender import Recommender, HIGH_PROTEIN_G, MAX_SWAPS

st.set_page_config(page_title="Smart Diet pilot", layout="wide")


@st.cache_resource(show_spinner="Loading recipes ...")
def load():
    return Recommender()


rs = load()

CATEGORY_ORDER = ["Vegetables", "Fruits", "Meat & fish", "Eggs & dairy", "Grains, pasta & bread", "Legumes & tofu",
                  "Nuts & seeds", "Herbs & spices", "Baking", "Sweeteners", "Oils & fats", "Sauces & condiments",
                  "Canned goods & broths", "Drinks & alcohol"]
items_by_cat = {}
for item, cat in rs.item_category.items():
    if item not in rs.staple_items:
        items_by_cat.setdefault(cat, []).append(item)
categories = [c for c in CATEGORY_ORDER if c in items_by_cat] + \
             sorted(c for c in items_by_cat if c not in CATEGORY_ORDER)

EXAMPLES = {
    "Student (basic pantry)": ["egg", "milk", "butter", "flour", "sugar", "onion", "garlic", "tomato", "pasta",
                               "rice", "cheddar", "potato"],
    "Vegetarian": ["onion", "garlic", "tomato", "bell pepper", "spinach", "chickpea", "beans", "rice", "pasta",
                   "feta", "yogurt", "lemon", "olive oil", "mushroom", "carrot", "egg", "cumin"],
    "Gym-goer": ["chicken", "egg", "rice", "broccoli", "yogurt", "oats", "banana", "peanut butter", "tuna",
                 "cottage cheese", "spinach", "garlic", "olive oil", "sweet potato", "milk", "soy sauce"],
}

# result views: (label, use substitutions, min swaps, max swaps)
VIEWS = {
    "All results": (True, 0, MAX_SWAPS),
    "Only recipes made possible by a substitution": (True, 1, MAX_SWAPS),
    "Exact matches only (no substitution)": (False, 0, 0),
}


def set_pantry(items):
    for c in categories:
        st.session_state[f"cat_{c}"] = [i for i in items if rs.item_category.get(i) == c]


def clear_pantry():
    set_pantry([])


# ------------------------------------------------------------------ sidebar: settings
with st.sidebar:
    st.subheader("Diet filters")
    use_cal = st.checkbox("Calorie limit per serving")
    max_cal = st.slider("Max kcal per serving", 150, 1200, 600, 50, disabled=not use_cal)
    vegetarian = st.checkbox("Vegetarian")
    high_protein = st.checkbox(f"High-protein (at least {HIGH_PROTEIN_G} g per serving)")

    st.subheader("Matching")
    staples = st.toggle("Assume staples: " + ", ".join(rs.staple_items), value=True)
    max_missing = st.radio("Ingredients I am willing to buy", [0, 1, 2], horizontal=True)
    top_n = st.slider("Number of results", 5, 30, 10, 5)

    st.subheader("Example pantries")
    ex = st.selectbox("Example", ["–"] + list(EXAMPLES), label_visibility="collapsed")
    c1, c2 = st.columns(2)
    c1.button("Load", on_click=lambda: set_pantry(EXAMPLES.get(ex, [])), disabled=ex == "–",
              width="stretch")
    c2.button("Clear", on_click=clear_pantry, width="stretch")

# ------------------------------------------------------------------ 1. pantry
st.title("Smart Diet – recipe recommender")
st.caption("Pilot prototype for the thesis. Data: Food.com recipes and reviews. "
           "Step 1: diet filters. Step 2: pantry matching, with substitutions taken from reviews.")

st.subheader("1. Pantry")
cols = st.columns(3)
for k, cat in enumerate(categories):
    with cols[k % 3].expander(f"{cat} ({len(items_by_cat[cat])})"):
        st.multiselect(cat, sorted(items_by_cat[cat]), key=f"cat_{cat}", label_visibility="collapsed",
                       placeholder="Type to search")

pantry = sorted({i for c in categories for i in st.session_state.get(f"cat_{c}", [])})
if not pantry:
    st.info("The pantry is empty. Select ingredients above, or load an example pantry in the sidebar.")
    st.stop()
st.markdown(f"**Selected ({len(pantry)}):** " + ", ".join(pantry))

# ------------------------------------------------------------------ 2. overview: exact vs substitutions
diet = dict(max_calories=max_cal if use_cal else None, vegetarian=vegetarian, high_protein=high_protein)
c = rs.cookable(pantry, assume_staples=staples, **diet)
n_diet, n_exact, n_subs = int(c["diet"].sum()), int(c["exact"].sum()), int(c["with_subs"].sum())

st.subheader("2. Overview")
m1, m2, m3 = st.columns(3)
m1.metric("Recipes matching the diet filters", f"{n_diet:,}")
m2.metric("Cookable now, exact match", f"{n_exact:,}")
m3.metric("Cookable now, with substitutions", f"{n_subs:,}",
          delta=f"+{n_subs - n_exact:,} through substitutions", delta_color="off")

# ------------------------------------------------------------------ 3. results
st.subheader("3. Recommendations")
view = st.radio("Show", list(VIEWS), horizontal=True, label_visibility="collapsed")
use_subs, min_swaps, max_swaps = VIEWS[view]
top, n_found = rs.recommend(pantry, max_missing=max_missing, use_substitutions=use_subs, assume_staples=staples,
                            top_n=top_n, max_swaps=max_swaps, min_swaps=min_swaps, **diet)

if top.empty:
    st.warning("No recipe found. Allow 1–2 ingredients to buy, change the view, or add ingredients.")
    st.stop()
st.caption(f"{n_found:,} recipes fit these settings; the best {len(top)} are shown.")
if view == "All results" and not top["n_swaps"].any() and n_subs > n_exact:
    st.info(f"Exact matches rank first, so no substitution appears in this list. "
            f"{n_subs - n_exact:,} further recipes are cookable with a substitution: "
            f"choose **Only recipes made possible by a substitution** above to see them.")

# summary of the substitutions used in the shown results
swap_rows = [(t["missing"], t["use"], t["reviews"], t["rating"]) for tips in top["swap_tips"] for t in tips]
if swap_rows:
    s = pd.DataFrame(swap_rows, columns=["Missing ingredient", "Substitute from your pantry", "Reviews", "Avg. rating"])
    s = (s.groupby(["Missing ingredient", "Substitute from your pantry", "Reviews", "Avg. rating"], as_index=False)
           .size().rename(columns={"size": "Used in shown recipes"})
           .sort_values(["Used in shown recipes", "Reviews"], ascending=False, kind="mergesort"))
    with st.container(border=True):
        st.markdown("**Substitutions used in these results**")
        st.caption("Each substitution was made by reviewers of Food.com recipes. "
                   "'Reviews' = how many reviews report this swap.")
        st.dataframe(s, hide_index=True, width="stretch")

details = rs.recipes.set_index("id")
for _, r in top.iterrows():
    with st.container(border=True):
        left, right = st.columns([3, 1])
        if r["n_swaps"]:
            status = f"Cookable with {r['n_swaps']} substitution{'s' if r['n_swaps'] > 1 else ''}"
        elif r["n_missing"]:
            status = f"{r['n_missing']} ingredient{'s' if r['n_missing'] > 1 else ''} to buy"
        else:
            status = "Exact match"
        if r["n_swaps"] and r["n_missing"]:
            status += f", {r['n_missing']} to buy"
        left.markdown(f"**{r['name']}**  \n:gray[{status}]")
        facts = [f"{r['calories']:.0f} kcal", f"{r['protein_g']:.0f} g protein", f"{r['minutes']} min",
                 f"rating {r['weighted_rating']:.2f} ({r['n_ratings']} ratings)"]
        if r["vegetarian"]:
            facts.append("vegetarian")
        left.caption(" · ".join(facts))
        right.progress(float(min(r["coverage"], 1.0)),
                       text=f"{r['n_have']} of {r['n_ingredients']} ingredients in pantry")

        for t in r["swap_tips"]:
            st.info(f"**Substitution:** replace **{t['missing']}** with **{t['use']}** "
                    f"(reported in {t['reviews']} reviews, avg. rating {t['rating']})")
        if r["missing"]:
            st.markdown("**To buy:** " + ", ".join(r["missing"]))
        d = details.loc[r["id"]]
        with st.expander("Ingredients and steps"):
            a, b = st.columns([1, 2])
            a.markdown("\n".join(f"- {i}" for i in d["ingredients"]))
            b.markdown("\n".join(f"{k + 1}. {s}" for k, s in enumerate(d["steps"])))

st.caption(f"Ranking: fewest missing ingredients, then fewest substitutions (max {MAX_SWAPS}), then most pantry "
           "items used, then weighted rating. Calories and protein refer to the original recipe; "
           "a substitution is not recalculated.")
