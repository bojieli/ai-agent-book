"""实验 6-5：全自动 TTS 质量评估流水线 —— 一条命令跑通。

    python demo.py                      # 默认 4 个 OpenAI 配置 x 4 条语料
    python demo.py --providers openai,minimax   # 跨服务商横向对比
    python demo.py --text '一段话'       # 自定义文本
    python demo.py --gemini             # 评审改用 Gemini 多模态直接听音频（需 GEMINI_API_KEY）
    python demo.py --quick              # 只用前 2 条语料，快速冒烟
    python demo.py --list-providers     # 离线：查看 provider 及配置状态
    python demo.py --dump-rubric        # 离线：查看 Rubric 维度定义

流程：多 provider TTS 合成 -> ffprobe 时长 -> Whisper 回译 -> CER/字准确率
      -> LLM/Gemini Rubric 打分 -> 打印逐条明细 + 配置对比汇总表。
幂等：音频写入 output/ 并复用（除非 --fresh）。完整参数见 `python demo.py --help`。
"""

import argparse
import json
import os
import sys
import time
import traceback
from statistics import mean

import config
import pipeline

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")


def load_env():
    """极简 .env 加载（不引第三方依赖）。"""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def audio_path(cfg_name: str, sample_id: str) -> str:
    return os.path.join(OUT_DIR, f"{cfg_name}__{sample_id}.mp3")


def evaluate_one(cfg, sample, use_gemini: bool, fresh: bool,
                 judge_model: str = None) -> dict:
    """对单个 (配置, 语料) 跑完整链路。任一步失败返回 error 记录，不抛出。"""
    rec = {"config": cfg.name, "sample": sample.id, "challenge": sample.challenge,
           "provider": getattr(cfg, "provider", "openai"), "ok": False, "error": None}
    path = audio_path(cfg.name, sample.id)
    try:
        # 1) 合成（幂等：已存在且非 fresh 则复用）
        if fresh or not os.path.exists(path) or os.path.getsize(path) == 0:
            pipeline.synthesize(cfg, sample.text, path)
        # 2) 时长
        dur = pipeline.probe_duration(path)
        # 3) 回译
        hyp = pipeline.transcribe(path)
        # 4) CER / 字准确率
        er = pipeline.char_error_rate(sample.text, hyp)
        # 5) Rubric 打分
        if use_gemini:
            rub = pipeline.judge_gemini_audio(sample.text, sample.emotion, path)
        else:
            rub = pipeline.judge_rubric(sample.text, sample.emotion, hyp, dur, er.cer,
                                        model=judge_model)
        rec.update({
            "ok": True, "duration": dur, "hypothesis": hyp,
            "cer": er.cer, "accuracy": er.accuracy,
            "speed": (er.ref_len / dur) if dur else 0.0,
            "scores": rub.scores, "reasons": rub.reasons,
        })
    except Exception as e:  # 单条失败不影响整表
        rec["error"] = f"{type(e).__name__}: {e}"
    return rec


def fmt(x, nd=2):
    return f"{x:.{nd}f}" if isinstance(x, (int, float)) else str(x)


def print_detail(rec, sample_text):
    head = f"[{rec['config']} | {rec['sample']}] {rec['challenge']}"
    if not rec["ok"]:
        print(f"  {head}\n    !! 失败: {rec['error']}")
        return
    print(f"  {head}")
    print(f"    原文  : {sample_text}")
    print(f"    回译  : {rec['hypothesis']}")
    print(f"    时长  : {fmt(rec['duration'])}s   语速: {fmt(rec['speed'])} 字/秒"
          f"   CER: {fmt(rec['cer'],3)}   字准确率: {fmt(rec['accuracy']*100,1)}%")
    s, r = rec["scores"], rec["reasons"]
    for dim in pipeline.RUBRIC_DIMENSIONS:
        print(f"    {dim:<4}: {s.get(dim,'-')}/5  {r.get(dim,'')}")


