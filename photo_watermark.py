#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import argparse
from PIL import Image, ImageDraw, ImageFont
from PIL.ExifTags import TAGS
from datetime import datetime


def get_exif_data(image_path):
    """从图片中提取EXIF数据"""
    try:
        image = Image.open(image_path)
        exif_data = image._getexif()
        if exif_data is not None:
            return {TAGS.get(tag, tag): value for tag, value in exif_data.items()}
    except Exception as e:
        print(f"读取EXIF数据时出错: {e}")
        return None
    return None


def extract_datetime(exif_data):
    """从EXIF数据中提取拍摄时间"""
    if not exif_data:
        return None
    
    # 尝试获取拍摄时间
    datetime_str = exif_data.get('DateTimeOriginal') or exif_data.get('DateTime')
    if datetime_str:
        try:
            # 解析时间字符串
            dt = datetime.strptime(datetime_str, '%Y:%m:%d %H:%M:%S')
            # 返回年月日格式
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            pass
    return None


def create_watermark_text(image_path):
    """为图片创建水印文本"""
    exif_data = get_exif_data(image_path)
    if exif_data:
        date_text = extract_datetime(exif_data)
        if date_text:
            return date_text
    # 如果无法获取EXIF时间信息，则使用文件修改时间
    try:
        mtime = os.path.getmtime(image_path)
        mdate = datetime.fromtimestamp(mtime)
        return mdate.strftime('%Y-%m-%d')
    except Exception:
        pass
    # 如果都无法获取时间，则返回默认文本
    return "Unknown Date"


def add_watermark(image_path, output_path, watermark_text, font_size=20, 
                  font_color=(255, 255, 255), position='bottom-right'):
    """在图片上添加水印"""
    try:
        # 打开图片
        image = Image.open(image_path).convert('RGBA')
        width, height = image.size
        
        # 创建水印图层
        watermark_layer = Image.new('RGBA', image.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(watermark_layer)
        
        # 尝试使用系统字体，如果失败则使用默认字体
        try:
            # 在不同系统上尝试不同的字体路径
            if sys.platform == "darwin":  # macOS
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", font_size)
            elif sys.platform.startswith("win"):  # Windows
                font = ImageFont.truetype("arial.ttf", font_size)
            else:  # Linux
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
        except:
            # 使用默认字体
            font = ImageFont.load_default()
        
        # 计算文本尺寸
        bbox = draw.textbbox((0, 0), watermark_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # 根据位置参数确定水印位置
        margin = 10
        if position == 'top-left':
            x, y = margin, margin
        elif position == 'top-right':
            x, y = width - text_width - margin, margin
        elif position == 'bottom-left':
            x, y = margin, height - text_height - margin
        elif position == 'center':
            x, y = (width - text_width) // 2, (height - text_height) // 2
        else:  # 默认为右下角
            x, y = width - text_width - margin, height - text_height - margin
        
        # 绘制水印
        draw.text((x, y), watermark_text, font=font, fill=font_color)
        
        # 合并图层
        watermarked_image = Image.alpha_composite(image, watermark_layer)
        
        # 转换为RGB模式以保存为JPEG等格式
        watermarked_image = watermarked_image.convert('RGB')
        
        # 保存图片
        watermarked_image.save(output_path)
        print(f"水印已添加并保存到: {output_path}")
        
    except Exception as e:
        print(f"添加水印时出错: {e}")


def process_image(image_path, font_size, font_color, position):
    """处理单个图片"""
    if not os.path.exists(image_path):
        print(f"错误: 文件不存在: {image_path}")
        return
    
    # 获取水印文本
    watermark_text = create_watermark_text(image_path)
    print(f"使用水印文本: {watermark_text}")
    
    # 确定输出目录
    dir_name = os.path.dirname(image_path)
    file_name = os.path.basename(image_path)
    name, ext = os.path.splitext(file_name)
    
    # 创建_watermark子目录
    watermark_dir = os.path.join(dir_name, f"{name}_watermark")
    if not os.path.exists(watermark_dir):
        os.makedirs(watermark_dir)
    
    # 确定输出文件路径
    output_path = os.path.join(watermark_dir, file_name)
    
    # 添加水印
    add_watermark(image_path, output_path, watermark_text, font_size, font_color, position)


def main():
    parser = argparse.ArgumentParser(description='为图片添加时间水印')
    parser.add_argument('image_path', help='图片文件路径')
    parser.add_argument('-s', '--font-size', type=int, default=20, help='字体大小 (默认: 20)')
    parser.add_argument('-c', '--font-color', nargs=3, type=int, default=[255, 255, 255], 
                        help='字体颜色 RGB值 (默认: 255 255 255)')
    parser.add_argument('-p', '--position', 
                        choices=['top-left', 'top-right', 'bottom-left', 'bottom-right', 'center'],
                        default='bottom-right', help='水印位置 (默认: bottom-right)')
    
    args = parser.parse_args()
    
    # 解析颜色参数
    font_color = tuple(args.font_color)
    
    # 处理图片
    process_image(args.image_path, args.font_size, font_color, args.position)


if __name__ == '__main__':
    main()