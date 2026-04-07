from xlodit.parsing import parse_formula_references


def test_parse_formula_references_a1_and_sheet() -> None:
    refs = parse_formula_references("=A1+Sheet2!B2+'My Sheet'!C3", "Sheet1")
    assert [(r.sheet, r.cell) for r in refs] == [
        ("Sheet1", "A1"),
        ("Sheet2", "B2"),
        ("My Sheet", "C3"),
    ]
