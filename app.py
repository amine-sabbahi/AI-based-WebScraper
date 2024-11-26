import streamlit as st
from streamlit_tags import st_tags_sidebar
import pandas as pd
import json
from datetime import datetime
from scraper import fetch_html_selenium, save_raw_data, format_data, save_formatted_data,html_to_markdown_with_readability, create_dynamic_listing_model,create_listings_container_model

from configurations import AI_MODELS


# Initialize Streamlit app
st.set_page_config(page_title="Universal Web Scraper")
st.title("Universal Web Scraper 🦑")

# Sidebar components
st.sidebar.title("Web Scraper Settings")
model_selection = st.sidebar.selectbox("Select Model", options=list(AI_MODELS.keys()), index=0)
url_input = st.sidebar.text_input("Enter URL")


# Tags input specifically in the sidebar
tags = st.sidebar.empty()  # Create an empty placeholder in the sidebar
tags = st_tags_sidebar(
    label='Enter Fields to Extract:',
    text='Press enter to add a field',
    value=[],  # Default values if any
    suggestions=[],  # You can still offer suggestions, or keep it empty for complete freedom
    maxtags=-1,  # Set to -1 for unlimited tags
    key='tags_input'
)


st.sidebar.markdown("---")

# Process tags into a list
fields = tags

# Initialize variables to store token and cost information
input_tokens = output_tokens = total_cost = 0  # Default values

# Buttons to trigger scraping
# Define the scraping function
def perform_scrape():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    raw_html = fetch_html_selenium(url_input)
    markdown = html_to_markdown_with_readability(raw_html)
    save_raw_data(markdown, timestamp)
    DynamicListingModel = create_dynamic_listing_model(fields)
    DynamicListingsContainer = create_listings_container_model(DynamicListingModel)
    formatted_data, tokens_count = format_data(markdown, DynamicListingsContainer,DynamicListingModel,model_selection)
    df = save_formatted_data(formatted_data, timestamp)

    return df, formatted_data, markdown, tokens_count, timestamp

# Handling button press for scraping
if 'perform_scrape' not in st.session_state:
    st.session_state['perform_scrape'] = False

if st.sidebar.button("Scrape"):
    with st.spinner('Please wait... Data is being scraped.'):
        st.session_state['results'] = perform_scrape()
        st.session_state['perform_scrape'] = True

if st.session_state.get('perform_scrape'):
    df, formatted_data, markdown, tokens_count, timestamp = st.session_state['results']
    # Display the DataFrame and other data
    st.write("Scraped Data:", df)
    st.sidebar.markdown("## Token Usage")
    st.sidebar.markdown(f"**Input Tokens:** {tokens_count["input_tokens"]  if 'input_tokens' in tokens_count else 'N/A' }")
    st.sidebar.markdown(f"**Output Tokens:** {tokens_count["output_tokens"] if 'output_tokens' in tokens_count else 'N/A'}")

    # Create columns for download buttons
    # col1, col2, col3, col4 = st.columns(4)
    # with col1:
    #     st.download_button("Download as JSON format", data=json.dumps(formatted_data.dict() if hasattr(formatted_data, 'dict') else formatted_data, indent=4), file_name=f"{timestamp}_data.json")
    # with col2:
    #     # Convert formatted data to a dictionary if it's not already (assuming it has a .dict() method)
    #     if isinstance(formatted_data, str):
    #         # Parse the JSON string into a dictionary
    #         data_dict = json.loads(formatted_data)
    #     else:
    #         data_dict = formatted_data.dict() if hasattr(formatted_data, 'dict') else formatted_data

        
    #     # Access the data under the dynamic key
    #     first_key = next(iter(data_dict))  # Safely get the first key
    #     main_data = data_dict[first_key]   # Access data using this key

    #     # Create DataFrame from the data
    #     df = pd.DataFrame(main_data)

    #     # data_dict=json.dumps(formatted_data.dict(), indent=4)
    #     st.download_button("Download as CSV format", data=df.to_csv(index=False), file_name=f"{timestamp}_data.csv")
    # with col3:
    #     st.download_button("Download as Markdown format", data=markdown, file_name=f"{timestamp}_data.md")
    # with col4:
    #     # Read the existing Excel file from the output folder
    #     excel_path = f"output/sorted_data_{timestamp}.xlsx"
        
    #     try:
    #         with open(excel_path, "rb") as file:
    #             excel_data = file.read()
    #         st.download_button(
    #             "Download as Excel format",
    #             data=excel_data,
    #             file_name=f"{timestamp}_data.xlsx",
    #             mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    #         )
    #     except FileNotFoundError:
    #         st.error(f"Excel file not found: {excel_path}")

# Ensure that these UI components are persistent and don't rely on re-running the scrape function
if 'results' in st.session_state:
    df, formatted_data, markdown, tokens_count, timestamp = st.session_state['results']