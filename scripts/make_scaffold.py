"""Create a clean BIT-branded PPTX scaffold. Requires python-pptx."""
from pathlib import Path
import argparse,copy,zipfile
from pptx import Presentation
from pptx.opc.constants import RELATIONSHIP_TYPE as RT


def create(source,target,count):
    if count<1:raise ValueError('Slide count must be positive')
    if target.exists():raise FileExistsError('Choose a new output filename')
    if source.resolve()==target.resolve():raise ValueError('Keep the reference unchanged')
    deck=Presentation(source)
    if len(deck.slides)<2:raise ValueError('Reference needs a cover and content page')
    for index in range(len(deck.slides)-1,1,-1):
        sid=deck.slides._sldIdLst[index];deck.part.drop_rel(sid.rId);deck.slides._sldIdLst.remove(sid)
    values={'Cover_2':'报告题目','Cover_3':'报告类型','Cover_4':'汇报人 / 单位','Header_9':'页面标题','Header_5':'1'}
    for index,slide in enumerate(deck.slides):
        keep={'Cover_2','Cover_3','Cover_4'} if index==0 else {'Header_9','Header_5'}
        for shape in list(slide.shapes):
            if shape.name not in keep:
                slide.shapes._spTree.remove(shape._element);continue
            paragraphs=shape.text_frame.paragraphs
            if paragraphs and paragraphs[0].runs:
                paragraphs[0].runs[0].text=values[shape.name]
                for run in paragraphs[0].runs[1:]:run.text=''
                for paragraph in paragraphs[1:]:
                    for run in paragraph.runs:run.text=''
            else:shape.text=values[shape.name]
        for relationship in list(slide.part.rels.values()):
            if relationship.reltype!=RT.SLIDE_LAYOUT:slide.part.drop_rel(relationship.rId)
    body=deck.slides[1]
    if count==1:
        sid=deck.slides._sldIdLst[1];deck.part.drop_rel(sid.rId);deck.slides._sldIdLst.remove(sid)
    while len(deck.slides)<count:
        slide=deck.slides.add_slide(body.slide_layout)
        for shape in list(slide.shapes):slide.shapes._spTree.remove(shape._element)
        for shape in body.shapes:
            slide.shapes._spTree.insert_element_before(copy.deepcopy(shape._element),'p:extLst')
        for shape in slide.shapes:
            if shape.name=='Header_5':shape.text=str(len(deck.slides)-1)
    deck.core_properties.title='BIT Academic Slides'
    deck.core_properties.subject='Reusable blank academic presentation structure'
    deck.core_properties.author='';deck.core_properties.last_modified_by=''
    deck.core_properties.keywords='';deck.core_properties.comments=''
    target.parent.mkdir(parents=True,exist_ok=True);deck.save(target)
    with zipfile.ZipFile(target) as archive:assert archive.testzip() is None
    assert len(Presentation(target).slides)==count
    print(f'Created {count}-slide native scaffold: {target}')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output',type=Path);parser.add_argument('--slides',type=int,default=8)
    parser.add_argument('--source',type=Path,default=Path(__file__).resolve().parents[1]/'assets/layout-scaffold.pptx')
    args=parser.parse_args();create(args.source,args.output,args.slides)
if __name__=='__main__':main()
