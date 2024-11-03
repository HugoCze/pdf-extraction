import pdfplumber
from collections import defaultdict
import re

class AcademicBookMapper:
    def __init__(self, file_path):
        self.file_path = file_path
        self.structure = {
            'toc': [],              # Table of Contents
            'chapters': [],         # Chapter information
            'sections': [],         # Section information
            'figures': [],          # Figure locations
            'tables': [],          # Table locations
            'equations': [],       # Equation locations
            'references': [],      # Reference section
            'appendices': []       # Appendices
        }
        self.current_chapter = None
        self.hierarchy = defaultdict(list)

    def analyze(self):
        """Main analysis function"""
        with pdfplumber.open(self.file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                if text:
                    self._analyze_page_structure(text, page_num)
                    self._detect_figures_tables(page, page_num)
        
        return self._generate_book_map()

    def _analyze_page_structure(self, text, page_num):
        """Analyze the hierarchical structure of the page"""
        lines = text.split('\n')
        
        for line in lines:
            # Chapter detection
            chapter_match = re.match(r'^(?:Chapter|CHAPTER)\s+(\d+|[IVXLC]+)[.:]\s*(.+)', line)
            if chapter_match:
                chapter_num, chapter_title = chapter_match.groups()
                self.current_chapter = {
                    'number': chapter_num,
                    'title': chapter_title.strip(),
                    'page': page_num,
                    'sections': []
                }
                self.structure['chapters'].append(self.current_chapter)
                continue

            # Section detection
            section_match = re.match(r'^(\d+\.(?:\d+)*)\s+(.+)', line)
            if section_match:
                section_num, section_title = section_match.groups()
                section = {
                    'number': section_num,
                    'title': section_title.strip(),
                    'page': page_num,
                    'level': len(section_num.split('.')) - 1
                }
                
                if self.current_chapter:
                    self.current_chapter['sections'].append(section)
                self.structure['sections'].append(section)
                continue

            # Reference section detection
            if re.match(r'^References$|^Bibliography$', line, re.IGNORECASE):
                self.structure['references'].append({
                    'title': line.strip(),
                    'page': page_num
                })
                continue

            # Appendix detection
            appendix_match = re.match(r'^Appendix\s+([A-Z]):\s*(.+)', line)
            if appendix_match:
                appendix_letter, appendix_title = appendix_match.groups()
                self.structure['appendices'].append({
                    'letter': appendix_letter,
                    'title': appendix_title.strip(),
                    'page': page_num
                })

    def _detect_figures_tables(self, page, page_num):
        """Detect figures and tables on the page"""
        text = page.extract_text()
        
        # Figure detection
        figure_matches = re.finditer(r'Figure\s+(\d+\.?\d*)[.:]\s*(.+)', text)
        for match in figure_matches:
            fig_num, fig_caption = match.groups()
            self.structure['figures'].append({
                'number': fig_num,
                'caption': fig_caption.strip(),
                'page': page_num
            })

        # Table detection
        table_matches = re.finditer(r'Table\s+(\d+\.?\d*)[.:]\s*(.+)', text)
        for match in table_matches:
            table_num, table_caption = match.groups()
            self.structure['tables'].append({
                'number': table_num,
                'caption': table_caption.strip(),
                'page': page_num
            })

        # Equation detection
        equations = re.finditer(r'\(\s*(?:eq|equation)?\s*(\d+\.?\d*)\s*\)', text, re.IGNORECASE)
        for match in equations:
            eq_num = match.group(1)
            self.structure['equations'].append({
                'number': eq_num,
                'page': page_num
            })

    def _generate_book_map(self):
        """Generate a structured map of the book"""
        book_map = {
            'summary': {
                'total_chapters': len(self.structure['chapters']),
                'total_figures': len(self.structure['figures']),
                'total_tables': len(self.structure['tables']),
                'total_equations': len(self.structure['equations'])
            },
            'structure': {
                'chapters': [
                    {
                        'number': chapter['number'],
                        'title': chapter['title'],
                        'page': chapter['page'],
                        'sections': [
                            {
                                'number': section['number'],
                                'title': section['title'],
                                'page': section['page'],
                                'level': section['level']
                            }
                            for section in chapter['sections']
                        ]
                    }
                    for chapter in self.structure['chapters']
                ],
                'figures': self.structure['figures'],
                'tables': self.structure['tables'],
                'equations': self.structure['equations'],
                'references': self.structure['references'],
                'appendices': self.structure['appendices']
            }
        }
        return book_map

def map_academic_book(file_path):
    """Convenience function to map an academic book's structure"""
    mapper = AcademicBookMapper(file_path)
    return mapper.analyze()



book_structure = map_academic_book("DataEngineerGarethEdgar.pdf")