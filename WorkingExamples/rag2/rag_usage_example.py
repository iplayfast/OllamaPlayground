# example_usage.py
from rag_ollama import RAGEngine

def main():
    # Initialize the RAG engine with default config
    rag = RAGEngine()
    
    # Create some sample game lore
    game_lore = """
    The Kingdom of Eldara is a vast realm filled with ancient magic and mysterious creatures. 
    The capital city, Crystal Haven, is built upon the ruins of an ancient civilization.
    
    The Great War of the Crystal happened 1000 years ago, when the Dark Sorcerer Malakai 
    attempted to steal the Sacred Crystal from the Temple of Light. The Crystal's power was 
    said to grant immortality, but its true purpose was to maintain the balance between the 
    realms of light and shadow.
    
    The current ruler, Queen Aria, is a descendant of the legendary hero Thorian who defeated 
    Malakai. She possesses the Crown of Wisdom, one of the five Ancient Artifacts. The other 
    artifacts are: the Shield of Dawn, the Sword of Twilight, the Staff of Seasons, and the 
    Amulet of Dreams.
    
    The kingdom is protected by an elite group of warriors known as the Crystal Guard. Each 
    member of the Guard undergoes rigorous training in both combat and magical arts at the 
    Academy of Light and Shadow.
    """
    
    # Save the lore to a file
    with open("game_lore.txt", "w") as f:
        f.write(game_lore)
    
    # Index the documents6
    rag.load_and_index_documents("game_lore.txt")
    
    # Example queries
    queries = [
        "What are the five Ancient Artifacts?",
        "Tell me about the Crystal Guard",
        "What happened in the Great War of the Crystal?",
        "Who is the current ruler and what is their connection to the kingdom's history?"
    ]
    
    print("\n=== Basic Queries ===")
    for query in queries:
        print(f"\nQuestion: {query}")
        response = rag.query(query)
        print(f"Answer: {response['result']}")
        print("-" * 80)  # Separator line for readability

if __name__ == "__main__":
    main()
