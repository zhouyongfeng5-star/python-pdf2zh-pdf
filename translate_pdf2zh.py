from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


WORK_DIR = Path(__file__).resolve().parent
PDF2ZH_HOME = WORK_DIR / ".pdf2zh_home"
DEFAULT_OUTPUT_DIR = WORK_DIR / "translated"


def prepare_pdf2zh_home() -> None:
    """Keep pdf2zh cache/config files in this project folder."""
    PDF2ZH_HOME.mkdir(parents=True, exist_ok=True)

    # pdf2zh initializes its SQLite cache during import. On some Windows setups,
    # the default home path can fail to open, so set these before importing it.
    os.environ["USERPROFILE"] = str(PDF2ZH_HOME)
    os.environ["HOME"] = str(PDF2ZH_HOME)


def collect_pdf_files(source: Path, recursive: bool) -> list[Path]:
    if source.is_file():
        if source.suffix.lower() != ".pdf":
            raise ValueError(f"输入文件不是 PDF: {source}")
        return [source]

    if source.is_dir():
        pattern = "**/*.pdf" if recursive else "*.pdf"
        return sorted(path for path in source.glob(pattern) if path.is_file())

    raise FileNotFoundError(f"找不到输入路径: {source}")


def parse_pages(raw_pages: str | None) -> list[int] | None:
    if not raw_pages:
        return None

    pages: set[int] = set()
    for part in raw_pages.split(","):
        part = part.strip()
        if not part:
            continue

        if "-" in part:
            start_text, end_text = part.split("-", 1)
            start = int(start_text)
            end = int(end_text)
            if start <= 0 or end <= 0 or end < start:
                raise ValueError(f"页码范围无效: {part}")
            pages.update(range(start - 1, end))
        else:
            page = int(part)
            if page <= 0:
                raise ValueError(f"页码必须从 1 开始: {part}")
            pages.add(page - 1)

    return sorted(pages)


def translate_pdfs(
    source: Path,
    output_dir: Path,
    service: str,
    lang_in: str,
    lang_out: str,
    thread: int,
    recursive: bool,
    pages: list[int] | None,
    onnx: str | None,
) -> list[tuple[str, str]]:
    prepare_pdf2zh_home()

    from pdf2zh import translate
    from pdf2zh.doclayout import ModelInstance, OnnxModel

    pdf_files = collect_pdf_files(source, recursive)
    if not pdf_files:
        raise ValueError(f"没有找到 PDF 文件: {source}")

    output_dir.mkdir(parents=True, exist_ok=True)
    if onnx:
        ModelInstance.value = OnnxModel(onnx)
    elif ModelInstance.value is None:
        ModelInstance.value = OnnxModel.load_available()

    print(f"待翻译 PDF 数量: {len(pdf_files)}")
    print(f"输出目录: {output_dir}")
    print(f"翻译服务: {service}")
    print()

    results: list[tuple[str, str]] = []
    for index, pdf_file in enumerate(pdf_files, start=1):
        print(f"[{index}/{len(pdf_files)}] 翻译: {pdf_file}")
        translated = translate(
            files=[str(pdf_file)],
            output=str(output_dir),
            pages=pages,
            lang_in=lang_in,
            lang_out=lang_out,
            service=service,
            thread=thread,
            model=ModelInstance.value,
        )
        results.extend(translated)

    return results


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="使用 pdf2zh 将单个 PDF 或文件夹内的 PDF 批量翻译成中文。"
    )
    parser.add_argument("source", help="PDF 文件路径，或包含 PDF 的文件夹路径")
    parser.add_argument(
        "-o",
        "--output",
        default=str(DEFAULT_OUTPUT_DIR),
        help=f"输出目录，默认: {DEFAULT_OUTPUT_DIR}",
    )
    parser.add_argument(
        "-s",
        "--service",
        default="google",
        help="翻译服务，例如 google、bing、deepl、openai、ollama 等，默认: google",
    )
    parser.add_argument("--lang-in", default="en", help="源语言，默认: en")
    parser.add_argument("--lang-out", default="zh", help="目标语言，默认: zh")
    parser.add_argument("-t", "--thread", type=int, default=4, help="线程数，默认: 4")
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="输入为文件夹时，递归处理子文件夹中的 PDF",
    )
    parser.add_argument(
        "--pages",
        help="只翻译指定页，页码从 1 开始，例如: 1,3,5-8",
    )
    parser.add_argument(
        "--onnx",
        help="指定本地 doclayout ONNX 模型路径；不填则自动下载/使用缓存模型",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        results = translate_pdfs(
            source=Path(args.source).expanduser().resolve(),
            output_dir=Path(args.output).expanduser().resolve(),
            service=args.service,
            lang_in=args.lang_in,
            lang_out=args.lang_out,
            thread=args.thread,
            recursive=args.recursive,
            pages=parse_pages(args.pages),
            onnx=args.onnx,
        )
    except Exception as exc:
        print(f"翻译失败: {exc}", file=sys.stderr)
        return 1

    print()
    print("翻译完成，生成文件:")
    for mono_file, dual_file in results:
        print(f"- 仅译文: {mono_file}")
        print(f"- 双语版: {dual_file}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
