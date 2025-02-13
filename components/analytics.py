import streamlit.components.v1 as components

def add_simple_analytics():
    components.html(
        """
        <!-- 100% privacy-first analytics -->
        <script data-collect-dnt="true" async src="https://scripts.simpleanalyticscdn.com/latest.js"></script>
        """,
        height=0
    ) 