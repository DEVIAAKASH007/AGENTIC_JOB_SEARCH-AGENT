from langchain_community.document_loaders import PyPDFLoader


def load_resume(file_path):

    loader = PyPDFLoader(file_path)

    documents = loader.load()

    resume_text = "\n".join(
        document.page_content
        for document in documents
    )

    return resume_text