def summarize(records):
    """按配置聚合：平均 CER、平均字准确率、各 Rubric 维度均分、成功数。"""
    by_cfg = {}
    for rec in records:
        by_cfg.setdefault(rec["config"], []).append(rec)
    rows = []
    for cfg_name, recs in by_cfg.items():
        ok = [r for r in recs if r["ok"]]
        row = {"config": cfg_name, "n_ok": len(ok), "n": len(recs)}
        if ok:
            row["cer"] = mean(r["cer"] for r in ok)
            row["accuracy"] = mean(r["accuracy"] for r in ok)
            for dim in pipeline.RUBRIC_DIMENSIONS:
                row[dim] = mean(r["scores"].get(dim, 0) for r in ok)
        rows.append(row)
    # 按整体分降序、CER 升序排序
    rows.sort(key=lambda x: (-x.get("整体", 0), x.get("cer", 1)))
    return rows


def print_table(rows):
    cols = ["整体", "清晰度", "自然度", "停顿节奏"]
    header = (f"{'配置':<18}{'成功':>6}{'字准确率':>10}{'CER':>8}"
              + "".join(f"{c:>9}" for c in cols))
    print(header)
    print("-" * 74)
    for r in rows:
        ok_str = f"{r['n_ok']}/{r['n']}"
        if not r.get("n_ok"):
            print(f"{r['config']:<18}{ok_str:>6}   (全部失败)")
            continue
        acc = f"{r['accuracy']*100:.1f}%"
        line = f"{r['config']:<18}{ok_str:>6}{acc:>10}{r['cer']:>8.3f}"
        line += "".join(f"{r.get(c,0):>9.2f}" for c in cols)
        print(line)


def print_providers():
    """离线打印所有可用 TTS provider 及其配置状态（无需任何 API key）。"""
    print("可用 TTS provider（书中：OpenAI / ElevenLabs / Fish Audio / Minimax / 豆包）：\n")
    for key, p in config.PROVIDERS.items():
        state = "已配置" if p.configured() else "未配置"
        env = " + ".join(p.env)
        print(f"  [{key}]  {p.label}   ({state}；需 {env})")
        print(f"      {p.note}")
    print("\n用 --providers openai,minimax 选择跨服务商横向对比（默认仅 OpenAI）。")
    print("非 OpenAI provider 需各自的 key（见 env.example）；缺 key 时该行记为失败，不中断整表。")


def print_rubric():
    """离线打印 Rubric 维度定义（无需任何 API key）。"""
    print("TTS 质量评估 Rubric（1-5 分，5 最好）：\n")
    for dim in pipeline.RUBRIC_DIMENSIONS:
        print(f"  {dim}：{pipeline.RUBRIC_DESCRIPTIONS.get(dim, '')}")
    print("\n默认（Whisper 回译 + LLM）评审基于「转写文本 + 时长 + 语速 + CER」保守打分；")
    print("--gemini 让多模态模型直接听音频，可覆盖书中「情感表达 / 音色一致性」维度。")


