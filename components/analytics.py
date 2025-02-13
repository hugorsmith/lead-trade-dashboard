import streamlit as st
import pathlib
import logging
import shutil
from bs4 import BeautifulSoup

def inject_simple_analytics():
    ANALYTICS_ID = "simple_analytics"
    
    ANALYTICS_JS = """
    <!-- 100% privacy-first analytics -->
    <script data-collect-dnt="true" async src="https://scripts.simpleanalyticscdn.com/latest.js"></script>
    """

    # Get the path to Streamlit's static index.html
    index_path = pathlib.Path(st.__file__).parent / "static" / "index.html"
    logging.info(f'editing {index_path}')
    
    # Parse the HTML
    soup = BeautifulSoup(index_path.read_text(), features="html.parser")
    
    # Only inject if not already present
    if not soup.find(id=ANALYTICS_ID):
        # Create backup if it doesn't exist
        bck_index = index_path.with_suffix('.bck')
        if bck_index.exists():
            shutil.copy(bck_index, index_path)
        else:
            shutil.copy(index_path, bck_index)
        
        # Insert the analytics script
        html = str(soup)
        new_html = html.replace('</head>', ANALYTICS_JS + '\n</head>')
        index_path.write_text(new_html)

def add_simple_analytics():
    # First try to inject the script into the template
    try:
        inject_simple_analytics()
    except Exception as e:
        logging.warning(f"Failed to inject analytics into template: {e}")
        # Fallback to components method if injection fails
        st.components.v1.html(
            """
            <!-- 100% privacy-first analytics -->
            <script data-collect-dnt="true" async src="https://scripts.simpleanalyticscdn.com/latest.js"></script>
            """,
            height=0
        ) 