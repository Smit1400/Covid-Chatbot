import plotly.graph_objects as go
import pandas as pd

df = pd.read_csv("time_series_covid_19_confirmed.csv")
df = df.rename(columns= {"Country/Region" : "Country", "Province/State": "Province"})

total_list = df.groupby('Country')['4/13/20'].sum().tolist()

country_list = df["Country"].tolist()
country_set = set(country_list)
country_list = list(country_set)
country_list.sort()

new_df = pd.DataFrame(list(zip(country_list, total_list)), 
               columns =['Country', 'Total_Cases'])

colors = ["#F9F9F5", "#FAFAE6", "#FCFCCB", "#FCFCAE",  "#FCF1AE", "#FCEA7D", "#FCD97D",
          "#FCCE7D", "#FCC07D", "#FEB562", "#F9A648",  "#F98E48", "#FD8739", "#FE7519",
          "#FE5E19", "#FA520A", "#FA2B0A", "#9B1803",  "#861604", "#651104", "#570303",]


fig = go.Figure(data=go.Choropleth(
    locationmode = "country names",
    locations = new_df['Country'],
    z = new_df['Total_Cases'],
    text = new_df['Country'],
    colorscale = colors,
    autocolorscale=False,
    reversescale=False,
    colorbar_title = 'Reported Covid-19 Cases',
))

fig.update_layout(
    title_text='Reported Covid-19 Cases',
    geo=dict(
        showcoastlines=True,
    ),
)

fig.write_html('first_figure.html', auto_open=True)

print("Hello")