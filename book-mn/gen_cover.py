#!/usr/bin/env python3
"""Зураг үүсгэдэг Model ашиглан номын хавтасны зураг бүтээнэ.

Энэ нь ном өөрийн тайлбарлаж буй аргаа өөр дээрээ хэрэглэж буй сонирхолтой жишээ:
AI Agent-ийн тухай номын хавтсыг зураг үүсгэдэг Model дуудаж бүтээнэ.
Нэг удаа ажиллуулахад хангалттай. images/cover-image.png файл байвал хавтас
(cover.tex) автоматаар түүнийг ашиглана — өөр өөрчлөлт хэрэггүй.
Дараа нь хэвлэлийн тэмдэглэлд хавтсыг AI-ээр бүтээсэн гэдгийг дурьдаж болно.

Ашиглах заавар (анхдагч нь OpenAI):
    pip install openai
    export OPENAI_API_KEY=your-openai-api-key
    python gen_cover.py

Үйлчилгээ үзүүлэгч солих: доорх generate() функцийг засна. Tongyi Wanxiang
(DashScope), Jimeng/Kolors, Flux (fal / Replicate)-ийн загвар код, тэмдэглэл
байгаа тул боломжтойг нь сонго. Хамгийн чухал нь Prompt бөгөөд тодорхой
үйлчилгээ үзүүлэгчээс үл хамаарна.
"""
import os

# ── Prompt ────────────────────────────────────────────────────────────
# O’Reilly-ийн «амьтантай номын» хавтсыг хүндэтгэсэн загвар: цэвэр
# цагаан дэвсгэр дээрх сийлбэр маягийн нэг амьтан; cover.tex үүнийг сериф
# гарчгийн доор давхарлана. Наймаалж нь AI Agent-ийн номд тохирно —
# маш ухаалаг, Tool ашигладгаараа алдартай, хагас бие даасан найман тэмтрүүл
# ≈ нэг тархи + олон Tool/гар (бүр олон Agent). Өөр амьтан хүсвэл Prompt-д солино.
PROMPT = (
    "Vintage scientific engraving illustration of an octopus, in the classic style of "
    "19th-century natural-history woodcuts and the O'Reilly animal book covers. Finely "
    "detailed black pen-and-ink crosshatching and fine line work; pure black line art, "
    "no color, no gray wash, no shading fills. The whole octopus rendered elegantly with "
    "gracefully curling tentacles, anatomically believable, slightly stylized. Perfectly "
    "clean pure white background, no scenery, no frame, no border, no text, no lettering, "
    "no numbers. Centered composition, crisp, high detail."
)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images", "cover-image.png")


def generate_openai(prompt, out):
    """OpenAI Images API. Боломжтой бол gpt-image-1, үгүй бол dall-e-3 ашиглана."""
    from openai import OpenAI
    import base64, urllib.request
    client = OpenAI()
    try:
        # gpt-image-1: Prompt сайн дагана; b64 буцаана. Босоо зураг 1024x1536.
        r = client.images.generate(model="gpt-image-1", prompt=prompt,
                                    size="1024x1536", quality="high", n=1)
        data = base64.b64decode(r.data[0].b64_json)
        open(out, "wb").write(data)
    except Exception as e:
        print(f"gpt-image-1 unavailable ({e}); falling back to dall-e-3 …")
        r = client.images.generate(model="dall-e-3", prompt=prompt,
                                    size="1024x1792", quality="hd",
                                    style="natural", n=1)
        url = r.data[0].url
        urllib.request.urlretrieve(url, out)


# ── Өөр үйлчилгээ үзүүлэгчид (ашиглахын тулд тайлбарын тэмдгийг авч, тохируул) ──
# def generate_dashscope(prompt, out):   # Alibaba Tongyi Wanxiang (wanx)
#     import dashscope  # pip install dashscope ; export DASHSCOPE_API_KEY=...
#     rsp = dashscope.ImageSynthesis.call(model="wanx-v1", prompt=prompt,
#                                         n=1, size="1024*1536")
#     import urllib.request
#     urllib.request.urlretrieve(rsp.output.results[0].url, out)
#
# def generate_fal(prompt, out):         # Flux via fal.ai
#     import fal_client, urllib.request   # pip install fal-client ; export FAL_KEY=...
#     r = fal_client.run("fal-ai/flux-pro/v1.1",
#                        arguments={"prompt": prompt, "image_size": "portrait_4_3"})
#     urllib.request.urlretrieve(r["images"][0]["url"], out)


def generate(prompt, out):
    return generate_openai(prompt, out)   # ← энд өөрийн үйлчилгээ үзүүлэгчээр солино


if __name__ == "__main__":
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    print("Generating cover image …")
    generate(PROMPT, OUT)
    print(f"Saved {OUT}")
    print("Now rebuild:  bash build_pdf.sh   (cover.tex auto-detects the image)")
