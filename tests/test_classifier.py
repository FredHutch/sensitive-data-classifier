from core.classifier import AdvancedPHIClassifier

def test_heuristic_classification_no_phi():
    clf = AdvancedPHIClassifier()
    res = clf.classify_document("Quarterly financial report about Q3 revenue and growth.")
    assert "risk_level" in res
    assert "confidence" in res

def test_heuristic_classification_with_phi():
    clf = AdvancedPHIClassifier()
    text = "Patient: John Smith, DOB 01/02/1970, SSN 123-45-6789, Phone 206-555-1234."
    res = clf.classify_document(text)
    assert res.get("contains_phi") is True
    assert res.get("total_phi_identifiers", 0) >= 1
