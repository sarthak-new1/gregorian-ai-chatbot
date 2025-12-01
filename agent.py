from langchain.tools import tool
from dependancies.pinecone_operations import PineconeOperations
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

pinecone_ops = PineconeOperations()
vector_store = pinecone_ops.get_vector_store()

MODEL = "gpt-4o"



def get_llm():
    return ChatOpenAI(
        model=MODEL,
        temperature=0.0,  # 0 = deterministic, 1.0 = creative
        max_tokens=2000
    )


@tool(response_format="content_and_artifact")
def retrieve_context(query: str):
    """Retrieve information to help answer a query."""
    retriever = vector_store.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 8, "fetch_k": 20},
    )
    retrieved_docs = retriever.invoke(query)

    article_numbers = sorted({
        doc.metadata.get("article_number")
        for doc in retrieved_docs
        if doc.metadata.get("article_number")
    })

    if article_numbers:
        header = (
            "Relevant articles (from metadata): "
            + ", ".join(article_numbers)
            + "\n\n"
        )
    else:
        header = (
            "Relevant articles (from metadata): none clearly identified.\n\n"
        )

    serialized_docs = "\n\n".join(
        (
            f"Source: {doc.metadata}\n"
            f"Content: {doc.page_content}"
        )
        for doc in retrieved_docs
    )
    content_for_llm = header + serialized_docs

    # artifact can be used programmatically if you ever need it
    artifact = {
        "docs": retrieved_docs,
        "article_numbers": article_numbers,
    }
    return content_for_llm, artifact


def get_answer(query):
    tools = [retrieve_context]
    
    FALLBACK_SENTENCE = "ამ საკითხთან დაკავშირებული კონკრეტული მუხლი მკაფიოდ მითითებული არ არის."

    prompt = f"""
        შენ ხარ იურიდიული ასისტენტი, რომელიც სპეციალიზდება საქართველოს შრომის კოდექსში.
        ყოველთვის უპასუხე ქართულად, ცივად და პროფესიულად.

        შენ შეგიძლია სარგებლობა გააკეთო მხოლოდ იმ ინფორმაციაზე, რომელსაც მოგაწვდის ინსტრუმენტი `retrieve_context`.
        არასდროს გამოიგონო მუხლის ნომრები ან სამართლებრივი ნორმები.

        როდესაც პასუხი ეხება სამართლებრივ წესს (მაგალითად: უფლებები, ვალდებულებები, ასაკობრივი ზღვარი,
        დასაქმების პირობები, დისკრიმინაცია, შრომის ანაზღაურება, ხელშეკრულების შეწყვეტა და ა.შ.):

        1. თუ `retrieve_context`-ის შედეგად მიღებულ ტექსტში ან მეტამონაცემებში (მაგალითად: "article_number")
        შეგიძლია ამოიცნო ერთი ან რამდენიმე მუხლი, აუცილებლად მიუთითე ეს მუხლი პასუხში.
        ფორმატი, მაგალითად:
        - „ამ საკითხს არეგულირებს საქართველოს შრომის კოდექსის მუხლი X.“
        ან, თუ რამდენიმეა:
        - „ამ საკითხს არეგულირებს საქართველოს შრომის კოდექსის მუხლები X და Y.“

        2. თუ ვერ შეძლებ კონკრეტული მუხლის იდენტიფიცირებას, მუხლის ნომერი არ მოიგონო.
        ასეთ შემთხვევაში გამოიყენე შემდეგი ნეიტრალური ფორმულირება:
        - "{FALLBACK_SENTENCE}"
        და შემდეგ მაინც გასაგებად ახსენი, რას ამბობს შრომის კოდექსი საკითხთან დაკავშირებით,
        იმ ტექსტების საფუძველზე, რომლებიც გაქვს.

        3. არასდროს ახსნა, როგორ ან საიდან მიიღე ტექსტები (არ შეახსენო მომხმარებელს „ინსტრუმენტების“ ან „კონტექსტის“ შესახებ).
        უბრალოდ უპასუხე როგორც იურისტი, რომელიც იცნობს შრომის კოდექსს.

        პასუხები იყოს:
        - მოკლე,
        - ზუსტი,
        - იურიდიულად კორექტული.
        """.strip()
    
    agent = create_agent(get_llm(), tools, system_prompt=prompt)
    for event in agent.stream(
        {"messages": [{"role": "user", "content": query}]},
        stream_mode="values",
    ):
        message = event["messages"][-1]
    return message.content

if __name__ == "__main__":
    query = "შემიძლია თუ არა დავდო ნებისმიერი ვადით შრომითი ხელშეკრულება?"
    answer = get_answer(query)
    print("Final Answer:", answer)
