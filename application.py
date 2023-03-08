# Importing necessary libraries
import streamlit as st
import requests as r

# Define a title for our project
st.title("EHRI Data Workshop")

########################################      INTRO SECTION      ########################################

# Let's try some basic streamlit commands

# Let's add a header

st.header('Intro to Streamlit')

# Let's now observe the following Python dictionary.

data = {
    'Fruit': ['Apples', 'Oranges', 'Bananas'],
    'Count': [5, 10, 15]
}

# We create a bar chart with the names of the fruits on the x axis and their count on the y axis
st.bar_chart(data, x='Fruit', y='Count')

# Let's visualise our current location on a map
coordinates = {
    'lat': [51.521676],
    'lon': [-0.127801]
}

st.map(coordinates)

##########################      COUNTRY DATA SECTION & GRAPHQL API    ##########################


# Defining the EHRI GraphQL API endpoint
GraphQLEndpoint = 'https://portal.ehri-project-stage.eu/api/graphql'

# Defining an empty dictionary in which we'll later store our data
countries = {
    'name': [],
    'itemCount': [],
    'repos': []
}

# Defining the GraphQL query to retrieve country information
def holders_per_country():
    countries_query = """
        query Countries {
            countries{
                items {
                    name
                    itemCount
                    repositories {
                        items {
                            latitude
                            longitude
                        }
                    }
                }
            }
        }
    """
    # Send the query to the GraphQL endpoint and retrieve the response
    res = r.post(GraphQLEndpoint, headers={"X-Stream": "true"}, json={'query': countries_query})
    # Convert the response to JSON format
    res_json = res.json()
    res_data = res_json['data']['countries']['items']
    # Loop through the results and store each country's details in the dictionary that we created earlier
    for i in res_data:
        countries['name'].append(i['name'])
        countries['itemCount'].append(i['itemCount'])
        countries['repos'].append(i['repositories']['items'])


# Call the function to retrieve and process country data    
holders_per_country()

# Create a Streamlit header
st.header('Archival Institutions per Country')

# Visualise the itemCount per country
st.bar_chart(countries, x='name', y='itemCount')

########################################       MAP OF REPOS        ########################################

# To create a map visualisation of the repositories, we need to convert the data into a format that
# the Streamlit method st.map() can understand, ie. a dict with two keys (lat, lon)
# the values of which will be the long/lat values of each point we want to draw on the map

# We create a dict to store the mapping data
map_data = {
    'lat': [],
    'lon': []
}

# Loop through every list containing the repos of a country and extract the lat/lon values in the format 
# that st.map() expects
for lst in countries['repos']:
    for d in lst:
        if d['latitude'] and d['longitude']:
            map_data["lat"].append(d["latitude"])
            map_data["lon"].append(d["longitude"])

# Create a Streamlit header
st.header('Archival Institutions Map')

# Let's visualise the repositories
st.map(map_data)

####################       ARCHIVAL DESCRIPTIONS AND THE EHRI REST API        ####################

# Create a Streamlit header for the archival descriptions histogram
st.header('Archival Descriptions Histogram')

# Allow the user to enter a search term
query = st.text_input('Enter a search term (Optional)', '')

# Define the payload to retrieve archival description data
payload = {
    'q': query,
    'type': 'DocumentaryUnit',
    'limit':0,
    'facet': 'dates',
}

# Send the query to the EHRI API and retrieve the response
result = r.get('https://portal.ehri-project-stage.eu/api/v1/search?', payload)

# Extract the archival description query metadata (counts per date, etc.)
dcs = result.json()['meta']['facets'][0]['facets']

# Create a dictionary to store the results
docUnits = {
    'count': [],
    'date': [],
    'name': []
}

# Loop through the data and store it in the dictionary
for d in dcs:
    docUnits['count'].append(d['count'])
    docUnits['date'].append(d['value'])
    docUnits['name'].append(d['name'])


# Visualise the count per date
st.bar_chart(docUnits, x='date', y='count')






