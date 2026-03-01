from ca_desktop.backend.src.modules.documents.tagger import match_tags_to_filename
from ca_desktop.backend.src import models


class TestTagger:
    def test_match_tags_exact(self):
        tag = models.DocumentTag(name="ITR", regex_pattern=r"ITR|Income Tax Return")
        match = match_tags_to_filename("ITR_2024.pdf", [tag])

        assert match is not None
        matched_tag, confidence = match
        assert matched_tag == tag
        assert confidence == 0.95

    def test_match_tags_partial(self):
        tag = models.DocumentTag(name="ITR", regex_pattern=r"ITR|Income Tax Return")
        # 'ITR' is in regex but name 'ITR' is not substring of 'Income Tax Return 2024.pdf' (wait, regex matches 'Income Tax Return')
        # Logic: if name.lower() in filename.lower() -> 0.95, else 0.7

        # Test 0.7 confidence: regex matches but name doesn't
        # Tag name: ITR
        # Filename: Income Tax Return.pdf
        # Regex matches 'Income Tax Return'
        # 'itr' is NOT in 'income tax return.pdf'
        match = match_tags_to_filename("Income Tax Return 2024.pdf", [tag])

        assert match is not None
        matched_tag, confidence = match
        assert matched_tag == tag
        assert confidence == 0.7

    def test_no_match(self):
        tag = models.DocumentTag(name="ITR", regex_pattern=r"ITR")
        match = match_tags_to_filename("BankStatement.pdf", [tag])
        assert match is None

    def test_multiple_tags_best_match(self):
        # Filename: "ITR Tax 2024.pdf"
        # Matches both regexes.
        # tag1 name "Tax" in filename -> 0.95
        # tag2 name "ITR" in filename -> 0.95
        # It picks max. If equal, it picks one (stable sort usually, or implementation defined)

        # Let's try diff confidences
        # Tag 3: name="Statement", regex="State" -> in "Statement" -> 0.95
        # Tag 4: name="Bank", regex="State" -> matches "Statement" but name "Bank" not in "Statement" -> 0.7

        tag3 = models.DocumentTag(name="Statement", regex_pattern=r"State")
        tag4 = models.DocumentTag(name="Bank", regex_pattern=r"State")

        match = match_tags_to_filename("Statement.pdf", [tag3, tag4])
        assert match is not None
        assert match[0].name == "Statement"
        assert match[1] == 0.95
