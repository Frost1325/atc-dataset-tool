# ATC Dataset Tool

用于 ATC 音频数据集准备的工具集合。

## 文件

- `convert_audio_to_wav.py`
- `convert_label_studio_export.py`
- `start_label_studio.bat`

## 使用前提

先激活你的 conda 环境，再运行脚本。

```powershell
conda activate your_env_name
```

## 统一安装依赖

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

说明：

- `ffmpeg` 用于音频格式转换
- `label-studio` 用于标注
- `torch` 和 `torchaudio` 作为后续音频处理和数据集脚本的通用依赖

## 最简单的用法

### 1. 转换音频到 WAV

```powershell
python .\convert_audio_to_wav.py "D:\path\to\your\audio_folder"
```

### 2. 整理 Label Studio 导出

```powershell
python .\convert_label_studio_export.py ".\project.json"
```

### 3. 启动 Label Studio

```powershell
.\start_label_studio.bat
```

或：

```powershell
label-studio start
```

访问：

```text
http://localhost:8080
```

## 扩展功能

### convert_audio_to_wav.py

用途：

- 递归扫描目录
- 把常见音频格式统一转成 `.wav`
- 输出到原文件所在目录

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

参数：

- `--overwrite`
  覆盖已存在的 `.wav`
- `--extensions`
  自定义本次处理的扩展名
- `--ffmpeg`
  手动指定 `ffmpeg.exe` 路径

示例：

```powershell
python .\atc_dataset_tool\convert_audio_to_wav.py "D:\audio" --overwrite
```

```powershell
python .\atc_dataset_tool\convert_audio_to_wav.py "D:\audio" --extensions .aac .mp3 .amr
```

```powershell
python .\atc_dataset_tool\convert_audio_to_wav.py "D:\audio" --ffmpeg "D:\tools\ffmpeg\bin\ffmpeg.exe"
```

特点：

- 默认跳过已存在的 `.wav`
- 单个文件失败不会中断整个批处理
- 启动时会打印本次匹配的扩展名

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

- `id` 使用组合规则，避免跨任务冲突
- 默认只读取正式 `annotations`
- 自动忽略 `drafts`

参数：

- `-o`
  自定义输出文件
- `--indent`
  控制输出 JSON 缩进

示例：

```powershell
python .\atc_dataset_tool\convert_label_studio_export.py ".\project.json" -o ".\dataset.json"
```

```powershell
python .\atc_dataset_tool\convert_label_studio_export.py ".\project.json" --indent 4
```

输出示例：

```json
[
  {
    "id": "project1_task3_annotation2_VwtOD",
    "project_id": 1,
    "task_id": 3,
    "annotation_id": 2,
    "region_id": "VwtOD",
    "audio": "example.wav",
    "start": 70.84401659751036,
    "end": 155.10546058091288,
    "text": "ababa",
    "speaker": "ATC",
    "language": "zh",
    "label": "Speech"
  }
]
```
