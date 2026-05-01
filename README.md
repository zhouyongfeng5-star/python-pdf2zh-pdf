# 使用 pdf2zh 批量翻译 PDF

这个目录里的 `translate_pdf2zh.py` 可以把单个 PDF，或一个文件夹内的 PDF 文件翻译成中文。

## 基本用法

翻译单个文件:

```powershell
python .\translate_pdf2zh.py "D:\papers\example.pdf"
```

翻译文件夹内的所有 PDF:

```powershell
python .\translate_pdf2zh.py "D:\papers"
```

递归翻译文件夹和子文件夹内的 PDF:

```powershell
python .\translate_pdf2zh.py "D:\papers" -r
```

指定输出目录:

```powershell
python .\translate_pdf2zh.py "D:\papers" -o "D:\papers_zh"
```

只翻译部分页码，页码从 1 开始:

```powershell
python .\translate_pdf2zh.py "D:\papers\example.pdf" --pages 1,3,5-8
```

指定本地 doclayout ONNX 模型:

```powershell
python .\translate_pdf2zh.py "D:\papers" --onnx "D:\models\doclayout_yolo_docstructbench_imgsz1024.onnx"
```

## 输出文件

每个 PDF 会生成两个文件:

- `xxx-mono.pdf`: 中文译文版
- `xxx-dual.pdf`: 原文和译文双语版

默认输出到当前目录下的 `translated` 文件夹。

## 翻译服务

默认使用 `google`:

```powershell
python .\translate_pdf2zh.py "D:\papers" -s google
```

也可以换成你本机 `pdf2zh` 支持的服务，例如:

```powershell
python .\translate_pdf2zh.py "D:\papers" -s bing
python .\translate_pdf2zh.py "D:\papers" -s deepl
python .\translate_pdf2zh.py "D:\papers" -s openai
python .\translate_pdf2zh.py "D:\papers" -s ollama
python .\translate_pdf2zh.py "D:\papers" -s deepseek
```

不同服务可能需要网络或 API Key。

### DeepSeek API

先在 CMD 里设置 DeepSeek API Key:

```cmd
set DEEPSEEK_API_KEY=你的DeepSeek_API_Key
set DEEPSEEK_MODEL=deepseek-chat
```

再运行翻译:

```cmd
python .\translate_pdf2zh.py "D:\papers" -s deepseek
```

递归翻译文件夹并指定输出目录:

```cmd
python .\translate_pdf2zh.py "D:\test_API\PDF_work" -r -o "D:\test_API\translate" -s deepseek
```

如果想长期保存环境变量，使用 `setx`:

```cmd
setx DEEPSEEK_API_KEY "你的DeepSeek_API_Key"
setx DEEPSEEK_MODEL "deepseek-chat"
```

使用 `setx` 后，需要关闭当前 CMD，重新打开一个新的 CMD 才会生效。

### 其他常见服务配置

DeepL:

```cmd
set DEEPL_AUTH_KEY=你的DeepL_API_Key
python .\translate_pdf2zh.py "D:\papers" -s deepl
```

OpenAI:

```cmd
set OPENAI_API_KEY=你的OpenAI_API_Key
set OPENAI_MODEL=gpt-4o-mini
python .\translate_pdf2zh.py "D:\papers" -s openai
```

Ollama:

```cmd
set OLLAMA_MODEL=gemma2
python .\translate_pdf2zh.py "D:\papers" -s ollama
```
