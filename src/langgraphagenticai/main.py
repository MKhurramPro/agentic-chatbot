import streamlit as st
import uuid
from src.langgraphagenticai.ui.streamlitui.loadui import LoadStreamlitUI
from src.langgraphagenticai.LLMS.openaillm import OpenaiLLM
from src.langgraphagenticai.graph.graph_builder import GraphBuilder
from src.langgraphagenticai.ui.streamlitui.display_result import DisplayResultStreamlit


@st.cache_resource
def get_graph(usecase, model):
    graph_builder = GraphBuilder(model)
    return graph_builder.setup_graph(usecase)


def load_langgraph_agenticai_app():
    """
    Loads and runs the LangGraph AgenticAI application with Streamlit UI.
    This function initializes the UI, handles user input, configures the LLM model,
    sets up the graph based on the selected use case, and displays the output while 
    implementing exception handling for robustness.

    """

    if "thread_id" not in st.session_state:
        st.session_state.thread_id = str(uuid.uuid4())

    # Create IDs once per Streamlit session
    # if "thread_id" not in st.session_state:
    #     st.session_state.thread_id = str(uuid.uuid4())

    if "news_thread_id" not in st.session_state:
        st.session_state.news_thread_id = str(uuid.uuid4())

    # Keep the rest of your existing code below

    ##Load UI
    ui=LoadStreamlitUI()
    user_input=ui.load_streamlit_ui()

    if not user_input:
        st.error("Error: Failed to load user input from the UI.")
        return
    
    # Text input for user message
    if st.session_state.IsFetchButtonClicked:
        user_message = st.session_state.timeframe 
    else :
        user_message = st.chat_input("Enter your message:")

    if user_message:
        try:
            ## Configure The LLM's
            obj_llm_config=OpenaiLLM(user_contols_input=user_input)
            model=obj_llm_config.get_llm_model()

            if not model:
                st.error("Error: LLM model could not be initialized")
                return
            
            # Initialize and set up the graph based on use case
            usecase=user_input.get("selected_usecase")

            if not usecase:
                    st.error("Error: No use case selected.")
                    return
            
            ## Graph Builder

            
            try:
                graph = get_graph(usecase, model)

                print(user_message)

                DisplayResultStreamlit(
                    usecase, graph, user_message
                ).display_result_on_ui()

            except Exception as e:
                st.error(f"Error: Graph set up failed- {e}")
                return


        except Exception as e:
            st.error(f"Error: Graph set up failed- {e}")
            return   