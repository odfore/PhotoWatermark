# PhotoWatermark

一个用于给图片添加时间水印的Python命令行工具。

## 功能

- 从图片EXIF信息中提取拍摄时间作为水印文本
- 可自定义字体大小、颜色和位置
- 自动创建输出目录保存添加水印后的图片

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

```bash
python photo_watermark.py [-h] [-s FONT_SIZE] [-c FONT_COLOR [FONT_COLOR ...]] [-p {top-left,top-right,bottom-left,bottom-right,center}] image_path
```

### 参数说明

- `image_path`: 图片文件路径 (必需)
- `-s FONT_SIZE`, `--font-size FONT_SIZE`: 字体大小 (默认: 20)
- `-c FONT_COLOR [FONT_COLOR ...]`, `--font-color FONT_COLOR [FONT_COLOR ...]`: 字体颜色 RGB值 (默认: 255 255 255)
- `-p {top-left,top-right,bottom-left,bottom-right,center}`, `--position {top-left,top-right,bottom-left,bottom-right,center}`: 水印位置 (默认: bottom-right)

### 示例

```bash
# 基本使用
python photo_watermark.py /path/to/image.jpg

# 自定义字体大小和颜色
python photo_watermark.py /path/to/image.jpg -s 30 -c 255 0 0

# 自定义位置
python photo_watermark.py /path/to/image.jpg -p top-left
```

## 输出

程序会在原图片所在目录创建一个名为`[原文件名]_watermark`的子目录，并将添加水印后的图片保存在该目录中。