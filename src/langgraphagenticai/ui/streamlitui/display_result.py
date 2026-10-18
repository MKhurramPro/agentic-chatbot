
import streamlit as st

from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    ToolMessage,
)


class DisplayResultStreamlit:
    def __init__(self, usecase, graph, user_message):
        self.usecase = usecase
        self.graph = graph
        self.user_message = user_message

    def display_result_on_ui(self):
        usecase = self.usecase
        graph = self.graph
        user_message = self.user_message

        if usecase in ("Basic Chatbot", "Chatbot with Web"):

            # Initialize a stable conversation ID.
            if "thread_id" not in st.session_state:
                import uuid
                st.session_state.thread_id = str(uuid.uuid4())

            # Store messages for displaying the chat UI.
            if "chat_history" not in st.session_state:
                st.session_state.chat_history = []

            config = {
                "configurable": {
                    "thread_id": st.session_state.thread_id
                }
            }

            # Display previous messages once.
            for message in st.session_state.chat_history:
                if isinstance(message, HumanMessage):
                    with st.chat_message("user"):
                        st.write(message.content)

                elif isinstance(message, AIMessage):
                    if message.content:
                        with st.chat_message("assistant"):
                            st.write(message.content)

                elif isinstance(message, ToolMessage):
                    with st.expander("Tool result"):
                        st.write(message.content)

            # Display the current question.
            human_message = HumanMessage(content=user_message)

            with st.chat_message("user"):
                st.write(user_message)

            # Save the question to the UI history.
            st.session_state.chat_history.append(human_message)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):

                    # LangGraph loads previous state using thread_id.
                    response = graph.invoke(
                        {"messages": [HumanMessage(content=user_message)]},
                        config=config
                    )

                    # Read newly generated messages from the result.
                    new_messages = response["messages"]

                    # Find the latest assistant message with content.
                    answer_message = next(
                        (
                            message
                            for message in reversed(new_messages)
                            if isinstance(message, AIMessage)
                            and message.content
                        ),
                        None
                    )

                    if answer_message is not None:
                        st.write(answer_message.content)

                        # Store only the new assistant answer in UI history.
                        st.session_state.chat_history.append(
                            answer_message
                        )

        elif usecase == "AI News":
            import os
            import uuid

            frequency = self.user_message

            # Initialize a stable news thread ID.
            if "news_thread_id" not in st.session_state:
                st.session_state.news_thread_id = str(uuid.uuid4())

            config = {
                "configurable": {
                    "thread_id": st.session_state.news_thread_id
                }
            }

            ai_news_path = f"./AINews/{frequency.lower()}_summary.md"

            try:
                with st.spinner("Fetching and summarizing news..."):
                    # Run the graph.
                    result = graph.invoke(
                        {"messages": frequency},
                        config=config
                    )

                    # Read the generated Markdown file.
                    if not os.path.exists(ai_news_path):
                        st.error(f"News file not found: {ai_news_path}")
                        return

                    with open(
                        ai_news_path,
                        "r",
                        encoding="utf-8-sig",
                        errors="replace"
                    ) as file:
                        markdown_content = file.read()

                    st.markdown(markdown_content)

            except Exception as error:
                st.error(f"AI News error: {error}")