def main():
    global OUT_DIR
    ap = argparse.ArgumentParser(
        description="全自动 TTS 质量评估流水线（实验 6-5）：多 provider 合成 + 多模态 LLM Rubric 评审",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="示例：\n"
               "  python demo.py                          默认 4 个 OpenAI 配置 × 4 条语料\n"
               "  python demo.py --providers openai,minimax   跨服务商横向对比\n"
               "  python demo.py --text '今天天气不错' --gemini   自定义文本 + Gemini 多模态评审\n"
               "  python demo.py --list-providers         离线查看 provider 及配置状态\n"
               "  python demo.py --dump-rubric            离线查看 Rubric 维度定义",
    )
    ap.add_argument("--text", metavar="文本",
                    help="用一段自定义文本替换测试语料库（只评这一句）")
    ap.add_argument("--providers", metavar="列表",
                    help="逗号分隔的 provider（openai,elevenlabs,fishaudio,minimax,doubao），"
                         "每个取代表性配置做横向对比；默认仅 OpenAI 的多配置")
    ap.add_argument("--judge-model", metavar="模型", dest="judge_model",
                    help=f"覆盖 LLM 评审模型（默认 {config.JUDGE_MODEL}）；--gemini 时不生效")
    ap.add_argument("--output", metavar="目录",
                    help=f"输出目录（音频 + results.json），默认 {OUT_DIR}")
    ap.add_argument("--extra", action="store_true", help="额外加入 gpt-4o-mini-tts 配置")
    ap.add_argument("--gemini", action="store_true", help="用 Gemini 多模态直接听音频评审（需 GEMINI_API_KEY）")
    ap.add_argument("--quick", action="store_true", help="只用前 2 条语料快速冒烟")
    ap.add_argument("--fresh", action="store_true", help="忽略已有音频，全部重新合成")
    ap.add_argument("--list-providers", action="store_true", dest="list_providers",
                    help="离线打印所有 TTS provider 及配置状态后退出（无需 key）")
    ap.add_argument("--dump-rubric", action="store_true", dest="dump_rubric",
                    help="离线打印 Rubric 维度定义后退出（无需 key）")
    args = ap.parse_args()

    load_env()

    # 离线路径：不联网、不需要任何 key，打印后直接退出。
    if args.list_providers:
        print_providers()
        return
    if args.dump_rubric:
        print_rubric()
        return

    if args.output:
        OUT_DIR = os.path.abspath(args.output)
    os.makedirs(OUT_DIR, exist_ok=True)

    if not os.environ.get("OPENAI_API_KEY", "").strip():
        print("错误：缺少 OPENAI_API_KEY（回译/默认评审需要）。请 export 或写入 .env 后重试。",
              file=sys.stderr)
        sys.exit(1)

    # 选择待对比的配置：--providers 优先（跨服务商），否则默认 OpenAI 多配置。
    if args.providers:
        configs = []
        for key in [p.strip() for p in args.providers.split(",") if p.strip()]:
            if key not in config.PROVIDER_CONFIGS:
                print(f"错误：未知 provider {key!r}。可用：{', '.join(config.PROVIDER_CONFIGS)}",
                      file=sys.stderr)
                sys.exit(1)
            configs.append(config.PROVIDER_CONFIGS[key])
    else:
        configs = list(config.TTS_CONFIGS)
        if args.extra:
            configs += config.EXTRA_CONFIGS

    if args.text:
        corpus = [config.Sample(id="custom", text=args.text,
                                challenge="自定义文本", emotion="中性")]
    else:
        corpus = config.CORPUS[:2] if args.quick else config.CORPUS

    judge_model = args.judge_model or config.JUDGE_MODEL
    mode = ("Gemini 多模态音频评审" if args.gemini
            else f"Whisper 回译 + LLM Rubric（{judge_model}）")
    providers_used = sorted({getattr(c, "provider", "openai") for c in configs})
    print("=" * 72)
    print(f"实验 6-5：全自动 TTS 质量评估流水线")
    print(f"评审模式：{mode}")
    print(f"参与 provider：{', '.join(providers_used)}")
    print(f"配置数：{len(configs)}   语料数：{len(corpus)}   "
          f"共 {len(configs)*len(corpus)} 条待评估")
    print("=" * 72)

    records = []
    t0 = time.time()
    for cfg in configs:
        print(f"\n### 配置 {cfg.name}  (provider={getattr(cfg,'provider','openai')}, "
              f"model={cfg.model}, voice={cfg.voice}, speed={cfg.speed})")
        for sample in corpus:
            rec = evaluate_one(cfg, sample, args.gemini, args.fresh,
                               judge_model=None if args.gemini else args.judge_model)
            print_detail(rec, sample.text)
            records.append(rec)

    rows = summarize(records)
    print("\n" + "=" * 72)
    print("配置对比汇总（按 整体 分降序）")
    print("=" * 72)
    print_table(rows)

    ok = sum(1 for r in records if r["ok"])
    print(f"\n完成：{ok}/{len(records)} 条成功，耗时 {time.time()-t0:.1f}s。")

    # 落盘结构化结果，便于二次分析
    out_json = os.path.join(OUT_DIR, "results.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump({"records": records, "summary": rows}, f,
                  ensure_ascii=False, indent=2)
    print(f"明细结果已写入 {out_json}")


if __name__ == "__main__":
    main()
