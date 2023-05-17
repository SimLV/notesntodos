from notesntodos.notes import findCheckOffsets, FindUncheckedHtmlRe, makeHtml


def test_find_check_offsets():
    src = "- [ ] This is some text\n   - [x] some more text [ ] a false check\n* - [X] and a final check\n- [x ] this is not a check"
    offsets = findCheckOffsets(src)
    assert len(offsets) == 3
    assert src[offsets[0]] == " "
    assert src[offsets[1]] == "x"
    assert src[offsets[2]] == "X"


def test_find_unchecked_html_re():
    src = "- [ ] This is some text\n   - [x] some more text [ ] a false check\n* - [ ] check with www.link.test\n- [x ] this is not a check"
    html = makeHtml(src)
    matches = [x for x in FindUncheckedHtmlRe.finditer(html)]
    assert len(matches) == 2
    assert matches[0].group(1) == "0"
    assert matches[0].group(2).strip() == "This is some text"
    assert matches[1].group(1) == "2"
    assert matches[1].group(2).strip().startswith("check with <a href")
    assert matches[1].group(2).strip().endswith("</a>")


def test_find_unchecked_html_re2():
    src = """- [ ] Check1
- [ ] Check2
- [ ] Check3

- [ ] Check4"""
    html = makeHtml(src)
    matches = [x for x in FindUncheckedHtmlRe.finditer(html)]
    assert len(matches) == 4


def test_make_noreferrer_links():
    src = "Some random www.link.test\n"
    html = makeHtml(src)
    assert ' <a href="http://www.link.test" rel="noreferrer">www.link.test</a>' in html
