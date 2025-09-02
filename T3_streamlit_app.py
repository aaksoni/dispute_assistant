import streamlit as st
import pandas as pd
from Task3 import DisputeAnalyzer
import plotly.express as px


def initialize_analyzer():
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = DisputeAnalyzer()


def create_visualization(result):
    if isinstance(result, pd.DataFrame):
        return result
    elif isinstance(result, pd.Series):
        if result.name == 'size':  # For value_counts() or groupby().size()
            fig = px.bar(result)
            return fig
    return result


def main():
    st.title("Dispute Analysis Dashboard")
    initialize_analyzer()

    # Sidebar with example queries
    st.sidebar.header("Example Queries")
    example_queries = [
        "How many duplicate charges today?",
        "List unresolved fraud disputes",
        "Break down disputes by type",
        "Count all disputes",
        "Show fraud disputes"
    ]

    selected_query = st.sidebar.selectbox(
        "Select an example query",
        [""] + example_queries
    )

    # Main query input
    user_query = st.text_input(
        "Enter your query:",
        value=selected_query
    )

    if user_query:
        with st.spinner("Processing query..."):
            response = st.session_state.analyzer.process_query(user_query)

            # Display generated code
            with st.expander("View Generated Code"):
                st.code(response['generated_code'], language='python')

            # Display results
            if response['success']:
                st.subheader("Results")
                result = create_visualization(response['result'])

                if isinstance(result, pd.DataFrame):
                    st.dataframe(result)
                elif str(type(result).__module__) == 'plotly.graph_objs._figure':
                    st.plotly_chart(result)
                else:
                    st.write(result)
            else:
                st.error(response['error'])


if __name__ == "__main__":
    main()