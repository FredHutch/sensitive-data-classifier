from core.generator import SyntheticHealthDataGenerator
from core.classifier import AdvancedPHIClassifier

def test_integration_phi_detected_on_generated():
    gen = SyntheticHealthDataGenerator()
    clf = AdvancedPHIClassifier()
    docs = gen.generate_synthetic_documents(2, formats=["txt"])
    for d in docs:
        res = clf.classify_document(d.get("content", ""))
        assert "contains_phi" in res
