    """info about ai tools, bound to be out of date
    
    def get_tools_info():
    """
    Returns a list of dictionaries representing tools with name, description, and implementation.
    """
    tools = [
        {
            "name": "Tool 1",
            "description": "Description of Tool 1.",
            "implementation": "Implementation details of Tool 1."
        },
        {
            "name": "Tool 2",
            "description": "Description of Tool 2.",
            "implementation": "Implementation details of Tool 2."
        },
        {
            "name": "Tool 3",
            "description": "Description of Tool 3.",
            "implementation": "Implementation details of Tool 3."
        },
        # Add more tools as needed
    ]
    return tools

# Example usage:
tools_list = get_tools_info()
for tool in tools_list:
    print("Name:", tool["name"])
    print("Description:", tool["description"])
    print("Implementation:", tool["implementation"])
    print()  # Print an empty line for better readability

    
    
    """
def get_tools_list()    
    tools = [
        {
            "name": "CodeDocsSearchTool",
            "description": "The CodeDocsSearchTool is a powerful RAG (Retrieval-Augmented Generation) tool designed for semantic searches within code documentation. It enables users to efficiently find specific information or topics within code documentation. By providing a docs_url during initialization, the tool narrows down the search to that particular documentation site. Alternatively, without a specific docs_url, it searches across a wide array of code documentation known or discovered throughout its execution, making it versatile for various documentation search needs.",
            "implementation": "tool = CodeDocsSearchTool(docs_url='https://docs.example.com/reference') # To search any code documentation content if the URL is known or discovered during its execution:"

        },
        {
            "name": "CSVSearchTool",
            "description": "This tool is used to perform a RAG (Retrieval-Augmented Generation) search within a CSV file's content. It allows users to semantically search for queries in the content of a specified CSV file. This feature is particularly useful for extracting information from large CSV datasets where traditional search methods might be inefficient. All tools with "Search" in their name, including CSVSearchTool, are RAG tools designed for searching different sources of data.",
            "implementation": "tool = CSVSearchTool(csv='path/to/your/csvfile.csv')"
        },
        {
            "name": "DirectoryReadTool",
            "description": "The DirectoryReadTool is a highly efficient utility designed for the comprehensive listing of directory contents. It recursively navigates through the specified directory, providing users with a detailed enumeration of all files, including those nested within subdirectories. This tool is indispensable for tasks requiring a thorough inventory of directory structures or for validating the organization of files within directories.",
            "implementation": "tool = DirectoryReadTool(directory='/path/to/your/directory')"
        },
        {
            "name" : "DirectorySearchTool",
            "description": "This tool is designed to perform a semantic search for queries within the content of a specified directory. Utilizing the RAG (Retrieval-Augmented Generation) methodology, it offers a powerful means to semantically navigate through the files of a given directory. The tool can be dynamically set to search any directory specified at runtime or can be pre-configured to search within a specific directory upon initialization.",
            "implementation": "tool = DirectorySearchTool(directory='/path/to/directory')"
        },
        {
            "name" : "DOCXSearchTool",
            "description": "The DOCXSearchTool is a RAG tool designed for semantic searching within DOCX documents. It enables users to effectively search and extract relevant information from DOCX files using query-based searches. This tool is invaluable for data analysis, information management, and research tasks, streamlining the process of finding specific information within large document collections.",
            "implementation": "tool = DOCXSearchTool(docx='path/to/your/document.docx')"
        },
        {
            "name" : "FileReadTool",
            "description": "The FileReadTool is a versatile component of the crewai_tools package, designed to streamline the process of reading and retrieving content from files. It is particularly useful in scenarios such as batch text file processing, runtime configuration file reading, and data importation for analytics. This tool supports various text-based file formats including .txt, .csv, .json, and adapts its functionality based on the file type, for instance, converting JSON content into a Python dictionary for easy use.",
            "implementation": "file_read_tool = FileReadTool(file_path='path/to/your/file.txt')"
        },
        {
            "name" : "GitHubSearchTool",
            "description": "",
            "implementation": ""
        },
        {
            "name" : "",
            "description": "",
            "implementation": ""
        },
        {
            "name" : "",
            "description": "",
            "implementation": ""
        },
        {
            "name" : "",
            "description": "",
            "implementation": ""
        },
        {
            "name" : "",
            "description": "",
            "implementation": ""
        },
        {
            "name" : "",
            "description": "",
            "implementation": ""
        },
        {
            "name" : "",
            "description": "",
            "implementation": ""
        },
        {
            "name" : "",
            "description": "",
            "implementation": ""
        },
        {
            "name" : "",
            "description": "",
            "implementation": ""
        },
        {
            "name" : "",
            "description": "",
            "implementation": ""
        },
        {
            "name" : "",
            "description": "",
            "implementation": ""
        },
        {
            "name" : "",
            "description": "",
            "implementation": ""
        },
        {
            "name" : "",
            "description": "",
            "implementation": ""
        },
        {
            "name" : "",
            "description": "",
            "implementation": ""
        },
        {
            "name" : "",
            "description": "",
            "implementation": ""
        },
        {
            "name" : "",
            "description": "",
            "implementation": ""
        },
        {
            "name" : "",
            "description": "",
            "implementation": ""
        },
        {
            "name" : "",
            "description": "",
            "implementation": ""
        }
        
        
        
        # Add more tools as needed
    ]
    return tools

    