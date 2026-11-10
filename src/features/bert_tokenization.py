"""Encode a known error span with markers while preserving it during cropping.

Shared by the BERT experiment runner; no model loading or training side effects.
"""

def encode_span(row,tokenizer,max_length=128):
    text=row['sentence']; start,end=row['error_start'],row['error_end']
    if not 0<=start<=end<=len(text) or text[start:end]!=row['error_span']: raise ValueError('Invalid original span')
    # Three regions preserve the complete annotated span even at partial-token boundaries.
    left=tokenizer.encode(text[:start],add_special_tokens=False)
    span=tokenizer.encode(text[start:end],add_special_tokens=False)
    right=tokenizer.encode(text[end:],add_special_tokens=False)
    budget=max_length-4-len(span)
    if budget<0: raise ValueError('Annotated span exceeds available sequence budget')
    nl=min(len(left),budget//2); nr=min(len(right),budget-nl)
    nl=min(len(left),budget-nr)
    ids=[tokenizer.cls_token_id]+(left[-nl:] if nl else [])+[tokenizer.convert_tokens_to_ids('[SPAN_START]')]+span+[tokenizer.convert_tokens_to_ids('[SPAN_END]')]+right[:nr]+[tokenizer.sep_token_id]
    assert len(ids)<=max_length
    return {'input_ids':ids,'attention_mask':[1]*len(ids)}, {'truncated':nl<len(left) or nr<len(right),'original_subwords':len(left)+len(span)+len(right)+4,'span_subwords':len(span)}
