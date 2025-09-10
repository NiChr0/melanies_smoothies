# Import python packages
import streamlit as st
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col
import requests
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
st.text(smoothiefroot_response.json())

# Write directly to the app
st.title(f":cup_with_straw: Customize Your Smoothie!:cup_with_straw:")
st.write(f"Choose the fruits you want in your custom Smoothie!")

# Create Snowflake session for Streamlit
@st.cache_resource
def create_session():
    session = Session.builder.configs(st.secrets["connections"]["snowflake"]).create()
    # Explicitly set the warehouse
    session.sql("USE WAREHOUSE COMPUTE_WH").collect()
    return session

session = create_session()

name_on_order = st.text_input("Name on Smoothie")
st.write("The name on your Smoothie will be:", name_on_order)

my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    my_dataframe,
    max_selections=5
)

# Initialize ingredients_string outside the conditional
ingredients_string = ''

if ingredients_list:
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
            values ('""" + ingredients_string + """','""" + name_on_order + """')"""

time_to_insert = st.button('Submit Order')
if time_to_insert:
    if ingredients_list and name_on_order:
        session.sql(my_insert_stmt).collect()
        st.success(f"Your Smoothie is ordered {name_on_order}!", icon="✅")
    else:
        st.error("Please select ingredients and enter a name!")
