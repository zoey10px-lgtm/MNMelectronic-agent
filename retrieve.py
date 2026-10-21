"""Offline lexical retrieval. Pure Python; no model/API/embedding dependency."""
from pathlib import Path
import argparse, json, math, re, unicodedata, collections

ROOT=Path(__file__).resolve().parent
def normalize(s):
    return ''.join(c for c in unicodedata.normalize('NFKD',s.lower()) if not unicodedata.combining(c))
def tokens(s):
    # Keep Korean syllables before accent folding (NFKD decomposes Hangul).
    syllables=re.findall(r'[가-힣]+',unicodedata.normalize('NFC',s))
    out=re.findall(r'[a-z0-9]+',normalize(s))
    for w in syllables:
        out.append(w)
        out.extend(w[i:i+2] for i in range(len(w)-1))
    return out

ALIASES={
 'scratch':['scratch','scratches','긁힘','긁혔','스크래치','trầy xước'],
 'dent':['dent','dented','찍힘','찍혔','눌림','móp','dập'],
 'crack':['crack','균열','금이','nứt'],
 'fracture':['fracture','broken','break','파손','부러','갈라','깨졌','깨짐','gãy','tách rời'],
 'porosity':['porosity','cavity','cavities','기공','빈 공간','rỗ khí','lỗ rỗ'],
 'deformation':['deformation','bent','warped','휘어','휘었','휨','변형','cong vênh','cong'],
 'missing_feature':['missing feature','missing material','material loss','형상 누락','재료 결손','가장자리 일부가 빠져','thiếu liệu','thiếu vật liệu'],
 'hole_diameter':['hole diameter','구멍 지름','구멍 크기','đường kính lỗ'],
 'hole_misalignment':['hole alignment','misalignment','구멍 위치','lỗ không khớp'],
 'thickness':['thickness','두께','độ dày'],
 'burr':['burr','날카로운','ba via'],
 'corrosion':['corrosion','rust','부식','녹이','ăn mòn'],
 'discoloration':['discoloration','변색','색상이','đổi màu'],
 'coating_peel':['peeling','코팅','bong tróc','lớp phủ'],
 'size_mismatch':['overall dimensions','전체 치수','kích thước tổng thể'],
 'assembly_interference':['interference','간섭','조립 중','bị vướng'],
 'loose_fit':['loose','흔들','유격','bị lỏng'],
 'wrong_model':['wrong model','오배송','다른 모델','다른 제품','giao sai mẫu'],
 'wrong_quantity':['quantity','수량','số lượng'],
 'packaging_damage':['packaging','포장','bao bì'],
 'contamination':['contamination','oil','기름','이물','dị vật'],
 'repeat_issue':['recurr','repeated','반복','lặp lại'],
}
def retrieve(query, model=None, category=None, k=5, include_examples=False, include_unconfirmed=False):
    if k<1:raise ValueError('k must be positive')
    docs=[json.loads(l) for l in (ROOT/'rag/documents.jsonl').read_text(encoding='utf-8').splitlines() if l]
    m=(model.upper().replace('-','').replace(' ','')) if model else None
    if m and m not in {'A156','A176','A276','A376'}:raise ValueError('Unknown product model')
    if category and category not in ALIASES:raise ValueError('Unknown category')
    docs=[d for d in docs if (include_examples or not d['synthetic']) and (not m or d.get('product_model') in [None,m])]
    if not include_unconfirmed:
        docs=[d for d in docs if d.get('annotation_status')!='source_roi_requires_confirmation']
    if category:docs=[d for d in docs if d.get('category') in [None,category]]
    corpus=[tokens(d['text']) for d in docs];df=collections.Counter(t for ts in corpus for t in set(ts));N=len(docs)
    avg=sum(map(len,corpus))/max(N,1);q=tokens(query)
    inferred={c for c,als in ALIASES.items() if any(normalize(a) in normalize(query) for a in als)}
    if category:inferred={category}
    ranked=[]
    for d,ts in zip(docs,corpus):
        tf=collections.Counter(ts);score=0
        for t in set(q):
            f=tf[t]
            if f:
                idf=math.log(1+(N-df[t]+.5)/(df[t]+.5));score+=idf*f*2.2/(f+1.2*(.25+.75*len(ts)/max(avg,1)))
        if d.get('category') in inferred:score+=15
        if score>0 and m and d.get('product_model')==m:score+=1
        # Prefer an actionable guide over a loosely related marked photo.
        if d['kind']=='review_guide' and d.get('category') in inferred:score+=5
        if score>0:ranked.append({'score':round(score,5),**d})
    return sorted(ranked,key=lambda d:(-d['score'],d['id']))[:k]
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--query',required=True);p.add_argument('--model');p.add_argument('--category');p.add_argument('--k',type=int,default=5);p.add_argument('--include-examples',action='store_true')
    a=p.parse_args();print(json.dumps(retrieve(a.query,a.model,a.category,a.k,a.include_examples),ensure_ascii=False,indent=2))
