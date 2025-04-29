# from langchain_openai.chat_models.azure import AzureChatOpenAI
# from langgraph_supervisor import create_supervisor
# from langgraph.prebuilt import create_react_agent
# from services.text_service import TextService
# from services.rag_service import RAG
# from services.image_service import ImageGenerator
# from langchain_core.tools import tool
# import os

# llm = AzureChatOpenAI(
#     openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
#     azure_deployment=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
# )

# class MultiAgent:

#     rag_tool = RAG.get_context_from_index
#     description_tool = TextService.generate_descriptive_text
#     image_tool = ImageGenerator.generate_images

#     descriptive_agent = create_react_agent(
#         model=llm, 
#         tools=[description_tool],
#         name="descriptive_agent",
#         #prompt="You are a smart assistant that helps people to train themselfs by generating content for them."
#     )

#     rag_agent = create_react_agent(
#         model = llm,
#         tools = [rag_tool],
#         name = "rag_agent"
#     )

#     image_agent = create_react_agent(
#          model = llm,
#          tools = [image_tool],
#          name = "image_agent",
#         # prompt = "You are a smart agent that can generate helpful images for training documents."
#      )

#     workflow = create_supervisor(
#         agents = [rag_agent, descriptive_agent, image_agent],
#         model = llm,
#         prompt= ("You are a smart assistant. Your have access to multiple agents," 
#                  "your job is to act like a router and decide which agent comes to play."
#                  "If user query is simple greeting, continue with conversation without calling agents."
#                  "Here is the list of agents: rag_agent, descriptive_agent, images_agent"
#                  "For queries related to gen ai in art, gen ai in music, call the rag_agent"
#                  "If queries are unrelated to the previous topics, say that you don't know."
#                  "Always handsoff to the descriptive_agent to generate a description for an image based on rag_agent output"
#                  "For image, diagrams, charts, first use rag_agent, then descriptive_agent and finally images_agent"
#                  "Call the rag_agent just one time per user query"
#                  "Include the last agent response in yours."  
#      )
#     )

#     app = workflow.compile()