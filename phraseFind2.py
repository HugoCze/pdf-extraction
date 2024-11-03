import pdfplumber
import re
from typing import List, Tuple

def find_chapters_with_details(input_pdf: str) -> List[Tuple]:
    """
    Find chapters using exact pattern "Chapter X: " (with space after colon)
    """
    # Exact pattern match
    pattern = re.compile(r'Chapter \d+: ')  # Matches "Chapter X: " exactly
    
    results = []
    print(f"Analyzing {input_pdf} for exact chapter pattern 'Chapter X: '...")
    
    with pdfplumber.open(input_pdf) as pdf:
        total_pages = len(pdf.pages)
        
        for page_num in range(total_pages):
            if page_num % 10 == 0:
                print(f"Scanning page {page_num + 1}/{total_pages}")
            
            page = pdf.pages[page_num]
            text = page.extract_text()
            
            # Find all matches
            matches = pattern.finditer(text)
            for match in matches:
                # Extract the chapter number
                chapter_text = match.group()  # e.g., "Chapter 1: "
                chapter_num = int(re.search(r'\d+', chapter_text).group())
                
                if 1 <= chapter_num <= 25:
                    # Get some context
                    start = max(0, match.start() - 30)
                    end = min(len(text), match.end() + 30)
                    context = text[start:end].replace('\n', ' ').strip()
                    
                    # Try to get font size
                    words = page.extract_words(keep_blank_chars=True, extra_attrs=['size'])
                    font_size = None
                    for word in words:
                        if 'Chapter' in word['text']:
                            font_size = word['size']
                            break
                    
                    results.append((
                        chapter_num,
                        page_num,
                        font_size,
                        context,
                        chapter_text
                    ))
    
    # Sort by chapter number
    results.sort(key=lambda x: x[0])
    return results

def display_chapter_analysis(results: List[Tuple]) -> None:
    """
    Display found chapters with their details
    """
    if not results:
        print("\nNo chapters found! Check if the pattern 'Chapter X: ' matches exactly.")
        return
    
    print("\nFound chapters:")
    print("-" * 100)
    print(f"{'Chapter':<10} {'Page':<8} {'Font Size':<12} {'Matched Text':<20} {'Context'}")
    print("-" * 100)
    
    for chapter_num, page, font_size, context, matched_text in results:
        # Truncate context if too long
        if len(context) > 40:
            context = context[:37] + "..."
        font_size_str = f"{font_size:.1f}" if font_size else "unknown"
        print(f"Chapter {chapter_num:<3} {page + 1:<8} {font_size_str:<12} {matched_text:<20} {context}")
    
    print(f"\nTotal chapters found: {len(results)}")
    print("Page numbers for splitting:", [page + 1 for _, page, _, _, _ in results])

    # Check for missing chapters
    found_chapters = set(chapter_num for chapter_num, _, _, _, _ in results)
    if found_chapters:
        expected_chapters = set(range(1, max(found_chapters) + 1))
        missing_chapters = expected_chapters - found_chapters
        if missing_chapters:
            print(f"Missing chapters: {sorted(missing_chapters)}")

def main():
    try:
        results = find_chapters_with_details('WorkPdf.pdf')
        display_chapter_analysis(results)
        
    except FileNotFoundError:
        print("Error: PDF file not found!")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == '__main__':
    main()