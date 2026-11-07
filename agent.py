from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

from tools import dbm_to_watts, wavelength_m, free_space_path_loss_db
from main import llm, get_store, search_notes

store = get_store()


@tool
def search_telecom_docs(question: str) -> str:
    """Search the telecom documents for theory, explanations and measured values.
    Use this for 'why' and 'how' questions. Returns text with its source."""
    return search_notes(store, question, k=5)


tools_list = [
    tool(dbm_to_watts),
    tool(wavelength_m),
    tool(free_space_path_loss_db),
    search_telecom_docs,
]
llm_with_tools = llm.bind_tools(tools_list)
tools_by_name = {t.name: t for t in tools_list}

SYSTEM_PROMPT = (
    "You are a telecom troubleshooting assistant. Use search_telecom_docs "
    "for theory and cite the source in brackets. Use the calculator tools "
    "for numbers. If the documents do not contain the answer, say so."
)


def run_agent(question, max_steps=5):
    messages = [SystemMessage(SYSTEM_PROMPT), HumanMessage(question)]
    for _ in range(max_steps):
        response = llm_with_tools.invoke(messages)
        messages.append(response)

        if not response.tool_calls:
            return response.text

        for call in response.tool_calls:
            print(f"  [tool] {call['name']} {call['args']}")
            try:
                result = tools_by_name[call["name"]].invoke(call["args"])
            except Exception as e:
                result = f"Error: {e}"
            messages.append(ToolMessage(content=str(result), tool_call_id=call["id"]))

    return "Stopped: too many steps."


if __name__ == "__main__":
    print(run_agent("Who won the 2022 World Cup?"))