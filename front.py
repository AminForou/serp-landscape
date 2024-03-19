import streamlit as st
from backend import fetch_and_save_serp_results
import os
import json
from datetime import datetime
from bokeh.plotting import figure
from bokeh.models import HoverTool, ColumnDataSource, SingleIntervalTicker
import glob




# Streamlit frontend interface
api_key = "31ad7d714d83de34f5bab5656666ccb1e3117b2bfdcacf2bde109a26cc2bda5c"  # Keep your API key here securely

st.set_page_config(page_title="SERP Landscapre Analysis",layout="wide")
st.title('SERP Landscape Analysis')
# Sidebar for selecting existing result files
st.sidebar.title("Existing Results")
results_dir = '/Users/aminforout/Documents/PycharmProjects/serp-landscape/results/'
files = sorted(glob.glob(f'{results_dir}serp_results_*.json'), key=os.path.getmtime, reverse=True)
file_names_to_paths = {os.path.basename(file): file for file in files}
selected_file_name = st.sidebar.selectbox("Select a result file", list(file_names_to_paths.keys()))
selected_file = file_names_to_paths[selected_file_name]
# Main UI for new search
keywords_input = st.text_input("Enter one or more keywords separated by commas:")
location = st.selectbox("Select a location:", ("USA", "Canada", "Britain"))
num_results = st.number_input("Enter the number of desired results:", min_value=1, value=10, step=1)
user_domains_input = st.text_input("Enter one or more domains separated by commas:")

def load_results(file_path):
    with open(file_path) as file:
        return json.load(file)

# Function to display chart
def display_chart(data):
    keywords = data['keywords']
    user_domains = data['user_domains']
    results = data['results']

    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]
    domain_colors = {domain: colors[i % len(colors)] for i, domain in enumerate(user_domains)}

    source_data = {'x': [], 'y': [], 'color': [], 'domain': [], 'keyword': [], 'position': []}



    for keyword in keywords:
        for result in results[keyword]:
            parsed_domain = result['URL'].split('/')[2]
            source_data['x'].append(keywords.index(keyword))
            source_data['y'].append(result['Rank'])
            source_data['color'].append(domain_colors.get(parsed_domain, 'lightgray'))
            source_data['domain'].append(parsed_domain)
            source_data['keyword'].append(keyword)
            source_data['position'].append(result['Rank'])
    max_position = max(source_data['y'])
    source = ColumnDataSource(data=source_data)

    # Right after calculating max_position and before creating the ColumnDataSource

    col1, col2,col3 = st.columns(3)  # Create two columns
    with col1:
      position_slider = st.slider("Select position range", 1, max_position, max_position, key="position_slider")
    p = figure(title="Domain Positions by Keyword",
               x_axis_label='Keywords', y_axis_label='Positions',
               width=1000, height=position_slider * 35, y_range=(position_slider + 0.5, 0.5))
    p.yaxis.ticker = SingleIntervalTicker(interval=1)
    p.yaxis.minor_tick_line_color = None

    p.circle('x', 'y', source=source, color='color', fill_alpha=0.2, size=10)

    hover = HoverTool()
    hover.tooltips = """
        <div>
            <div><strong>Domain:</strong>@domain</div>
            <div><strong>Position: </strong>@position</div>
            <div><strong>Keyword: </strong>@keyword</div>
        </div>
    """
    p.add_tools(hover)
    p.xaxis.ticker = list(range(len(keywords)))
    p.xaxis.major_label_orientation = "vertical"
    p.xaxis.major_label_overrides = {i: keyword for i, keyword in enumerate(keywords)}
    st.bokeh_chart(p, use_container_width=True)

    # Immediately after displaying the chart with st.bokeh_chart
# This section recalculates and updates total results and domain frequencies based on the slider

# Recalculate top 3 most repeated domains based on the updated domain_frequency

    st.markdown('#')
    filtered_positions = [pos for pos in source_data['y'] if pos <= position_slider]
    filtered_domains = [source_data['domain'][i] for i, pos in enumerate(source_data['y']) if pos <= position_slider]

    # Calculate the total number of results within the selected range
    total_results_within_range = len(filtered_positions)

    # Calculate domain frequencies within the selected range
    domain_frequency_within_range = {domain: filtered_domains.count(domain) for domain in set(filtered_domains)}

    # Find the top 3 most repeated domains within the selected range
    top_3_domains_within_range = sorted(domain_frequency_within_range.items(), key=lambda x: x[1], reverse=True)[:3]

    # Display updated total results and domain frequencies using columns
    col1, col2 = st.columns(2)

    with col1:
        st.write(f"Total results within range: {total_results_within_range}")
        st.write("Domain Frequencies within range:")
        for domain, frequency in domain_frequency_within_range.items():
            if domain in user_domains:  # Highlight user-specified domains
                color = domain_colors.get(domain, 'lightgray')  # Fetch color for the domain
                st.markdown(f'<span style="color: {color};">{domain}:<strong> {frequency} times</strong></span>', unsafe_allow_html=True)

    with col2:
        st.write("Top 3 Most Repeated Domains within range:")
        for domain, frequency in top_3_domains_within_range:
            color = domain_colors.get(domain, 'lightgray') if domain in domain_colors else 'lightgray'
            st.markdown(f'<span style="color: {color};">{domain}: {frequency} times</span>', unsafe_allow_html=True)




# Handling new search
if st.button('Fetch SERP Results'):
    now = datetime.now()
    formatted_now = now.strftime("%H-%M-%d-%m")
    output_file_location = f'{results_dir}serp_results_{formatted_now}.json'
    keywords = [keyword.strip() for keyword in keywords_input.split(',')]
    user_domains = [domain.strip() for domain in user_domains_input.split(',') if domain]
    location_map = {"USA": "United States", "Canada": "Canada", "Britain": "United Kingdom"}
    fetch_and_save_serp_results(keywords, location_map[location], num_results, api_key, user_domains, output_file_location)
    data = load_results(output_file_location)
    display_chart(data)

# Handling file selection
elif selected_file:
    data = load_results(selected_file)
    display_chart(data)

def load_results(file_path):
    with open(file_path) as file:
        return json.load(file)
