from core.generator import SyntheticHealthDataGenerator

def test_generate_documents_basic():
    gen = SyntheticHealthDataGenerator()
    docs = gen.generate_synthetic_documents(3, formats=["txt"])
    assert len(docs) == 3
    assert all("content" in d for d in docs)
