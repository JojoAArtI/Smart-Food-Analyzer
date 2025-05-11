import streamlit as st
import requests

st.set_page_config(page_title="Smart Food Analyzer", page_icon="🍎")

st.title("🍏 Smart Food Analyzer")
st.markdown("Search for food products using the **OpenFoodFacts API**.")

# Input field for product name
query = st.text_input("🔍 Enter product name (e.g., Nutella, Coca Cola):")

if query:
    with st.spinner("Searching for products..."):
        search_url = f"https://world.openfoodfacts.org/cgi/search.pl?search_terms={query}&search_simple=1&action=process&json=1&page_size=10"
        response = requests.get(search_url)
        results = response.json().get("products", [])

    if results:
        options = {
            f"{p.get('product_name', 'Unnamed')} ({p.get('brands', 'Unknown brand')})": p.get("code")
            for p in results if p.get("product_name")
        }

        selection = st.selectbox("Select a product to view details:", list(options.keys()))

        if selection:
            code = options[selection]
            product_url = f"https://world.openfoodfacts.org/api/v0/product/{code}.json"
            data = requests.get(product_url).json()

            if data.get("status") == 1:
                product = data["product"]
                st.header(product.get("product_name", "Unnamed Product"))

                if product.get("image_front_url"):
                    st.image(product["image_front_url"], width=300)

                nutriments = product.get("nutriments", {})
                st.subheader("🍽 Nutrition Facts (per 100g)")
                st.table({
                    "Energy (kcal)": nutriments.get("energy-kcal_100g", "N/A"),
                    "Fat": nutriments.get("fat_100g", "N/A"),
                    "Saturated Fat": nutriments.get("saturated-fat_100g", "N/A"),
                    "Carbohydrates": nutriments.get("carbohydrates_100g", "N/A"),
                    "Sugars": nutriments.get("sugars_100g", "N/A"),
                    "Proteins": nutriments.get("proteins_100g", "N/A"),
                    "Salt": nutriments.get("salt_100g", "N/A"),
                })

                nutri_score = product.get("nutriscore_grade")
                if nutri_score:
                    st.markdown(f"### 🟩 Nutri-Score: **{nutri_score.upper()}**")
                    if nutri_score in ['a', 'b']:
                        st.success("This product is considered healthy ✅")
                    elif nutri_score in ['d', 'e']:
                        st.warning("This product may be unhealthy ⚠️")
                    else:
                        st.info("Moderate nutrition level.")
            else:
                st.error("⚠️ Failed to fetch detailed product data.")
    else:
        st.error("❌ No matching products found.")
