# Importing necessary libraries
import streamlit as st
import requests as r
import pandas as pd

# Define a title for our project
st.title("EHRI Data Workshop")

# Defining the EHRI GraphQL API endpoint
GraphQLEndpoint = 'https://portal.ehri-project-stage.eu/api/graphql'

# Defining an empty dictionary in which we'll later save our data
countries = {}

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
    res_json = res.json()
    # Convert the response to JSON format
    res_data = res_json['data']['countries']['items']
    # Loop through the data to create a dictionary of countries and their itemCounts and repository 
    for i in res_data:
        repos = []
        for h in i['repositories']['items']:
            # Check if the repository has longitude and latitude values
            if h['longitude'] and h['latitude']:
                repos.append(h)
        # Create a dictionary entry for the country with its name as the key and itemCount and repo coordinates as values
        countries[i['name']]= {'itemCount':i['itemCount'],'repositories':repos}
        

# Call the function to retrieve and process country data    
holders_per_country()

# Create a Streamlit header
st.header("Repositories per country")

# Convert the country dictionary to a pandas dataframe to help us with the visualisation
df = pd.DataFrame.from_dict(countries,orient="index", columns=['itemCount', 'repositories'])

# Create a bar chart to display the number of repositories per country
st.bar_chart(df,y='itemCount')

# Create a Streamlit header for the map visualization
st.header("Map of Repositories")

# Drop the itemCount column and explode the repositories column into multiple row
geo_df = df.drop(['itemCount'], axis=1).explode('repositories')

# Convert the repository data from JSON format to a pandas dataframe
geo_df = pd.json_normalize(geo_df.repositories).dropna()

# Create a map visualization of the repository locations
st.map(geo_df)

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

# Convert the archival description data to a pandas dataframe for visualisation purposes
docUnit_df = pd.DataFrame(dcs)

# Create a bar chart to display the number of repositories per country
st.bar_chart(docUnit_df, x='value', y='count')

