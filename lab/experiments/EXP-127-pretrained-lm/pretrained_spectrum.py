import numpy as np, torch, json
from transformers import AutoTokenizer, AutoModelForCausalLM
P=113
def power(W):
    sq=(np.abs(np.fft.fft(W.astype(np.float64),axis=0))**2).sum(1); return 2*sq[1:57]/P
out={}
for repo,rev in [("EleutherAI/pythia-160m","50f5173d932e8e61f858120bcb800b97af589f46"),("openai-community/gpt2","607a30d783dfa663caf39e06633721c8d4cfcd7e")]:
    tok=AutoTokenizer.from_pretrained(repo,revision=rev); m=AutoModelForCausalLM.from_pretrained(repo,revision=rev)
    ids=[tok.encode(f" {n}",add_special_tokens=False)[0] for n in range(P)]
    for side,W in (("in",m.get_input_embeddings().weight),("out",m.get_output_embeddings().weight)):
        X=W.detach()[ids].numpy(); pw=power(X); sh=pw/pw.sum()
        top=np.argsort(sh)[::-1][:8]+1
        out[f"{repo}:{side}"]={"top8":top.tolist(),"share":[round(float(sh[k-1]),3) for k in top],"top5_share":round(float(np.sort(sh)[::-1][:5].sum()),3),
          "k11":round(float(sh[10]),3),"k23":round(float(sh[22]),3),"k45":round(float(sh[44]),3),"k56":round(float(sh[55]),3)}
        print(repo,side,out[f"{repo}:{side}"])
targets={s:json.load(open(f"lab/confirm/lm1_splits/seed{s}.json"))["targets"] for s in (4000,4001)}
print(targets)
json.dump(out,open("lab/experiments/EXP-127-pretrained-lm/pretrained_spectrum.json","w"),indent=1)
