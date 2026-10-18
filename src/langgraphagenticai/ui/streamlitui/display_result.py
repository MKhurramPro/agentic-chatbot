
import os
import uuid
import streamlit as st

from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    AIMessageChunk,
    ToolMessage,
)


class DisplayResultStreamlit:
    def __init__(self, usecase, graph, user_message):
        self.usecase = usecase
        self.graph = graph
        self.user_message = user_message

    def stream_graph_text(self, graph_input, config):
        """Yield assistant text chunks as the graph generates them."""
        for message_chunk, metadata in self.graph.stream(
            graph_input,
            config=config,
            stream_mode="messages",
        ):
            if isinstance(message_chunk, AIMessageChunk):
                content = message_chunk.content

                # Text chunks are usually strings. Handle text-block content too.
                if isinstance(content, str) and content:
                    yield content
                elif isinstance(content, list):
                    for block in content:
                        if (
                            isinstance(block, dict)
                            and block.get("type") == "text"
                            and block.get("text")
                        ):
                            yield block["text"]

    def display_result_on_ui(self):
        usecase = self.usecase
        graph = self.graph
        user_message = self.user_message

        # --------------------------------------------------
        # Basic Chatbot + Chatbot with Web
        # --------------------------------------------------
        if usecase in ("Basic Chatbot", "Chatbot with Web"):

            if "thread_id" not in st.session_state:
                st.session_state.thread_id = str(uuid.uuid4())

            if "chat_history" not in st.session_state:
                st.session_state.chat_history = []

            config = {
                "configurable": {
                    "thread_id": st.session_state.thread_id
                }
            }

            # Show previous conversation messages.
            for message in st.session_state.chat_history:
                if isinstance(message, HumanMessage):
                    with st.chat_message("user"):
                        st.write(message.content)

                elif isinstance(message, AIMessage):
                    if message.content:
                        with st.chat_message("assistant"):
                            st.markdown(message.content)

                elif isinstance(message, ToolMessage):
                    with st.expander("Tool result"):
                        st.write(message.content)

            # Display and save the current question.
            human_message = HumanMessage(content=user_message)

            with st.chat_message("user"):
                st.write(user_message)

            st.session_state.chat_history.append(human_message)

            # Stream the assistant response.
            with st.chat_message("assistant"):
                try:
                    answer = st.write_stream(
                        self.stream_graph_text(
                            {"messages": [human_message]},
                            config,
                        )
                    )

                    # Save the completed answer for UI history.
                    if answer:
                        st.session_state.chat_history.append(
                            AIMessage(content=answer)
                        )

                except Exception as error:
                    st.error(f"Chat error: {error}")

        # --------------------------------------------------
        # AI News
        # --------------------------------------------------
        elif usecase == "AI News":

            frequency = user_message.lower()

            if "news_thread_id" not in st.session_state:
                st.session_state.news_thread_id = str(uuid.uuid4())

            config = {
                "configurable": {
                    "thread_id": st.session_state.news_thread_id
                }
            }

            ai_news_path = f"./AINews/{frequency}_summary.md"

            try:
                st.subheader(f"{frequency.capitalize()} AI News")

                with st.spinner("Fetching news and preparing the report..."):
                    streamed_report = st.write_stream(
                        self.stream_graph_text(
                            {"messages": frequency},
                            config,
                        )
                    )

                # If the graph produced no visible text chunks,
                # fall back to the report saved by the graph.
                if not streamed_report:
                    if not os.path.exists(ai_news_path):
                        st.error(f"News file not found: {ai_news_path}")
                        return

                    with open(
                        ai_news_path,
                        "r",
                        encoding="utf-8-sig",
                        errors="replace",
                    ) as file:
                        markdown_content = file.read()

                    st.markdown(markdown_content)

            except Exception as error:
                st.error(f"AI News error: {error}")
