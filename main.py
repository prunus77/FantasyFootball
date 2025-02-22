from src.data.data_loader import DataLoader
from src.data.data_processor import DataProcessor
from src.agent.fantasy_agent import FantasyFootballAgent

def main():
    # Initialize the fantasy football agent
    print("Initializing Fantasy Football Agent...")
    
    # Load and process data
    combine_data, injuries_data, rush_data = DataLoader.load_data()
    combine_data, injuries_data, rush_data = DataProcessor.clean_data(
        combine_data, injuries_data, rush_data
    )
    documents = DataProcessor.create_documents(
        combine_data, injuries_data, rush_data
    )
    
    # Create and initialize the agent
    agent = FantasyFootballAgent()
    agent.initialize_index(documents)
    agent.initialize_agent()
    
    # Interactive loop
    print("\nFantasy Football Agent Ready! Type 'quit' to exit.")
    while True:
        question = input("\nEnter your question: ")
        if question.lower() == 'quit':
            break
            
        response = agent.get_response(question)
        print(f"\nResponse: {response}")

if __name__ == "__main__":
    main() 