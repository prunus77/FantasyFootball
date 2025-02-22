import streamlit as st
from streamlit_chat import message
import os
from src.data.data_loader import DataLoader
from src.data.data_processor import DataProcessor
from src.agent.fantasy_agent import FantasyFootballAgent
from src.utils.config import FANTASY_RULES, DATA_DIR
from src.utils.yahoo_fantasy import YahooFantasyManager

def handle_input():
    """Handle user input and return response"""
    if st.session_state.user_input_field != "":
        user_question = st.session_state.user_input_field
        response = st.session_state.agent.get_response(user_question)
        st.session_state.chat_history.append((user_question, response))
        st.session_state.user_input_field = ""

def initialize_agent():
    """Initialize the Fantasy Football Agent"""
    try:
        st.write(f"Looking for data in: {DATA_DIR}")
        combine_data, injuries_data, rush_data = DataLoader.load_data()
        combine_data, injuries_data, rush_data = DataProcessor.clean_data(
            combine_data, injuries_data, rush_data
        )
        documents = DataProcessor.create_documents(
            combine_data, injuries_data, rush_data
        )
        agent = FantasyFootballAgent()
        agent.initialize_index(documents)
        agent.initialize_agent()
        return agent
    except Exception as e:
        st.error(f"Error initializing agent: {str(e)}")
        return None

def main():
    # Set page configuration
    st.set_page_config(
        page_title="Fantasy Football AI Assistant",
        page_icon="🏈",
        layout="wide"
    )

    # Initialize session states
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'agent' not in st.session_state:
        with st.spinner("Initializing Fantasy Football Agent..."):
            agent = initialize_agent()
            if agent is not None:
                st.session_state.agent = agent
            else:
                st.error("Failed to initialize agent. Please check the data files and try again.")
                return

    # Sidebar for Fantasy Football Rules
    with st.sidebar:
        st.title("Fantasy Football Rules")
        st.markdown(FANTASY_RULES)

    # Main content
    st.title("Fantasy Football AI Assistant 🏈")

    # Top section with example questions and team info
    top_col1, top_col2 = st.columns([1, 1])

    with top_col1:
        st.subheader("Quick Questions")
        example_questions = [
            "Who are the top 3 running backs for PPR leagues?",
            "Which players have the highest injury risk?",
            "What rookies should I target in the draft?",
            "Help me optimize my lineup for week 1",
            "Should I trade Player A for Player B?"
        ]
        
        # Display example questions in a grid
        for i in range(0, len(example_questions), 2):
            col1, col2 = st.columns(2)
            with col1:
                if i < len(example_questions):
                    if st.button(example_questions[i], key=f"example_{i}"):
                        st.session_state.user_input_field = example_questions[i]
                        handle_input()
            with col2:
                if i + 1 < len(example_questions):
                    if st.button(example_questions[i + 1], key=f"example_{i + 1}"):
                        st.session_state.user_input_field = example_questions[i + 1]
                        handle_input()

    with top_col2:
        if st.session_state.agent and st.session_state.agent.yahoo_manager:
            st.subheader("My Fantasy Team")
            roster = st.session_state.agent.yahoo_manager.get_roster()
            
            # Display roster in a more compact format
            cols = st.columns(3)
            for idx, player in enumerate(roster):
                cols[idx % 3].write(f"• {player['name']} ({', '.join(player['position'])})")
            
            # League info in expandable section
            with st.expander("League Information"):
                league_info = st.session_state.agent.yahoo_manager.get_league_info()
                st.write(f"Current Week: {league_info['current_week']}")
                st.write("Standings:")
                st.write(league_info['standings'])

    # Chat interface (full width)
    st.markdown("---")
    chat_container = st.container()
    
    with chat_container:
        # Messages container with custom height
        messages_container = st.container()
        with messages_container:
            st.markdown(
                """
                <style>
                    .stChatMessage {
                        max-width: 800px;
                        margin: 0 auto;
                    }
                </style>
                """,
                unsafe_allow_html=True
            )
            for i, (question, answer) in enumerate(st.session_state.chat_history):
                message(question, is_user=True, key=f"user_{i}")
                message(answer, key=f"assistant_{i}")

        # Input field (centered)
        st.text_input(
            "Your question: (Press Enter to submit)",
            key="user_input_field",
            on_change=handle_input
        )

    # Available Players section at bottom
    st.markdown("---")
    if st.session_state.agent and st.session_state.agent.yahoo_manager:
        st.subheader("Available Players")
        waiver = st.session_state.agent.yahoo_manager.get_waiver_players()
        
        # Display available players in a grid
        cols = st.columns(4)
        for idx, player in enumerate(waiver):
            cols[idx % 4].write(f"• {player['name']} ({', '.join(player['position'])})")

    # Clear chat button (bottom right)
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    with col4:
        if st.button("Clear Chat"):
            st.session_state.chat_history = []
            st.session_state.user_input_field = ""
            st.rerun()

if __name__ == "__main__":
    main() 