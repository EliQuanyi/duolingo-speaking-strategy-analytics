"""Rasterize actual Office-exported PDFs with bundled Poppler for visual QA."""
import argparse
import json
from pathlib import Path
from pypdf import PdfReader
from pdf2image import convert_from_path
from PIL import Image, ImageOps, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
POPPLER = Path.home() / '.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/Library/bin'

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('paths', nargs='+')
    args = ap.parse_args()
    summaries = []
    for relative in args.paths:
        p = ROOT / relative
        out = ROOT / 'reports/generated/visual_qa' / p.stem
        out.mkdir(parents=True, exist_ok=True)
        reader = PdfReader(p)
        images = convert_from_path(p, dpi=125, poppler_path=POPPLER)
        if len(images) != len(reader.pages):
            raise ValueError('Page rasterization count mismatch')
        thumbs = []
        for i, im in enumerate(images, 1):
            im.save(out / f'page-{i}.png')
            thumb = ImageOps.contain(im, (380, 545))
            tile = Image.new('RGB', (400, 585), 'white')
            tile.paste(thumb, ((400-thumb.width)//2, 22))
            ImageDraw.Draw(tile).text((12, 562), f'Page {i}', fill='black')
            thumbs.append(tile)
        for offset in range(0, len(thumbs), 6):
            ts = thumbs[offset:offset+6]
            sheet = Image.new('RGB', (1200, 585*((len(ts)+2)//3)), '#dddddd')
            for j, tile in enumerate(ts):
                sheet.paste(tile, ((j%3)*400, (j//3)*585))
            sheet.save(out / f'contact-{offset//6+1}.png')
        extracted = '\n\n'.join(page.extract_text() or '' for page in reader.pages)
        (out / 'extracted_text.txt').write_text(extracted, encoding='utf-8')
        summaries.append({'pdf':relative, 'pages':len(reader.pages), 'page_text_lengths':[len(p.extract_text() or '') for p in reader.pages], 'png_dir':str(out), 'engine':'Microsoft Office PDF then bundled Poppler', 'visual_review':'pending human/model image inspection'})
    print(json.dumps(summaries, ensure_ascii=False))

if __name__ == '__main__':
    main()
