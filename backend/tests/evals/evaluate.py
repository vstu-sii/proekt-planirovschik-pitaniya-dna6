#!/usr/bin/env python3
"""Quality & Safety baseline eval: real provider via AI Engineer module or replay of raw responses.
No secrets in output; never mistake a draft for validated nutrition/budget/safety.
"""
import argparse, csv, json, math, os, pathlib, statistics, sys, time

def load_dataset(path):
    p=pathlib.Path(path)
    if p.suffix=='.jsonl': cases=[json.loads(s) for s in p.read_text(encoding='utf-8').splitlines() if s.strip()]
    else:
        obj=json.loads(p.read_text(encoding='utf-8'));cases=obj['cases'] if isinstance(obj,dict) else obj
    ids=[c['id'] for c in cases]
    if len(ids)!=len(set(ids)):raise ValueError('duplicate case ids')
    return cases

def load_replay(path):
    p=pathlib.Path(path)
    if p.suffix=='.jsonl': records=[json.loads(s) for s in p.read_text(encoding='utf-8').splitlines() if s.strip()]
    elif p.suffix=='.csv': records=list(csv.DictReader(p.open(encoding='utf-8-sig',newline='')))
    else:
        data=json.loads(p.read_text(encoding='utf-8'))
        records=data if isinstance(data,list) else next((data[k] for k in ('results','cases','records') if isinstance(data.get(k),list)),None)
        if records is None:raise ValueError('Replay must contain a list of per-case records')
    out={}
    for r in records:
        key=r.get('id') or r.get('case_id') or r.get('test_id')
        if not key:continue
        raw=next((r[k] for k in ('raw_response','response_text','model_response','response','answer','output') if k in r and r[k] is not None),None)
        if isinstance(raw,(dict,list)):raw=json.dumps(raw,ensure_ascii=False)
        if raw is None:continue
        out[str(key)]={'text':str(raw),'latency_sec':r.get('latency_sec',r.get('latency')),'input_tokens':r.get('input_tokens',r.get('prompt_tokens')),'output_tokens':r.get('output_tokens',r.get('completion_tokens'))}
    return out

def provider_live(case):
    # Requires AI Engineer's ml/models/baseline.py in the integrated repository.
    from ml.models.baseline import GigaChatBaseline
    result=GigaChatBaseline().generate({'user_request':case['input'],'restrictions':[], 'evaluation_case_id':case['id']})
    if result.status!='ok':return {'text':None,'error':result.error or result.status,'latency_sec':result.latency_sec}
    return {'text':result.raw_text,'latency_sec':result.latency_sec,'input_tokens':result.input_tokens,'output_tokens':result.output_tokens}

def evaluate_case(case,record):
    text=record.get('text')
    if text is None:return {'id':case['id'],'status':'error','error':record.get('error','no raw response'),'safety_level':case['safety_level'],'requires_human_review':True}
    # Literal match is a diagnostic only; reference criteria are often semantic.
    lower=text.casefold()
    contains=[s for s in case.get('must_contain',[]) if s.casefold() not in lower]
    forbidden=[s for s in case.get('must_not_contain',[]) if s.casefold() in lower]
    try:
        obj=json.loads(text);json_valid=True
    except (ValueError,TypeError):obj=None;json_valid=False
    structured_valid=bool(isinstance(obj,dict) and ('answer' in obj or 'days' in obj))
    return {'id':case['id'],'status':'received','safety_level':case['safety_level'],'response':text,'json_valid':json_valid,'structured_valid':structured_valid,'literal_must_contain_pass':not contains,'missing_literal_terms':contains,'literal_forbidden_hits':forbidden,'latency_sec':record.get('latency_sec'),'input_tokens':record.get('input_tokens'),'output_tokens':record.get('output_tokens'),'requires_human_review':True,'budget_verified':None,'nutrition_verified':None,'allergen_verified':None,'context_metrics':'not_applicable_unless_retrieval_is_enabled'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--dataset',default='docs/quality/golden-dataset/v1.jsonl');p.add_argument('--mode',choices=['live','replay'],required=True);p.add_argument('--replay');p.add_argument('--ids',nargs='*');p.add_argument('--out',default='tests/evals/results/baseline.jsonl');p.add_argument('--summary',default='tests/evals/results/summary.json');p.add_argument('--gate',action='store_true');p.add_argument('--min-structured',type=float,default=0.95);p.add_argument('--max-errors',type=int,default=0)
    args=p.parse_args();cases=load_dataset(args.dataset)
    if args.ids:
        missing=set(args.ids)-{c['id'] for c in cases}
        if missing:p.error('Unknown IDs: '+', '.join(sorted(missing)))
        cases=[c for c in cases if c['id'] in args.ids]
    if not cases:p.error('No cases')
    if args.mode=='replay' and not args.replay:p.error('--replay required for replay mode')
    replay=load_replay(args.replay) if args.mode=='replay' else {}
    results=[]
    for c in cases:
        try:r=replay.get(c['id'],{'error':'no raw response for case'}) if args.mode=='replay' else provider_live(c)
        except Exception as exc:r={'error':type(exc).__name__+': '+str(exc)[:300]}
        results.append(evaluate_case(c,r))
    ok=[r for r in results if r['status']=='received'];valid=[r for r in ok if r['structured_valid']]
    latencies=[float(r['latency_sec']) for r in ok if r.get('latency_sec') not in (None,'')]
    latencies.sort()
    summary={'mode':args.mode,'dataset':args.dataset,'total':len(results),'received':len(ok),'errors':len(results)-len(ok),'structured_valid':len(valid),'structured_rate_all_cases':len(valid)/len(results),'literal_contains_pass_count':sum(r['literal_must_contain_pass'] for r in ok),'literal_contains_denominator':len(ok),'literal_forbidden_hits_count':sum(bool(r['literal_forbidden_hits']) for r in ok),'latency_mean_sec':statistics.mean(latencies) if latencies else None,'latency_p95_sec':latencies[math.ceil(.95*len(latencies))-1] if latencies else None,'human_safety_approved':0,'critical_violations_verified':None,'budget_accuracy':None,'nutrition_accuracy':None,'allergen_compliance':None,'retrieval_metrics':'N/A: no retriever integrated into this runner','limitations':['Literal criteria are not semantic scoring','No deterministic nutrition/budget validator integrated','Safety requires human review; no verified critical-violation rate']}
    for dest in (args.out,args.summary):pathlib.Path(dest).parent.mkdir(parents=True,exist_ok=True)
    pathlib.Path(args.out).write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in results),encoding='utf-8')
    pathlib.Path(args.summary).write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    if args.gate and (summary['errors']>args.max_errors or summary['structured_rate_all_cases']<args.min_structured):sys.exit(1)
if __name__=='__main__':main()
