import unittest
from crawl import normalize_url, get_h1_from_html, get_first_paragraph_from_html, get_urls_from_html, get_images_from_html, extract_page_data


class TestCrawl(unittest.TestCase):
    def test_normalize_url(self):
        input_url = "https://blog.boot.dev/path"
        actual = normalize_url(input_url)
        expected = "blog.boot.dev/path"
        self.assertEqual(actual, expected)

    def test_strip_trailing_slash(self):
        input_url = "http://example.com/path/"
        actual = normalize_url(input_url)
        expected = "example.com/path/"
        self.assertEqual(actual, expected)

    def test_ignore_protocol_and_case(self):
        input_url = "HTTPS://BLOG.BOOT.DEV/Some/Path/"
        actual = normalize_url(input_url)
        expected = "BLOG.BOOT.DEV/Some/Path/"
        self.assertEqual(actual, expected)

    def test_edge_case_only_domain(self):
        input_url = "https://example.com"
        actual = normalize_url(input_url)
        expected = "example.com"
        self.assertEqual(actual, expected)

    def test_getting_h1_tag(self):
        html = "<html><body><h1>Welcome to Boot.dev</h1><main><p>" \
        "Learn to code by building real projects.</p><p>This is the second paragraph." \
        "</p></main></body></html>"
        actual = get_h1_from_html(html)
        expected = "Welcome to Boot.dev"
        self.assertEqual(actual, expected)
    
    def test_get_h1_from_html_basic(self):
        input_body = '<html><body><h1>Test Title</h1></body></html>'
        actual = get_h1_from_html(input_body)
        expected = "Test Title"
        self.assertEqual(actual, expected)

    def test_getting_first_paragraph_tag(self):
        html = "<html><body><h1>Welcome to Boot.dev</h1><main><p>" \
        "Learn to code by building real projects.</p><p>This is the second paragraph." \
        "</p></main></body></html>"
        actual = get_first_paragraph_from_html(html)
        expected = "Learn to code by building real projects."
        self.assertEqual(actual, expected)
    
    def test_not_returning_second_paragraph(self):
        html = "<html><body><h1>Welcome to Boot.dev</h1><main><p>" \
        "Learn to code by building real projects.</p><p>This is the second paragraph." \
        "</p></main></body></html>"
        actual = get_first_paragraph_from_html(html)
        expected = "This is the second paragraph."
        self.assertNotEqual(actual, expected)
    
    def test_get_first_paragraph_from_html_main_priority(self):
        input_body = '''<html><body>
            <p>Outside paragraph.</p>
            <main>
                <p>Main paragraph.</p>
            </main>
        </body></html>'''
        actual = get_first_paragraph_from_html(input_body)
        expected = "Main paragraph."
        self.assertEqual(actual, expected)
    
    def test_no_p_tag_in_html(self):
        input_body = '''<html><body>
            <main>
            </main>
        </body></html>'''
        actual = get_first_paragraph_from_html(input_body)
        expected = ""
        self.assertEqual(actual, expected)
    
    def test_no_main_tag_in_html(self):
        input_body = '''<html><body>
        <p>Only paragraph body.</p>
        </body></html>'''
        actual = get_first_paragraph_from_html(input_body)
        expected = "Only paragraph body."
        self.assertEqual(actual, expected)
    
    def test_get_urls_from_html_absolute(self):
        input_url = "https://blog.boot.dev"
        input_body = '<html><body><a href="https://blog.boot.dev"><span>Boot.dev</span></a></body></html>'
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://blog.boot.dev"]
        self.assertEqual(actual, expected)
    
    def test_get_urls_from_relative_html(self):
        input_url = "https://blog.boot.dev"
        input_body = """
        <html>
        <body>
            <a href="https://blog.boot.dev/page1">Absolute</a>
            <a href="/page2">Relative</a>
        </body>
        </html>
        """
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://blog.boot.dev/page1", "https://blog.boot.dev/page2"]
        self.assertEqual(actual, expected)
    
    def test_get_urls_from_html_ignores_invalid_hrefs(self):
        input_url = "https://blog.boot.dev"
        input_body = """
        <html>
        <body>
            <a>No href here</a>
            <a href="">Empty href</a>
            <a href="#section">Fragment only</a>
            <a href="page3">Valid relative</a>
        </body>
        </html>
        """
        actual = get_urls_from_html(input_body, input_url)
        expected = [
        "https://blog.boot.dev#section",
        "https://blog.boot.dev/page3",
        ]
        self.assertEqual(actual, expected)

    def test_get_images_from_html_relative(self):
        input_url = "https://blog.boot.dev"
        input_body = '<html><body><img src="/logo.png" alt="Logo"></body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://blog.boot.dev/logo.png"]
        self.assertEqual(actual, expected)

    def test_get_images_from_html_absolute(self):
        input_url = "https://blog.boot.dev"
        input_body = '<html><body><img src="https://blog.boot.dev/images/pic.jpg"></body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://blog.boot.dev/images/pic.jpg"]
        self.assertEqual(actual, expected)
    
    def test_get_images_from_html_ignores_invalid_src(self):
        input_url = "https://blog.boot.dev"
        input_body = """
        <html>
        <body>
            <img alt="no src">
            <img src="">
            <img src="icons/icon.png">
        </body>
        </html>
        """
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://blog.boot.dev/icons/icon.png"]
        self.assertEqual(actual, expected)
    
    def test_extract_page_data_basic(self):
        input_url = "https://blog.boot.dev"
        input_body = '''<html><body>
            <h1>Test Title</h1>
            <p>This is the first paragraph.</p>
            <a href="/link1">Link 1</a>
            <img src="/image1.jpg" alt="Image 1">
        </body></html>'''
        actual = extract_page_data(input_body, input_url)
        expected = {
            "url": "https://blog.boot.dev",
            "h1": "Test Title",
            "first_paragraph": "This is the first paragraph.",
            "outgoing_links": ["https://blog.boot.dev/link1"],
            "image_urls": ["https://blog.boot.dev/image1.jpg"]
        }
        self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
