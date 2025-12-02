try:
    import langchain
    print(f"Langchain version: {langchain.__version__}")
    from langchain.chains import RetrievalQA
    print("Successfully imported RetrievalQA from langchain.chains")
except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"Error: {e}")

try:
    import langchain_community
    print(f"Langchain Community version: {langchain_community.__version__}")
except ImportError:
    print("Langchain Community not found")
