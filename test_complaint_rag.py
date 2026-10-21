"""Regression tests for text complaint retrieval (no model weights/API key needed)."""
import unittest

from retrieve import knowledge_documents, retrieve


class ComplaintRAGTests(unittest.TestCase):
    def test_synthetic_cases_exist(self):
        cases = [d for d in knowledge_documents() if d.get("synthetic") and d.get("kind") == "synthetic_case"]
        self.assertGreaterEqual(len(cases), 88)

    def test_guide_first_and_example_available(self):
        docs = retrieve("A176 표면에 긁힘이 있어요", model="A176", k=5, include_examples=True)
        self.assertTrue(docs)
        self.assertFalse(docs[0].get("synthetic"))
        self.assertTrue(any(d.get("synthetic") for d in docs))

    def test_examples_never_overrule_product_filter(self):
        docs = retrieve("A276 assembly gap 조립 벌어짐", model="A276", k=5, include_examples=True)
        self.assertTrue(all(d.get("product_model") in (None, "A276") for d in docs))

    def test_unconfirmed_visual_roi_excluded(self):
        docs = retrieve("A176 fracture", model="A176", k=20, include_examples=True)
        self.assertTrue(all(d.get("annotation_status") != "source_roi_requires_confirmation" for d in docs))

    def test_unknown_model_rejected(self):
        with self.assertRaises(ValueError):
            retrieve("scratch", model="INVALID")


if __name__ == "__main__":
    unittest.main()
