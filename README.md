# ATC Dataset Tool

用于 ATC 音频数据准备的工具目录。

## 目录结构

```text
atc_dataset_tool/
├─ 01_raw_audio/
├─ 02_wav_audio/
├─ 03_label_studio_exports/
├─ 04_dataset_json/
├─ convert_audio_to_wav.py
├─ convert_label_studio_export.py
└─ start_label_studio.bat
```

推荐约定：

- 原始音频统一放到 `01_raw_audio`
- 转换后的 `.wav` 输出到 `02_wav_audio`
- Label Studio 导出的原始 JSON 放到 `03_label_studio_exports`
- 整理后的数据集 JSON 输出到 `04_dataset_json`

## 使用前提

先激活你自己的环境：

```powershell
conda activate your_env_name
```

## 安装依赖

```powershell
conda activate your_env_name
conda install -c conda-forge ffmpeg
pip install torch torchaudio label-studio
```

验证：

```powershell
where ffmpeg
python -c "import torch, torchaudio; print(torch.__version__)"
label-studio --version
```

## 最简单的推荐流程

### 1. 把原始音频放进固定目录

把所有待处理音频放进：

```text
.\01_raw_audio
```

### 2. 统一转换成 WAV

```powershell
python .\convert_audio_to_wav.py ".\01_raw_audio" --output-root ".\02_wav_audio"
```

### 3. 启动 Label Studio

```powershell
.\start_label_studio.bat
```

或：

```powershell
label-studio start
```

启动后访问：

```text
http://localhost:8080
```

### 4. 导出标注结果

把 Label Studio 导出的 JSON 文件统一保存到：

```text
.\03_label_studio_exports
```

### 5. 整理成扁平数据集 JSON

```powershell
python .\convert_label_studio_export.py ".\03_label_studio_exports\project.json" --output-dir ".\04_dataset_json"
```

## 脚本说明

### convert_audio_to_wav.py

用途：

- 递归扫描输入目录
- 把常见音频格式统一转成 `.wav`
- 支持输出到独立目录，并保留原有相对目录结构

默认支持：

- `.aac`
- `.mp3`
- `.m4a`
- `.wav`
- `.flac`
- `.ogg`
- `.opus`
- `.wma`
- `.mp4`
- `.webm`

常用参数：

- `--output-root`
  指定统一输出目录
- `--overwrite`
  覆盖已存在的 `.wav`
- `--extensions`
  自定义处理扩展名
- `--ffmpeg`
  手动指定 `ffmpeg.exe`

推荐用法：

```powershell
python .\convert_audio_to_wav.py ".\01_raw_audio" --output-root ".\02_wav_audio"
```

其他示例：

```powershell
python .\convert_audio_to_wav.py ".\01_raw_audio" --output-root ".\02_wav_audio" --overwrite
```

```powershell
python .\convert_audio_to_wav.py ".\01_raw_audio" --output-root ".\02_wav_audio" --extensions .aac .mp3 .amr
```

说明：

- 如果源文件本身是 `.wav`，脚本会复制到输出目录，而不是重复转码
- 默认跳过已存在的目标文件
- 单个文件失败不会中断整个批处理

### convert_label_studio_export.py

用途：

- 把 Label Studio 导出的 JSON 整理成扁平数据
- 一条音频片段对应一条记录

输出字段：

- `id`
- `project_id`
- `task_id`
- `annotation_id`
- `region_id`
- `audio`
- `start`
- `end`
- `text`
- `speaker`
- `language`
- `label`

规则：

- `audio` 优先提取原始文件名
- 默认只读取正式 `annotations`
- 自动忽略 `drafts`
- `id` 使用组合规则，避免跨任务冲突

常用参数：

- `--output-dir`
  指定统一输出目录
- `-o`
  手动指定输出文件
- `--indent`
  控制 JSON 缩进

推荐用法：

```powershell
python .\convert_label_studio_export.py ".\03_label_studio_exports\project.json" --output-dir ".\04_dataset_json"
```

其他示例：

```powershell
python .\convert_label_studio_export.py ".\03_label_studio_exports\project.json" -o ".\04_dataset_json\dataset.json"
```

```powershell
python .\convert_label_studio_export.py ".\03_label_studio_exports\project.json" --output-dir ".\04_dataset_json" --indent 4
```

## 推荐工作流

1. 原始音频放进 `01_raw_audio`
2. 用 `convert_audio_to_wav.py` 统一输出到 `02_wav_audio`
3. 在 Label Studio 中导入 `02_wav_audio`
4. 导出 JSON 到 `03_label_studio_exports`
5. 用 `convert_label_studio_export.py` 整理到 `04_dataset_json`

